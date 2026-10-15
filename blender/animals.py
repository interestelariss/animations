"""Los 20 animales de renacimiento, con el mismo estilo de bloques que los huevos.

Del 1 (Conejo) al 20 (Genesis Beast) suben el detalle, la animación y los VFX:
1-4 animales sencillos y adorables, 5-10 depredadores y criaturas míticas,
11-20 formas fantásticas: titanes, criaturas dimensionales y entidades cósmicas.
"""

import math

from mathutils import Quaternion, Vector

from eggs import _hash, _wing
from eggs_themes import fbm, flame, horn, membrane_wing
from voxel import Model, crystal, polyline, quat, ring, segment, star

TAU = math.tau

ANIMALS = [
    # (n, id, nombre, título, requisito, bonificación)
    (1, "rabbit", "Rabbit", "The Newborn", "Comienzo del juego", "Estadísticas base"),
    (2, "cat", "Cat", "The Agile Hunter", "500 de fuerza", "×2 progreso · +10% velocidad"),
    (3, "dog", "Dog", "The Loyal Beast", "5.000 de fuerza", "×3 progreso · +15% resistencia"),
    (4, "cheetah", "Cheetah", "The Speed Demon", "50.000 de fuerza", "×4 progreso · +25% velocidad"),
    (5, "wolf", "Wolf", "The Wild Predator", "500.000 de fuerza", "×5 progreso · +25% fuerza"),
    (6, "lion", "Lion", "The King", "5 millones de fuerza", "×7 progreso · +30% monedas"),
    (7, "frost_tiger", "Frost Tiger", "The Ice Stalker", "50 millones de fuerza", "×10 progreso · +35% velocidad"),
    (8, "phoenix", "Phoenix", "The Reborn Flame", "500 millones de fuerza", "×15 progreso · +50% monedas"),
    (9, "ancient_dragon", "Ancient Dragon", "The Elder", "5.000 millones de fuerza", "×20 progreso · +50% fuerza"),
    (10, "cosmic_worm", "Cosmic Worm", "The Star Eater", "50.000 millones de fuerza", "×30 progreso · +75% monedas"),
    (11, "celestial_wolf", "Celestial Wolf", "The Moon Guardian", "500.000 millones de fuerza", "×40 progreso · +75% velocidad"),
    (12, "griffin_emperor", "Griffin Emperor", "The Sky Ruler", "5 billones de fuerza", "×55 progreso · +100% monedas"),
    (13, "abyss_hydra", "Abyss Hydra", "The Many-Headed Beast", "50 billones de fuerza", "×75 progreso · +100% fuerza"),
    (14, "world_titan", "Mountain Behemoth", "The Mountain Breaker", "500 billones de fuerza", "×100 progreso · +125% fuerza"),
    (15, "prismatic_unicorn", "Prismatic Unicorn", "The Lightbringer", "5 cuatrillones de fuerza", "×150 progreso · +150% monedas"),
    (16, "shadow_sovereign", "Shadow Sovereign", "The Dark King", "50 cuatrillones de fuerza", "×200 progreso · +175% fuerza"),
    (17, "cosmic_leviathan", "Cosmic Leviathan", "The Universe Swimmer", "500 cuatrillones de fuerza", "×300 progreso · +200% monedas"),
    (18, "phoenix_deity", "Phoenix Deity", "The Eternal Sun", "5 quintillones de fuerza", "×450 progreso · +250% fuerza"),
    (19, "world_serpent", "World Serpent", "The Reality Eater", "50 quintillones de fuerza", "×650 progreso · +300% monedas"),
    (20, "genesis_beast", "Genesis Beast", "The Creator of Worlds", "500 quintillones de fuerza", "×1.000 progreso · +500% monedas"),
]


# ----------------------------------------------------------------------------- utilidades
def cosmic_col(p, pal=("#140a3a", "#1d0f52", "#2a1470", "#3a1a8a"), neb=("#d14ee8", "#2bc4e6")):
    h = _hash(p.x, p.y, p.z)
    if h > 0.975:
        return ("#ffffff", 3.0, "twinkle")
    f = fbm(p, 1.1, 5.0)
    if f > 0.64:
        return (neb[0], 0.8, "nebula")
    if f < 0.32:
        return (neb[1], 0.6, "nebula")
    return pal[int(h * 97) % len(pal)]


