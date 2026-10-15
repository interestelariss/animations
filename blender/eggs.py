"""Huevos mágicos hechos de cubos (estilo pets de Roblox / Claude Design).

* Huevo Celestial: cáscara de vóxeles azules con destellos, jaula dorada de
  rombos, emblema de cristal, gema superior, halo, alas de plumas, anillos de
  neón orbitando, estrellas y pedestal con anillos de energía.
* Huevo de Hielo: cáscara de escamas azul marino con vetas cian brillantes,
  corona de cristales, alas de esquirlas de hielo, espirales de energía,
  esquirlas orbitando y un estanque con ondas.
"""

import math

from mathutils import Vector

from voxel import (Model, crystal, egg_radius, egg_surface, egg_voxels, polyline, quat, ring,
                   segment, star)

TAU = math.tau


def _hash(*v):
    h = 0
    for x in v:
        h = (h * 73856093) ^ int(round(x * 1000)) * 19349663
    return ((h & 0xFFFFFFFF) % 1000) / 1000


def _wing(m, part, sx, rows, bone, blade_col, metal_col=None):
    """Ala de plumas. rows = [(n, largo_min, largo_max, ancho, z, colores)]."""
    def P(x, y, z=0.0):
        return (sx * x, y, z)

    # hueso del ala (dorado) con un pincho
    pts = [P(*p) for p in bone]
    polyline(m, part, pts, 0.24, metal_col or blade_col, metal=1 if metal_col else 0)
    for (n, lmin, lmax, width, z, cols) in rows:
        for i in range(n):
            k = i / max(n - 1, 1)
            # punto de anclaje a lo largo del hueso
            seg = k * (len(bone) - 1)
            j = min(int(seg), len(bone) - 2)
            u = seg - j
            ax = bone[j][0] + (bone[j + 1][0] - bone[j][0]) * u
            ay = bone[j][1] + (bone[j + 1][1] - bone[j][1]) * u
            theta = -45 + k * 128  # de abajo-fuera (base) a arriba (punta)
            L = lmin + (lmax - lmin) * math.sin(k * math.pi * 0.85 + 0.25)
            d = Vector((math.cos(math.radians(theta)), math.sin(math.radians(theta)), 0))
            ang = theta - 90 if sx > 0 else 90 - theta
            dd = Vector((d.x * sx, d.y, 0))
            base = Vector(P(ax, ay, z))
            for s_i, (frac, wf) in enumerate(((0.0, 1.0), (0.32, 0.92), (0.6, 0.7))):
                seg_len = L * (0.45 if s_i < 2 else 0.38)
                c = base + dd * (L * frac + seg_len / 2)
                m.box(part, c, (width * wf, seg_len + 0.05, 0.13), cols[min(s_i, len(cols) - 1)], r=(0, 0, ang))
            # punta fina
            c = base + dd * (L * 0.97)
            m.box(part, c, (width * 0.25, L * 0.12, 0.12), cols[-1], r=(0, 0, ang))


# ======================================================================================
#  HUEVO CELESTIAL
# ======================================================================================

GOLD = "#f6c64a"
GOLD_DARK = "#c98f22"
GOLD_LIGHT = "#ffe58a"
CORE = "#9dfbe6"
TEAL = "#33ffd0"
PINK = "#ff7ce0"
STAR = "#eaffff"
PED = "#1a2244"
PED2 = "#232e5c"
FEATHER = ["#f7fcff", "#e4f5ff", "#c4ecff"]
FEATHER2 = ["#ffffff", "#eef9ff", "#d6f2ff"]


