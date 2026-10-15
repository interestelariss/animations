"""Construye los modelos en Blender y exporta .blend, .glb, .json y un render.

Uso (con Blender instalado):
    blender -b -P blender/build.py -- [shark_dino|mailbox ...] [--samples N] [--res PX]
o con el módulo de Python `bpy` (pip install bpy):
    python blender/build.py [modelos...]
"""

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import eggs  # noqa: E402
import eggs_themes  # noqa: E402
import mailbox_monster  # noqa: E402
import shark_dino  # noqa: E402
import tiers  # noqa: E402

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


def material(cache, col, emit, metal=0):
    key = (col, emit, metal)
    if key in cache:
        return cache[key]
    mat = bpy.data.materials.new(f"{col}{'_glow' if emit else ''}")
    mat.diffuse_color = (*hex_rgb(col), 1)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*hex_rgb(col), 1)
    bsdf.inputs["Roughness"].default_value = 0.28 if metal else 0.55
    bsdf.inputs["Metallic"].default_value = 1.0 if metal else 0.0
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*hex_rgb(col), 1)
        bsdf.inputs["Emission Strength"].default_value = emit * 0.35  # brillo contenido
    cache[key] = mat
    return mat


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_model(m):
    mats = {}
    root = bpy.data.objects.new(m.name, None)
    root.empty_display_type = "ARROWS"
    root.rotation_euler = (math.radians(90), 0, 0)  # Y-arriba -> Z-arriba
    bpy.context.scene.collection.objects.link(root)

    empties = {}
    for part in m.parts.values():
        e = bpy.data.objects.new(part.name, None)
        e.empty_display_size = 0.3
        e.parent = root if part.parent is None else empties[part.parent]
        e.location = part.pivot
        e.rotation_mode = "QUATERNION"
        e.rotation_quaternion = part.quat
        bpy.context.scene.collection.objects.link(e)
        empties[part.name] = e

        if not part.boxes:
            continue
        mesh = bpy.data.meshes.new(f"{part.name}_mesh")
        bm = bmesh.new()
        slots = []
        for b in part.boxes:
            mat = material(mats, b["col"], b["emit"], b.get("metal", 0))
            if mat not in slots:
                slots.append(mat)
            geom = bmesh.ops.create_cube(bm, size=1.0)
            mtx = Matrix.LocRotScale(b["c"], b["q"], b["s"])
            bmesh.ops.transform(bm, matrix=mtx, verts=geom["verts"])
            idx = slots.index(mat)
            for f in {f for v in geom["verts"] for f in v.link_faces}:
                f.material_index = idx
        bm.to_mesh(mesh)
        bm.free()
        for mat in slots:
            mesh.materials.append(mat)
        ob = bpy.data.objects.new(f"{part.name}_geo", mesh)
        ob.parent = e
        bev = ob.modifiers.new("Bevel", "BEVEL")
        bev.width = 0.025
        bev.segments = 2
        bev.limit_method = "NONE"
        bpy.context.scene.collection.objects.link(ob)

    # keyframes de la animación muestreada
    tracks, _ = m.sample()
    scene = bpy.context.scene
    scene.render.fps = m.fps
    scene.frame_start, scene.frame_end = 1, m.frames
    for name, rows in tracks.items():
        e = empties[name]
        for f, row in enumerate(rows + rows[:1]):  # repite el primero para cerrar el bucle
            e.location = row[0:3]
            e.rotation_quaternion = (row[6], row[3], row[4], row[5])
            e.scale = row[7:10]
            for path in ("location", "rotation_quaternion", "scale"):
                e.keyframe_insert(path, frame=f + 1)
    scene.frame_end = m.frames
    return root


def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def hex_lin(h, k=1.0):
    return tuple(c * k for c in hex_rgb(h))


def stage(name, samples, res, m=None):
    st = STAGES.get(name)
    if st is None:  # huevos de la colección: escenario a partir de su ajuste web
        cy = m.parts["egg"].pivot.y
        st = dict(world=hex_lin(m.stage["bgTop"], 0.6), floor=m.stage.get("ground") or "#101010",
                  cam=(13, -17, cy + 4.2), target=(0, 0, cy - 0.3), lens=45)
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
        m.save_json(os.path.join(OUT, f"{name}.json"))
        if json_only:
            continue
        clear_scene()
        build_model(m)
        bpy.ops.export_scene.gltf(
            filepath=os.path.join(OUT, f"{name}.glb"),
            export_format="GLB",
            export_apply=False,  # el bisel queda como modificador en el .blend; el .glb pesa mucho menos
            export_animations=True,
        )
        stage(name, samples, res, m)
        scene = bpy.context.scene
        scene.frame_set(frame or 1)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f"{name}.blend"), compress=True)
        scene.render.filepath = os.path.join(OUT, f"{name}.png")
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
