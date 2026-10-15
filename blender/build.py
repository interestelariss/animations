"""Construye los modelos en Blender y exporta .blend, .glb, .json y un render.

Uso (con Blender instalado):
    blender -b -P blender/build.py -- [shark_dino|mailbox ...] [--samples N] [--res PX]
o con el módulo de Python `bpy` (pip install bpy):
    python blender/build.py [modelos...]
"""

import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Quaternion, Vector  # noqa: E402

import eggs  # noqa: E402
import eggs_themes  # noqa: E402
import mailbox_monster  # noqa: E402
import shark_dino  # noqa: E402
import tiers  # noqa: E402
import rebirth  # noqa: E402
import pets  # noqa: E402

MODELS = {
    "egg_celestial": eggs.build_celestial,
    "egg_ice": eggs.build_ice,
    "egg_inferno": eggs_themes.build_inferno,
    "egg_swamp": eggs_themes.build_swamp,
    "egg_galaxy": eggs_themes.build_galaxy,
    "egg_storm": eggs_themes.build_storm,
    "egg_sakura": eggs_themes.build_sakura,
    "shark_dino": shark_dino.build,
    "mailbox": mailbox_monster.build,
    **tiers.BUILDERS,
    **rebirth.BUILDERS,
    **pets.BUILDERS,
}

# rareza de los huevos destacados (los hechos a mano)
FEATURED = {
    "egg_celestial": ("Huevo Celestial", "legendario"),
    "egg_ice": ("Huevo de Hielo", "mitico"),
    "egg_inferno": ("Huevo Infernal", "mitico"),
    "egg_swamp": ("Huevo del Pantano", "epico"),
    "egg_galaxy": ("Huevo Galaxia", "legendario"),
    "egg_storm": ("Huevo Tormenta", "mitico"),
    "egg_sakura": ("Huevo Sakura", "legendario"),
}
OUT = os.path.join(os.path.dirname(HERE), "exports")

# Escenario y cámara de cada render (fondo, suelo, encuadre)
STAGES = {
    "shark_dino": dict(world=(0.012, 0.016, 0.03), floor="#0c1018", cam=(16, -20, 9), target=(0, 0, 4.2), lens=50),
    "egg_celestial": dict(world=(0.01, 0.012, 0.035), floor="#0b1024", cam=(13, -17, 9), target=(0, 0, 4.6), lens=45),
    "egg_ice": dict(world=(0.008, 0.015, 0.035), floor="#081428", cam=(13, -17, 9), target=(0, 0, 4.4), lens=45),
    "egg_inferno": dict(world=(0.03, 0.006, 0.004), floor="#120605", cam=(13, -17, 9), target=(0, 0, 4.6), lens=45),
    "egg_swamp": dict(world=(0.006, 0.02, 0.01), floor="#0e1a0f", cam=(13, -17, 9), target=(0, 0, 4.3), lens=45),
    "egg_galaxy": dict(world=(0.012, 0.006, 0.04), floor="#0a0618", cam=(13, -17, 9), target=(0, 0, 4.5), lens=45),
    "egg_storm": dict(world=(0.014, 0.018, 0.03), floor="#0b0e15", cam=(13, -17, 9), target=(0, 0, 4.6), lens=45),
    "egg_sakura": dict(world=(0.04, 0.015, 0.045), floor="#1a0f1c", cam=(13, -17, 9), target=(0, 0, 4.5), lens=45),
    "mailbox": dict(world=(0.45, 0.68, 0.95), floor="#5fb548", cam=(10, -13, 7.5), target=(0, 0, 4.2), lens=50),
}


def hex_rgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]


_STUD_IMG = None


def stud_image():
    """Mapa de relieve de un stud (botón tipo LEGO), generado una vez."""
    global _STUD_IMG
    if _STUD_IMG is None:
        n = 64
        img = bpy.data.images.new("stud_bump", n, n, alpha=False, float_buffer=False)
        px = []
        for y in range(n):
            for x in range(n):
                dx, dy = (x + 0.5) / n - 0.5, (y + 0.5) / n - 0.5
                r = math.hypot(dx, dy)
                h = 0.45 if (x < 2 or y < 2) else 0.5
                if r < 0.3:
                    h = 0.85 + 0.15 * (1 - r / 0.3)
                elif r < 0.34:
                    h = 0.3
                px.extend((h, h, h, 1.0))
        img.pixels.foreach_set(px)
        img.pack()
        _STUD_IMG = img
    return _STUD_IMG


