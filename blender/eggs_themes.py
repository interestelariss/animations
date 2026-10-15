"""Cinco huevos temáticos más, con el mismo lenguaje que los huevos base:
cáscara de vóxeles con patrón, emblema frontal, corona, alas, anillos/órbitas,
base escénica, VFX por etiquetas de brillo y animación en bucle.

Infierno · Pantano · Galaxia · Tormenta · Sakura
"""

import math

from mathutils import Quaternion, Vector

from eggs import _hash, _wing
from voxel import (Model, crystal, egg_radius, egg_surface, egg_voxels, polyline, quat, ring,
                   segment, star)

TAU = math.tau


# ------------------------------------------------------------------------- ruido
def _lattice(ix, iy, iz):
    h = (ix * 374761393 + iy * 668265263 + iz * 2147483647) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return (h & 0xFFFF) / 65535


def vnoise(x, y, z):
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - ix, y - iy, z - iz
    s = lambda t: t * t * (3 - 2 * t)
    ux, uy, uz = s(fx), s(fy), s(fz)
    v = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (ux if dx else 1 - ux) * (uy if dy else 1 - uy) * (uz if dz else 1 - uz)
                v += w * _lattice(ix + dx, iy + dy, iz + dz)
    return v


def fbm(p, scale=1.0, seed=0.0):
    x, y, z = p.x * scale + seed, p.y * scale + seed * 0.7, p.z * scale - seed * 1.3
    return 0.65 * vnoise(x, y, z) + 0.35 * vnoise(x * 2.1, y * 2.1, z * 2.1)