def vox_box(m, part, c, s, v, colfn):
    """Caja rellena de vóxeles (solo la superficie) coloreada por una función."""
    c, s = Vector(c), Vector(s)
    nx, ny, nz = (max(1, int(round(s[i] / v))) for i in range(3))
    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                if 0 < ix < nx - 1 and 0 < iy < ny - 1 and 0 < iz < nz - 1:
                    continue
                p = c + Vector(((ix + 0.5) * s.x / nx - s.x / 2, (iy + 0.5) * s.y / ny - s.y / 2, (iz + 0.5) * s.z / nz - s.z / 2))
                res = colfn(p)
                col, emit, tag = (res + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
                m.box(part, p, (s.x / nx, s.y / ny, s.z / nz), col, emit=emit, tag=tag)


def vox_ball(m, part, c, r, v, colfn):
    c = Vector(c)
    n = int(r / v) + 1
    for ix in range(-n, n + 1):
        for iy in range(-n, n + 1):
            for iz in range(-n, n + 1):
                p = Vector((ix, iy, iz)) * v
                if p.length > r or p.length < r - v * 1.5:
                    continue
                res = colfn(c + p)
                col, emit, tag = (res + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
                m.box(part, c + p, (v, v, v), col, emit=emit, tag=tag)


def eyes(m, part, hs, z, y=0.08, iris="#3a2a2a", glow=0.0, x=0.25, size=1.0):
    for sx in (1, -1):
        e = (sx * hs * x, hs * y, z)
        m.box(part, e, (hs * 0.25 * size, hs * 0.27 * size, 0.05), "#ffffff")
        m.box(part, (e[0], e[1] - hs * 0.02, z + 0.02), (hs * 0.17 * size, hs * 0.21 * size, 0.04), iris, emit=glow, tag="eyes" if glow else None)
        m.box(part, (e[0], e[1] - hs * 0.03, z + 0.04), (hs * 0.07 * size, hs * 0.15 * size, 0.03), "#0a0a0a")
        m.box(part, (e[0] + sx * hs * 0.04, e[1] + hs * 0.06, z + 0.05), (hs * 0.05, hs * 0.05, 0.02), "#ffffff")


# ----------------------------------------------------------------------------- cuadrúpedo genérico
def quad(m, P):
    """Cuadrúpedo de bloques. Devuelve el diccionario de medidas útiles."""
    L, W, H = P["L"], P["W"], P["H"]
    leg, lw, hs, sn = P["leg"], P["lw"], P["hs"], P["snout"]
    c = P["cols"]
    main, belly, dark = c["main"], c.get("belly", c["main"]), c.get("dark", "#2a2a2a")
    m.part("body", "root", (0, leg + H / 2, 0))
    if P.get("cosmic"):
        vox_box(m, "body", (0, 0, 0), (W, H, L), P.get("vox", 0.2), P["cosmic"])
    else:
        m.box("body", (0, 0, 0), (W, H, L), main)
        m.box("body", (0, -H / 2 + 0.05, 0.05), (W * 0.82, 0.12, L * 0.78), belly)
        m.box("body", (0, H * 0.18, L / 2 - L * 0.12), (W * 1.06, H * 0.8, L * 0.26), main)  # hombros
        m.box("body", (0, H * 0.1, -L / 2 + L * 0.14), (W * 1.04, H * 0.85, L * 0.28), main)  # cadera
        m.box("body", (0, -H * 0.12, L / 2 + 0.02), (W * 0.8, H * 0.6, 0.12), belly)  # pecho
        if P.get("back"):
            m.box("body", (0, H / 2 + 0.02, -0.05), (W * 0.45, 0.06, L * 0.85), P["back"])
    # patrón
    pat = P.get("pattern")
    if pat == "stripes":
        n = P.get("stripes", 5)
        for i in range(n):
            z = -L / 2 + (i + 0.7) * L / (n + 0.4)
            for sx in (1, -1):
                m.box("body", (sx * (W / 2 + 0.015), H * 0.1, z), (0.04, H * 0.7, 0.1), c["accent"], emit=P.get("pattern_emit", 0),
                      tag="glow" if P.get("pattern_emit") else None, r=(18 * sx, 0, 0))
            m.box("body", (0, H / 2 + 0.015, z), (W * 0.7, 0.04, 0.1), c["accent"], emit=P.get("pattern_emit", 0), tag="glow" if P.get("pattern_emit") else None)
    elif pat == "spots":
        for i in range(P.get("spots", 22)):
            u, v = _hash(i, 1), _hash(i, 2)
            side = 1 if i % 3 else 0
            if side:
                sx = 1 if i % 2 else -1
                m.box("body", (sx * (W / 2 + 0.015), (v - 0.5) * H * 0.7, (u - 0.5) * L * 0.85), (0.04, 0.12, 0.12), c["accent"])
            else:
                m.box("body", ((v - 0.5) * W * 0.7, H / 2 + 0.015, (u - 0.5) * L * 0.85), (0.12, 0.04, 0.12), c["accent"])
    elif pat == "runes":
        for i in range(P.get("runes", 8)):
            z = -L / 2 + (i % 4 + 0.6) * L / 4.4
            sx = 1 if i < 4 else -1
            yy = H * 0.05
            m.box("body", (sx * (W / 2 + 0.02), yy, z), (0.04, H * 0.45, 0.06), c["accent"], emit=2.5, tag="glow")
            m.box("body", (sx * (W / 2 + 0.02), yy + H * 0.1, z), (0.04, 0.06, L * 0.12), c["accent"], emit=2.5, tag="glow")

    # cuello y cabeza
    nl = P.get("neck", 0.0)
    neck_top = Vector((0, H * 0.35 + nl * 0.8, L / 2 + nl * 0.45))
    if nl > 0:
        segment(m, "body", (0, H * 0.2, L / 2 - 0.1), neck_top, (W * 0.55, W * 0.6), main)
        if P.get("mane_neck"):
            pts = 6
            for i in range(pts):
                k = i / (pts - 1)
                p = Vector((0, H * 0.2, L / 2 - 0.1)).lerp(neck_top, k)
                m.box("body", p + Vector((0, W * 0.35, -0.1)), (0.22, 0.4, 0.3), P["mane_neck"][i % len(P["mane_neck"])],
                      emit=P.get("mane_emit", 0), tag="glow" if P.get("mane_emit") else None)
    m.part("head", "body", tuple(neck_top + Vector((0, hs * 0.1, 0.05))))
    head_col = c.get("head", main)
    m.box("head", (0, 0, hs * 0.35), (hs, hs * 0.88, hs * 0.92), head_col)
    m.box("head", (0, -hs * 0.18, hs * 0.35), (hs * 1.08, hs * 0.4, hs * 0.7), c.get("cheek", head_col))  # mofletes
    if sn > 0:
        m.box("head", (0, -hs * 0.17, hs * 0.81 + sn / 2), (hs * 0.55, hs * 0.38, sn + 0.02), c.get("muzzle", belly))
        m.box("head", (0, -hs * 0.02, hs * 0.81 + sn), (hs * 0.24, hs * 0.14, 0.08), c.get("nose", "#2a1a1a"))
    zf = hs * 0.82
    eyes(m, "head", hs, zf, iris=c.get("eye", "#3a2a2a"), glow=P.get("eye_glow", 0), size=P.get("eye_size", 1.0))
    # mandíbula
    m.part("jaw", "head", (0, -hs * 0.36, hs * 0.55))
    m.box("jaw", (0, 0, (sn + hs * 0.3) / 2), (hs * 0.48, hs * 0.13, sn + hs * 0.3), c.get("muzzle", belly))
    m.box("jaw", (0, 0.05, (sn + hs * 0.3) / 2), (hs * 0.4, 0.04, sn + hs * 0.2), "#5a1a22")
    if P.get("teeth"):
        for sx in (1, -1):
            m.box("head", (sx * hs * 0.16, -hs * 0.38, hs * 0.81 + sn * 0.85), (0.06, 0.12, 0.06), "#f6f0e2")
    if P.get("tongue"):
        m.box("jaw", (0, 0.06, sn + hs * 0.25), (hs * 0.22, 0.05, hs * 0.3), "#ff6a8a", r=(-25, 0, 0))
    # orejas
    ear = P.get("ear", "pointy")
    for side, sx in (("L", 1), ("R", -1)):
        e = f"ear_{side}"
        m.part(e, "head", (sx * hs * 0.3, hs * 0.42, hs * 0.22), (0, 0, sx * -8))
        if ear == "long":
            m.box(e, (0, hs * 0.5, 0), (hs * 0.22, hs * 1.05, hs * 0.14), head_col)
            m.box(e, (0, hs * 0.5, 0.06), (hs * 0.12, hs * 0.85, 0.04), c.get("inner", "#ffb8c8"))
        elif ear == "pointy":
            for j in range(3):
                w = hs * (0.34 - j * 0.1)
                m.box(e, (0, hs * (0.08 + j * 0.13), 0), (w, hs * 0.14, hs * 0.12), head_col)
            m.box(e, (0, hs * 0.12, 0.05), (hs * 0.16, hs * 0.16, 0.04), c.get("inner", "#ffb8c8"))
        elif ear == "round":
            m.box(e, (0, hs * 0.08, 0), (hs * 0.26, hs * 0.22, hs * 0.12), head_col)
            m.box(e, (0, hs * 0.08, 0.05), (hs * 0.14, hs * 0.12, 0.04), c.get("inner", "#3a2a2a"))
        elif ear == "floppy":
            m.box(e, (sx * hs * 0.14, -hs * 0.25, 0), (hs * 0.16, hs * 0.6, hs * 0.3), c.get("ear_col", dark), r=(0, 0, sx * 12))
    # patas
    legs = {}
    for name, (px, pz) in (("FL", (1, 1)), ("FR", (-1, 1)), ("BL", (1, -1)), ("BR", (-1, -1))):
        back = pz < 0
        ll = leg * (P.get("back_scale", 1.0) if back else 1.0)
        lww = lw * (P.get("back_w", 1.0) if back else 1.0)
        n = f"leg_{name}"
        m.part(n, "body", (px * W * 0.3, -H * 0.3, pz * L * 0.36))
        m.box(n, (0, -ll / 2 + H * 0.15, 0), (lww, ll + H * 0.3, lww), c.get("leg", main))
        m.box(n, (0, -ll + H * 0.3 + 0.06 - H * 0.15, 0.04), (lww * 1.15, 0.14, lww * 1.35), c.get("paw", belly))
        if P.get("claws"):
            for k in (-1, 0, 1):
                m.box(n, (k * lww * 0.3, -ll + H * 0.3 - H * 0.15 + 0.02, lww * 0.75), (0.05, 0.06, 0.1), P["claws"])
        if P.get("paw_extra"):
            m.box(n, (0, -ll + H * 0.3 - H * 0.15 + 0.12, 0), (lww * 1.3, 0.12, lww * 1.4), P["paw_extra"], emit=1.5, tag="glow")
        legs[name] = n
    # cola
    tail = P.get("tail", "long")
    tn = P.get("tail_n", 5)
    parent, piv = "body", (0, H * 0.25, -L / 2)
    tcol = c.get("tail", main)
    if tail == "none":
        tn = 0
    elif tail == "puff":
        m.part("tail0", "body", piv)
        m.box("tail0", (0, 0, -0.1), (hs * 0.4, hs * 0.4, hs * 0.35), "#ffffff")
    else:
        for i in range(tn):
            k = i / max(tn - 1, 1)
            n = f"tail{i}"
            m.part(n, parent, piv, (P.get("tail_lift", -18) if i == 0 else P.get("tail_curve", 6), 0, 0))
            seg = P.get("tail_seg", 0.32)
            if tail == "bushy":
                w = lw * (0.9 + 0.8 * math.sin(k * math.pi * 0.9 + 0.2))
            elif tail == "tuft":
                w = lw * 0.45
            else:
                w = lw * (0.65 - 0.25 * k)
            col = tcol if not (P.get("tail_tip") and i >= tn - 1) else P["tail_tip"]
            if P.get("tail_rings") and i % 2 == 1:
                col = c["accent"]
            m.box(n, (0, 0, -seg / 2), (w, w, seg + 0.03), col, emit=P.get("tail_emit", 0) * k, tag="glow" if P.get("tail_emit") else None)
            parent, piv = n, (0, 0, -seg)
        if tail == "tuft":
            m.box(parent, (0, 0, -0.1), (lw * 1.1, lw * 1.1, lw * 1.2), P.get("tuft_col", dark))
    return dict(L=L, W=W, H=H, leg=leg, hs=hs, legs=legs, tail_n=1 if tail == "puff" else tn)



def walk_pose(pose, t, amp=25, speed=2, gallop=False, bob=0.05):
    a = t * TAU * speed
    ph = {"FL": 0, "BR": 0, "FR": math.pi, "BL": math.pi} if not gallop else {"FL": 0, "FR": 0.5, "BL": math.pi, "BR": math.pi + 0.5}
    for k, p in ph.items():
        pose[f"leg_{k}"] = {"r": quat((amp * math.sin(a + p), 0, 0))}
    pose["body"] = {"p": (0, bob * abs(math.sin(a)), 0), "r": quat((2 * math.sin(a * 2) if gallop else 0, 0, 0))}
    return pose


def tail_pose(pose, t, n, amp=12, speed=1, axis="y", start=0):
    a = t * TAU * speed
    for i in range(start, n):
        ang = amp * math.sin(a - i * 0.6)
        pose[f"tail{i}"] = {"r": quat((0, ang, 0) if axis == "y" else (ang, 0, 0))}
    return pose


# ----------------------------------------------------------------------------- base / pedestal por nivel
def add_base(m, tier, energy, ground="#5fae3a", ground2="#4f9a35"):
    """Sube el cuerpo y pone una base bajo el animal. Devuelve la altura de la base."""
    lo, hi = m.bounds()
    span = max(hi.x - lo.x, hi.z - lo.z)
    R = span * (0.42 if tier <= 4 else 0.48) + (0.25 if tier <= 4 else 0.5)
    bh = 0.3 if tier <= 4 else (0.5 if tier <= 10 else 0.8)
    for n in ("body", "titan", "worm", "bird"):
        if n in m.parts and m.parts[n].parent == "root":
            m.parts[n].pivot.y += bh
    if tier <= 4:
        for k in range(16):
            a = k / 16 * TAU
            m.box("root", (math.cos(a) * R * 0.75, bh / 2, math.sin(a) * R * 0.75), (R * 0.32, bh, R * 0.32), ground if k % 2 else ground2,
                  r=(0, -math.degrees(a), 0))
        m.box("root", (0, bh / 2, 0), (R * 1.2, bh, R * 1.2), ground, r=(0, 22.5, 0))
        m.box("root", (0, bh / 2, 0), (R * 1.2, bh, R * 1.2), ground, r=(0, 67.5, 0))
        for k in range(10):
            a = k / 10 * TAU + 0.3
            r_ = R * (0.6 + 0.3 * _hash(k, 3))
            m.box("root", (math.cos(a) * r_, bh + 0.1, math.sin(a) * r_), (0.06, 0.2, 0.06), "#3f8a2a")
        return bh
    base = "#262b38" if tier <= 10 else "#161a28"
    base2 = "#323848" if tier <= 10 else "#20263a"
    m.box("root", (0, bh * 0.35, 0), (R * 2, bh * 0.7, R * 2), base)
    m.box("root", (0, bh * 0.35, 0), (R * 2, bh * 0.7, R * 2), base, r=(0, 45, 0))
    m.box("root", (0, bh * 0.85, 0), (R * 1.6, bh * 0.3, R * 1.6), base2, r=(0, 22.5, 0))
    ring(m, "root", R * 0.85, 48, (0.1, 0.06), energy, center=(0, bh + 0.01, 0), emit=1.5 + 0.1 * tier, tag="neon")
    for k in range(8):
        a = k / 8 * TAU + TAU / 16
        m.box("root", (math.cos(a) * R * 1.02, bh * 0.75, math.sin(a) * R * 1.02), (0.3, bh * 0.6, 0.3), "#f2c14e" if tier > 10 else "#6c7178",
              r=(0, -math.degrees(a), 0), metal=1)
    if tier >= 11:
        m.part("floor_rings", "root", (0, 0.04, 0))
        ring(m, "floor_rings", R * 1.35, 72, (0.1, 0.04), energy, emit=2.0, tag="neon")
        ring(m, "floor_rings", R * 1.5, 80, (0.05, 0.04), energy, emit=1.6, tag="neon")
        for k in range(12):  # runas en el suelo
            a = k / 12 * TAU
            m.box("floor_rings", (math.cos(a) * R * 1.42, 0, math.sin(a) * R * 1.42), (0.22, 0.04, 0.08), energy, r=(0, -math.degrees(a) + 45, 0),
                  emit=2.5, tag="neon")
    return bh


def stage_for(tier, energy, bg, particles=None, special=True, extra=None):
    st = {
        "bgTop": bg, "bgBottom": _mix(bg, "#000000", 0.85), "fog": [40, 120, _mix(bg, "#000000", 0.6)],
        "ground": _mix(bg, "#000000", 0.5), "dist": 1.35 if tier > 10 else 1.5, "targetY": None,
        "envTint": [_mix(energy, "#ffffff", 0.5), _mix(bg, "#000000", 0.5)],
        "lights": {"sky": _mix(energy, "#ffffff", 0.65), "groundCol": _mix(bg, "#000000", 0.4), "hemi": 1.0, "key": 2.5, "points": []},
        "bloom": {"strength": min(0.65, 0.05 + 0.035 * tier), "threshold": 1.3, "radius": 1.0, "exposure": 0.95},
        "emitScale": 0.45, "particles": particles or [], "special": special, "shakePart": "body",
        "burstColor": energy, "burstColor2": _mix(energy, "#ffffff", 0.5),
        "views": {"front": [0, 0.12], "side": [1.5708, 0.1], "tq": [0.75, 0.2]},
    }
    if tier >= 5:
        st["lights"]["points"].append({"color": energy, "intensity": 1.5 + 0.15 * tier, "pos": [0, 3, 4], "distance": 16})
        st["groundGlow"] = _rgba(energy, min(0.4, 0.08 + 0.015 * tier))
        st["groundGlowSize"] = 8 + tier * 0.4
    if extra:
        st.update(extra)
    return st


def P_(kind, count, color, size=0.18, radius=(2, 7), height=(0.3, 8), speed=0.5, sprite="dot", intensity=2.0, twinkle=False):
    return {"kind": kind, "count": count, "color": color, "size": size, "radius": list(radius), "height": list(height), "speed": speed,
            "sprite": sprite, "intensity": intensity, "twinkle": twinkle}


def _mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(A[i] + (B[i] - A[i]) * t):02x}" for i in range(3))


def _rgba(h, a):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{a:.2f})"