def build_celestial():
    m = Model("egg_celestial", fps=24, frames=96)
    m.part("root")
    R, HB, HT, V = 2.0, 2.2, 2.9, 0.2
    CY = 4.5  # centro del huevo

    # ---------------- pedestal ----------------
    m.box("root", (0, 0.2, 0), (4.4, 0.4, 4.4), PED)
    m.box("root", (0, 0.2, 0), (4.4, 0.4, 4.4), PED, r=(0, 45, 0))
    m.box("root", (0, 0.55, 0), (3.3, 0.3, 3.3), PED2)
    m.box("root", (0, 0.55, 0), (3.3, 0.3, 3.3), PED2, r=(0, 45, 0))
    m.box("root", (0, 0.8, 0), (2.2, 0.2, 2.2), "#2c3a72", r=(0, 22.5, 0))
    for k in range(8):  # remates dorados en las esquinas del octógono
        a = k / 8 * TAU + TAU / 16
        m.box("root", (math.cos(a) * 2.32, 0.42, math.sin(a) * 2.32), (0.3, 0.12, 0.3), GOLD, r=(0, -math.degrees(a), 0), metal=1)
    ring(m, "root", 1.75, 32, (0.08, 0.06), TEAL, center=(0, 0.72, 0), emit=5, tag="neon")
    ring(m, "root", 2.35, 40, (0.06, 0.05), TEAL, center=(0, 0.42, 0), emit=3, tag="neon")
    # haz de luz bajo el huevo
    for i in range(5):
        m.box("root", (0, 0.92 + i * 0.02, 0), (1.6 - i * 0.25, 0.04, 1.6 - i * 0.25), CORE, r=(0, 45 * i, 0), emit=2 + i, tag="core")

    # anillos de energía en el suelo (giran)
    m.part("floor_rings", "root", (0, 0.05, 0))
    ring(m, "floor_rings", 3.2, 64, (0.1, 0.04), TEAL, emit=4, tag="neon")
    ring(m, "floor_rings", 3.7, 72, (0.05, 0.04), TEAL, emit=3, tag="neon")
    for k in range(6):
        a = k / 6 * TAU
        m.box("floor_rings", (math.cos(a) * 3.45, 0, math.sin(a) * 3.45), (0.16, 0.05, 0.16), STAR, r=(0, 45, 0), emit=6, tag="twinkle")

    # ---------------- huevo ----------------
    m.part("egg", "root", (0, CY, 0))
    m.part("shell", "egg")
    blues = ["#2f63f5", "#3b74ff", "#4985ff", "#2a56e6", "#5a97ff"]
    for p, n in egg_voxels(R, HB, HT, V):
        h = _hash(p.x, p.y, p.z)
        t = (p.y + HB) / (HB + HT)
        if h > 0.975:
            col, emit, tag = "#f2fbff", 2.0, "twinkle"
        elif h > 0.9:
            col, emit, tag = "#9fd2ff", 0.0, None
        else:
            col = blues[int(h * 97) % len(blues)]
            if t < 0.22 and h > 0.5:
                col = "#5a4ef0"  # base violeta
            elif t > 0.8 and h > 0.55:
                col = "#79b8ff"  # brillo superior
            emit, tag = 0.0, None
        m.box("shell", p, (V, V, V), col, emit=emit, tag=tag)

    # jaula dorada de rombos (hélices cruzadas)
    m.part("cage", "egg")
    OFF = 0.13
    y0, y1 = -HB + 0.35, HT - 0.45
    for sgn in (1, -1):
        for k in range(8):
            pts = []
            for i in range(29):
                u = i / 28
                y = y0 + (y1 - y0) * u
                a = k / 8 * TAU + sgn * u * TAU / 4
                pts.append(egg_surface(R, HB, HT, y, a, OFF))
            polyline(m, "cage", pts, 0.13, GOLD, metal=1)
    for y, th in ((0.15, 0.24), (y1, 0.2), (y0, 0.2)):
        r_ = egg_radius(y, R, HB, HT) + OFF + 0.04
        ring(m, "cage", r_, 48, (th, 0.12), GOLD_DARK if th < 0.22 else GOLD, center=(0, y, 0), metal=1)
    # tachuelas en los cruces del ecuador
    for k in range(16):
        a = k / 16 * TAU
        p = egg_surface(R, HB, HT, 0.15, a, OFF + 0.14)
        m.box("cage", p, (0.18, 0.18, 0.18), GOLD_LIGHT, r=(0, math.degrees(a) + 45, 45), metal=1)
    # corona superior
    for i, (rr, yy) in enumerate(((0.75, HT - 0.3), (0.55, HT - 0.12), (0.35, HT + 0.02))):
        ring(m, "cage", rr, 16, (0.16, 0.14), GOLD if i % 2 == 0 else GOLD_DARK, center=(0, yy, 0), metal=1)
    m.box("cage", (0, HT + 0.12, 0), (0.3, 0.3, 0.3), GOLD_LIGHT, r=(0, 45, 0), metal=1)

    # emblema frontal: rombo dorado + cristal brillante
    m.part("emblem", "egg", (0, 0.35, egg_radius(0.35, R, HB, HT) + 0.12))
    W, H = 1.25, 1.85
    polyline(m, "emblem", [(0, H / 2, 0), (W / 2, 0, 0), (0, -H / 2, 0), (-W / 2, 0, 0)], (0.2, 0.2), GOLD, closed=True, metal=1)
    polyline(m, "emblem", [(0, H / 2 + 0.25, -0.05), (W / 2 + 0.2, 0, -0.05), (0, -H / 2 - 0.25, -0.05), (-W / 2 - 0.2, 0, -0.05)],
             (0.08, 0.08), GOLD_DARK, closed=True, metal=1)
    for j in range(9):
        k = (j + 0.5) / 9 * 2 - 1
        w = (W - 0.3) * (1 - abs(k))
        m.box("emblem", (0, k * (H - 0.3) / 2, 0.02), (w + 0.04, (H - 0.3) / 9 + 0.01, 0.12), CORE, emit=2.5, tag="core")
    m.box("emblem", (0, 0.1, 0.1), (0.18, 0.5, 0.06), "#ffffff", emit=4, tag="core")
    m.box("emblem", (0, 0.1, 0.1), (0.36, 0.08, 0.06), "#ffffff", emit=4, tag="core")

    # gema superior y halo
    m.part("topgem", "egg", (0, HT + 1.0, 0))
    crystal(m, "topgem", (0, 0, 0), 0.95, 1.7, CORE, emit=1.6, tag="core")
    crystal(m, "topgem", (0, 0, 0), 0.5, 1.3, "#ffffff", emit=2.5, tag="core")
    m.part("halo", "egg", (0, HT + 2.15, 0), (8, 0, 0))
    ring(m, "halo", 1.15, 36, (0.26, 0.2), GOLD, metal=1)
    ring(m, "halo", 1.15, 36, (0.1, 0.24), GOLD_LIGHT, emit=1.5, tag="halo")

    # alas
    rows = [
        (13, 1.9, 3.7, 0.72, -0.16, FEATHER),
        (11, 1.2, 2.3, 0.7, -0.02, FEATHER2),
        (8, 0.7, 1.3, 0.66, 0.12, ["#ffffff", "#ffffff", "#e9f8ff"]),
    ]
    bone = [(0, 0), (0.9, 0.7), (1.8, 1.7), (2.5, 2.7)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.55, 0.7, -0.9), (0, sx * -22, sx * 8))
        _wing(m, w, sx, rows, bone, GOLD, GOLD)
        # cuchillas doradas en la base del ala (como en la referencia)
        for i, (bx, by, h_, a_) in enumerate(((0.35, 0.25, 1.4, -35), (0.8, 0.8, 1.0, -55))):
            crystal(m, w, (sx * bx, by, 0.25), 0.42, h_, GOLD, rot=(0, 0, sx * a_), metal=1)
        m.box(w, (0, 0, 0), (0.5, 0.5, 0.5), GOLD_DARK, r=(0, 0, 45), metal=1)

    # anillos de neón orbitando
    m.part("orbit1", "egg", (0, 0.2, 0), (72, 0, 18))
    ring(m, "orbit1", 3.25, 72, (0.08, 0.08), TEAL, emit=5, tag="neon")
    for i in range(4):
        m.box("orbit1", (3.25, 0, -0.18 * i), (0.3 - i * 0.06, 0.3 - i * 0.06, 0.25), "#e0fff6", emit=7 - i, tag="neon")
    m.part("orbit2", "egg", (0, 0.4, 0), (-62, 0, -28))
    ring(m, "orbit2", 2.95, 64, (0.07, 0.07), PINK, emit=5, tag="neon")
    for i in range(4):
        m.box("orbit2", (-2.95, 0, 0.18 * i), (0.28 - i * 0.06, 0.28 - i * 0.06, 0.25), "#ffe6fa", emit=7 - i, tag="neon")

    # estrellas que titilan
    stars = [(-3.0, 7.6, 0.6, 0.6), (3.2, 8.2, -0.4, 0.5), (-3.6, 3.4, 1.2, 0.45), (3.7, 2.8, 1.0, 0.55),
             (2.2, 9.6, 0.8, 0.35), (-2.0, 1.6, 2.4, 0.4), (0.6, 10.2, -1.2, 0.3)]
    for i, (x, y, z, s) in enumerate(stars):
        n = f"star{i}"
        m.part(n, "root", (x, y, z))
        star(m, n, (0, 0, 0), s, STAR, emit=6, tag="twinkle")

    # ---------------- animación ----------------
    def animate(t):
        a = t * TAU
        pose = {}
        pose["egg"] = {"p": (0, 0.18 * math.sin(a * 2), 0), "r": quat((2.5 * math.sin(a * 2 + 0.6), 0, 2 * math.sin(a)))}
        pose["topgem"] = {"p": (0, 0.12 * math.sin(a * 4), 0), "r": quat((0, math.degrees(a * 2), 0))}
        pose["halo"] = {"p": (0, 0.15 * math.sin(a * 2 + 1.2), 0), "r": quat((5 * math.sin(a * 2), math.degrees(a), 0))}
        flap = math.sin(a * 4)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 14 * flap))}
        pose["orbit1"] = {"r": quat((0, -math.degrees(a * 2), 0))}
        pose["orbit2"] = {"r": quat((0, math.degrees(a * 2), 0))}
        pose["floor_rings"] = {"r": quat((0, math.degrees(a), 0))}
        pose["emblem"] = {"s": (1 + 0.04 * math.sin(a * 4),) * 3}
        for i in range(7):
            tw = 0.55 + 0.45 * abs(math.sin(a * 2 + i * 1.7))
            pose[f"star{i}"] = {"s": (tw, tw, tw), "r": quat((0, 0, math.degrees(a) * (1 if i % 2 else -1)))}
        return pose

    def glow(t):
        a = t * TAU
        return {"core": 0.75 + 0.25 * math.sin(a * 4), "neon": 0.8 + 0.2 * math.sin(a * 8),
                "twinkle": 0.5 + 0.5 * math.sin(a * 6) ** 2, "halo": 0.8 + 0.2 * math.sin(a * 2)}

    m.animate, m.glow = animate, glow
    return m