# ------------------------------------------------------------------------- piezas
def egg_scene(name, R, HB, HT, V, CY, shell_fn, frames=96):
    m = Model(name, fps=24, frames=frames)
    m.part("root")
    m.part("egg", "root", (0, CY, 0))
    m.part("shell", "egg")
    for p, n in egg_voxels(R, HB, HT, V):
        t = (p.y + HB) / (HB + HT)
        res = shell_fn(p, n, t, math.atan2(p.x, p.z))
        if res:
            col, emit, tag = (res + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
            m.box("shell", p, (V, V, V), col, emit=emit, tag=tag)
    return m


def horn(m, part, base, out_dir, length, w0, curl, col, tip_col, steps=10, tip_emit=0, tag=None):
    pos = Vector(base)
    d = Vector(out_dir).normalized()
    axis = d.cross(Vector((0, 1, 0))).normalized()
    rq = Quaternion(axis, math.radians(curl))
    step = length / steps
    for i in range(steps):
        k = i / steps
        w = w0 * (1 - k * 0.85)
        nxt = pos + d * step
        tip = k >= 0.7
        segment(m, part, pos, nxt, (w, w), tip_col if tip else col, emit=tip_emit if tip else 0, tag=tag if tip else None)
        # anillos del cuerno
        if i % 2 == 0 and not tip:
            segment(m, part, pos + d * step * 0.4, pos + d * step * 0.55, (w * 1.12, w * 1.12), tip_col if False else "#24140f")
        pos = nxt
        d = rq @ d


def flame(m, part, c, h, w, seed=0, tag="fire"):
    cols = ["#ff2a00", "#ff4d00", "#ff7a00", "#ffa200", "#ffcc33", "#fff1a0"]
    c = Vector(c)
    n = 6
    for j in range(n):
        k = j / n
        ww = w * (1 - k) ** 0.75 + 0.06
        off = Vector((math.sin(seed + j * 1.3) * 0.08 * j, (j + 0.5) * h / n, math.cos(seed + j) * 0.05 * j))
        m.box(part, c + off, (ww, h / n + 0.04, ww), cols[j], r=(0, 45 * (j % 2) + seed * 10, 0), emit=2.5 + j * 0.6, tag=tag)


def leaf(m, part, base, ang, length, width, col, vein, sx=1, z=0.0, steps=8):
    """Hoja plana en el plano XY; ang en grados desde +X (espejo con sx)."""
    a = math.radians(ang)
    d = Vector((sx * math.cos(a), math.sin(a), 0))
    rot = (0, 0, ang - 90 if sx > 0 else 90 - ang)
    b = Vector(base) + Vector((0, 0, z))
    step = length / steps
    for i in range(steps):
        k = (i + 0.5) / steps
        w = width * math.sin(math.pi * min(0.98, k * 0.95 + 0.05)) + 0.05
        m.box(part, b + d * step * (i + 0.5), (w, step + 0.03, 0.1), col if i < steps - 1 else vein, r=rot)
    m.box(part, b + d * length * 0.5, (0.07, length * 0.95, 0.13), vein, r=rot)


def flower(m, part, c, size, petal, center, rot=(0, 0, 0), emit=0, tag=None, petal2=None):
    rq = quat(rot) if not isinstance(rot, Quaternion) else rot
    c = Vector(c)
    for k in range(5):
        a = k / 5 * TAU
        off = rq @ Vector((math.cos(a) * size * 0.36, math.sin(a) * size * 0.36, 0))
        m.box(part, c + off, (size * 0.42, size * 0.5, size * 0.08), petal if k % 2 == 0 or not petal2 else petal2,
              r=rq @ quat((0, 0, math.degrees(a) - 90)), emit=emit, tag=tag)
    m.box(part, c + rq @ Vector((0, 0, size * 0.06)), (size * 0.26, size * 0.26, size * 0.1), center, r=rq @ quat((0, 0, 45)),
          emit=emit * 1.5, tag=tag)


def mushroom(m, part, c, h, r, cap, spot, stem="#e8e0c8", emit=0, tag=None):
    c = Vector(c)
    m.box(part, c + Vector((0, h / 2, 0)), (r * 0.45, h, r * 0.45), stem)
    m.box(part, c + Vector((0, h, 0)), (r * 2.0, r * 0.4, r * 2.0), cap, emit=emit, tag=tag)
    m.box(part, c + Vector((0, h + r * 0.32, 0)), (r * 1.55, r * 0.35, r * 1.55), cap, emit=emit, tag=tag)
    m.box(part, c + Vector((0, h + r * 0.58, 0)), (r * 0.9, r * 0.25, r * 0.9), cap, emit=emit, tag=tag)
    for k in range(4):
        a = k / 4 * TAU + 0.4
        m.box(part, c + Vector((math.cos(a) * r * 0.62, h + r * 0.5, math.sin(a) * r * 0.62)), (r * 0.25, r * 0.12, r * 0.25), spot,
              emit=emit * 1.4, tag=tag)


def cloud(m, part, c, s, col, col2):
    c = Vector(c)
    for (dx, dy, dz, w, h, d, cc) in ((0, 0, 0, 1.7, 0.9, 1.2, col), (-0.9, -0.1, 0.1, 1.1, 0.7, 1.0, col2),
                                      (0.95, -0.12, -0.1, 1.2, 0.65, 0.95, col2), (0.2, 0.55, 0, 1.0, 0.7, 0.9, col),
                                      (-0.4, 0.4, 0.2, 0.8, 0.5, 0.7, col2)):
        m.box(part, c + Vector((dx, dy, dz)) * s, (w * s, h * s, d * s), cc)


def bolt(m, part, a, b, n, col, seed, thick=0.12, emit=5, tag=None, branch=True):
    a, b = Vector(a), Vector(b)
    d = b - a
    perp = d.cross(Vector((0.3, 0.1, 1))).normalized()
    perp2 = d.cross(perp).normalized()
    pts = [a]
    for i in range(1, n):
        k = i / n
        j = (_hash(seed, i) - 0.5) * 0.9
        j2 = (_hash(i, seed) - 0.5) * 0.5
        pts.append(a + d * k + perp * j + perp2 * j2)
    pts.append(b)
    polyline(m, part, pts, thick, col, emit=emit, tag=tag)
    if branch and n > 3:
        p0 = pts[n // 2]
        polyline(m, part, [p0, p0 + (d * 0.25 + perp * 0.6), p0 + (d * 0.4 + perp * 0.7)], thick * 0.7, col, emit=emit, tag=tag)


def voxel_ball(m, part, c, r, v, colfn):
    c = Vector(c)
    n = int(r / v) + 1
    for ix in range(-n, n + 1):
        for iy in range(-n, n + 1):
            for iz in range(-n, n + 1):
                p = Vector((ix, iy, iz)) * v
                if p.length > r or p.length < r - v * 1.5:
                    continue
                res = colfn(p)
                if res:
                    col, emit, tag = (res + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
                    m.box(part, c + p, (v, v, v), col, emit=emit, tag=tag)


def membrane_wing(m, part, sx, joint, tips, bone, membrane, membrane2, step=0.16):
    """Ala de murciélago: dedos óseos + membrana rellena con barras."""
    J = Vector((sx * joint[0], joint[1], 0))
    root = Vector((0, 0, 0))
    segment(m, part, root, J, 0.32, bone)
    T = [Vector((sx * x, y, 0)) for x, y in tips]
    for t_ in T:
        segment(m, part, J, t_, 0.16, bone)
        m.box(part, t_, (0.22, 0.22, 0.22), bone, r=(0, 0, 45))
    tris = [(root, J, T[0])] + [(J, T[i], T[i + 1]) for i in range(len(T) - 1)] + [(root, J, T[-1])]
    for ti, (A, B, C) in enumerate(tris):
        L = max((B - A).length, (C - A).length)
        n = max(3, int(L / step))
        for i in range(1, n):
            u = i / n * 0.94
            P, Q = A.lerp(B, u), A.lerp(C, u)
            # borde festoneado: la membrana se mete hacia dentro en el centro
            mid = (P + Q) / 2
            sag = (A - mid).normalized() * 0.25 * u * u if ti > 0 else Vector()
            segment(m, part, P, mid + sag, (step + 0.03, 0.06), membrane if ti % 2 else membrane2)
            segment(m, part, mid + sag, Q, (step + 0.03, 0.06), membrane if ti % 2 else membrane2)


def base_anim(t, egg_amp=0.18):
    a = t * TAU
    return {"egg": {"p": (0, egg_amp * math.sin(a * 2), 0), "r": quat((2 * math.sin(a * 2 + 0.6), 5 * math.sin(a), 2 * math.sin(a)))}}


# ======================================================================================
#  1. INFIERNO
# ======================================================================================
def build_inferno():
    R, HB, HT, V, CY = 2.0, 2.2, 2.85, 0.2, 4.6
    obs = ["#1b0e10", "#25110f", "#2f1612", "#140a0b", "#3a1a14"]

    def shell(p, n, t, ang):
        f = fbm(p, 1.15, 3.0)
        rid = abs(f - 0.5)
        if rid < 0.028:
            return ("#ff6a14", 3.0, "lava")
        if rid < 0.055:
            return ("#c2300c", 1.2, "lava")
        if t < 0.18 and _hash(p.x, p.y, p.z) > 0.55:
            return ("#ff4a10", 1.5, "lava")
        return obs[int(_hash(p.x, p.y, p.z) * 97) % len(obs)]

    m = egg_scene("egg_inferno", R, HB, HT, V, CY, shell)

    # base de obsidiana con lava
    for i, (w, h, y, rot) in enumerate(((5.0, 0.5, 0.25, 0), (4.0, 0.4, 0.7, 22), (3.0, 0.3, 1.05, 45))):
        m.box("root", (0, y, 0), (w, h, w), ["#120808", "#1c0c0b", "#261210"][i], r=(0, rot, 0))
    for k in range(40):  # lava alrededor
        a = k / 40 * TAU
        r_ = 3.2 + 0.25 * math.sin(k * 1.7)
        m.box("root", (math.cos(a) * r_, 0.06, math.sin(a) * r_), (0.7, 0.12, 0.7), "#ff5a10" if k % 3 else "#ffa12a",
              r=(0, -math.degrees(a), 0), emit=2.5, tag="lava")
    for k in range(9):  # rocas puntiagudas
        a = k / 9 * TAU + 0.2
        r_ = 4.0 + 0.4 * _hash(k, 2)
        h = 0.9 + 1.4 * _hash(k, 5)
        m.box("root", (math.cos(a) * r_, h / 2 - 0.1, math.sin(a) * r_), (0.6, h, 0.6), "#1d0f0e",
              r=(15 * math.sin(k), math.degrees(a), 12 * math.cos(k * 2)))
        m.box("root", (math.cos(a) * r_, h - 0.05, math.sin(a) * r_), (0.3, 0.4, 0.3), "#ff6a14", r=(0, 45, 0), emit=2, tag="lava")
    ring(m, "root", 1.6, 28, (0.1, 0.06), "#ff7a1a", center=(0, 1.22, 0), emit=3, tag="lava")

    # banda de hierro con pinchos
    yb = 0.0
    rb = egg_radius(yb, R, HB, HT) + 0.12
    ring(m, "egg", rb, 44, (0.3, 0.18), "#3a3c42", center=(0, yb, 0), metal=1)
    for k in range(12):
        a = k / 12 * TAU
        p = Vector((math.sin(a) * (rb + 0.15), yb, math.cos(a) * (rb + 0.15)))
        m.box("egg", p, (0.26, 0.26, 0.26), "#55585f", r=(0, math.degrees(a), 45), metal=1)

    # ojo demoníaco
    zf = egg_radius(0.6, R, HB, HT) + 0.05
    m.part("eye", "egg", (0, 0.6, zf))
    polyline(m, "eye", [(0, 0.75, 0), (0.6, 0, 0), (0, -0.75, 0), (-0.6, 0, 0)], (0.16, 0.16), "#2a2c31", closed=True, metal=1)
    for j in range(9):
        k = (j + 0.5) / 9 * 2 - 1
        w = 1.0 * (1 - abs(k))
        m.box("eye", (0, k * 0.65, 0.02), (w + 0.04, 0.16, 0.1), "#ffb020" if abs(k) < 0.6 else "#ff5a10", emit=3, tag="eyeglow")
    m.box("eye", (0, 0, 0.09), (0.12, 1.0, 0.06), "#120404")

    # cuernos
    for sx in (1, -1):
        horn(m, "egg", (sx * 1.15, 1.75, 0.1), (sx * 1, 0.45, 0.1), 3.3, 0.62, 15, "#3b2620", "#ff7a2a", tip_emit=2.5, tag="lava")

    # corona de llamas
    for i in range(5):
        a = i / 5 * TAU
        n = f"flame{i}"
        r_ = 0.0 if i == 0 else 0.55
        m.part(n, "egg", (math.sin(a) * r_ if i else 0, HT - 0.25, math.cos(a) * r_ if i else 0))
        flame(m, n, (0, 0, 0), 1.7 if i == 0 else 1.1, 0.7 if i == 0 else 0.45, seed=i)
    for k in range(8):
        a = k / 8 * TAU
        p = egg_surface(R, HB, HT, HT - 0.55, a, 0.05)
        m.box("egg", p + Vector((0, 0.25, 0)), (0.2, 0.6, 0.2), "#1d0f0e", r=(math.cos(a) * 20, 0, -math.sin(a) * 20))

    # alas de murciélago
    tips = [(1.2, 2.6), (2.7, 2.5), (3.7, 1.3), (3.6, -0.3), (2.5, -1.2)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.55, 0.6, -0.8), (0, sx * -25, sx * 5))
        membrane_wing(m, w, sx, (1.3, 1.5), tips, "#2b1612", "#5c0f14", "#4a0c10")
        for t_ in tips[:3]:
            m.box(w, (sx * t_[0], t_[1] + 0.2, 0), (0.12, 0.35, 0.12), "#ff7a2a", emit=2, tag="lava")

    # anillo de brasas orbitando
    m.part("orbit", "egg", (0, 0.3, 0), (70, 0, 12))
    ring(m, "orbit", 3.2, 60, (0.08, 0.08), "#ff6a14", emit=4, tag="lava")
    for i in range(6):
        n = f"rune{i}"
        a = i / 6 * TAU
        m.part(n, "orbit", (math.cos(a) * 3.2, 0, math.sin(a) * 3.2))
        star(m, n, (0, 0, 0), 0.45, "#ffb020", emit=4, tag="eyeglow")

    def animate(t):
        a = t * TAU
        pose = base_anim(t)
        for i in range(5):
            f = 1 + 0.12 * math.sin(a * 8 + i * 2.1) + 0.06 * math.sin(a * 13 + i)
            pose[f"flame{i}"] = {"s": (1 / f ** 0.5, f, 1 / f ** 0.5), "r": quat((0, 20 * math.sin(a * 2 + i), 0))}
        flap = math.sin(a * 2)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 14 * flap, sx * 10 * flap))}
        blink = max(0.0, 1 - abs(t - 0.6) / 0.04)
        pose["eye"] = {"s": (1, 1 - 0.9 * blink, 1)}
        pose["orbit"] = {"r": quat((0, -math.degrees(a * 2), 0))}
        for i in range(6):
            pose[f"rune{i}"] = {"r": quat((0, math.degrees(a * 4), 0))}
        return pose

    def glow(t):
        a = t * TAU
        return {"lava": 0.7 + 0.3 * math.sin(a * 2) ** 2, "fire": 0.85 + 0.15 * math.sin(a * 16), "eyeglow": 0.8 + 0.2 * math.sin(a * 4)}

    m.animate, m.glow = animate, glow
    m.stage = {
        "bgTop": "#2a0906", "bgBottom": "#060102", "fog": [26, 70, "#0c0302"], "ground": "#120605", "dist": 1.85, "targetY": 4.6,
        "envTint": ["#ffb08a", "#200806"],
        "lights": {"sky": "#ffb48f", "groundCol": "#3a0c05", "hemi": 0.7, "key": 2.0, "keyColor": "#ffd7c2",
                   "points": [{"color": "#ff5a10", "intensity": 4, "pos": [0, 1.2, 3], "distance": 14},
                              {"color": "#ff2a00", "intensity": 3, "pos": [-5, 7, -4], "distance": 16}]},
        "bloom": {"strength": 0.5, "threshold": 1.2, "radius": 1.0, "exposure": 0.95}, "emitScale": 0.4,
        "groundGlow": "rgba(255,90,20,0.35)", "groundGlowSize": 12,
        "particles": [
            {"kind": "rise", "count": 220, "color": "#ff7a1a", "size": 0.16, "radius": [0.5, 6], "height": [0, 13], "speed": 0.9, "sprite": "square", "intensity": 3},
            {"kind": "float", "count": 100, "color": "#6a5a55", "size": 0.12, "radius": [5, 18], "height": [0.5, 14], "speed": 0.5, "sprite": "square", "intensity": 0.8},
        ],
        "burstPart": "shell", "shakePart": "egg", "burstColor": "#ff7a1a", "burstColor2": "#ffd04a",
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.22]},
    }
    return m