def material(cache, col, emit, metal=0, studs=False):
    key = (col, emit, metal, studs)
    if key in cache:
        return cache[key]
    mat = bpy.data.materials.new(f"{col}{'_glow' if emit else ''}")
    mat.diffuse_color = (*hex_rgb(col), 1)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*hex_rgb(col), 1)
    bsdf.inputs["Roughness"].default_value = 0.28 if metal else 0.55
    bsdf.inputs["Metallic"].default_value = 1.0 if metal else 0.0
    if studs:
        nt = mat.node_tree
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = stud_image()
        tex.interpolation = "Linear"
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.6
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(tex.outputs["Color"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*hex_rgb(col), 1)
        bsdf.inputs["Emission Strength"].default_value = emit * 0.35  # brillo contenido
    cache[key] = mat
    return mat


def clear_scene():
    global _STUD_IMG
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _STUD_IMG = None


def build_model(m):
    """Esqueleto (un hueso por parte) + una malla con grupos de vértices + animación en los huesos."""
    mats = {}
    scene = bpy.context.scene
    rest_world = {n: m.world_matrix(n) for n in m.parts}
    lo, hi = m.bounds()
    blen = max(0.15, (hi - lo).length * 0.03)

    arm_data = bpy.data.armatures.new(f"{m.name}_rig")
    arm_data.display_type = "STICK"
    arm = bpy.data.objects.new(m.name, arm_data)
    arm.rotation_euler = (math.radians(90), 0, 0)  # Y-arriba -> Z-arriba
    arm.show_in_front = True
    scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    ebones = {}
    for part in m.parts.values():
        eb = arm_data.edit_bones.new(part.name)
        eb.head, eb.tail = (0, 0, 0), (0, blen, 0)
        eb.matrix = rest_world[part.name]
        eb.length = blen
        if part.parent:
            eb.parent = ebones[part.parent]
            eb.use_connect = False
        ebones[part.name] = eb
    bpy.ops.object.mode_set(mode="OBJECT")

    # malla única con un grupo de vértices por hueso (piel rígida), construida de golpe
    corners = [Vector((x, y, z)) * 0.5 for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    studs = bool(m.stage and m.stage.get("studs"))
    stud = (m.stage or {}).get("studSize", 0.3)
    face_axes = [(1, 2), (1, 2), (0, 2), (0, 2), (0, 1), (0, 1)]
    verts, faces, fmat, slots, vg_idx, uvs = [], [], [], [], {}, []
    for part in m.parts.values():
        W = rest_world[part.name]
        ids = vg_idx.setdefault(part.name, [])
        for b in part.boxes:
            mat = material(mats, b["col"], b["emit"], b.get("metal", 0), studs and not b["emit"])
            if mat not in slots:
                slots.append(mat)
            M = W @ Matrix.LocRotScale(b["c"], b["q"], b["s"])
            if studs:
                for qi, q in enumerate(quads):
                    a, bb = face_axes[qi]
                    ra = max(1, round(b["s"][a] / stud))
                    rb = max(1, round(b["s"][bb] / stud))
                    for i in q:
                        c = corners[i]
                        uvs.extend(((c[a] + 0.5) * ra, (c[bb] + 0.5) * rb))
            base = len(verts)
            verts.extend(M @ c for c in corners)
            ids.extend(range(base, base + 8))
            faces.extend(tuple(base + i for i in q) for q in quads)
            fmat.extend([slots.index(mat)] * 6)
    # piezas suaves: esferas y cápsulas
    def add_sphere(W, c, r, q, mat_i, ids, nu=18, nv=12):
        base = len(verts)
        M = W @ Matrix.LocRotScale(c, q, r)
        for j in range(nv + 1):
            th = math.pi * j / nv
            for i in range(nu + 1):
                ph = 2 * math.pi * i / nu
                verts.append(M @ Vector((math.sin(th) * math.cos(ph), math.cos(th), math.sin(th) * math.sin(ph))))
                if studs:
                    uvs_v.append((i / nu * max(1, round(math.pi * (r.x + r.z) / stud)), (1 - j / nv) * max(1, round(math.pi * r.y / stud))))
        ids.extend(range(base, len(verts)))
        for j in range(nv):
            for i in range(nu):
                a = base + j * (nu + 1) + i
                b = a + nu + 1
                faces.append((a, a + 1, b + 1, b))
                fmat.append(mat_i)
                if studs:
                    uvs_f.append((a, a + 1, b + 1, b))

    def add_capsule(W, a, b, r0, r1, mat_i, ids, nu=18):
        d = b - a
        L = d.length
        if L > 1e-4:
            q = Vector((0, 1, 0)).rotation_difference(d.normalized())
            base = len(verts)
            for j, (y, r) in enumerate(((0.0, r0), (L, r1))):
                for i in range(nu + 1):
                    ph = 2 * math.pi * i / nu
                    verts.append(W @ (a + q @ Vector((math.cos(ph) * r, y, math.sin(ph) * r))))
                    if studs:
                        uvs_v.append((i / nu * max(1, round(math.pi * (r0 + r1) / stud)), j * max(1, round(L / stud))))
            ids.extend(range(base, len(verts)))
            for i in range(nu):
                f = (base + i, base + nu + 1 + i, base + nu + 2 + i, base + i + 1)
                faces.append(f)
                fmat.append(mat_i)
                if studs:
                    uvs_f.append(f)
        add_sphere(W, a, Vector((r0, r0, r0)), Quaternion(), mat_i, ids)
        add_sphere(W, b, Vector((r1, r1, r1)), Quaternion(), mat_i, ids)

    uvs_v, uvs_f = [], []
    box_faces = len(faces)
    for part in m.parts.values():
        W = rest_world[part.name]
        ids = vg_idx.setdefault(part.name, [])
        for pr in part.prims:
            mat = material(mats, pr["col"], pr["emit"], pr.get("metal", 0), studs and not pr["emit"])
            if mat not in slots:
                slots.append(mat)
            sh = pr["shape"]
            if sh[0] == "ell":
                add_sphere(W, sh[1], sh[2], sh[3], slots.index(mat), ids)
            else:
                add_capsule(W, sh[1], sh[2], sh[3], sh[4], slots.index(mat), ids)
    mesh = bpy.data.meshes.new(f"{m.name}_mesh")
    mesh.from_pydata([tuple(v) for v in verts], [], faces)
    mesh.polygons.foreach_set("material_index", fmat)
    if studs:
        uvl = mesh.uv_layers.new(name="UVMap")
        prim_base = len(verts) - len(uvs_v)
        loop_uv = list(uvs)
        for f in faces[box_faces:]:
            for vi in f:
                loop_uv.extend(uvs_v[vi - prim_base])
        uvl.data.foreach_set("uv", loop_uv)
    mesh.update()
    for mat in slots:
        mesh.materials.append(mat)
    ob = bpy.data.objects.new(f"{m.name}_geo", mesh)
    ob.parent = arm
    scene.collection.objects.link(ob)
    for n, ids in vg_idx.items():
        vg = ob.vertex_groups.new(name=n)
        vg.add(ids, 1.0, "REPLACE")
    bev = ob.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.02
    bev.segments = 2
    bev.limit_method = "NONE"
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm

    # animación muestreada -> keyframes de los huesos
    tracks, _ = m.sample()
    scene.render.fps = m.fps
    scene.frame_start, scene.frame_end = 1, m.frames
    for name, rows in tracks.items():
        part = m.parts[name]
        rest_inv = Matrix.LocRotScale(part.pivot, part.quat, Vector((1, 1, 1))).inverted()
        pb = arm.pose.bones[name]
        pb.rotation_mode = "QUATERNION"
        for f, row in enumerate(rows + rows[:1]):  # el primero se repite para cerrar el bucle
            local = Matrix.LocRotScale(Vector(row[0:3]), Quaternion((row[6], row[3], row[4], row[5])), Vector(row[7:10]))
            pb.matrix_basis = rest_inv @ local
            for path in ("location", "rotation_quaternion", "scale"):
                pb.keyframe_insert(path, frame=f + 1)
    scene.frame_end = m.frames
    return arm


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def hex_lin(h, k=1.0):
    return tuple(c * k for c in hex_rgb(h))


def stage(name, samples, res, m=None):
    st = STAGES.get(name)
    if st is None:  # escenario a partir del ajuste web, con la cámara encuadrada al tamaño del modelo
        lo_, hi_ = m.bounds()
        size = max(hi_.x - lo_.x, hi_.y - lo_.y, hi_.z - lo_.z)
        c = Vector(((lo_.x + hi_.x) / 2, -(lo_.z + hi_.z) / 2, (lo_.y + hi_.y) * 0.45))  # Y-arriba -> Z-arriba
        if "egg" in m.parts:
            c.z = m.parts["egg"].pivot.y - 0.3
        dirv = Vector((13, -17, 9)).normalized()
        cam = c + dirv * size * 1.75
        st = dict(world=hex_lin(m.stage["bgTop"], 0.6), floor=m.stage.get("ground") or "#101010",
                  cam=tuple(cam), target=tuple(c), lens=45)
    scene = bpy.context.scene
    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*st["world"], 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    scene.world = world

    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Floor"
    floor.data.materials.append(material({}, st["floor"], 0))

    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = st["lens"]
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = st["cam"]
    scene.collection.objects.link(cam)
    look_at(cam, st["target"])
    scene.camera = cam

    def light(kind, loc, energy, color=(1, 1, 1), size=None):
        ld = bpy.data.lights.new(kind + "_light", kind)
        ld.energy = energy
        ld.color = color
        if size is not None:
            ld.size = size
        lo = bpy.data.objects.new(ld.name, ld)
        lo.location = loc
        scene.collection.objects.link(lo)
        look_at(lo, st["target"])

    if name == "shark_dino":
        light("AREA", (8, -10, 14), 4500, (0.75, 0.85, 1.0), 6)
        light("AREA", (14, -6, 5), 1500, (0.8, 0.9, 1.0), 5)
        light("AREA", (-10, 6, 6), 1800, (1.0, 0.25, 0.2), 4)  # contraluz rojo
        light("AREA", (0, -14, 2), 500, (0.6, 0.7, 1.0), 6)
    elif name.startswith("egg"):
        light("AREA", (7, -9, 12), 3000, (0.85, 0.92, 1.0), 6)
        light("AREA", (-9, 4, 8), 2000, (0.5, 0.8, 1.0), 5)
        light("AREA", (2, -12, 3), 800, (1.0, 0.9, 0.95), 6)
    else:
        light("SUN", (6, -8, 12), 4.5, (1.0, 0.96, 0.88))
        light("AREA", (-8, -6, 6), 900, (0.7, 0.85, 1.0), 6)

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = res
    scene.render.resolution_y = res
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"


def main():
    bpy.context.preferences.filepaths.save_version = 0  # sin copias .blend1
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    samples, res, names, frame, json_only = 48, 1200, [], None, False
    it = iter(argv)
    for a in it:
        if a == "--samples":
            samples = int(next(it))
        elif a == "--res":
            res = int(next(it))
        elif a == "--json-only":
            json_only = True
        elif a == "--frame":
            frame = int(next(it))
        else:
            names.append(a)
    os.makedirs(OUT, exist_ok=True)
    for name in names or MODELS:
        m = MODELS[name]()
        if name in FEATURED:
            title, rarity = FEATURED[name]
            m.meta = {"title": title, "rarity": rarity, "rarityName": tiers.RARITIES[rarity][0], "level": tiers.RARITIES[rarity][1],
                      "featured": True}
        print(f"[{name}] {m.box_count()} cubos, {len(m.parts)} partes")
        t0 = time.time()
        m.save_json(os.path.join(OUT, f"{name}.json"))
        if json_only:
            continue
        clear_scene()
        build_model(m)
        light = name.startswith("pet_")
        want_glb = name.startswith("animal_") or name in ("shark_dino", "mailbox") or "--glb" in sys.argv
        if want_glb:
          bpy.ops.export_scene.gltf(
            filepath=os.path.join(OUT, f"{name}.glb"),
            export_format="GLB",
            export_apply=False,  # el bisel queda como modificador en el .blend; el .glb pesa mucho menos
            export_animations=True,
            export_force_sampling=False,
            export_optimize_animation_size=True,
        )
        t1 = time.time()
        stage(name, samples, res, m)
        scene = bpy.context.scene
        scene.frame_set(frame or 1)
        if not light:
            bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{name}.blend"), compress=True)
        scene.render.filepath = os.path.join(OUT, f"{name}.png")
        t2 = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"[{name}] escena+exportar {t1 - t0:.1f}s · render {time.time() - t2:.1f}s")


if __name__ == "__main__":
    main()