def new_model(id_, frames=72):
    m = Model("animal_" + id_, fps=24, frames=frames)
    m.part("root")
    return m


def finish(m, n, tier_energy, bg, particles=None, extra=None, ground=("#5fae3a", "#4f9a35")):
    main = [k for k in ("body", "titan", "worm", "bird") if k in m.parts][0]
    m.ground(main)
    add_base(m, n, tier_energy, *ground)
    meta = ANIMALS[n - 1]
    m.meta = {"title": f"{meta[2]}", "subtitle": meta[3], "rarity": "animal", "rarityName": f"Renacimiento {n}", "level": n,
              "requirement": meta[4], "bonus": meta[5], "rebirth": n}
    m.stage = stage_for(n, tier_energy, bg, particles, extra=dict({"shakePart": main}, **(extra or {})))
    return m


# ======================================================================================
# 1-4: animales sencillos
# ======================================================================================
def build_rabbit():
    m = new_model("rabbit", 48)
    P = dict(L=0.95, W=0.85, H=0.78, leg=0.26, lw=0.26, hs=0.82, snout=0.1, ear="long", tail="puff", back_scale=1.25, back_w=1.25,
             cols=dict(main="#f4eee6", belly="#ffffff", inner="#ffb8c8", eye="#4a3020", nose="#ff8aa8", muzzle="#ffffff", cheek="#f8f2ea", paw="#ffffff"))
    quad(m, P)
    for sx in (1, -1):  # mofletes rosados
        m.box("head", (sx * 0.3, -0.12, 0.68), (0.14, 0.08, 0.04), "#ffc8d6")
    m.box("head", (0, -0.26, 0.82), (0.05, 0.08, 0.04), "#c87a8a")  # boquita

    def animate(t):
        a = t * TAU
        hop = max(0.0, math.sin(a))  # un saltito por bucle
        pose = {"body": {"p": (0, 0.55 * hop, 0.0), "r": quat((-10 * hop, 0, 0))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-35 * hop, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((50 * hop, 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((-25 * hop + 4 * math.sin(a * 3), 0, sx * (6 * math.sin(a * 2))))}
        pose["head"] = {"r": quat((6 * math.sin(a * 2), 8 * math.sin(a), 0))}
        pose["tail0"] = {"s": (1 + 0.1 * math.sin(a * 4),) * 3}
        return pose

    m.animate = animate
    return finish(m, 1, "#9fe0a0", "#7fbfe8", particles=[], extra={"bloom": {"strength": 0, "threshold": 2, "radius": 1}, "dist": 2.2, "special": True})


def build_cat():
    m = new_model("cat", 48)
    P = dict(L=1.45, W=0.75, H=0.72, leg=0.62, lw=0.2, hs=0.78, snout=0.12, ear="pointy", tail="long", tail_n=7, tail_seg=0.2, tail_lift=-45, tail_curve=12,
             pattern="stripes", stripes=5,
             cols=dict(main="#f2a24a", belly="#fff2e0", accent="#c8661a", inner="#ffc8c8", eye="#8fe05a", nose="#ff9aa8", muzzle="#fff2e0", paw="#fff2e0", tail="#f2a24a"))
    quad(m, P)
    for sx in (1, -1):  # bigotes
        for j in (-1, 1):
            m.box("head", (sx * 0.42, -0.12 + j * 0.04, 0.92), (0.32, 0.015, 0.015), "#ffffff", r=(0, 0, sx * j * 8))

    def animate(t):
        a = t * TAU
        pose = walk_pose({}, t, amp=20, speed=2, bob=0.03)
        tail_pose(pose, t, 7, amp=14, speed=1, axis="y", start=1)
        twitch = max(0.0, math.sin(a * 3)) ** 8
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((-20 * twitch, sx * 25 * twitch, 0))}
        pose["head"] = {"r": quat((3 * math.sin(a * 4), 12 * math.sin(a), 0))}
        return pose

    m.animate = animate
    return finish(m, 2, "#ffd27a", "#8ac4ec", particles=[P_("float", 20, "#ffffff", 0.1, (2, 6), (0.3, 4), 0.4, "square", 1.0)],
                  extra={"bloom": {"strength": 0, "threshold": 2, "radius": 1}, "dist": 1.8})


def build_dog():
    m = new_model("dog", 48)
    P = dict(L=1.75, W=1.0, H=0.95, leg=0.62, lw=0.3, hs=0.95, snout=0.42, ear="floppy", tail="bushy", tail_n=4, tail_seg=0.2, tail_lift=-55, tongue=True,
             cols=dict(main="#c07a3a", belly="#f6e2c6", dark="#7a4a22", ear_col="#7a4a22", eye="#3a2414", nose="#1a1210", muzzle="#f6e2c6", paw="#f6e2c6",
                       head="#c07a3a", tail="#c07a3a"))
    quad(m, P)
    # collar con chapa
    m.box("body", (0, 0.42, 0.95), (0.95, 0.14, 0.2), "#d8322a", r=(-30, 0, 0))
    m.box("body", (0, 0.3, 1.04), (0.16, 0.16, 0.06), "#f2c14e", r=(0, 0, 45), metal=1)
    m.box("head", (0, 0.3, 0.32), (0.5, 0.06, 0.5), "#7a4a22")  # mancha en la cabeza

    def animate(t):
        a = t * TAU
        pose = walk_pose({}, t, amp=22, speed=2, bob=0.05)
        for i in range(4):
            pose[f"tail{i}"] = {"r": quat((0, 30 * math.sin(a * 6 - i * 0.5), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 4), 6 * math.sin(a), 0))}
        pose["jaw"] = {"r": quat((12 + 4 * math.sin(a * 8), 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((8 * math.sin(a * 4), 0, sx * 8 * math.sin(a * 4)))}
        return pose

    m.animate = animate
    return finish(m, 3, "#ffb36a", "#86c0e8", particles=[P_("float", 30, "#fff0d0", 0.12, (2, 6), (0.3, 4), 0.5, "square", 1.2)],
                  extra={"bloom": {"strength": 0.05, "threshold": 1.8, "radius": 1}, "dist": 1.7})


def build_cheetah():
    m = new_model("cheetah", 36)
    P = dict(L=2.2, W=0.8, H=0.8, leg=0.95, lw=0.2, hs=0.78, snout=0.22, ear="round", tail="long", tail_n=8, tail_seg=0.24, tail_lift=-10, tail_curve=-4,
             tail_rings=True, pattern="spots", spots=34, claws="#2a2a2a",
             cols=dict(main="#f0c060", belly="#fff4dc", accent="#2a1a10", inner="#2a1a10", eye="#ffb020", nose="#2a1a10", muzzle="#fff4dc", paw="#f0c060"))
    quad(m, P)
    for sx in (1, -1):  # lágrimas negras
        m.box("head", (sx * 0.17, -0.1, 0.83), (0.05, 0.3, 0.03), "#1a1210")

    def animate(t):
        pose = walk_pose({}, t, amp=40, speed=2, gallop=True, bob=0.12)
        tail_pose(pose, t, 8, amp=8, speed=2, axis="x", start=1)
        pose["head"] = {"r": quat((-4 * math.sin(t * TAU * 4), 0, 0))}
        return pose

    m.animate = animate
    return finish(m, 4, "#ffcf6a", "#e8c48a", particles=[P_("rise", 60, "#d8b88a", 0.22, (0.5, 3), (0, 1.2), 1.2, "square", 1.2)],
                  extra={"bloom": {"strength": 0.08, "threshold": 1.7, "radius": 1}}, ground=("#d8b878", "#c8a868"))


# ======================================================================================
# 5-10
# ======================================================================================
def wolf_like(m, white=False):
    c = dict(main="#c8ccd4", belly="#eef0f4", dark="#6a707c", inner="#4a4e58", eye="#7fd0ff", nose="#1a1a1e", muzzle="#eef0f4", paw="#eef0f4",
             back="#8a909c", tail="#c8ccd4")
    if white:
        c.update(main="#f4f8ff", belly="#ffffff", back="#d8e6ff", tail="#f4f8ff", inner="#9fc8ff", eye="#5fd8ff")
    P = dict(L=2.3, W=1.0, H=1.05, leg=0.95, lw=0.3, hs=1.0, snout=0.62, ear="pointy", tail="bushy", tail_n=5, tail_seg=0.32, tail_lift=-30,
             teeth=True, claws="#2a2a2a", eye_glow=1.5, cols=c)
    if white:
        P.update(pattern="runes", runes=8, tail="none", eye_glow=2.5)
        P["cols"]["accent"] = "#5fb8ff"
    d = quad(m, P)
    # pelaje del cuello (gorguera)
    for i in range(5):
        m.box("body", (0, 0.35 - i * 0.12, 1.05 + i * 0.02), (1.0 - i * 0.08, 0.2, 0.3), c["main"] if i % 2 else c["belly"], r=(-20, 0, 0))
    return d


def build_wolf():
    m = new_model("wolf", 72)
    wolf_like(m)

    def animate(t):
        a = t * TAU
        howl = max(0.0, math.sin(a)) ** 2
        pose = {"body": {"r": quat((-6 * howl, 0, 0))}, "head": {"r": quat((-50 * howl + 3 * math.sin(a * 6), 0, 0))},
                "jaw": {"r": quat((30 * howl, 0, 0))}}
        tail_pose(pose, t, 5, amp=10, speed=1, axis="y", start=1)
        for side in ("L", "R"):
            pose[f"ear_{side}"] = {"r": quat((-10 * howl, 0, 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"eyes": 0.7 + 0.6 * max(0.0, math.sin(t * TAU)) ** 2, "neon": 0.8 + 0.2 * math.sin(t * TAU * 2)}
    return finish(m, 5, "#7fd0ff", "#1a2a44", particles=[P_("float", 60, "#bfe8ff", 0.14, (3, 9), (0.3, 7), 0.5, "dot", 1.8, True)])


def build_lion():
    m = new_model("lion", 72)
    P = dict(L=2.6, W=1.3, H=1.25, leg=1.0, lw=0.38, hs=1.15, snout=0.5, ear="round", tail="tuft", tail_n=6, tail_seg=0.3, tail_lift=-20, tail_curve=8,
             teeth=True, claws="#e8dcc0", tuft_col="#7a3a14",
             cols=dict(main="#e2aa4c", belly="#f6dca0", dark="#7a3a14", inner="#7a3a14", eye="#ffb020", nose="#5a2a1a", muzzle="#f6e2b8", paw="#e2aa4c"))
    quad(m, P)
    # melena por capas (bloques alrededor de la cabeza)
    m.part("mane", "head", (0, 0, 0.25))
    cols = ["#8a4a1a", "#a85a20", "#6e3812", "#b8682a"]
    for layer in range(3):
        r_ = 0.72 + layer * 0.2
        n = 14 + layer * 4
        for k in range(n):
            a = k / n * TAU
            x, y = math.cos(a) * r_, math.sin(a) * r_ * 0.95
            m.box("mane", (x, y - 0.05, -0.15 - layer * 0.16), (0.42, 0.42, 0.36), cols[(k + layer) % 4], r=(0, 0, math.degrees(a) + 45))
    for k in range(6):  # barba
        m.box("mane", ((k - 2.5) * 0.18, -0.85, 0.05), (0.2, 0.4, 0.3), cols[k % 4])
    m.part("crown_l", "head", (0, 0.75, 0.25))
    for k in range(5):  # pequeña corona de oro del rey
        a = k / 5 * TAU
        m.box("crown_l", (math.cos(a) * 0.3, 0.1, math.sin(a) * 0.3), (0.12, 0.3, 0.12), "#f2c14e", metal=1)
    ring(m, "crown_l", 0.3, 12, (0.1, 0.12), "#f2c14e", metal=1)

    def animate(t):
        a = t * TAU
        roar = max(0.0, math.sin(a)) ** 3
        pose = walk_pose({}, t, amp=12 * (1 - roar), speed=1, bob=0.04)
        pose["head"] = {"r": quat((-8 * roar, 0, 0)), "p": (0, 0, 0.1 * roar)}
        pose["jaw"] = {"r": quat((38 * roar, 0, 0))}
        pose["mane"] = {"s": (1 + 0.12 * roar,) * 3}
        tail_pose(pose, t, 6, amp=10, speed=1, axis="y", start=1)
        return pose

    m.animate = animate
    return finish(m, 6, "#ffcf5a", "#3a2a14", particles=[P_("rise", 80, "#ffd27a", 0.18, (1, 5), (0.3, 6), 0.4, "sparkle", 2.2)])


def build_frost_tiger():
    m = new_model("frost_tiger", 72)
    P = dict(L=2.8, W=1.2, H=1.15, leg=1.05, lw=0.36, hs=1.1, snout=0.45, ear="round", tail="long", tail_n=8, tail_seg=0.3, tail_lift=-25,
             pattern="stripes", stripes=7, pattern_emit=1.6, teeth=True, claws="#bff3ff", paw_extra="#9fe8ff", eye_glow=2.0,
             cols=dict(main="#e8f6ff", belly="#ffffff", accent="#3fa8e8", inner="#7fc8ff", eye="#5fd8ff", nose="#2a4a6a", muzzle="#ffffff", paw="#dff2ff"))
    quad(m, P)
    for i in range(6):  # cristales de hielo en el lomo
        crystal(m, "body", (0, 0.65 + 0.1 * (i % 2), 1.0 - i * 0.42), 0.3, 0.7 + 0.2 * (i % 2), "#9fe8ff", rot=(-20, 0, 0), emit=1.2, tag="glow")
    for sx in (1, -1):
        m.box("head", (sx * 0.3, 0.3, 0.86), (0.25, 0.05, 0.04), "#3fa8e8", emit=1.5, tag="glow", r=(0, 0, sx * 20))
    # huellas congeladas en la base (se añaden tras finish, en root)

    def animate(t):
        a = t * TAU
        leap = max(0.0, math.sin(a)) ** 1.5
        pose = {"body": {"p": (0, 1.2 * leap, 0), "r": quat((-12 * math.sin(a) * leap, 0, 0))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-60 * leap, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((55 * leap, 0, 0))}
        pose["head"] = {"r": quat((10 * leap, 0, 0))}
        pose["jaw"] = {"r": quat((20 * leap, 0, 0))}
        tail_pose(pose, t, 8, amp=10, speed=1, axis="x", start=1)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 0.9, "neon": 0.9}
    m = finish(m, 7, "#7fe8ff", "#0e2440", particles=[P_("snow", 220, "#e6fbff", 0.14, (0.5, 12), (0, 14), 0.9, "square", 1.8),
                                                    P_("rise", 60, "#9fe8ff", 0.2, (0.5, 3), (0.3, 3), 0.8, "sparkle", 2.4)],
               ground=("#cfeaf7", "#e6f7ff"))
    for k in range(6):  # huellas de hielo
        x = (0.4 if k % 2 else -0.4)
        m.box("root", (x, 0.52, -1.6 + k * 0.6), (0.3, 0.04, 0.34), "#9fe8ff", emit=1.5, tag="glow")
    return m


def bird(m, P):
    """Ave de bloques (fénix): cuerpo, cuello, cabeza con pico, alas de plumas, cola en abanico."""
    s = P["s"]
    c = P["cols"]
    m.part("bird", "root", (0, 3.2 * s, 0))
    m.box("bird", (0, 0, 0), (1.2 * s, 1.1 * s, 1.6 * s), c["main"])
    m.box("bird", (0, -0.2 * s, 0.6 * s), (1.0 * s, 0.9 * s, 0.5 * s), c["belly"], emit=P.get("belly_emit", 0), tag="glow" if P.get("belly_emit") else None)
    segment(m, "bird", (0, 0.4 * s, 0.6 * s), (0, 1.1 * s, 1.0 * s), (0.6 * s, 0.6 * s), c["main"])
    m.part("head", "bird", (0, 1.3 * s, 1.1 * s))
    m.box("head", (0, 0, 0.1 * s), (0.75 * s, 0.7 * s, 0.75 * s), c["head"])
    m.box("head", (0, -0.05 * s, 0.6 * s), (0.3 * s, 0.25 * s, 0.4 * s), c["beak"], metal=1 if P.get("beak_metal") else 0)
    m.box("head", (0, -0.15 * s, 0.82 * s), (0.18 * s, 0.18 * s, 0.14 * s), c["beak"], r=(30, 0, 0), metal=1 if P.get("beak_metal") else 0)
    eyes(m, "head", 0.75 * s, 0.48 * s, y=0.1, iris=c["eye"], glow=P.get("eye_glow", 0), x=0.3, size=0.9)
    # cresta
    m.part("crest", "head", (0, 0.35 * s, 0))
    for i in range(5):
        if P.get("crest_flames"):
            flame(m, "crest", (0, 0, -i * 0.15 * s), (0.9 - i * 0.12) * s, 0.25 * s, seed=i)
        else:
            m.box("crest", (0, (0.3 + 0.1 * i) * s, -i * 0.15 * s), (0.12 * s, (0.6 - 0.08 * i) * s, 0.12 * s), c["accent"], r=(-25, 0, 0))
    # alas
    rows = P["wing_rows"]
    bone = [(0, 0), (0.9, 0.7), (1.8, 1.7), (2.6, 2.8)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "bird", (sx * 0.55 * s, 0.35 * s, 0.1 * s), (0, sx * -15, 0))
        _wing(m, w, sx, [(n, a * s, b * s, wd * s, z, cols) for (n, a, b, wd, z, cols) in rows], [(x * s, y * s) for x, y in bone],
              P["bone"], P["bone"])
    # cola en abanico
    m.part("tailfan", "bird", (0, 0.1 * s, -0.8 * s))
    for i in range(P.get("tail_feathers", 7)):
        k = i / (P.get("tail_feathers", 7) - 1) - 0.5
        ang = k * 70
        Lf = (2.2 - abs(k) * 1.2) * s
        rq = quat((25, ang, 0))
        for j, col in enumerate(P["tail_cols"]):
            p = rq @ Vector((0, 0, -(0.3 + j * 0.33) * Lf))
            m.box("tailfan", p, (0.3 * s * (1 - j * 0.15), 0.08 * s, 0.36 * Lf), col, r=rq, emit=P.get("tail_emit", 0) * (j + 1) / 3,
                  tag="glow" if P.get("tail_emit") else None)
    # patas
    for sx in (1, -1):
        segment(m, "bird", (sx * 0.3 * s, -0.5 * s, 0), (sx * 0.3 * s, -1.2 * s, 0.1 * s), 0.12 * s, c["leg"])
        for k in (-1, 0, 1):
            segment(m, "bird", (sx * 0.3 * s, -1.2 * s, 0.1 * s), (sx * 0.3 * s + k * 0.15 * s, -1.25 * s, 0.4 * s), 0.07 * s, c["leg"])


def build_phoenix():
    m = new_model("phoenix", 48)
    fire = ["#ff8a1a", "#ffb020", "#ffe14a"]
    bird(m, dict(s=1.0, crest_flames=True, eye_glow=1.5, belly_emit=1.0, tail_emit=1.5, tail_feathers=7,
                 cols=dict(main="#ff5a1a", belly="#ffb020", head="#ff6a1a", beak="#ffe08a", eye="#ffe14a", accent="#ffe14a", leg="#c8401a"),
                 wing_rows=[(12, 1.8, 3.4, 0.62, -0.12, fire), (10, 1.1, 2.0, 0.58, 0.0, ["#ff6a1a", "#ff9a2a", "#ffd23a"]),
                            (7, 0.6, 1.0, 0.55, 0.12, ["#ff4a1a", "#ff7a1a", "#ffb020"])],
                 bone="#f2c14e", tail_cols=["#ff4a1a", "#ff8a1a", "#ffd23a"]))

    def animate(t):
        a = t * TAU
        flap = math.sin(a * 2)
        pose = {"bird": {"p": (0, 0.35 * math.sin(a * 2 - 1), 0), "r": quat((-5 * flap, 0, 0))}}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 15 * flap, sx * 35 * flap))}
        pose["tailfan"] = {"r": quat((8 * math.sin(a * 2 + 1), 6 * math.sin(a), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 2), 10 * math.sin(a), 0))}
        pose["crest"] = {"s": (1, 1 + 0.12 * math.sin(a * 8), 1)}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.75 + 0.25 * math.sin(t * TAU * 4), "fire": 0.85 + 0.15 * math.sin(t * TAU * 12), "eyes": 1.0, "neon": 0.9}
    return finish(m, 8, "#ff8a1a", "#2a0e06", particles=[P_("rise", 200, "#ff8a1a", 0.18, (0.5, 4), (0.5, 10), 0.8, "square", 2.4),
                                                       P_("snow", 40, "#ffb020", 0.3, (1, 5), (0, 9), 0.4, "sparkle", 2.4)],
                  extra={"beam": {"color": "#ff8a1a", "top": 1.4, "bottom": 0.8, "height": 2.2, "y": 0.5, "intensity": 0.5}})