# ======================================================================================
#  2. PANTANO
# ======================================================================================
def build_swamp():
    R, HB, HT, V, CY = 2.05, 2.2, 2.75, 0.2, 4.3
    greens = ["#3d5a2a", "#4b6b30", "#5a7a35", "#33492a"]

    def shell(p, n, t, ang):
        h = _hash(p.x, p.y, p.z)
        if h > 0.975:
            return ("#c6ff5a", 2.5, "spores")
        if t < 0.2:
            return "#3a2e1e" if h > 0.4 else "#4a3a24"
        f = fbm(p, 1.0, 7.0)
        if f > 0.6:
            return "#8bbd40" if h > 0.5 else "#7aa838"
        if f < 0.33:
            return "#4a3a24" if h > 0.5 else "#56442b"
        return greens[int(h * 97) % len(greens)]

    m = egg_scene("egg_swamp", R, HB, HT, V, CY, shell)

    # lianas en espiral con hojitas
    for k in range(3):
        pts = []
        for i in range(36):
            u = i / 35
            y = -HB + 0.4 + u * (HB + HT - 0.9)
            a = k / 3 * TAU + u * TAU * 1.1
            pts.append(egg_surface(R, HB, HT, y, a, 0.1))
        polyline(m, "egg", pts, 0.15, "#2f5f24")
        for i in range(2, 34, 4):
            p = pts[i]
            nrm = Vector((p.x, 0, p.z)).normalized()
            m.box("egg", p + nrm * 0.15, (0.36, 0.14, 0.24), "#5fae3a", r=(0, math.degrees(math.atan2(p.x, p.z)), 30))

    # emblema: cristal tóxico con marco de raíces
    zf = egg_radius(0.3, R, HB, HT) + 0.1
    m.part("emblem", "egg", (0, 0.3, zf))
    polyline(m, "emblem", [(0, 0.95, 0), (0.62, 0.1, 0), (0.2, -0.8, 0), (-0.25, -0.85, 0), (-0.6, 0.05, 0)], (0.18, 0.18), "#5a3d22", closed=True)
    for j in range(8):
        k = (j + 0.5) / 8 * 2 - 1
        m.box("emblem", (0, k * 0.75, 0.04), (1.0 * (1 - abs(k)) + 0.05, 0.2, 0.12), "#a6ff3a", emit=2.5, tag="spores")

    # setas brillantes en la cima
    m.part("shrooms", "egg", (0, HT - 0.35, 0))
    mushroom(m, "shrooms", (0, 0, 0), 0.8, 0.55, "#4ff0c0", "#e6fff6", emit=1.6, tag="shroom")
    mushroom(m, "shrooms", (0.55, -0.15, 0.25), 0.5, 0.35, "#b06bff", "#f3e6ff", emit=1.4, tag="shroom")
    mushroom(m, "shrooms", (-0.5, -0.2, -0.2), 0.45, 0.32, "#4ff0c0", "#e6fff6", emit=1.6, tag="shroom")
    for k in range(10):
        a = k / 10 * TAU
        m.box("shrooms", (math.sin(a) * 0.7, -0.05, math.cos(a) * 0.7), (0.35, 0.2, 0.35), "#6f9a35", r=(0, math.degrees(a), 0))
    # setas pequeñas en los costados
    for k, (yy, aa) in enumerate(((-0.8, 1.9), (0.9, -2.1), (-1.3, -1.0))):
        p = egg_surface(R, HB, HT, yy, aa, 0.0)
        nrm = Vector((p.x, 0, p.z)).normalized()
        mushroom(m, "egg", p + nrm * 0.05, 0.25, 0.22, "#b06bff" if k % 2 else "#4ff0c0", "#ffffff", emit=1.4, tag="shroom")

    # alas de hojas
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.6, 0.5, -0.7), (0, sx * -22, 0))
        for i in range(7):
            k = i / 6
            ang = -25 + k * 105
            L = 1.8 + 1.5 * math.sin(k * math.pi * 0.85 + 0.25)
            leaf(m, w, (0, 0, 0), ang, L, 0.85, "#4f9a35" if i % 2 else "#5fae3a", "#2f6b22", sx=sx, z=-0.12 * (i % 2))
        for i in range(4):
            k = i / 3
            leaf(m, w, (0, 0, 0.12), -10 + k * 80, 1.2, 0.6, "#7fc24a", "#3f7d2a", sx=sx)
        m.box(w, (0, 0, 0), (0.5, 0.5, 0.5), "#3a2e1e", r=(0, 0, 45))

    # estanque turbio, nenúfares y juncos
    m.box("root", (0, 0.1, 0), (7.4, 0.2, 7.4), "#2a2216")
    for ix in range(-9, 10):
        for iz in range(-9, 10):
            x, z = ix * 0.4, iz * 0.4
            d = math.hypot(x, z)
            if d < 3.6:
                h = _hash(x, z, 3)
                m.box("root", (x, 0.24, z), (0.4, 0.08, 0.4), "#2f5a3a" if h > 0.35 else "#36664a", emit=0.25, tag="water")
            elif d < 4.2:
                m.box("root", (x, 0.3, z), (0.4, 0.3 + 0.3 * _hash(x, z), 0.4), "#3a2e1e" if _hash(z, x) > 0.4 else "#56702f")
    m.box("root", (0, 0.5, 0), (2.4, 0.5, 2.4), "#4a3a24", r=(0, 15, 0))  # tocón
    m.box("root", (0, 0.85, 0), (1.9, 0.3, 1.9), "#5e4a2e", r=(0, 15, 0))
    ring(m, "root", 0.7, 16, (0.08, 0.05), "#7a6040", center=(0, 1.01, 0))
    m.part("pads", "root", (0, 0, 0))
    for k, (x, z, s) in enumerate(((2.4, 1.2, 1.0), (-2.2, 1.8, 0.8), (1.0, -2.6, 0.9), (-2.6, -1.4, 1.1), (2.7, -1.0, 0.7))):
        m.box("pads", (x, 0.31, z), (0.9 * s, 0.06, 0.9 * s), "#4fa83a", r=(0, k * 37, 0))
        m.box("pads", (x, 0.32, z), (0.7 * s, 0.06, 0.7 * s), "#5fbe45", r=(0, k * 37 + 45, 0))
        if k % 2 == 0:
            flower(m, "pads", (x, 0.45, z), 0.45, "#ff9ad0", "#ffe14a", rot=(-90, 0, 0))
    for k in range(12):  # juncos con espadañas
        a = k / 12 * TAU + 0.3
        r_ = 3.6 + 0.3 * _hash(k, 9)
        h = 1.6 + 1.2 * _hash(k, 4)
        x, z = math.cos(a) * r_, math.sin(a) * r_
        m.box("root", (x, h / 2, z), (0.08, h, 0.08), "#4f7a2a", r=(6 * math.sin(k), 0, 6 * math.cos(k)))
        m.box("root", (x, h * 0.85, z), (0.18, 0.5, 0.18), "#6a4424")

    def animate(t):
        a = t * TAU
        pose = base_anim(t, 0.14)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((4 * math.sin(a * 2), sx * 8 * math.sin(a * 2), sx * 6 * math.sin(a * 2 + 1)))}
        sq = 1 + 0.05 * math.sin(a * 4)
        pose["shrooms"] = {"s": (sq, 2 - sq, sq)}
        pose["pads"] = {"p": (0, 0.03 * math.sin(a * 2), 0)}
        pose["emblem"] = {"s": (1 + 0.03 * math.sin(a * 4),) * 3}
        return pose

    def glow(t):
        a = t * TAU
        return {"spores": 0.6 + 0.4 * math.sin(a * 3) ** 2, "shroom": 0.75 + 0.25 * math.sin(a * 2), "water": 0.8 + 0.2 * math.sin(a * 4)}

    m.animate, m.glow = animate, glow
    m.stage = {
        "bgTop": "#13301f", "bgBottom": "#030a06", "fog": [18, 60, "#06130c"], "ground": "#0e1a0f", "dist": 1.85, "targetY": 4.2,
        "envTint": ["#cfeab0", "#0d1f10"],
        "lights": {"sky": "#cfe8b0", "groundCol": "#1a2a12", "hemi": 0.9, "key": 2.2, "keyColor": "#f2ffd8",
                   "points": [{"color": "#b6ff5a", "intensity": 3, "pos": [0, 2, 3], "distance": 12},
                              {"color": "#4ff0c0", "intensity": 3, "pos": [-4, 8, -2], "distance": 14}]},
        "bloom": {"strength": 0.5, "threshold": 1.2, "radius": 1.0, "exposure": 0.95}, "emitScale": 0.45,
        "groundGlow": "rgba(120,255,120,0.18)", "groundGlowSize": 10,
        "particles": [
            {"kind": "float", "count": 120, "color": "#d6ff5a", "size": 0.2, "radius": [2, 9], "height": [0.5, 9], "speed": 1.2, "intensity": 3, "twinkle": True},
            {"kind": "rise", "count": 70, "color": "#7fffb0", "size": 0.16, "radius": [0.3, 3.4], "height": [0.3, 6], "speed": 0.4, "sprite": "square", "intensity": 2},
        ],
        "burstPart": "shell", "shakePart": "egg", "burstColor": "#a6ff3a", "burstColor2": "#4ff0c0",
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.22]},
    }
    return m