# ======================================================================================
#  HUEVO DE HIELO
# ======================================================================================

ICE = "#8ff3ff"
ICE_L = "#d9fcff"
ICE_D = "#47c6f0"
VEIN = "#5ff4ff"
LAV = "#c8a8ff"
WATER = "#2fb8f0"
RIM = "#a9cfe6"
SCALES = ["#1b3170", "#223e88", "#2a4ea3"]
SCALE_EDGE = "#121f4d"


def build_ice():
    m = Model("egg_ice", fps=24, frames=96)
    m.part("root")
    R, HB, HT, V = 2.05, 2.2, 2.8, 0.2
    CY = 4.3

    # ---------------- estanque ----------------
    for k in range(30):  # borde de piedra clara
        a = k / 30 * TAU
        m.box("root", (math.cos(a) * 3.55, 0.25, math.sin(a) * 3.55), (0.85, 0.5, 0.6), RIM if k % 2 else "#8fbcd8",
              r=(0, -math.degrees(a), 0))
    m.box("root", (0, 0.08, 0), (6.6, 0.16, 6.6), "#0f4f86", r=(0, 0, 0))
    for ix in range(-8, 9):  # agua de vóxeles
        for iz in range(-8, 9):
            x, z = ix * 0.4, iz * 0.4
            if x * x + z * z < 3.2 ** 2:
                h = _hash(x, z)
                m.box("root", (x, 0.2, z), (0.4, 0.1, 0.4), WATER if h > 0.3 else "#3dc9f7", emit=0.6, tag="water")
    for i in range(3):
        n = f"ripple{i}"
        m.part(n, "root", (0, 0.28, 0))
        ring(m, n, 1.0, 40, (0.09, 0.04), ICE_L, emit=4, tag="ripple")
    m.box("root", (0, 0.35, 0), (1.6, 0.2, 1.6), ICE_L, r=(0, 45, 0), emit=1.5, tag="water")

    # ---------------- huevo ----------------
    m.part("egg", "root", (0, CY, 0))
    m.part("shell", "egg")
    for p, n in egg_voxels(R, HB, HT, V):
        ang = math.atan2(p.x, p.z)  # 0 = frente
        row = math.floor((p.y + HB) / 0.5)
        col = math.floor((ang / TAU + 0.5) * 18 + (row % 2) * 0.5)
        fy = ((p.y + HB) / 0.5) % 1
        # vetas: meridianos brillantes y un rombo en el frente
        a6 = (ang / TAU * 6) % 1
        diamond = abs(ang) / 0.62 + abs(p.y - 0.3) / 1.45
        if 0.86 < diamond < 1.0 and p.z > 0:
            m.box("shell", p, (V, V, V), VEIN, emit=4, tag="vein")
            continue
        if diamond <= 0.86 and p.z > 0:
            continue  # hueco para el cristal frontal
        colr = SCALE_EDGE if fy < 0.22 else SCALES[(row + col) % 3]
        if fy > 0.7 and _hash(p.x, p.y, p.z) > 0.6:
            colr = "#3b64c4"
        m.box("shell", p, (V, V, V), colr)

    # cristal frontal facetado
    zf = egg_radius(0.3, R, HB, HT) - 0.15
    m.part("emblem", "egg", (0, 0.3, zf))
    for j in range(11):
        k = (j + 0.5) / 11 * 2 - 1
        w = 2 * 0.62 * zf * (1 - abs(k)) * 0.95
        for d_ in range(3):
            m.box("emblem", (0, k * 1.4, 0.05 + d_ * 0.12), (max(w - d_ * 0.35, 0.05), 0.27, 0.14),
                  [ICE_D, ICE, ICE_L][d_], emit=0.5 + d_ * 0.6, tag="core")
    star(m, "emblem", (0.25, 0.45, 0.45), 0.5, "#ffffff", emit=6, tag="core")

    # anillo ecuatorial
    ring(m, "egg", egg_radius(-0.6, R, HB, HT) + 0.1, 48, (0.14, 0.14), VEIN, center=(0, -0.6, 0), emit=3, tag="vein")

    # corona de cristales
    m.part("crown", "egg", (0, HT - 0.35, 0))
    def spike(c, h, w, rot):
        rq = quat(rot)
        c = Vector(c)
        n = 8
        for j in range(n):
            k = j / n
            ww = w * (1 - k ** 1.6) + 0.05
            y = (j + 0.5) * h / n
            col = ICE_D if j < 2 else (ICE if j < 6 else ICE_L)
            m.box("crown", c + rq @ Vector((0, y, 0)), (ww, h / n + 0.02, ww), col, r=rq @ quat((0, 45, 0)), emit=0.8 + k * 2, tag="core")
    spike((0, 0, 0), 2.4, 0.7, (0, 0, 0))
    for k in range(6):
        a = k / 6 * TAU + 0.3
        spike((math.sin(a) * 0.65, -0.15, math.cos(a) * 0.65), 1.3 + 0.3 * (k % 2), 0.45,
              (math.degrees(math.cos(a)) * 0.45, 0, -math.degrees(math.sin(a)) * 0.45))

    # alas de esquirlas
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.7, 0.6, -0.6), (0, sx * -20, 0))
        for layer, (n, lmin, lmax, wd, z, cols) in enumerate(((11, 1.6, 3.4, 0.62, -0.15, (ICE, ICE_L)),
                                                             (8, 0.9, 1.9, 0.58, 0.1, (ICE_L, "#ffffff")))):
            for i in range(n):
                k = i / (n - 1)
                theta = math.radians(-30 + k * 120)
                L = lmin + (lmax - lmin) * math.sin(k * math.pi * 0.85 + 0.25)
                d = Vector((sx * math.cos(theta), math.sin(theta), 0))
                c = d * (0.3 + L / 2) + Vector((0, 0, z))
                rot = (0, 0, math.degrees(theta) - 90 if sx > 0 else 90 - math.degrees(theta))
                crystal(m, w, c, wd, L, cols[i % 2], rot=rot, emit=0.5 + 0.3 * layer, tag="core")
        crystal(m, w, (0, 0, 0.1), 0.7, 0.9, ICE_D, emit=1.2, tag="core")

    # espirales de energía
    m.part("spiral", "egg")
    for off, colr in ((0, VEIN), (math.pi, LAV)):
        pts = []
        for i in range(90):
            u = i / 89
            a = off + u * TAU * 2.2
            y = -2.6 + u * 5.6
            r_ = 2.75 + 0.25 * math.sin(u * math.pi)
            pts.append((math.sin(a) * r_, y, math.cos(a) * r_))
        polyline(m, "spiral", pts, 0.08, colr, emit=5, tag="neon")
    m.part("halo_ring", "egg", (0, 2.0, 0), (10, 0, 0))
    ring(m, "halo_ring", 2.3, 56, (0.06, 0.06), LAV, emit=4, tag="neon")

    # esquirlas orbitando
    for i in range(8):
        n = f"shard{i}"
        a = i / 8 * TAU
        m.part(n, "root", (math.cos(a) * 4.4, CY + 1.2 * math.sin(a * 2), math.sin(a) * 4.4), (20 * i, 30 * i, 15))
        crystal(m, n, (0, 0, 0), 0.35, 0.8 + 0.2 * (i % 3), ICE if i % 2 else ICE_L, emit=1.5, tag="core")

    # ---------------- animación ----------------
    def animate(t):
        a = t * TAU
        pose = {}
        pose["egg"] = {"p": (0, 0.2 * math.sin(a * 2), 0), "r": quat((0, 6 * math.sin(a), 2 * math.sin(a * 2)))}
        pose["crown"] = {"s": (1, 1 + 0.03 * math.sin(a * 4), 1)}
        flap = math.sin(a * 4)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 8 * flap, sx * 10 * flap))}
        pose["spiral"] = {"r": quat((0, math.degrees(a * 2), 0))}
        pose["halo_ring"] = {"r": quat((6 * math.sin(a * 2), -math.degrees(a * 2), 0))}
        for i in range(3):
            ph = (t * 2 + i / 3) % 1
            sc = 0.6 + 2.8 * ph
            pose[f"ripple{i}"] = {"s": (sc, 1, sc)}
        for i in range(8):
            base = i / 8 * TAU
            ang = base + a
            m_part = m.parts[f"shard{i}"]
            target = Vector((math.cos(ang) * 4.4, CY + 1.2 * math.sin(base * 2) + 0.4 * math.sin(a * 2 + i), math.sin(ang) * 4.4))
            pose[f"shard{i}"] = {"p": tuple(target - m_part.pivot), "r": quat((0, math.degrees(a * 2), math.degrees(a)))}
        return pose

    def glow(t):
        a = t * TAU
        return {"core": 0.75 + 0.25 * math.sin(a * 4), "neon": 0.8 + 0.2 * math.sin(a * 8),
                "vein": 0.6 + 0.4 * math.sin(a * 2) ** 2, "water": 0.85 + 0.15 * math.sin(a * 4),
                "ripple": 1.0 - (t * 2) % 1}

    m.animate, m.glow = animate, glow
    return m