def dragon(m, P):
    d = quad(m, dict(L=P["L"], W=P["W"], H=P["H"], leg=P["leg"], lw=P["lw"], hs=P["hs"], snout=P["snout"], ear="none", tail="long", tail_n=P.get("tail_n", 10),
                     tail_seg=P.get("tail_seg", 0.4), tail_lift=-5, tail_curve=-3, neck=P["neck"], teeth=True, claws=P["claw"], eye_glow=P.get("eye_glow", 2),
                     cols=P["cols"], cosmic=P.get("cosmic"), vox=P.get("vox", 0.22), mane_neck=P.get("spines"), mane_emit=P.get("spine_emit", 0)))
    c = P["cols"]
    # placas/pinchos en el lomo y la cola
    for i in range(7):
        m.box("body", (0, P["H"] / 2 + 0.15, P["L"] / 2 - 0.3 - i * P["L"] / 7), (0.12, 0.42, 0.42), P["spike"], r=(45, 0, 0),
              emit=P.get("spine_emit", 0), tag="glow" if P.get("spine_emit") else None)
    for i in range(1, d["tail_n"], 2):
        m.box(f"tail{i}", (0, 0.28, -0.2), (0.08, 0.3, 0.3), P["spike"], r=(45, 0, 0))
    m.box(f"tail{d['tail_n'] - 1}", (0, 0, -0.5), (0.7, 0.1, 0.6), P["spike"], r=(0, 45, 0))  # punta en pala
    # cuernos
    hs = P["hs"]
    for sx in (1, -1):
        horn(m, "head", (sx * hs * 0.32, hs * 0.38, hs * 0.1), (sx * 0.4, 0.6, -0.7), P["horn_len"], hs * 0.2, -14, P["horn"], P["horn_tip"],
             tip_emit=P.get("horn_emit", 0), tag="glow" if P.get("horn_emit") else None)
    for sx in (1, -1):  # crestas de las mejillas
        m.box("head", (sx * hs * 0.55, 0, hs * 0.15), (0.08, hs * 0.3, hs * 0.5), P["spike"], r=(0, sx * 20, 0))
    # alas
    pairs = P.get("wing_pairs", 1)
    for pi in range(pairs):
        for side, sx in (("L", 1), ("R", -1)):
            w = f"wing{pi}_{side}"
            m.part(w, "body", (sx * P["W"] * 0.45, P["H"] * 0.4, P["L"] * (0.2 - 0.25 * pi)), (0, sx * (-20 + 15 * pi), sx * (10 - 10 * pi)))
            sc = P["wing_scale"] * (1 - 0.18 * pi)
            tips = [(1.2 * sc, 2.6 * sc), (2.7 * sc, 2.6 * sc), (3.8 * sc, 1.3 * sc), (3.7 * sc, -0.3 * sc), (2.6 * sc, -1.2 * sc)]
            membrane_wing(m, w, sx, (1.3 * sc, 1.6 * sc), tips, P["wing_bone"], P["membrane"][0], P["membrane"][1])
    return d