# ======================================================================================
#  3. GALAXIA
# ======================================================================================
def build_galaxy():
    R, HB, HT, V, CY = 2.0, 2.2, 2.85, 0.2, 4.7
    space = ["#140a3a", "#1d0f52", "#24125f", "#100830"]

    def shell(p, n, t, ang):
        h = _hash(p.x, p.y, p.z)
        if h > 0.985:
            return ("#fff1c2", 4.0, "twinkle")
        if h > 0.955:
            return ("#ffffff", 2.5, "twinkle")
        f = fbm(p, 0.9, 11.0)
        g = fbm(p, 1.4, 2.0)
        if f > 0.64:
            return ("#d14ee8", 0.6, "nebula") if g > 0.5 else ("#9a2bd1", 0.4, "nebula")
        if f > 0.56:
            return "#5a24a8" if g > 0.5 else "#3a1a8a"
        if g > 0.68:
            return ("#2bc4e6", 0.6, "nebula")
        return space[int(h * 97) % len(space)]

    m = egg_scene("egg_galaxy", R, HB, HT, V, CY, shell)

    # galaxia espiral frontal (gira)
    zf = egg_radius(0.2, R, HB, HT) + 0.1
    m.part("emblem", "egg", (0, 0.2, zf))
    for arm in range(2):
        for i in range(26):
            u = i / 25
            a = arm * math.pi + u * TAU * 0.9
            r_ = 0.12 + u * 0.95
            col = "#ffffff" if u < 0.3 else ("#ffb8f0" if arm else "#9fe8ff")
            s = 0.2 - u * 0.1
            m.box("emblem", (math.cos(a) * r_, math.sin(a) * r_ * 0.8, 0.02), (s, s, 0.08), col, r=(0, 0, math.degrees(a)), emit=3 - u * 1.5, tag="core")
    m.box("emblem", (0, 0, 0.05), (0.32, 0.32, 0.12), "#fff6d8", r=(0, 0, 45), emit=5, tag="core")

    # anillos planetarios
    m.part("rings", "egg", (0, 0.1, 0), (18, 0, -14))
    for rr, col, em in ((2.9, "#f2c6ff", 0), (3.25, "#c99bff", 1.2), (3.6, "#8fd6ff", 0), (3.9, "#ffe1f6", 0.8)):
        ring(m, "rings", rr, int(rr * 22), (0.32, 0.06), col, emit=em, tag="ringglow" if em else None)

    # luna creciente en la cima
    m.part("moon", "egg", (0, HT + 1.1, 0), (0, 0, -25))

    def moon_col(p):
        if (p - Vector((0.35, 0.15, 0))).length < 0.6:
            return None
        return ("#ffe08a", 1.4, "core") if _hash(p.x, p.y, p.z) > 0.3 else ("#ffcf5a", 1.0, "core")

    voxel_ball(m, "moon", (0, 0, 0), 0.7, 0.13, moon_col)
    for k in range(3):
        a = k / 3 * TAU
        star(m, "moon", (math.cos(a) * 1.0, math.sin(a) * 0.6 + 0.3, 0.2), 0.35, "#ffffff", emit=4, tag="twinkle")

    # alas de constelación
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.6, 0.6, -0.8), (0, sx * -22, 0))
        pts = []
        for i in range(10):
            k = i / 9
            theta = math.radians(-30 + k * 120)
            L = 1.7 + 1.7 * math.sin(k * math.pi * 0.85 + 0.25)
            d = Vector((sx * math.cos(theta), math.sin(theta), 0))
            rot = (0, 0, math.degrees(theta) - 90 if sx > 0 else 90 - math.degrees(theta))
            crystal(m, w, d * (0.3 + L / 2), 0.55, L, ["#6a4cff", "#a77bff", "#5fbfff"][i % 3], rot=rot, emit=0.7, tag="nebula")
            tip = d * (0.4 + L)
            pts.append(tip)
            star(m, w, tip + Vector((0, 0, 0.1)), 0.32, "#ffffff", emit=4, tag="twinkle")
        polyline(m, w, pts, 0.04, "#cfd8ff", emit=2, tag="twinkle")  # línea de constelación

    # lunas orbitando
    moons = [(0.55, 4.6, "#ff8a4a", "#c9522a"), (0.45, 5.2, "#7fe0ff", "#3a8ac9"), (0.38, 3.9, "#9cff8a", "#3f9a5a")]
    for i, (r_, orb, c1, c2) in enumerate(moons):
        n = f"planet{i}"
        a = i / 3 * TAU
        m.part(n, "root", (math.cos(a) * orb, CY + (i - 1) * 1.2, math.sin(a) * orb))
        voxel_ball(m, n, (0, 0, 0), r_, 0.12, lambda p, c1=c1, c2=c2: c1 if math.sin(p.y * 9) > 0 else c2)

    # asteroide base
    for ix in range(-7, 8):
        for iz in range(-7, 8):
            x, z = ix * 0.4, iz * 0.4
            d = math.hypot(x, z)
            if d < 2.9:
                depth = int((2.9 - d) * 1.6 + 2 * _hash(x, z))
                for k in range(depth):
                    y = 1.6 - k * 0.4
                    m.box("root", (x, y, z), (0.42, 0.42, 0.42), ["#3a3352", "#2d2842", "#4a4266"][int(_hash(x, z, k) * 3)])
    for k in range(6):
        a = k / 6 * TAU
        crystal(m, "root", (math.cos(a) * 2.2, 2.0, math.sin(a) * 2.2), 0.35, 0.8, "#c08bff", rot=(20 * math.cos(a), 0, -20 * math.sin(a)), emit=1.5, tag="core")
    ring(m, "root", 1.4, 28, (0.1, 0.06), "#b48cff", center=(0, 1.82, 0), emit=4, tag="ringglow")

    def animate(t):
        a = t * TAU
        pose = base_anim(t, 0.2)
        pose["emblem"] = {"r": quat((0, 0, -math.degrees(a)))}
        pose["rings"] = {"r": quat((0, math.degrees(a), 0))}
        pose["moon"] = {"p": (0, 0.15 * math.sin(a * 2 + 1), 0), "r": quat((0, 15 * math.sin(a), 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 8 * math.sin(a * 2), sx * 8 * math.sin(a * 2)))}
        for i, (r_, orb, *_c) in enumerate(moons):
            ang = i / 3 * TAU + a * (1 if i % 2 == 0 else -1)
            piv = m.parts[f"planet{i}"].pivot
            tgt = Vector((math.cos(ang) * orb, CY + (i - 1) * 1.2 + 0.3 * math.sin(a * 2 + i), math.sin(ang) * orb))
            pose[f"planet{i}"] = {"p": tuple(tgt - piv), "r": quat((0, math.degrees(a * 3), 20))}
        return pose

    def glow(t):
        a = t * TAU
        return {"twinkle": 0.5 + 0.5 * math.sin(a * 5) ** 2, "core": 0.8 + 0.2 * math.sin(a * 2), "nebula": 0.75 + 0.25 * math.sin(a * 3),
                "ringglow": 0.8 + 0.2 * math.sin(a * 4)}

    m.animate, m.glow = animate, glow
    m.stage = {
        "bgTop": "#120a3a", "bgBottom": "#010006", "fog": [35, 90, "#05021a"], "ground": None, "dist": 1.9, "targetY": 4.4,
        "envTint": ["#c9b5ff", "#0a0520"],
        "lights": {"sky": "#c9b5ff", "groundCol": "#140a2a", "hemi": 0.8, "key": 2.0, "keyColor": "#f0e8ff",
                   "points": [{"color": "#d14ee8", "intensity": 3, "pos": [-4, 6, 3], "distance": 14},
                              {"color": "#2bc4e6", "intensity": 3, "pos": [4, 3, 3], "distance": 14}]},
        "bloom": {"strength": 0.55, "threshold": 1.2, "radius": 1.1, "exposure": 0.95}, "emitScale": 0.4,
        "particles": [
            {"kind": "float", "count": 400, "color": "#ffffff", "size": 0.14, "radius": [8, 30], "height": [-6, 22], "speed": 0.6, "sprite": "square", "intensity": 2.2, "twinkle": True},
            {"kind": "orbit", "count": 120, "color": "#d6a8ff", "size": 0.28, "radius": [3, 6.5], "height": [1, 9], "speed": 0.2, "sprite": "sparkle", "intensity": 3},
        ],
        "burstPart": "shell", "shakePart": "egg", "burstColor": "#d14ee8", "burstColor2": "#9fe8ff",
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.2]},
    }
    return m