def build_ancient_dragon():
    m = new_model("ancient_dragon", 72)
    dragon(m, dict(L=3.2, W=1.5, H=1.4, leg=1.1, lw=0.45, hs=1.15, snout=0.8, neck=1.3, claw="#f2c14e", eye_glow=2.5,
                   cols=dict(main="#2f5a4a", belly="#d8c08a", dark="#1e3a30", eye="#ffb020", nose="#1a2a24", muzzle="#3a6a58", paw="#2f5a4a",
                             back="#24483a", head="#2f5a4a", tail="#2f5a4a", cheek="#3a6a58"),
                   spike="#c8a040", horn="#f2c14e", horn_tip="#fff0a0", horn_len=2.0, wing_scale=1.15, wing_bone="#24483a",
                   membrane=("#6a3a2a", "#8a4a32"), spines=None))
    for b in m.parts["head"].boxes:  # cuernos dorados metálicos
        if b["col"] in ("#f2c14e", "#fff0a0"):
            b["metal"] = 1
    # escamas esculpidas: filas de placas en los costados
    for i in range(6):
        for sx in (1, -1):
            for j in range(3):
                m.box("body", (sx * 0.76, 0.35 - j * 0.35, 1.3 - i * 0.5 - (j % 2) * 0.25), (0.06, 0.28, 0.4), "#3a6e5a" if (i + j) % 2 else "#24483a")

    def animate(t):
        a = t * TAU
        roar = max(0.0, math.sin(a)) ** 3
        flap = math.sin(a * 2)
        pose = {"body": {"p": (0, 0.06 * math.sin(a * 2), 0), "r": quat((-4 * roar, 0, 0))}}
        pose["head"] = {"r": quat((-15 * roar + 3 * math.sin(a * 2), 8 * math.sin(a) * (1 - roar), 0))}
        pose["jaw"] = {"r": quat((40 * roar, 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing0_{side}"] = {"r": quat((0, sx * 10 * flap, sx * (25 * flap + 10 * roar)))}
        tail_pose(pose, t, 10, amp=6, speed=1, axis="y", start=1)
        return pose

    m.animate = animate
    m.glow = lambda t: {"eyes": 0.8 + 0.4 * max(0.0, math.sin(t * TAU)) ** 3, "neon": 0.9, "glow": 1.0}
    return finish(m, 9, "#ffb020", "#14201c", particles=[P_("rise", 160, "#ffb020", 0.16, (0.5, 6), (0.3, 10), 0.6, "square", 2.2),
                                                       P_("float", 80, "#bfe8c8", 0.12, (6, 18), (0.5, 12), 0.5, "square", 1.4)])


def serpent(m, name, n, seg_len, r0, r1, path, colfn, v=0.2, head=None):
    """Cadena de segmentos de vóxeles a lo largo de una trayectoria (gusano/serpiente)."""
    parent = name
    prev = Vector(path(0))
    m.part(f"{name}0", name, tuple(prev))
    for i in range(1, n):
        k = i / (n - 1)
        p = Vector(path(k))
        m.part(f"{name}{i}", f"{name}{i - 1}", tuple(p - prev))
        prev = p
    for i in range(n):
        k = i / (n - 1)
        r_ = r0 + (r1 - r0) * k
        vox_ball(m, f"{name}{i}", (0, 0, 0), r_, v, colfn)
    return [f"{name}{i}" for i in range(n)]


def build_cosmic_worm():
    m = new_model("cosmic_worm", 96)
    m.part("worm", "root", (0, 1.0, 0))
    n = 14
    path = lambda k: (math.sin(k * 5.0) * 0.9, 0.3 + math.sin(k * math.pi) * 1.5 + k * 1.2, 2.4 - k * 5.0)
    segs = serpent(m, "w", n, 0.4, 0.62, 0.3, path, cosmic_col)
    m.parts["w0"].parent = "worm"
    # cabeza: anillo de mandíbulas y ojos brillantes
    h = segs[0]
    for k in range(8):
        a = k / 8 * TAU
        segment(m, h, (math.cos(a) * 0.45, math.sin(a) * 0.45, 0.4), (math.cos(a) * 0.3, math.sin(a) * 0.3, 0.95), 0.12, "#e6d6ff", emit=1.2, tag="nebula")
    for sx in (1, -1):
        m.box(h, (sx * 0.28, 0.32, 0.5), (0.16, 0.16, 0.08), "#fff3a0", emit=4, tag="eyes")
    ring(m, h, 0.55, 16, (0.08, 0.08), "#ffe08a", center=(0, 0, 0.42), rot=(90, 0, 0), emit=2, tag="neon")

    def animate(t):
        a = t * TAU
        pose = {"worm": {"p": (0, 0.2 * math.sin(a * 2), 0)}}
        for i in range(n):
            pose[f"w{i}"] = {"r": quat((6 * math.sin(a * 2 - i * 0.55), 10 * math.sin(a - i * 0.45), 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "neon": 0.9}
    return finish(m, 10, "#d14ee8", "#0a0626", particles=[P_("float", 300, "#ffffff", 0.12, (6, 24), (-2, 18), 0.6, "square", 2.0, True),
                                                        P_("rise", 140, "#c8a8ff", 0.2, (0.3, 3), (0.5, 8), 0.4, "sparkle", 2.4)])


# ======================================================================================
# 11-20
# ======================================================================================
def build_celestial_wolf():
    m = new_model("celestial_wolf", 96)
    wolf_like(m, white=True)
    # seis colas luminosas en abanico
    for ti in range(6):
        ang = -50 + ti * 20
        parent, piv = "body", (0, 0.45, -1.15)
        for i in range(6):
            k = i / 5
            n = f"t{ti}_{i}"
            m.part(n, parent, piv, (-40 if i == 0 else 8, ang if i == 0 else 0, 0))
            w = 0.26 + 0.22 * math.sin(k * math.pi * 0.9 + 0.2)
            col = "#ffffff" if k < 0.5 else ("#bfe8ff" if k < 0.8 else "#5fb8ff")
            m.box(n, (0, 0, -0.18), (w, w, 0.4), col, emit=0.5 + 2.5 * k, tag="glow")
            parent, piv = n, (0, 0, -0.36)
    # halo de luna creciente
    m.part("moon", "head", (0, 1.25, -0.2))
    for k in range(12):
        a = -0.9 + k / 11 * 3.4
        w = 0.24 * math.sin((k + 0.5) / 12 * math.pi) + 0.05
        m.box("moon", (math.cos(a + 1.2) * 0.5, math.sin(a + 1.2) * 0.5, 0), (w, w, 0.12), "#dff0ff", emit=2, tag="glow")
    for sx in (1, -1):  # runa en la frente
        m.box("head", (0, 0.32, 0.84), (0.06, 0.3, 0.03), "#5fb8ff", emit=3, tag="glow")

    def animate(t):
        a = t * TAU
        howl = max(0.0, math.sin(a)) ** 2
        pose = {"body": {"r": quat((-6 * howl, 0, 0)), "p": (0, 0.05 * math.sin(a * 2), 0)},
                "head": {"r": quat((-50 * howl, 0, 0))}, "jaw": {"r": quat((30 * howl, 0, 0))},
                "moon": {"r": quat((0, 0, math.degrees(a) * 0.5)), "s": (1 + 0.15 * howl,) * 3}}
        for ti in range(6):
            for i in range(1, 6):
                pose[f"t{ti}_{i}"] = {"r": quat((8 + 6 * math.sin(a * 2 - i * 0.6 + ti), 10 * math.sin(a - i * 0.5 + ti * 0.7), 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.75 + 0.25 * math.sin(t * TAU * 2), "eyes": 0.8 + 0.6 * max(0.0, math.sin(t * TAU)) ** 2, "neon": 0.9}
    return finish(m, 11, "#5fb8ff", "#0a1430", particles=[P_("orbit", 140, "#bfe8ff", 0.24, (2.5, 6), (0.5, 7), 0.25, "sparkle", 2.6),
                                                        P_("float", 200, "#ffffff", 0.12, (7, 22), (0.5, 16), 0.6, "square", 1.8, True)],
                  extra={"beam": {"color": "#5fb8ff", "top": 2.2, "bottom": 1.4, "height": 4, "y": 0.8, "intensity": 0.3}})


def build_griffin_emperor():
    m = new_model("griffin_emperor", 72)
    quad(m, dict(L=2.8, W=1.3, H=1.25, leg=1.05, lw=0.38, hs=1.1, snout=0.0, ear="pointy", tail="tuft", tail_n=6, tail_seg=0.32, tail_lift=-15,
                 claws="#f2c14e", eye_glow=1.5, tuft_col="#8a5a20",
                 cols=dict(main="#c89a52", belly="#f6e2b8", head="#ffffff", cheek="#f6f6f6", eye="#ffb020", inner="#e8e8e8", muzzle="#ffffff",
                           paw="#f2c14e", leg="#c89a52")))
    hs = 1.1
    m.box("head", (0, -0.05, hs * 0.81 + 0.3), (0.42, 0.34, 0.6), "#f2c14e", metal=1)  # pico dorado
    m.box("head", (0, -0.25, hs * 0.81 + 0.62), (0.24, 0.28, 0.16), "#f2c14e", r=(30, 0, 0), metal=1)
    for i in range(6):  # pecho emplumado
        for sx in (-1, 0, 1):
            m.box("body", (sx * 0.38, 0.4 - i * 0.16, 1.4 + 0.02 * i), (0.42, 0.24, 0.12), "#ffffff" if i % 2 else "#f0f0f0", r=(-15, 0, 0))
    m.part("crown_g", "head", (0, 0.6, 0.3))
    ring(m, "crown_g", 0.36, 14, (0.12, 0.16), "#f2c14e", metal=1)
    for k in range(7):
        a = k / 7 * TAU
        m.box("crown_g", (math.cos(a) * 0.36, 0.2, math.sin(a) * 0.36), (0.1, 0.32, 0.1), "#f2c14e", metal=1)
        m.box("crown_g", (math.cos(a) * 0.36, 0.4, math.sin(a) * 0.36), (0.12, 0.12, 0.12), "#ff4d6d" if k % 2 else "#4d9bff", r=(45, 0, 45), emit=1.2, tag="glow")
    gold = ["#fff6d8", "#ffe7a8", "#f2c14e"]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.6, 0.55, 0.6), (0, sx * -10, sx * 10))
        _wing(m, w, sx, [(13, 2.2, 4.2, 0.72, -0.14, gold), (11, 1.4, 2.6, 0.68, 0.0, ["#ffffff", "#fff6d8", "#ffe7a8"]),
                         (8, 0.7, 1.4, 0.64, 0.12, ["#ffffff", "#ffffff", "#fff6d8"])],
              [(0, 0), (1.1, 0.8), (2.2, 2.0), (3.1, 3.2)], "#f2c14e", "#f2c14e")

    def animate(t):
        a = t * TAU
        glide = math.sin(a)
        pose = {"body": {"p": (0, 1.4 + 0.3 * math.sin(a * 2), 0), "r": quat((-6, 0, 8 * glide))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-50, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((45, 0, 0))}
        flap = math.sin(a * 2) * 0.6
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 8 * flap, sx * (20 * flap - 5)))}
        pose["head"] = {"r": quat((6, -8 * glide, 0))}
        tail_pose(pose, t, 6, amp=8, speed=1, axis="y", start=1)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.85, "eyes": 1.0, "neon": 0.8 + 0.2 * math.sin(t * TAU * 2)}
    return finish(m, 12, "#ffd23a", "#1a2a4a", particles=[P_("snow", 70, "#fff6d8", 0.3, (1, 7), (0, 10), 0.35, "sparkle", 2.4),
                                                        P_("orbit", 120, "#ffffff", 0.14, (4, 8), (1, 8), 0.5, "square", 1.6)],
                  extra={"dist": 1.4})


def build_abyss_hydra():
    m = new_model("abyss_hydra", 96)
    quad(m, dict(L=3.0, W=2.0, H=1.4, leg=0.8, lw=0.5, hs=0.01, snout=0.0, ear="none", tail="long", tail_n=8, tail_seg=0.4, tail_lift=-5,
                 claws="#b06bff", pattern="runes", runes=8,
                 cols=dict(main="#1e1636", belly="#3a2a5a", accent="#b06bff", head="#1e1636", eye="#b06bff", paw="#2a1e48")))
    m.parts["head"].boxes.clear()
    for nm in ("jaw", "ear_L", "ear_R"):
        if nm in m.parts:
            m.parts[nm].boxes.clear()
    for i in range(7):  # siete cuellos con cabezas de serpiente
        ang = (i - 3) * 22
        parent, piv = "body", ((i - 3) * 0.26, 0.5, 1.3)
        for j in range(6):
            n = f"n{i}_{j}"
            m.part(n, parent, piv, (-45 if j == 0 else 8, ang if j == 0 else 0, 0))
            w = 0.42 - 0.03 * j
            m.box(n, (0, 0, 0.2), (w, w, 0.44), "#2a1e48" if j % 2 else "#1e1636")
            m.box(n, (0, w / 2, 0.2), (0.06, 0.04, 0.38), "#b06bff", emit=2, tag="glow")
            parent, piv = n, (0, 0, 0.42)
        h = f"h{i}"
        m.part(h, parent, piv, (40, 0, 0))
        m.box(h, (0, 0, 0.25), (0.5, 0.36, 0.6), "#2a1e48")
        m.box(h, (0, -0.08, 0.6), (0.36, 0.2, 0.3), "#3a2a5a")
        for sx in (1, -1):
            m.box(h, (sx * 0.2, 0.1, 0.42), (0.1, 0.08, 0.06), "#d8a8ff", emit=4, tag="eyes")
            m.box(h, (sx * 0.15, 0.22, 0.1), (0.08, 0.2, 0.08), "#b06bff", r=(-30, 0, sx * 20), emit=1.5, tag="glow")
        m.box(h, (0, -0.2, 0.45), (0.3, 0.06, 0.4), "#5a1a3a")
    for k in range(10):  # cristales oscuros en el lomo
        crystal(m, "body", ((k % 3 - 1) * 0.5, 0.85, 1.0 - k * 0.25), 0.28, 0.6, "#8a4ae8", emit=1.2, tag="glow")

    def animate(t):
        a = t * TAU
        pose = {"body": {"p": (0, 0.05 * math.sin(a * 2), 0)}}
        for i in range(7):
            for j in range(1, 6):
                pose[f"n{i}_{j}"] = {"r": quat((6 * math.sin(a * 2 - j * 0.5 + i), 8 * math.sin(a - j * 0.5 + i * 0.9), 0))}
            snap = max(0.0, math.sin(a * 2 + i * 0.9)) ** 8
            pose[f"h{i}"] = {"r": quat((40 - 25 * snap, 0, 0))}
        tail_pose(pose, t, 8, amp=8, speed=1, axis="y", start=1)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.6 + 0.4 * math.sin(t * TAU * 2) ** 2, "eyes": 1.0, "neon": 0.9}
    return finish(m, 13, "#b06bff", "#0c0618", particles=[P_("rise", 220, "#b06bff", 0.2, (0.5, 6), (0, 10), 0.5, "square", 2.4),
                                                        P_("float", 140, "#6a4aa8", 0.16, (6, 20), (0.5, 12), 0.4, "square", 1.4)])


def build_world_titan():
    m = new_model("world_titan", 72)
    stone, stone2, moss = "#6a6e78", "#7a7e88", "#4f7a3a"
    m.part("titan", "root", (0, 3.4, 0))
    m.box("titan", (0, 1.3, 0), (2.8, 2.6, 1.8), stone)  # torso
    m.box("titan", (0, 2.4, 0.2), (3.2, 0.8, 2.0), stone2)  # hombros
    m.box("titan", (0, 0.1, 0), (2.2, 0.6, 1.5), stone2)  # cintura
    m.box("titan", (0, 2.75, -0.2), (2.4, 0.3, 1.4), moss)
    for i in range(7):  # cristales incrustados
        a = i * 1.3
        crystal(m, "titan", (math.sin(a) * 1.2, 1.0 + (i % 3) * 0.6, 0.85 + 0.1 * (i % 2)), 0.4, 0.9, "#5ff4ff" if i % 2 else "#c88aff",
                rot=(70, 0, 20 * math.sin(a)), emit=1.5, tag="glow")
    for i in range(4):
        crystal(m, "titan", ((i - 1.5) * 0.7, 3.0, -0.4), 0.45, 1.3 + 0.3 * (i % 2), "#5ff4ff", rot=(-15, 0, (i - 1.5) * 10), emit=1.5, tag="glow")
    m.part("head", "titan", (0, 3.0, 0.4))
    m.box("head", (0, 0.4, 0), (1.2, 1.0, 1.1), stone2)
    m.box("head", (0, 0.65, 0.5), (1.25, 0.25, 0.25), stone)  # ceño
    for sx in (1, -1):
        m.box("head", (sx * 0.28, 0.4, 0.56), (0.24, 0.12, 0.05), "#5ff4ff", emit=4, tag="eyes")
    m.box("head", (0, 0.05, 0.56), (0.6, 0.12, 0.05), "#2a2c32")
    for side, sx in (("L", 1), ("R", -1)):
        sh = f"arm_{side}"
        m.part(sh, "titan", (sx * 1.9, 2.3, 0.1), (0, 0, sx * 8))
        m.box(sh, (0, 0.1, 0), (1.1, 1.1, 1.1), stone2)
        m.box(sh, (0, -1.0, 0), (0.9, 1.6, 0.9), stone)
        m.part(f"fore_{side}", sh, (0, -1.8, 0), (-15, 0, 0))
        m.box(f"fore_{side}", (0, -0.8, 0), (0.85, 1.6, 0.85), stone2)
        m.box(f"fore_{side}", (0, -1.8, 0.1), (1.2, 0.8, 1.2), stone)  # puño
        crystal(m, f"fore_{side}", (sx * 0.45, -0.6, 0), 0.3, 0.7, "#5ff4ff", rot=(0, 0, -sx * 70), emit=1.5, tag="glow")
        lg = f"leg_{side}"
        m.part(lg, "titan", (sx * 0.75, -0.1, 0))
        m.box(lg, (0, -0.9, 0), (1.0, 1.8, 1.0), stone)
        m.box(lg, (0, -2.4, 0), (0.95, 1.4, 0.95), stone2)
        m.box(lg, (0, -3.2, 0.2), (1.2, 0.4, 1.5), stone)
    m.part("quake", "root", (0, 0.86, 0))
    ring(m, "quake", 2.0, 40, (0.12, 0.05), "#ffcf7a", emit=2, tag="quake")

    def animate(t):
        a = t * TAU
        step = math.sin(a)
        pose = {"titan": {"p": (0, 0.15 * abs(step), 0), "r": quat((0, 4 * step, 3 * step))}}
        pose["leg_L"] = {"r": quat((-22 * max(0, step), 0, 0))}
        pose["leg_R"] = {"r": quat((-22 * max(0, -step), 0, 0))}
        pose["arm_L"] = {"r": quat((18 * step, 0, 0))}
        pose["arm_R"] = {"r": quat((-18 * step, 0, 0))}
        pose["head"] = {"r": quat((0, 10 * math.sin(a * 0.5 * 2), 0))}
        ph = (t * 2) % 1
        pose["quake"] = {"s": (0.6 + 3 * ph, 1, 0.6 + 3 * ph)}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "quake": 1 - (t * 2) % 1, "neon": 0.9}
    return finish(m, 14, "#5ff4ff", "#1a1c24", particles=[P_("rise", 160, "#b8a890", 0.22, (1, 7), (0, 3), 0.8, "square", 1.2),
                                                        P_("float", 120, "#5ff4ff", 0.16, (3, 12), (0.5, 12), 0.4, "sparkle", 2.0)],
                  extra={"shakePart": "titan", "dist": 1.3})


def build_prismatic_unicorn():
    m = new_model("prismatic_unicorn", 48)
    rainbow = ["#ff9ab8", "#ffd27a", "#fff3a0", "#a8f0b8", "#9ad8ff", "#c8a8ff"]
    quad(m, dict(L=2.6, W=1.0, H=1.05, leg=1.35, lw=0.28, hs=0.95, snout=0.55, ear="pointy", tail="long", tail_n=8, tail_seg=0.3, tail_lift=-30,
                 neck=1.0, mane_neck=rainbow, mane_emit=1.2, eye_glow=1.0,
                 cols=dict(main="#fbf8ff", belly="#ffffff", inner="#ffd6f0", eye="#c88aff", nose="#e6d6f0", muzzle="#f6f0ff", paw="#f2c14e", leg="#fbf8ff",
                           tail="#ffd6f0")))
    for i in range(8):
        for b in m.parts[f"tail{i}"].boxes:
            b["col"] = rainbow[i % 6]
            b["emit"], b["tag"] = 1.0, "glow"
    crystal(m, "head", (0, 0.8, 0.55), 0.25, 1.3, "#e8f6ff", rot=(-30, 0, 0), emit=2.0, tag="glow")  # cuerno cristalino
    crystal(m, "head", (0, 0.8, 0.55), 0.12, 1.1, "#ffffff", rot=(-30, 0, 0), emit=3.0, tag="glow")
    for k in range(6):  # flequillo arcoíris
        m.box("head", ((k - 2.5) * 0.12, 0.5, 0.3 - 0.05 * k), (0.14, 0.3, 0.3), rainbow[k], emit=1.0, tag="glow")

    def animate(t):
        a = t * TAU
        pose = walk_pose({}, t, amp=35, speed=2, gallop=True, bob=0.15)
        tail_pose(pose, t, 8, amp=10, speed=2, axis="x", start=1)
        pose["head"] = {"r": quat((-6 * math.sin(a * 4), 0, 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 4), "eyes": 1.0, "neon": 0.9}
    return finish(m, 15, "#ff9ad8", "#1a1030", particles=[P_("rise", 200, "#ffd6f0", 0.2, (0.4, 4), (0.3, 6), 1.2, "sparkle", 2.6),
                                                        P_("orbit", 160, "#9ad8ff", 0.18, (2.5, 6), (0.5, 7), 0.4, "square", 2.0),
                                                        P_("orbit", 120, "#fff3a0", 0.18, (3, 7), (0.5, 7), -0.3, "square", 2.0)],
                  extra={"beam": {"color": "#ffd6f0", "top": 2.2, "bottom": 1.6, "height": 4.5, "y": 0.8, "intensity": 0.3}})


def build_shadow_sovereign():
    m = new_model("shadow_sovereign", 72)
    dragon(m, dict(L=3.6, W=1.6, H=1.5, leg=1.15, lw=0.48, hs=1.2, snout=0.85, neck=1.4, claw="#b06bff", eye_glow=3,
                   cols=dict(main="#16121e", belly="#2a2238", dark="#0a080e", eye="#c88aff", nose="#0a080e", muzzle="#221c2e", paw="#16121e",
                             back="#0e0c14", head="#16121e", tail="#16121e", cheek="#221c2e"),
                   spike="#8a4ae8", spine_emit=1.8, horn="#1a1424", horn_tip="#c88aff", horn_emit=2.5, horn_len=2.2, wing_scale=1.2, wing_pairs=3,
                   wing_bone="#1a1424", membrane=("#3a1a5a", "#2a1240"), spines=["#8a4ae8", "#6a2ac8"]))
    for i in range(8):  # llamas violetas a lo largo del lomo
        n = f"vflame{i}"
        m.part(n, "body", (0, 0.85, 1.4 - i * 0.4))
        flame(m, n, (0, 0, 0), 0.8 - 0.05 * i, 0.32, seed=i, tag="vfire")
        for b in m.parts[n].boxes:
            b["col"] = ["#5a1aa8", "#7a2ac8", "#9a4ae8", "#b86aff", "#d8a8ff", "#f2e6ff"][min(5, int((b["c"].y / 0.8) * 6))]

    def animate(t):
        a = t * TAU
        flap = math.sin(a * 2)
        roar = max(0.0, math.sin(a)) ** 3
        pose = {"body": {"p": (0, 1.2 + 0.3 * math.sin(a * 2 - 1), 0), "r": quat((-4, 0, 0))}}
        for k in ("FL", "FR", "BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((25 if k[0] == "B" else -15, 0, 0))}
        for pi in range(3):
            for side, sx in (("L", 1), ("R", -1)):
                pose[f"wing{pi}_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 30 * math.sin(a * 2 - pi * 0.5)))}
        pose["head"] = {"r": quat((-12 * roar, 0, 0))}
        pose["jaw"] = {"r": quat((40 * roar, 0, 0))}
        for i in range(8):
            f = 1 + 0.15 * math.sin(a * 8 + i * 1.7)
            pose[f"vflame{i}"] = {"s": (1 / f ** 0.5, f, 1 / f ** 0.5)}
        tail_pose(pose, t, 10, amp=8, speed=1, axis="y", start=1)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 1.0, "vfire": 0.85 + 0.15 * math.sin(t * TAU * 12), "fire": 1.0, "neon": 0.9}
    return finish(m, 16, "#b06bff", "#08050e", particles=[P_("rise", 260, "#3a2a4a", 0.4, (0.5, 6), (0, 9), 0.5, "dot", 0.9),
                                                        P_("rise", 180, "#b06bff", 0.18, (0.5, 5), (0.5, 10), 0.8, "square", 2.4)],
                  extra={"dist": 1.3})


def build_cosmic_leviathan():
    m = new_model("cosmic_leviathan", 96)
    m.part("worm", "root", (0, 2.6, 0))
    n = 10
    path = lambda k: (0, math.sin(k * math.pi * 1.2) * 0.6, 3.6 - k * 7.4)

    def neb(p):
        return cosmic_col(p, pal=("#0a1a4a", "#102462", "#0e1e56", "#183080"), neb=("#5ff4ff", "#d14ee8"))

    segs = serpent(m, "w", n, 0.8, 1.3, 0.45, path, neb, v=0.24)
    m.parts["w0"].parent = "worm"
    h = segs[0]
    for sx in (1, -1):
        m.box(h, (sx * 0.9, 0.35, 0.8), (0.22, 0.2, 0.1), "#fff3a0", emit=4, tag="eyes")
        m.box(h, (sx * 1.2, -0.2, -0.2), (1.4, 0.1, 0.8), "#5ff4ff", r=(0, 0, sx * -25), emit=1.2, tag="glow")  # aletas
    m.box(h, (0, -0.45, 1.05), (1.4, 0.12, 0.4), "#2a1a4a")
    for i in range(2, n, 2):  # aletas dorsales de luz
        crystal(m, segs[i], (0, 1.3 - i * 0.08, 0), 0.4, 1.0, "#5ff4ff", rot=(-30, 0, 0), emit=1.5, tag="glow")
    tail = segs[-1]
    for sx in (1, -1):
        m.box(tail, (sx * 0.9, 0, -0.4), (1.6, 0.12, 0.8), "#5ff4ff", r=(0, sx * 25, 0), emit=1.5, tag="glow")
    for k in range(3):  # planetas que lo acompañan
        pn = f"planet{k}"
        a = k / 3 * TAU
        m.part(pn, "root", (math.cos(a) * 6, 3 + k, math.sin(a) * 6))
        vox_ball(m, pn, (0, 0, 0), 0.5 + 0.15 * k, 0.14, lambda p, k=k: ["#ff8a4a", "#7fe0ff", "#9cff8a"][k] if math.sin(p.y * 8) > 0 else "#2a2a4a")

    def animate(t):
        a = t * TAU
        pose = {"worm": {"p": (0, 0.4 * math.sin(a * 2), 0), "r": quat((0, 8 * math.sin(a), 0))}}
        for i in range(n):
            pose[f"w{i}"] = {"r": quat((7 * math.sin(a * 2 - i * 0.6), 4 * math.sin(a - i * 0.4), 0))}
        for k in range(3):
            ang = k / 3 * TAU + a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 6 - piv.x, 0.3 * math.sin(a * 2 + k), math.sin(ang) * 6 - piv.z),
                                  "r": quat((0, math.degrees(a * 2), 20))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "glow": 0.9, "neon": 0.9}
    return finish(m, 17, "#5ff4ff", "#040a24", particles=[P_("float", 400, "#ffffff", 0.14, (8, 30), (-4, 22), 0.6, "square", 2.0, True),
                                                        P_("orbit", 160, "#d14ee8", 0.24, (3, 8), (1, 8), 0.2, "sparkle", 2.4)],
                  extra={"ground": None, "dist": 1.2})