# ======================================================================================
#  4. TORMENTA
# ======================================================================================
def build_storm():
    R, HB, HT, V, CY = 2.0, 2.2, 2.8, 0.2, 4.6
    grays = ["#3a4660", "#46546f", "#52617d", "#2f3a52"]

    def shell(p, n, t, ang):
        h = _hash(p.x, p.y, p.z)
        f = fbm(p, 1.2, 5.0)
        if abs(f - 0.5) < 0.022:
            return ("#ffe14a", 3.0, "spark")
        g = fbm(p, 0.8, 9.0)
        if g > 0.62:
            return "#8a97b3" if h > 0.5 else "#7a88a6"
        return grays[int(h * 97) % len(grays)]

    m = egg_scene("egg_storm", R, HB, HT, V, CY, shell)

    # emblema: rayo dorado en marco de acero
    zf = egg_radius(0.3, R, HB, HT) + 0.12
    m.part("emblem", "egg", (0, 0.3, zf))
    hexa = [(math.sin(k / 6 * TAU) * 0.85, math.cos(k / 6 * TAU) * 0.95, 0) for k in range(6)]
    polyline(m, "emblem", hexa, (0.18, 0.18), "#c0c8d8", closed=True, metal=1)
    polyline(m, "emblem", [(0.2, 0.7, 0.05), (-0.25, 0.05, 0.05), (0.15, 0.05, 0.05), (-0.2, -0.7, 0.05)], (0.2, 0.16), "#ffe14a", emit=4, tag="spark")

    # banda metálica
    ring(m, "egg", egg_radius(-0.7, R, HB, HT) + 0.1, 44, (0.22, 0.14), "#c0c8d8", center=(0, -0.7, 0), metal=1)

    # nube de tormenta encima y espinas de rayo
    m.part("thunder", "egg", (0, HT + 1.4, 0))
    cloud(m, "thunder", (0, 0, 0), 1.0, "#5b6478", "#6e7890")
    cloud(m, "thunder", (0.9, -0.2, 0.4), 0.6, "#4e566a", "#5b6478")
    cloud(m, "thunder", (-0.9, -0.1, -0.3), 0.65, "#4e566a", "#6e7890")
    for i in range(3):
        bolt(m, "thunder", ((i - 1) * 0.6, -0.4, 0.2), ((i - 1) * 0.8, -1.6, 0.4), 4, "#fff27a", seed=i + 3, thick=0.1, emit=6, tag=f"flash{i}", branch=False)

    # rayos que caen alrededor
    for i in range(4):
        n = f"bolt{i}"
        a = i / 4 * TAU + 0.5
        m.part(n, "root", (0, 0, 0))
        top = Vector((math.cos(a) * 2.4, CY + 3.6, math.sin(a) * 2.4))
        bot = Vector((math.cos(a) * 4.3, 0.2, math.sin(a) * 4.3))
        bolt(m, n, top, bot, 8, "#fff27a", seed=i * 7 + 1, thick=0.13, emit=7, tag=f"flash{i % 3}")

    # alas de plumas de trueno
    rows = [
        (12, 1.8, 3.5, 0.66, -0.14, ["#6c7a96", "#8a98b4", "#ffe14a"]),
        (10, 1.1, 2.1, 0.62, 0.0, ["#7a88a6", "#9aa7c2", "#c9d3e8"]),
        (7, 0.6, 1.1, 0.6, 0.12, ["#9aa7c2", "#b8c3da", "#d8e0ef"]),
    ]
    bone = [(0, 0), (0.9, 0.7), (1.8, 1.7), (2.5, 2.7)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.55, 0.7, -0.9), (0, sx * -22, sx * 8))
        _wing(m, w, sx, rows, bone, "#c0c8d8", "#c0c8d8")
        bolt(m, w, (sx * 0.3, 0.2, 0.25), (sx * 2.2, 2.2, 0.25), 5, "#ffe14a", seed=11 + sx, thick=0.08, emit=4, tag="spark", branch=False)

    # nubes alrededor de la base (giran)
    m.part("clouds", "root", (0, 1.4, 0))
    for k in range(7):
        a = k / 7 * TAU
        cloud(m, "clouds", (math.cos(a) * 3.3, 0.3 * math.sin(k * 2), math.sin(a) * 3.3), 0.75, "#5b6478" if k % 2 else "#6e7890", "#4e566a")
    # plataforma rocosa con charcos
    m.box("root", (0, 0.3, 0), (3.6, 0.6, 3.6), "#2a2f3a", r=(0, 10, 0))
    m.box("root", (0, 0.75, 0), (2.8, 0.3, 2.8), "#353b48", r=(0, 35, 0))
    ring(m, "root", 1.5, 28, (0.1, 0.06), "#ffe14a", center=(0, 0.92, 0), emit=4, tag="spark")
    ring(m, "root", 3.0, 48, (0.08, 0.05), "#9fb8ff", center=(0, 0.05, 0), emit=3, tag="flash1")
    for k in range(5):
        a = k / 5 * TAU
        m.box("root", (math.cos(a) * 2.7, 0.03, math.sin(a) * 2.7), (0.9, 0.04, 0.6), "#5d7ab0", r=(0, k * 40, 0), emit=0.3, tag="flash2")

    def animate(t):
        a = t * TAU
        pose = base_anim(t, 0.16)
        pose["thunder"] = {"p": (0.1 * math.sin(a), 0.12 * math.sin(a * 2), 0), "s": (1 + 0.03 * math.sin(a * 4),) * 3}
        pose["clouds"] = {"r": quat((0, math.degrees(a), 0)), "p": (0, 0.1 * math.sin(a * 2), 0)}
        flap = math.sin(a * 4)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 14 * flap))}
        return pose

    def flash(t, offs):
        # destellos bruscos: dos golpes por bucle con parpadeo
        v = 0.08
        for o in offs:
            d = (t - o) % 1
            if d < 0.06:
                v = max(v, 1.6 if int(d * 100) % 2 == 0 else 0.4)
        return v

    def glow(t):
        a = t * TAU
        return {"spark": 0.75 + 0.25 * math.sin(a * 10) ** 2, "flash0": flash(t, (0.1, 0.55)), "flash1": flash(t, (0.3, 0.8)),
                "flash2": flash(t, (0.45, 0.95))}

    m.animate, m.glow = animate, glow
    m.stage = {
        "bgTop": "#1c2539", "bgBottom": "#04060b", "fog": [24, 70, "#080b14"], "ground": "#0b0e15", "dist": 1.85, "targetY": 4.6,
        "envTint": ["#d8e2ff", "#0d1220"],
        "lights": {"sky": "#c4d2ff", "groundCol": "#141a26", "hemi": 0.85, "key": 2.2, "keyColor": "#e8eeff",
                   "points": [{"color": "#ffe14a", "intensity": 3, "pos": [0, 2.5, 3.5], "distance": 12},
                              {"color": "#9fb8ff", "intensity": 3, "pos": [-4, 9, -2], "distance": 16}]},
        "bloom": {"strength": 0.55, "threshold": 1.2, "radius": 1.0, "exposure": 0.95}, "emitScale": 0.4,
        "groundGlow": "rgba(160,190,255,0.18)", "groundGlowSize": 11,
        "particles": [
            {"kind": "snow", "count": 300, "color": "#9fb8ff", "size": 0.1, "radius": [0.5, 14], "height": [0, 16], "speed": 6, "sprite": "square", "intensity": 1.6},
            {"kind": "rise", "count": 80, "color": "#ffe14a", "size": 0.18, "radius": [0.5, 3.2], "height": [0.8, 9], "speed": 0.9, "sprite": "sparkle", "intensity": 3},
        ],
        "burstPart": "shell", "shakePart": "egg", "burstColor": "#ffe14a", "burstColor2": "#9fb8ff",
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.22]},
    }
    return m


# ======================================================================================
#  5. SAKURA
# ======================================================================================
def build_sakura():
    R, HB, HT, V, CY = 2.0, 2.2, 2.85, 0.2, 4.5
    porcelain = ["#fbeef2", "#f7e3ea", "#f3d6e0", "#fff5f8"]

    def shell(p, n, t, ang):
        h = _hash(p.x, p.y, p.z)
        f = fbm(p, 1.3, 13.0)
        if abs(f - 0.5) < 0.018:
            return ("#e8b84a", 0.0, None)  # kintsugi
        g = fbm(p, 1.0, 4.0)
        if g > 0.63:
            return "#f59ab8" if h > 0.4 else "#ee7aa3"
        if t < 0.25 and h > 0.45:
            return "#f2b8cc"
        if h > 0.985:
            return ("#ffffff", 2.0, "twinkle")
        return porcelain[int(h * 97) % len(porcelain)]

    m = egg_scene("egg_sakura", R, HB, HT, V, CY, shell)
    # vetas kintsugi metálicas
    for b in m.parts["shell"].boxes:
        if b["col"] == "#e8b84a":
            b["metal"] = 1

    # ramas de cerezo envolviendo el huevo, con flores
    for k in range(2):
        pts = []
        for i in range(26):
            u = i / 25
            y = -1.6 + u * 3.6
            a = k * math.pi + 0.6 + u * 2.4
            pts.append(egg_surface(R, HB, HT, y, a, 0.12))
        polyline(m, "egg", pts, 0.18, "#4a2a20")
        for i in range(3, 25, 3):
            p = pts[i]
            nrm = Vector((p.x, p.y * 0.3, p.z)).normalized()
            q = Vector((0, 0, 1)).rotation_difference(nrm)
            flower(m, "egg", p + nrm * 0.16, 0.5, "#ffb7d0", "#ffe08a", rot=q, petal2="#ff9fc2", emit=0.4, tag="blossom")
            if i % 2:
                segment(m, "egg", p, p + nrm * 0.3 + Vector((0, 0.35, 0)), 0.09, "#4a2a20")

    # emblema: gran flor de sakura con borde de oro
    zf = egg_radius(0.4, R, HB, HT) + 0.12
    m.part("emblem", "egg", (0, 0.4, zf))
    flower(m, "emblem", (0, 0, 0.04), 1.5, "#ff9fc2", "#ffe08a", petal2="#ffb7d0", emit=0.6, tag="blossom")
    for k in range(5):
        a = k / 5 * TAU
        segment(m, "emblem", (math.cos(a) * 0.8, math.sin(a) * 0.8, 0), (math.cos(a + TAU / 5) * 0.8, math.sin(a + TAU / 5) * 0.8, 0), 0.1, "#e8b84a", metal=1)
    m.box("emblem", (0, 0, 0.14), (0.3, 0.3, 0.1), "#fff4c2", r=(0, 0, 45), emit=3, tag="core")

    # corona: anillo de flores + aguja dorada (kanzashi)
    m.part("crown", "egg", (0, HT - 0.2, 0))
    for k in range(6):
        a = k / 6 * TAU
        q = Vector((0, 0, 1)).rotation_difference(Vector((math.sin(a) * 0.6, 1, math.cos(a) * 0.6)).normalized())
        flower(m, "crown", (math.sin(a) * 0.55, 0.05, math.cos(a) * 0.55), 0.55, "#ffb7d0", "#ffe08a", rot=q, petal2="#ffd6e6", emit=0.4, tag="blossom")
    segment(m, "crown", (0, -0.2, 0), (0, 1.6, 0), 0.12, "#e8b84a", metal=1)
    crystal(m, "crown", (0, 1.8, 0), 0.4, 0.6, "#ff8fb8", emit=2, tag="core")
    for k in range(3):
        a = k / 3 * TAU
        segment(m, "crown", (0, 1.3, 0), (math.cos(a) * 0.5, 0.9, math.sin(a) * 0.5), 0.05, "#e8b84a", metal=1)
        m.box("crown", (math.cos(a) * 0.5, 0.78, math.sin(a) * 0.5), (0.16, 0.22, 0.16), "#ff8fb8", r=(0, 45, 0), emit=1.5, tag="core")

    # alas de pétalos
    rows = [
        (12, 1.8, 3.4, 0.74, -0.14, ["#ffe3ee", "#ffc4d9", "#ff9fc2"]),
        (10, 1.1, 2.1, 0.7, 0.0, ["#fff0f5", "#ffd6e6", "#ffb7d0"]),
        (7, 0.6, 1.1, 0.66, 0.12, ["#ffffff", "#fff0f5", "#ffd6e6"]),
    ]
    bone = [(0, 0), (0.9, 0.7), (1.8, 1.7), (2.5, 2.7)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.55, 0.7, -0.9), (0, sx * -22, sx * 8))
        _wing(m, w, sx, rows, bone, "#e8b84a", "#e8b84a")

    # base: estanque koi con piedras y farolillo de piedra
    for k in range(26):
        a = k / 26 * TAU
        m.box("root", (math.cos(a) * 3.4, 0.22, math.sin(a) * 3.4), (0.9, 0.44, 0.7), "#b9b2ad" if k % 2 else "#a39c97", r=(0, -math.degrees(a), 0))
    for ix in range(-8, 9):
        for iz in range(-8, 9):
            x, z = ix * 0.4, iz * 0.4
            if math.hypot(x, z) < 3.0:
                m.box("root", (x, 0.15, z), (0.4, 0.1, 0.4), "#5fc9c9" if _hash(x, z, 8) > 0.3 else "#72d6d0", emit=0.3, tag="water")
    m.box("root", (0, 0.45, 0), (2.0, 0.6, 2.0), "#8a5a3c", r=(0, 45, 0))  # tarima de madera
    m.box("root", (0, 0.8, 0), (1.6, 0.12, 1.6), "#e8b84a", r=(0, 45, 0), metal=1)
    for k, (x, z) in enumerate(((1.6, 1.9), (-2.0, -1.2), (2.1, -1.5))):  # peces koi
        m.box("root", (x, 0.24, z), (0.5, 0.1, 0.2), "#ff7a3a" if k % 2 else "#ffffff", r=(0, k * 60, 0))
        m.box("root", (x + 0.15, 0.25, z), (0.18, 0.1, 0.22), "#ff4a2a", r=(0, k * 60, 0))
    lx, lz = -2.7, 2.2  # farolillo
    for (w, h, y, col) in ((0.7, 0.2, 0.55, "#8f8a86"), (0.25, 0.8, 1.05, "#9d9893"), (0.8, 0.15, 1.5, "#8f8a86"),
                           (0.55, 0.5, 1.82, "#9d9893"), (0.95, 0.15, 2.15, "#8f8a86"), (0.45, 0.2, 2.32, "#8f8a86")):
        m.box("root", (lx, y, lz), (w, h, w), col)
    m.box("root", (lx, 1.82, lz), (0.6, 0.3, 0.3), "#ffcf7a", emit=3, tag="lantern")
    m.box("root", (lx, 1.82, lz), (0.3, 0.3, 0.6), "#ffcf7a", emit=3, tag="lantern")
    # anillos de pétalos
    m.part("petal_ring", "egg", (0, -0.4, 0), (75, 0, -15))
    for k in range(18):
        a = k / 18 * TAU
        m.box("petal_ring", (math.cos(a) * 3.1, 0, math.sin(a) * 3.1), (0.3, 0.06, 0.22), "#ffb7d0" if k % 2 else "#ffd6e6",
              r=(20 * math.sin(k), math.degrees(-a), 30), emit=0.5, tag="blossom")

    def animate(t):
        a = t * TAU
        pose = base_anim(t, 0.16)
        flap = math.sin(a * 2)
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 12 * flap))}
        pose["crown"] = {"r": quat((0, math.degrees(a), 0))}
        pose["petal_ring"] = {"r": quat((0, math.degrees(a * 2), 0))}
        pose["emblem"] = {"r": quat((0, 0, 8 * math.sin(a * 2)))}
        return pose

    def glow(t):
        a = t * TAU
        return {"blossom": 0.8 + 0.2 * math.sin(a * 2), "core": 0.8 + 0.2 * math.sin(a * 4), "twinkle": 0.5 + 0.5 * math.sin(a * 6) ** 2,
                "water": 0.85 + 0.15 * math.sin(a * 4), "lantern": 0.85 + 0.15 * math.sin(a * 14) * math.sin(a * 5)}

    m.animate, m.glow = animate, glow
    m.stage = {
        "bgTop": "#3b1d44", "bgBottom": "#0f0712", "fog": [28, 80, "#170a1a"], "ground": "#1a0f1c", "dist": 1.85, "targetY": 4.5,
        "envTint": ["#ffd6e6", "#2a1430"],
        "lights": {"sky": "#ffd6ea", "groundCol": "#2a1430", "hemi": 0.9, "key": 2.2, "keyColor": "#fff0f4",
                   "points": [{"color": "#ff8fb8", "intensity": 3, "pos": [0, 2.5, 3.5], "distance": 12},
                              {"color": "#ffcf7a", "intensity": 2, "pos": [-2.7, 2, 2.2], "distance": 8}]},
        "bloom": {"strength": 0.45, "threshold": 1.25, "radius": 1.0, "exposure": 0.9}, "emitScale": 0.45,
        "groundGlow": "rgba(255,150,190,0.22)", "groundGlowSize": 11,
        "particles": [
            {"kind": "snow", "count": 220, "color": "#ffb7d0", "size": 0.2, "radius": [0.5, 12], "height": [0, 15], "speed": 0.9, "sprite": "square", "intensity": 1.8},
            {"kind": "orbit", "count": 80, "color": "#ffe08a", "size": 0.26, "radius": [3, 5.5], "height": [1, 9], "speed": 0.25, "sprite": "sparkle", "intensity": 3},
        ],
        "burstPart": "shell", "shakePart": "egg", "burstColor": "#ff9fc2", "burstColor2": "#ffe08a",
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.22]},
    }
    return m