def build_phoenix_deity():
    m = new_model("phoenix_deity", 72)
    sun = ["#fff6d8", "#ffe14a", "#ffb020"]
    bird(m, dict(s=1.35, crest_flames=True, eye_glow=3, belly_emit=1.5, tail_emit=2.0, tail_feathers=9, beak_metal=True,
                 cols=dict(main="#ffb020", belly="#fff0a0", head="#ffcf3a", beak="#f2c14e", eye="#ffffff", accent="#ffffff", leg="#f2c14e"),
                 wing_rows=[(14, 2.0, 3.8, 0.66, -0.14, sun), (12, 1.2, 2.2, 0.62, 0.0, ["#ffffff", "#fff6d8", "#ffe14a"]),
                            (8, 0.6, 1.1, 0.58, 0.12, ["#ffffff", "#ffffff", "#fff6d8"])],
                 bone="#f2c14e", tail_cols=["#ff8a1a", "#ffd23a", "#fff6d8"]))
    # halo ardiente y disco solar
    m.part("halo", "head", (0, 0.2, -0.6))
    for k in range(16):
        a = k / 16 * TAU
        n = f"hf{k}"
        m.part(n, "halo", (math.cos(a) * 1.3, math.sin(a) * 1.3, 0), (0, 0, math.degrees(a) - 90))
        flame(m, n, (0, 0, 0), 0.6, 0.22, seed=k)
    ring(m, "halo", 1.3, 40, (0.14, 0.14), "#f2c14e", rot=(90, 0, 0), metal=1)
    m.part("sun", "bird", (0, 1.6, -1.6))
    for k in range(24):
        a = k / 24 * TAU
        segment(m, "sun", (math.cos(a) * 1.2, math.sin(a) * 1.2, 0), (math.cos(a) * 2.6, math.sin(a) * 2.6, 0), (0.12, 0.06), "#ffe14a", emit=1.5, tag="glow")
    ring(m, "sun", 1.1, 40, (0.2, 0.1), "#fff6d8", rot=(90, 0, 0), emit=2.0, tag="glow")

    def animate(t):
        a = t * TAU
        flap = math.sin(a * 2)
        pose = {"bird": {"p": (0, 0.4 * math.sin(a * 2 - 1), 0), "r": quat((-5 * flap, 0, 0))}}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 12 * flap, sx * 30 * flap))}
        pose["tailfan"] = {"r": quat((8 * math.sin(a * 2 + 1), 6 * math.sin(a), 0))}
        pose["halo"] = {"r": quat((0, 0, math.degrees(a)))}
        pose["sun"] = {"r": quat((0, 0, -math.degrees(a) * 0.5)), "s": (1 + 0.05 * math.sin(a * 4),) * 3}
        pose["crest"] = {"s": (1, 1 + 0.15 * math.sin(a * 8), 1)}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 4), "fire": 0.85 + 0.15 * math.sin(t * TAU * 12), "eyes": 1.0, "neon": 0.9}
    return finish(m, 18, "#ffb020", "#2a1404", particles=[P_("rise", 300, "#ffb020", 0.2, (0.5, 5), (0.5, 12), 0.8, "square", 2.6),
                                                        P_("orbit", 200, "#fff6d8", 0.24, (3, 8), (1, 10), 0.3, "sparkle", 2.6)],
                  extra={"beam": {"color": "#ffd23a", "top": 2.4, "bottom": 1.4, "height": 3.2, "y": 0.8, "intensity": 0.4}, "dist": 1.3})


def build_world_serpent():
    m = new_model("world_serpent", 96)
    m.part("worm", "root", (0, 2.0, 0))
    n = 26
    path = lambda k: (math.sin(k * TAU * 1.0) * 3.2, 1.2 + math.sin(k * TAU * 2) * 0.9 + k * 1.5, math.cos(k * TAU * 1.0) * 3.2 * (1 - 0.3 * k))

    def scales(p):
        h = _hash(p.x, p.y, p.z)
        if h > 0.97:
            return ("#9ffcff", 2.5, "twinkle")
        f = fbm(p, 1.3, 2.0)
        if abs(f - 0.5) < 0.03:
            return ("#3affd0", 2.0, "glow")
        return ["#0e2a2a", "#123434", "#0a2222", "#1a3e3a"][int(h * 97) % 4]

    segs = serpent(m, "w", n, 0.5, 0.75, 0.3, path, scales, v=0.22)
    m.parts["w0"].parent = "worm"
    h = segs[0]
    for sx in (1, -1):
        m.box(h, (sx * 0.4, 0.3, 0.55), (0.18, 0.12, 0.08), "#ff3a6a", emit=4, tag="eyes")
        horn(m, h, (sx * 0.4, 0.5, 0.0), (sx * 0.3, 0.6, -0.8), 1.2, 0.18, -10, "#1a3e3a", "#3affd0", tip_emit=2, tag="glow")
    # portales que atraviesa
    for k, kk in enumerate((0.2, 0.5, 0.8)):
        p = Vector(path(kk)) + Vector((0, 2.0, 0))
        pn = f"portal{k}"
        m.part(pn, "root", tuple(p))
        ring(m, pn, 1.1, 32, (0.18, 0.18), "#b06bff" if k % 2 else "#3affd0", rot=(90, k * 50, 0), emit=3, tag="portal")
        ring(m, pn, 0.9, 32, (0.06, 0.06), "#ffffff", rot=(90, k * 50, 0), emit=2, tag="portal")
    for k in range(4):  # planetas
        pn = f"planet{k}"
        a = k / 4 * TAU
        m.part(pn, "root", (math.cos(a) * 6.5, 3 + k * 0.8, math.sin(a) * 6.5))
        cols = [("#ff8a4a", "#c9522a"), ("#7fe0ff", "#3a8ac9"), ("#9cff8a", "#3f9a5a"), ("#e6d6ff", "#8a6ac8")][k]
        vox_ball(m, pn, (0, 0, 0), 0.5 + 0.15 * (k % 2), 0.14, lambda p, cols=cols: cols[0] if math.sin(p.y * 8) > 0 else cols[1])
        if k == 1:
            ring(m, pn, 1.0, 24, (0.2, 0.04), "#e6d6ff", rot=(20, 0, 10))

    def animate(t):
        a = t * TAU
        pose = {"worm": {"r": quat((0, math.degrees(a), 0))}}
        for i in range(n):
            pose[f"w{i}"] = {"r": quat((4 * math.sin(a * 2 - i * 0.5), 5 * math.sin(a * 2 - i * 0.4), 0))}
        for k in range(3):
            pose[f"portal{k}"] = {"s": (1 + 0.08 * math.sin(a * 4 + k),) * 3}
        for k in range(4):
            ang = k / 4 * TAU - a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 6.5 - piv.x, 0.3 * math.sin(a * 2 + k), math.sin(ang) * 6.5 - piv.z),
                                  "r": quat((0, math.degrees(a * 2), 15))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 1.0,
                        "portal": 0.8 + 0.2 * math.sin(t * TAU * 6), "neon": 0.9}
    return finish(m, 19, "#3affd0", "#020a0c", particles=[P_("float", 400, "#ffffff", 0.14, (8, 30), (-4, 22), 0.6, "square", 2.0, True),
                                                        P_("orbit", 220, "#b06bff", 0.22, (3, 8), (1, 9), 0.3, "sparkle", 2.4)],
                  extra={"dist": 1.15})


def build_genesis_beast():
    m = new_model("genesis_beast", 96)

    def cosmos(p):
        return cosmic_col(p, pal=("#0e0a2e", "#160f44", "#1d1456", "#0a0822"), neb=("#ffb8f0", "#7fe8ff"))

    quad(m, dict(L=3.6, W=1.7, H=1.6, leg=1.3, lw=0.5, hs=1.4, snout=0.6, ear="pointy", tail="long", tail_n=10, tail_seg=0.4, tail_lift=-20,
                 tail_emit=3, teeth=True, claws="#f2c14e", eye_glow=3, cosmic=cosmos, vox=0.25,
                 cols=dict(main="#160f44", belly="#2a1f6a", head="#1d1456", cheek="#221a60", eye="#fff6d8", inner="#7fe8ff", nose="#0a0822",
                           muzzle="#2a1f6a", paw="#f2c14e", leg="#160f44", tail="#ffb8f0")))
    hs = 1.4
    # melena de constelaciones
    m.part("mane", "head", (0, 0, 0.3))
    for layer in range(3):
        r_ = 0.95 + layer * 0.28
        nn = 16 + layer * 6
        for k in range(nn):
            a = k / nn * TAU
            col = ["#2a1f6a", "#3a2a8a", "#5a3ab8"][layer] if k % 3 else "#ffe9a8"
            em = 0 if k % 3 else 2.5
            m.box("mane", (math.cos(a) * r_, math.sin(a) * r_, -0.2 - layer * 0.2), (0.42, 0.42, 0.36), col, r=(0, 0, math.degrees(a) + 45),
                  emit=em, tag="twinkle" if em else None)
    pts = [(math.cos(k / 7 * TAU) * 1.9, math.sin(k / 7 * TAU) * 1.9, -0.5) for k in range(7)]
    polyline(m, "mane", pts, 0.04, "#fff6d8", closed=True, emit=2, tag="glow")
    for p in pts:
        star(m, "mane", p, 0.4, "#ffffff", emit=3, tag="twinkle")
    # cuernos de dragón dorados
    for sx in (1, -1):
        horn(m, "head", (sx * hs * 0.3, hs * 0.42, hs * 0.1), (sx * 0.35, 0.7, -0.6), 2.4, hs * 0.2, -12, "#f2c14e", "#fff6d8", tip_emit=2, tag="glow")
    for b in m.parts["head"].boxes:
        if b["col"] in ("#f2c14e", "#fff6d8"):
            b["metal"] = 1
    # alas cósmicas de cristal
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.8, 0.7, 0.4), (0, sx * -15, sx * 5))
        tips = []
        for i in range(12):
            k = i / 11
            th = math.radians(-25 + k * 115)
            Lw = 2.0 + 2.2 * math.sin(k * math.pi * 0.85 + 0.25)
            d = Vector((sx * math.cos(th), math.sin(th), 0))
            rot = (0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th))
            crystal(m, w, d * (0.3 + Lw / 2), 0.62, Lw, ["#6a4cff", "#ffb8f0", "#7fe8ff"][i % 3], rot=rot, emit=0.8, tag="nebula")
            tip = d * (0.4 + Lw)
            tips.append(tip)
            star(m, w, tip + Vector((0, 0, 0.1)), 0.4, "#ffffff", emit=3, tag="twinkle")
        polyline(m, w, tips, 0.04, "#cfd8ff", emit=2, tag="glow")
    # halo y galaxia girando encima
    m.part("halo", "body", (0, 3.4, 0.8), (70, 0, 0))
    ring(m, "halo", 1.6, 48, (0.22, 0.18), "#f2c14e", metal=1)
    ring(m, "halo", 1.6, 48, (0.08, 0.22), "#fff6d8", emit=1.5, tag="glow")
    m.part("galaxy", "root", (0, 9.0, 0), (75, 0, 0))
    for arm in range(3):
        for i in range(30):
            u = i / 29
            a = arm * TAU / 3 + u * TAU * 0.9
            r_ = 0.2 + u * 2.6
            col = "#ffffff" if u < 0.25 else ["#ffb8f0", "#7fe8ff", "#c8a8ff"][arm]
            m.box("galaxy", (math.cos(a) * r_, (_hash(i, arm) - 0.5) * 0.2, math.sin(a) * r_), (0.18 - 0.08 * u,) * 3, col, emit=3 - 2 * u, tag="twinkle")
    for k in range(4):  # mundos recién creados orbitando
        pn = f"planet{k}"
        a = k / 4 * TAU
        m.part(pn, "root", (math.cos(a) * 7, 4 + k * 0.7, math.sin(a) * 7))
        cols = [("#ff8a4a", "#c9522a"), ("#7fe0ff", "#3a8ac9"), ("#9cff8a", "#3f9a5a"), ("#ffe08a", "#c8a040")][k]
        vox_ball(m, pn, (0, 0, 0), 0.55, 0.14, lambda p, cols=cols: cols[0] if math.sin(p.y * 8 + p.x * 3) > 0 else cols[1])

    def animate(t):
        a = t * TAU
        pose = walk_pose({}, t, amp=14, speed=1, bob=0.06)
        pose["head"] = {"r": quat((-4 * math.sin(a * 2), 8 * math.sin(a), 0))}
        pose["mane"] = {"r": quat((0, 0, math.degrees(a) * 0.25)), "s": (1 + 0.05 * math.sin(a * 4),) * 3}
        flap = math.sin(a * 2)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 20 * flap))}
        pose["halo"] = {"r": quat((0, math.degrees(a), 0))}
        pose["galaxy"] = {"r": quat((0, math.degrees(a), 0))}
        tail_pose(pose, t, 10, amp=10, speed=1, axis="y", start=1)
        for k in range(4):
            ang = k / 4 * TAU + a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 7 - piv.x, 0.4 * math.sin(a * 2 + k), math.sin(ang) * 7 - piv.z),
                                  "r": quat((0, math.degrees(a * 2), 20))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "glow": 0.85 + 0.15 * math.sin(t * TAU * 4),
                        "eyes": 1.0, "neon": 0.9}
    return finish(m, 20, "#ffb8f0", "#06041a", particles=[P_("float", 450, "#ffffff", 0.14, (8, 32), (-4, 24), 0.6, "square", 2.2, True),
                                                        P_("orbit", 220, "#ffb8f0", 0.24, (3, 9), (1, 10), 0.25, "sparkle", 2.6),
                                                        P_("rise", 160, "#7fe8ff", 0.2, (0.5, 5), (0.5, 12), 0.6, "square", 2.4)],
                  extra={"beam": {"color": "#ffb8f0", "top": 3, "bottom": 2, "height": 5, "y": 0.8, "intensity": 0.3}, "dist": 1.25})


BUILDERS = {
    "animal_rabbit": build_rabbit, "animal_cat": build_cat, "animal_dog": build_dog, "animal_cheetah": build_cheetah,
    "animal_wolf": build_wolf, "animal_lion": build_lion, "animal_frost_tiger": build_frost_tiger, "animal_phoenix": build_phoenix,
    "animal_ancient_dragon": build_ancient_dragon, "animal_cosmic_worm": build_cosmic_worm, "animal_celestial_wolf": build_celestial_wolf,
    "animal_griffin_emperor": build_griffin_emperor, "animal_abyss_hydra": build_abyss_hydra, "animal_world_titan": build_world_titan,
    "animal_prismatic_unicorn": build_prismatic_unicorn, "animal_shadow_sovereign": build_shadow_sovereign,
    "animal_cosmic_leviathan": build_cosmic_leviathan, "animal_phoenix_deity": build_phoenix_deity, "animal_world_serpent": build_world_serpent,
    "animal_genesis_beast": build_genesis_beast,
}
