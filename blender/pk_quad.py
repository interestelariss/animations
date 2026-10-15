"""Cuadrúpedos (mamíferos, dinosaurios de cuatro patas, criaturas míticas), lagartos de patas
abiertas y terópodos (dinosaurios bípedos).

Cada especie se describe con un diccionario de proporciones y rasgos (orejas,
cuernos, trompa, melena, púas, joroba, cola, patrón de piel...).
"""

import math

from mathutils import Vector

from eggs import _wing
from eggs_themes import horn, membrane_wing, vnoise
from pk_common import TAU, eyes, mix, shades, skin, solid, spikes_on
from sculpt import cap, ell, surface_point, voxelize
from voxel import crystal, polyline, quat, ring, segment


def _sk(ctx, d, fallback=None):
    """Diccionario de piel -> función de color."""
    if d is None:
        return fallback
    if callable(d):
        return d
    if isinstance(d, str):
        return skin(d, ctx=ctx)
    return skin(ctx=ctx, **d)


# ----------------------------------------------------------------------------- cuernos
def horns(m, part, kind, hs, col, ctx, size=1.0, tip=None, x=0.28, y=0.38, z=-0.02):
    S = ctx.S
    hs_ = hs * size
    tip = tip or mix(col, "#ffffff", 0.35)
    if kind == "antlers":  # ciervo: ramas
        for sx in (1, -1):
            base = Vector((sx * x * hs, y * hs, z * hs))
            pts = [base + Vector((sx * 0.35 * u * hs_, 1.1 * u * hs_, -0.25 * u * hs_ + 0.15 * u * u * hs_)) for u in (j / 5 for j in range(6))]
            polyline(m, part, pts, 0.07 * hs_ + 0.02, col)
            for j, (k, ln) in enumerate(((1, 0.4), (3, 0.45), (4, 0.3))):
                a = pts[k]
                segment(m, part, a, a + Vector((sx * 0.08 * hs_, 0.35 * ln * hs_ * 2, (0.25 if j % 2 == 0 else -0.1) * hs_)), 0.055 * hs_ + 0.015, col)
    elif kind == "reindeer":
        for sx in (1, -1):
            base = Vector((sx * x * hs, y * hs, z * hs))
            pts = [base + Vector((sx * 0.5 * u * hs_, 1.3 * u * hs_ - 0.3 * u * u * hs_, -0.5 * u * hs_ + 0.6 * u * u * hs_)) for u in (j / 6 for j in range(7))]
            polyline(m, part, pts, 0.07 * hs_ + 0.02, col)
            for k in (2, 3, 4, 5, 6):
                a = pts[k]
                segment(m, part, a, a + Vector((sx * 0.05 * hs_, 0.3 * hs_, 0.12 * hs_)), 0.05 * hs_ + 0.015, col)
            segment(m, part, pts[1], pts[1] + Vector((0, 0.15 * hs_, 0.45 * hs_)), 0.05 * hs_, col)  # pala frontal
            m.box(part, pts[1] + Vector((0, 0.18 * hs_, 0.45 * hs_)), (0.04 * hs_, 0.18 * hs_, 0.18 * hs_), col)
    elif kind == "moose":  # palas
        for sx in (1, -1):
            base = Vector((sx * x * hs, y * hs, z * hs))
            segment(m, part, base, base + Vector((sx * 0.4 * hs_, 0.2 * hs_, 0)), 0.1 * hs_, col)
            c0 = base + Vector((sx * 0.75 * hs_, 0.35 * hs_, -0.05 * hs_))
            for j in range(6):
                k = j / 5
                m.box(part, c0 + Vector((sx * 0.1 * k * hs_, 0.12 * hs_ * k, 0.5 * (k - 0.5) * hs_)), (0.55 * hs_, 0.07 * hs_, 0.16 * hs_), col,
                      r=(0, 0, sx * 25))
                segment(m, part, c0 + Vector((sx * 0.25 * hs_, 0.1 * hs_ + 0.12 * hs_ * k, 0.5 * (k - 0.5) * hs_)),
                        c0 + Vector((sx * 0.45 * hs_, 0.4 * hs_ + 0.12 * hs_ * k, 0.55 * (k - 0.5) * hs_)), 0.06 * hs_, col)
    elif kind == "ram":
        for sx in (1, -1):
            horn(m, part, (sx * x * hs, y * hs * 0.9, z * hs - 0.05 * hs), (sx * 0.5, 0.4, -0.75), 1.5 * hs_, 0.22 * hs_, -38, col, tip, steps=14)
    elif kind == "bull":
        for sx in (1, -1):
            horn(m, part, (sx * (x + 0.05) * hs, y * hs * 0.85, z * hs), (sx * 1.0, 0.1, 0.15), 0.9 * hs_, 0.16 * hs_, 34, col, tip, steps=9)
    elif kind == "buffalo":  # base ancha que cubre la frente y punta hacia arriba
        m.box(part, (0, y * hs * 0.95, z * hs), (0.75 * hs_, 0.14 * hs_, 0.32 * hs_), col)
        for sx in (1, -1):
            horn(m, part, (sx * 0.35 * hs, y * hs * 0.9, z * hs), (sx * 1.0, -0.35, 0.1), 0.9 * hs_, 0.17 * hs_, 50, col, tip, steps=9)
    elif kind == "ibex":
        for sx in (1, -1):
            horn(m, part, (sx * (x - 0.1) * hs, y * hs, z * hs), (sx * 0.15, 0.75, -0.65), 1.7 * hs_, 0.16 * hs_, -14, col, tip, steps=14)
    elif kind == "goat":
        for sx in (1, -1):
            horn(m, part, (sx * (x - 0.08) * hs, y * hs, z * hs), (sx * 0.2, 0.8, -0.6), 0.55 * hs_, 0.11 * hs_, -18, col, tip, steps=7)
    elif kind == "gazelle":
        for sx in (1, -1):
            horn(m, part, (sx * (x - 0.1) * hs, y * hs, z * hs), (sx * 0.12, 0.9, -0.4), 1.0 * hs_, 0.08 * hs_, -10, col, tip, steps=10)
    elif kind == "oryx":
        for sx in (1, -1):
            horn(m, part, (sx * (x - 0.12) * hs, y * hs, z * hs), (sx * 0.06, 0.75, -0.65), 1.8 * hs_, 0.07 * hs_, -2, col, tip, steps=12)
    elif kind == "kudu":
        for sx in (1, -1):
            pos = Vector((sx * (x - 0.05) * hs, y * hs, z * hs))
            for j in range(18):
                a = j * 0.55
                nxt = pos + Vector((sx * (0.06 + 0.07 * math.cos(a)) * hs_, 0.085 * hs_, 0.07 * math.sin(a) * hs_ - 0.03 * hs_))
                segment(m, part, pos, nxt, 0.11 * hs_ * (1 - j / 22), col if j < 15 else tip)
                pos = nxt
    elif kind == "ossicones":  # jirafa
        for sx in (1, -1):
            segment(m, part, (sx * 0.16 * hs, y * hs, z * hs), (sx * 0.2 * hs, (y + 0.4) * hs_, (z - 0.05) * hs), 0.1 * hs_, col)
            m.box(part, (sx * 0.2 * hs, (y + 0.42) * hs_, (z - 0.05) * hs), (0.15 * hs_, 0.12 * hs_, 0.15 * hs_), "#2a1a10")
    elif kind == "unicorn":
        pos = Vector((0, (y + 0.05) * hs, 0.42 * hs))
        d = Vector((0, 0.82, 0.57)).normalized()
        for j in range(12):
            k = j / 11
            w = 0.16 * hs_ * (1 - k * 0.85) + 0.02
            m.box(part, pos + d * 1.25 * hs_ * k, (w, 1.25 * hs_ / 11 + 0.02, w), col if j % 2 else tip,
                  r=Vector((0, 1, 0)).rotation_difference(d) @ quat((0, 35 * j, 0)), emit=0.6 * (ctx.L >= 2), tag="glow" if ctx.L >= 2 else None)
    elif kind == "rhino":
        crystal(m, part, (0, 0.05 * hs, 0.95 * hs), 0.3 * hs_, 0.9 * hs_, col, rot=(-25, 0, 0))
        crystal(m, part, (0, 0.18 * hs, 0.6 * hs), 0.2 * hs_, 0.5 * hs_, col, rot=(-20, 0, 0))
    elif kind == "trike":  # triceratops: gorguera + 3 cuernos
        for sx in (1, -1):
            horn(m, part, (sx * 0.22 * hs, 0.42 * hs, 0.15 * hs), (sx * 0.15, 0.6, 0.8), 1.1 * hs_, 0.14 * hs_, -10, col, tip, steps=9)
        horn(m, part, (0, 0.0, 0.95 * hs), (0, 0.6, 0.6), 0.45 * hs_, 0.12 * hs_, -10, col, tip, steps=5)
    elif kind == "dragon":
        for sx in (1, -1):
            horn(m, part, (sx * x * hs, y * hs, z * hs), (sx * 0.3, 0.55, -0.75), 1.0 * hs_, 0.15 * hs_, -16, col, tip, steps=10,
                 tip_emit=0.8 if ctx.L >= 3 else 0, tag="glow" if ctx.L >= 3 else None)
            horn(m, part, (sx * (x + 0.15) * hs, (y - 0.2) * hs, (z - 0.1) * hs), (sx * 0.8, 0.1, -0.6), 0.5 * hs_, 0.09 * hs_, -10, col, tip,
                 steps=6)
    elif kind == "devil":
        for sx in (1, -1):
            horn(m, part, (sx * x * hs, y * hs, z * hs + 0.1 * hs), (sx * 0.45, 0.85, 0.15), 0.55 * hs_, 0.12 * hs_, 22, col, tip, steps=7)
    elif kind == "crescent":
        for sx in (1, -1):
            horn(m, part, (sx * x * hs, y * hs, z * hs), (sx * 0.9, 0.5, 0.0), 0.8 * hs_, 0.11 * hs_, 55, col, tip, steps=10,
                 tip_emit=1.0 if ctx.L >= 2 else 0, tag="glow" if ctx.L >= 2 else None)
    elif kind == "crystal":
        for j, (dx, h_, rz) in enumerate(((0, 1.0, 0), (0.25, 0.7, -25), (-0.25, 0.7, 25), (0.42, 0.45, -40), (-0.42, 0.45, 40))):
            crystal(m, part, (dx * hs, (y + 0.15 + h_ * 0.3) * hs_, z * hs), 0.22 * hs_, h_ * hs_, ctx.en if j % 2 == 0 else col, rot=(-15, 0, rz),
                    emit=1.2, tag="glow")
    elif kind == "antlers_tree":  # astas que son ramas con hojas/cristales
        for sx in (1, -1):
            base = Vector((sx * x * hs, y * hs, z * hs))
            pts = [base + Vector((sx * 0.5 * u * hs_, 1.4 * u * hs_, -0.2 * u * hs_)) for u in (j / 6 for j in range(7))]
            polyline(m, part, pts, 0.09 * hs_, col)
            for k in (2, 3, 4, 5, 6):
                a = pts[k]
                e = a + Vector((sx * 0.35 * hs_, 0.3 * hs_, (0.25 if k % 2 else -0.2) * hs_))
                segment(m, part, a, e, 0.06 * hs_, col)
                m.box(part, e, (0.16 * hs_,) * 3, ctx.en, r=(45, 0, 45), emit=1.3, tag="glow")


# ----------------------------------------------------------------------------- orejas
def ears(m, head, kind, hs, sk, inner, ctx, size=1.0, tilt=-10, x=0.3, y=0.38, z=0.0, tuft=None, v=0.1):
    if kind in (None, "none"):
        return
    es = hs * size
    for side, sx in (("L", 1), ("R", -1)):
        e = f"ear_{side}"
        m.part(e, head, (sx * x * hs, y * hs, z * hs), (0, 0, sx * tilt))
        if kind == "pointy":
            ep = [cap((0, 0, 0), (sx * 0.06 * es, 0.45 * es, -0.05 * es), 0.17 * es, 0.03 * es)]
        elif kind == "tall":  # zorro fénec, serval
            ep = [cap((0, 0, 0), (sx * 0.12 * es, 0.75 * es, -0.05 * es), 0.22 * es, 0.04 * es)]
        elif kind == "long":  # conejo
            ep = [ell((0, 0.55 * es, -0.02 * es), (0.13 * es, 0.6 * es, 0.07 * es))]
        elif kind == "lop":  # conejo belier: caen a los lados
            ep = [ell((sx * 0.12 * es, -0.25 * es, 0.05 * es), (0.1 * es, 0.5 * es, 0.15 * es))]
        elif kind == "round":
            ep = [ell((0, 0.1 * es, 0), (0.15 * es, 0.14 * es, 0.07 * es))]
        elif kind == "biground":  # ratón, koala
            ep = [ell((sx * 0.08 * es, 0.15 * es, -0.02 * es), (0.28 * es, 0.26 * es, 0.08 * es))]
        elif kind == "floppy":
            ep = [ell((sx * 0.12 * es, -0.2 * es, 0.05 * es), (0.1 * es, 0.32 * es, 0.17 * es))]
        elif kind == "fan":  # elefante
            ep = [ell((sx * 0.35 * es, -0.15 * es, -0.1 * es), (0.45 * es, 0.55 * es, 0.07 * es))]
        elif kind == "tiny":
            ep = [ell((0, 0.04 * es, 0), (0.08 * es, 0.07 * es, 0.05 * es))]
        elif kind == "side":  # ciervo, vaca: hacia los lados
            ep = [ell((sx * 0.25 * es, 0.05 * es, -0.02 * es), (0.25 * es, 0.1 * es, 0.08 * es))]
        elif kind == "bat":
            ep = [cap((0, 0, 0), (sx * 0.2 * es, 0.75 * es, -0.05 * es), 0.25 * es, 0.05 * es)]
        else:
            ep = []
        if ep:
            voxelize(m, e, ep, v * 0.75, lambda p, n, inner=inner: inner if (inner and n.z > 0.55 and kind in ("pointy", "tall", "long", "bat", "biground", "side"))
                     else sk(p, n))
        if tuft:  # lince, caracal: pincel negro en la punta
            tipp = Vector((sx * 0.08 * es, 0.5 * es, -0.05 * es)) if kind != "tall" else Vector((sx * 0.14 * es, 0.82 * es, -0.05 * es))
            segment(m, e, tipp, tipp + Vector((0, 0.3 * es, 0)), 0.05 * es, tuft)


# ----------------------------------------------------------------------------- colas
def tail(m, parent, piv, kind, ctx, n=6, seg=0.3, w=0.14, lift=-25, curve=6, sk=None, tuft=None, prefix="tail", v=0.1, yaw=0):
    S = ctx.S
    seg, w = seg * S, w * S
    if kind in (None, "none"):
        return 0
    if kind == "puff":
        m.part(prefix + "0", parent, piv, (lift, yaw, 0))
        voxelize(m, prefix + "0", [ell((0, 0, -0.05), (w * 2.2, w * 2.2, w * 2.0), 0.15, 5)], v * 0.8, sk)
        return 1
    if kind == "stub":
        m.part(prefix + "0", parent, piv, (lift, yaw, 0))
        voxelize(m, prefix + "0", [cap((0, 0, 0), (0, 0, -seg * 0.6), w, w * 0.7)], v * 0.8, sk)
        return 1
    if kind == "curl":  # cerdo: sacacorchos
        m.part(prefix + "0", parent, piv, (lift, yaw, 0))
        pts = [Vector((0.08 * S * math.cos(a), 0.08 * S * math.sin(a), -0.04 * S * a)) for a in (j * 0.7 for j in range(10))]
        polyline(m, prefix + "0", pts, w * 0.6, sk(Vector(), Vector((0, 1, 0))) if not isinstance(sk(Vector(), Vector((0, 1, 0))), tuple) else "#f0a0a0")
        return 1
    if kind == "flat":  # castor: pala
        m.part(prefix + "0", parent, piv, (lift, yaw, 0))
        voxelize(m, prefix + "0", [ell((0, 0, -seg * 1.2), (w * 2.6, w * 0.45, seg * 1.3))], v * 0.8,
                 lambda p, n: "#3a2a24" if ((p.x * 9) % 1 < 0.2 or (p.z * 9) % 1 < 0.2) else "#4a3a32")
        return 1
    if kind in ("scorpion", "snake"):  # cola de mantícora (aguijón) o de quimera (cabeza de serpiente)
        parent_, piv_ = parent, piv
        for i in range(n):
            nm = f"{prefix}{i}"
            m.part(nm, parent_, piv_, ((lift if i == 0 else curve), yaw if i == 0 else 0, 0))
            r_ = w * (1.3 - 0.5 * i / n) if kind == "scorpion" else w * (1 - 0.3 * i / n)
            voxelize(m, nm, [ell((0, 0, -seg / 2), (r_, r_, seg * 0.62))] if kind == "scorpion" else [cap((0, 0, 0), (0, 0, -seg * 1.05), r_, r_ * 0.92)], v * 0.8, sk)
            parent_, piv_ = nm, (0, 0, -seg)
        last = f"{prefix}{n - 1}"
        if kind == "scorpion":
            voxelize(m, last, [ell((0, 0, -seg * 1.2), (w * 1.4, w * 1.4, w * 1.8))], v * 0.8, solid(tuft or "#3a2a1a"))
            segment(m, last, (0, 0, -seg * 1.5), (0, -w * 2.2, -seg * 1.9), 0.06 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", emit=1.5 if ctx.L >= 3 else 0,
                    tag="glow" if ctx.L >= 3 else None)
        else:
            voxelize(m, last, [ell((0, w * 0.2, -seg * 1.2), (w * 1.5, w * 1.2, w * 2.2))], v * 0.8, solid(tuft or "#3a6a2a"))
            for sx in (1, -1):
                m.box(last, (sx * w * 0.8, w * 0.8, -seg * 1.6), (0.06 * S, 0.06 * S, 0.06 * S), "#ffd23a", emit=1.0, tag="eyes")
            segment(m, last, (0, 0, -seg * 2.0), (0, 0, -seg * 2.5), (0.05 * S, 0.02 * S), "#e8304a")
        return n
    parent_, piv_ = parent, piv
    for i in range(n):
        k = i / max(n - 1, 1)
        nm = f"{prefix}{i}"
        m.part(nm, parent_, piv_, (lift if i == 0 else curve, yaw if i == 0 else 0, 0))
        if kind == "bushy":
            r_ = w * (1.0 + 1.3 * math.sin(k * math.pi * 0.9 + 0.15))
            tp = [ell((0, 0, -seg / 2), (r_, r_, seg * 0.72), 0.15, 4)]
        elif kind == "fan":  # ardilla: muy grande y peluda
            r_ = w * (1.4 + 1.8 * math.sin(k * math.pi * 0.8 + 0.2))
            tp = [ell((0, 0, -seg / 2), (r_ * 0.8, r_, seg * 0.75), 0.2, 4)]
        elif kind in ("thick", "fishtail"):  # reptiles, canguro: gruesa en la base
            r_ = w * (1.6 - 1.25 * k)
            tp = [cap((0, 0, 0), (0, 0, -seg * 1.05), r_, r_ * 0.86)]
        elif kind == "thin":  # rata
            r_ = w * 0.45 * (1 - 0.5 * k)
            tp = [cap((0, 0, 0), (0, 0, -seg * 1.05), r_, r_ * 0.9)]
        else:  # long / tuft / ringed / club
            r_ = w * (1 - 0.45 * k)
            tp = [cap((0, 0, 0), (0, 0, -seg * 1.05), r_, r_ * 0.9)]
        if kind == "fishtail" and i == n - 1:  # capricornio: aleta de pez al final
            for sx in (1, -1):
                for j in range(4):
                    m.box(nm, (0, sx * (0.12 + j * 0.13) * S, -seg - (0.1 + j * 0.1) * S), (0.06 * S, 0.18 * S, 0.3 * S), tuft or "#5ff4ff")
        if kind == "tuft" and i == n - 1:
            voxelize(m, nm, [ell((0, 0, -seg), (w * 1.8, w * 1.8, w * 2.4), 0.25, 5)], v * 0.8, solid(tuft or "#3a2010"))
        if kind == "club" and i == n - 1:
            voxelize(m, nm, [ell((0, 0, -seg), (w * 2.6, w * 1.6, w * 2.4), 0.12, 4)], v * 0.8, sk)
        if kind == "ringed":
            voxelize(m, nm, tp, v * 0.8, (lambda p, n, i=i: tuft if (int((-p.z / seg) * 2 + i * 2) % 2) else sk(p, n)))
        else:
            voxelize(m, nm, tp, v * 0.8, sk)
        parent_, piv_ = nm, (0, 0, -seg)
    return n


# ----------------------------------------------------------------------------- alas
def wings(m, parent, kind, ctx, at, span=1.0, cols=None, prefix="wing"):
    S = ctx.S
    cols = cols or [ctx.shell[0], ctx.shell[1], ctx.acc]
    sc = span * S
    for side, sx in (("L", 1), ("R", -1)):
        w = f"{prefix}_{side}"
        m.part(w, parent, (sx * at[0], at[1], at[2]), (0, sx * -15, sx * 12))
        if kind == "feather":
            _wing(m, w, sx, [(9, 0.5 * sc, 1.5 * sc, 0.32 * sc, 0, cols[:3]), (7, 0.35 * sc, 0.9 * sc, 0.28 * sc, 0.15 * sc, [cols[0], cols[0], cols[1]])],
                  [(0, 0), (0.45 * sc, 0.35 * sc), (0.9 * sc, 0.8 * sc), (1.3 * sc, 1.35 * sc)], cols[2], cols[2])
        elif kind == "bat":
            membrane_wing(m, w, sx, (0.9 * sc, 1.0 * sc), [(0.8 * sc, 1.8 * sc), (1.9 * sc, 1.8 * sc), (2.6 * sc, 0.9 * sc), (2.5 * sc, -0.3 * sc)],
                          cols[2], cols[0], cols[1], step=0.11 * S)
        elif kind == "crystal":
            for i in range(7):
                k = i / 6
                th = math.radians(-20 + k * 110)
                Lw = (0.9 + 0.8 * math.sin(k * math.pi)) * sc
                d = Vector((sx * math.cos(th), math.sin(th), 0))
                crystal(m, w, d * (0.2 + Lw / 2), 0.3 * sc, Lw, ctx.en if i % 2 else cols[1],
                        rot=(0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th)), emit=0.7, tag="glow")
        elif kind == "butterfly":
            for j, (cx, cz, rx, rz) in enumerate(((0.75, 0.2, 0.7, 0.55), (0.55, -0.45, 0.5, 0.42))):
                voxelize(m, w, [ell((sx * cx * sc, 0, cz * sc), (rx * sc, 0.05 * sc, rz * sc))], ctx.v * 0.8,
                         lambda p, n: cols[2] if math.hypot(p.x, p.z) > 0.95 * sc else (cols[1] if vnoise(p.x * 3, 1, p.z * 3) > 0.62 else cols[0]))
    return [f"{prefix}_L", f"{prefix}_R"]


# ----------------------------------------------------------------------------- cuadrúpedo
def quad(m, P, ctx):
    S, v = ctx.S * P.get("size", 1.0), ctx.v * P.get("size", 1.0) ** 0.5
    L, W, H = P.get("L", 1.8) * S, P.get("W", 1.0) * S, P.get("H", 1.0) * S
    lf, lb = P.get("legF", 0.8) * S, P.get("legB", P.get("legF", 0.8)) * S
    lw = P.get("legW", 1.0)
    hs, sn = P.get("hs", 1.0) * S, P.get("sn", 0.3) * S
    nz = P.get("noise", 0.06)
    bsk = _sk(ctx, P.get("skin", "#a07040"))
    hsk = _sk(ctx, P.get("hskin"), bsk)
    lsk = _sk(ctx, P.get("lskin"), bsk)
    tsk = _sk(ctx, P.get("tskin"), bsk)
    ex = set(P.get("ex", ()))
    fat, chest, hip = P.get("fat", 0.0), P.get("chest", 1.0), P.get("hip", 1.0)
    m.part("body", "root", (0, max(lf, lb) * 0.95 + H * 0.5, 0))
    prims = [
        ell((0, 0.08 * H, 0.3 * L), (0.52 * W * chest, 0.55 * H * chest, 0.3 * L), nz, 3),
        ell((0, (0.02 - 0.08 * fat) * H, 0.05 * L), (0.48 * W * (1 + 0.3 * fat), 0.5 * H * (1 + 0.25 * fat), 0.33 * L), nz, 3),
        ell((0, 0.06 * H, -0.18 * L), (0.42 * W * (1 + 0.3 * fat) * P.get("waist", 1), 0.43 * H * (1 + 0.2 * fat) * P.get("waist", 1), 0.25 * L), nz, 3),
        ell((0, 0.1 * H, -0.33 * L), (0.46 * W * hip, 0.5 * H * hip, 0.2 * L), nz, 3),
        ell((0.3 * W, 0.3 * H, 0.3 * L), (0.22 * W, 0.28 * H, 0.16 * L), nz, 3),
        ell((-0.3 * W, 0.3 * H, 0.3 * L), (0.22 * W, 0.28 * H, 0.16 * L), nz, 3),
    ]
    hump = P.get("hump")
    if hump == 1:
        prims.append(ell((0, 0.5 * H, 0.0), (0.32 * W, 0.42 * H, 0.26 * L), 0.05, 3))
    elif hump == 2:
        prims += [ell((0, 0.48 * H, 0.17 * L), (0.28 * W, 0.36 * H, 0.17 * L), 0.05, 3), ell((0, 0.45 * H, -0.17 * L), (0.28 * W, 0.34 * H, 0.17 * L), 0.05, 3)]
    elif hump == "bison":
        prims.append(ell((0, 0.42 * H, 0.26 * L), (0.5 * W, 0.52 * H, 0.3 * L), 0.12, 3))
    if "wool" in ex:
        prims = [ell(pr[1], pr[2] * 1.15, 0.22, 5.0 / S) for pr in prims]
    nu, nf = P.get("neckUp", 0.35) * S, P.get("neckFwd", 0.3) * S
    neck_end = Vector((0, 0.25 * H + nu, 0.42 * L + nf))
    nw = P.get("neckW", 1.0)
    prims.append(cap((0, 0.2 * H, 0.36 * L), neck_end, 0.36 * W * nw, 0.3 * W * nw * P.get("neckTaper", 1.0), nz, 3))
    if P.get("neckUp", 0.35) > 1.0:  # cuello largo: articulación intermedia más gruesa
        prims.append(ell(Vector((0, 0.2 * H, 0.36 * L)).lerp(neck_end, 0.35), (0.33 * W * nw, 0.33 * W * nw, 0.33 * W * nw), nz, 3))
    voxelize(m, "body", prims, v, bsk)
    info = dict(L=L, W=W, H=H, lf=lf, lb=lb, hs=hs, sn=sn, S=S, v=v, neck_end=neck_end, body="body")

    heads = P.get("heads", 1)
    head_names = []
    for hi in range(heads):
        hn = "head" if hi == 0 else f"head{hi}"
        off = Vector((0, 0, 0))
        yaw = 0
        if heads == 3 and hi > 0:
            sx = 1 if hi == 1 else -1
            off = Vector((sx * 0.42 * W, -0.15 * hs, -0.12 * hs))
            yaw = sx * 22
        m.part(hn, "body", tuple(neck_end + Vector((0, 0.08 * hs, 0.05 * hs)) + off), (P.get("headPitch", 0), yaw, 0))
        head_names.append(hn)
        _head(m, hn, P, ctx, hs, sn, hsk, v, ex, info, suffix="" if hi == 0 else str(hi))
    info["head"] = "head"
    info["heads"] = head_names

    # extras del cuerpo
    if "mane" in ex:  # león
        mc = P.get("maneCol", "#7a4a1a")
        mane_parts = []
        for hn in head_names:
            mn = "mane" if hn == "head" else "mane" + hn[4:]
            m.part(mn, hn, (0, 0, -0.05 * hs))
            voxelize(m, mn, [ell((0, 0.02 * hs, -0.12 * hs), (0.98 * hs, 0.98 * hs, 0.6 * hs), 0.25, 2.6 / S)], v,
                     skin([mc, mix(mc, "#000000", 0.18), mix(mc, "#ffffff", 0.1)], ctx=ctx),
                     carve=[ell((0, 0.0, 0.42 * hs), (0.62 * hs, 0.6 * hs, 0.5 * hs))])
            mane_parts.append(mn)
        voxelize(m, "body", [ell((0, 0.3 * H, 0.4 * L), (0.55 * W, 0.55 * H, 0.3 * L), 0.25, 2.6 / S)], v,
                 skin([mc, mix(mc, "#000000", 0.18)], ctx=ctx))
    if "ridge" in ex:  # crin de caballo a lo largo del cuello
        mc = P.get("maneCol", "#3a2418")
        a, b = Vector((0, 0.45 * H, 0.25 * L)), neck_end + Vector((0, 0.2 * hs, -0.25 * hs))
        for j in range(9):
            k = j / 8
            p = a.lerp(b, k)
            m.box("body", p + Vector((0, 0.12 * S, -0.05 * S)), (0.12 * S, 0.32 * S, 0.24 * S), mc if j % 2 else mix(mc, "#ffffff", 0.12),
                  r=(-25, 0, 0))
        m.box("head", (0, 0.42 * hs, 0.28 * hs), (0.18 * hs, 0.14 * hs, 0.3 * hs), mc, r=(30, 0, 0))
    if "rainbow_mane" in ex:
        bands = ["#ff9ab8", "#ffd27a", "#fff3a0", "#a8f0b8", "#9ad8ff", "#c8a8ff"]
        a, b = Vector((0, 0.45 * H, 0.25 * L)), neck_end + Vector((0, 0.2 * hs, -0.25 * hs))
        for j in range(12):
            k = j / 11
            p = a.lerp(b, k)
            m.box("body", p + Vector((0, 0.15 * S, -0.08 * S)), (0.16 * S, 0.4 * S, 0.22 * S), bands[j % 6], r=(-30, 0, 0))
        m.box("head", (0, 0.42 * hs, 0.3 * hs), (0.2 * hs, 0.18 * hs, 0.32 * hs), bands[0], r=(30, 0, 0))
    if "quills" in ex or "porcupine" in ex:
        long = "porcupine" in ex
        pts, cen, R = [], Vector((0, 0.08 * H, 0.0)), Vector((0.5 * W, 0.55 * H, 0.5 * L))
        for i in range(14 if long else 18):
            for j in range(9 if long else 11):
                th = (i + 0.5 * (j % 2)) / (14 if long else 18) * math.pi
                ph = (j / ((9 if long else 11) - 1) - 0.5) * 2.4
                d = Vector((math.cos(th) * math.cos(ph * 0.55), abs(math.sin(th)) * math.cos(ph * 0.55) + 0.05, math.sin(ph * 0.55)))
                if d.y < 0.05 or d.z > 0.72:
                    continue
                pts.append((cen + Vector((d.x * R.x, d.y * R.y, d.z * R.z)), d.normalized()))
        qc = P.get("quillCol", "#5a4030")
        for p, d in pts:
            ln = (0.55 if long else 0.28) * S * (0.8 + 0.4 * ((p.x * 13 + p.z * 7) % 1))
            back = (d + Vector((0, 0, -0.6))).normalized()
            segment(m, "body", p, p + back * ln * 0.6, 0.06 * S, qc)
            segment(m, "body", p + back * ln * 0.55, p + back * ln, 0.04 * S, P.get("quillTip", "#f2ead6"))
    if "armor" in ex:  # armadillo / gliptodonte: bandas de placas
        ac = P.get("armorCol", "#9a8a72")
        for j in range(P.get("armorBands", 9)):
            z = (0.42 - j * 0.84 / (P.get("armorBands", 9) - 1)) * L
            ring_r = 0.56 * W * (1 - 0.25 * abs(z / L) ** 2 * 2)
            for k in range(13):
                a = math.pi * (0.04 + 0.92 * k / 12)
                p = Vector((math.cos(a) * ring_r * 1.02, 0.08 * H + math.sin(a) * 0.62 * H, z))
                m.box("body", p, (0.2 * S, 0.1 * S, 0.84 * L / P.get("armorBands", 9) * 0.92), ac if (j + k) % 2 else mix(ac, "#000000", 0.15),
                      r=(0, 0, math.degrees(a) - 90))
    if "scaled" in ex:  # pangolín: escamas superpuestas
        sc_col = P.get("scaleCol", "#8a6a4a")
        cen, R = Vector((0, 0.08 * H, 0.0)), Vector((0.52 * W, 0.58 * H, 0.52 * L))
        for i in range(10):
            for j in range(12):
                th = (i + 0.5 * (j % 2)) / 10 * math.pi
                z = (j / 11 - 0.5) * 1.9
                d = Vector((math.cos(th) * math.sqrt(max(0, 1 - (z / 2) ** 2)), math.sin(th) * math.sqrt(max(0, 1 - (z / 2) ** 2)), z / 2))
                if d.y < -0.1:
                    continue
                p = cen + Vector((d.x * R.x, d.y * R.y, d.z * R.z))
                q = Vector((0, 0, -1)).rotation_difference((-d * 0.3 + Vector((0, 0, -1))).normalized())
                m.box("body", p, (0.32 * S, 0.06 * S, 0.3 * S), sc_col if (i + j) % 3 else mix(sc_col, "#ffffff", 0.15),
                      r=quat((0, 0, math.degrees(th) - 90)) @ quat((-20, 0, 0)))
    if "spikes" in ex:  # cresta de púas en el lomo
        scol = P.get("spikeCol", ctx.acc)
        for j in range(8):
            k = j / 7
            z = (0.4 - 0.85 * k) * L
            hgt = (0.35 - 0.15 * abs(k - 0.4)) * S * P.get("spikeH", 1.0)
            crystal(m, "body", (0, 0.58 * H + hgt * 0.4, z), 0.16 * S, hgt * 1.4, scol, rot=(-25, 0, 0))
    if "plates" in ex:  # estegosaurio: placas en rombo, alternas a cada lado
        pc_ = P.get("plateCol", "#c86a3a")
        n_ = 9
        sp_ = 0.9 * L / (n_ - 1)
        for j in range(n_):
            k = j / (n_ - 1)
            z = (0.42 - 0.9 * k) * L
            h_ = (0.25 + 0.45 * math.sin(k * math.pi)) * S * P.get("plateH", 1.0)
            wmax = min(h_ * 0.6, sp_ * 1.5)
            sx = 1 if j % 2 else -1
            for q in range(6):
                u = (q + 0.5) / 6
                m.box("body", (sx * 0.06 * S, 0.55 * H + u * h_, z), (0.07 * S, h_ / 6 + 0.01, wmax * math.sin(math.pi * min(0.95, u * 0.85 + 0.12)) + 0.03),
                      pc_ if q < 4 else mix(pc_, "#ffffff", 0.2))
    if "sail" in ex:  # dimetrodonte / espinosaurio
        sc_ = P.get("sailCol", "#c84a3a")
        for j in range(13):
            k = j / 12
            z = (0.4 - 0.85 * k) * L
            h_ = (0.25 + 1.0 * math.sin(k * math.pi)) * S * P.get("sailH", 1.0)
            segment(m, "body", (0, 0.5 * H, z), (0, 0.5 * H + h_, z - 0.05 * S), 0.06 * S, mix(sc_, "#000000", 0.35))
            if j < 12:
                h2 = (0.25 + 1.0 * math.sin((j + 1) / 12 * math.pi)) * S * P.get("sailH", 1.0)
                hh = min(h_, h2)
                m.box("body", (0, 0.5 * H + hh * 0.5, z - 0.85 * L / 24), (0.04 * S, hh, 0.85 * L / 12 + 0.02), sc_ if j % 2 else mix(sc_, "#ffffff", 0.12))
    if "flamemane" in ex:  # crin de fuego
        a, b = Vector((0, 0.45 * H, 0.25 * L)), neck_end + Vector((0, 0.2 * hs, -0.25 * hs))
        for j in range(11):
            p_ = a.lerp(b, j / 10)
            for q in range(3):
                m.box("body", p_ + Vector((0, (0.15 + 0.15 * q) * S, -(0.05 + 0.08 * q) * S)), (0.14 * S * (1 - 0.25 * q), 0.18 * S, 0.18 * S),
                      ["#ff4a1a", "#ff8a1a", "#ffd23a"][q], emit=1.4 + 0.4 * q, tag="fire", r=(-25, 0, 0))
    if "fwings" in ex or "bwings" in ex or "cwings" in ex or "flywings" in ex:
        kind = "feather" if "fwings" in ex else ("bat" if "bwings" in ex else ("crystal" if "cwings" in ex else "butterfly"))
        info["wings"] = wings(m, "body", kind, ctx, (0.35 * W, 0.45 * H, 0.28 * L), span=P.get("wingSpan", 0.7), cols=P.get("wingCols"), prefix="qwing")
    if "glider" in ex:  # ardilla voladora / petauro: membrana entre patas
        gc = P.get("gliderCol", None)
        voxelize(m, "body", [ell((sx * 0.62 * W, -0.15 * H, 0.0), (0.32 * W, 0.06 * S, 0.42 * L)) for sx in (1, -1)], v * 0.85,
                 (lambda p, n: gc) if gc else bsk)
    if "pouch" in ex:
        m.box("body", (0, -0.25 * H, 0.15 * L), (0.5 * W, 0.35 * H, 0.08 * S), mix(P.get("pouchCol", "#c8a070"), "#000000", 0.15))

    # patas
    claws, hoof = P.get("claws"), P.get("hoof")
    paw_col = P.get("paw")
    for name, sx, sz, ll in (("FL", 1, 1, lf), ("FR", -1, 1, lf), ("BL", 1, -1, lb), ("BR", -1, -1, lb)):
        up, lo_ = f"leg_{name}", f"low_{name}"
        front = sz > 0
        m.part(up, "body", (sx * P.get("stance", 0.33) * W, -0.12 * H, (0.3 if front else -0.33) * L))
        tw = W * lw
        if front:
            upr = [cap((0, 0, 0), (0, -0.5 * ll, 0.05 * ll), 0.24 * tw, 0.17 * tw), ell((0, -0.05 * ll, 0.02 * ll), (0.25 * tw, 0.28 * ll, 0.24 * tw))]
        else:
            upr = [ell((0, -0.08 * ll, 0.02), (0.28 * tw, 0.34 * ll, 0.32 * tw)), cap((0, 0, 0), (0, -0.5 * ll, -0.1 * ll), 0.22 * tw, 0.16 * tw)]
        voxelize(m, up, upr, v, lsk)
        knee = Vector((0, -0.5 * ll, (0.05 if front else -0.1) * ll))
        m.part(lo_, up, tuple(knee))
        lwr = [cap((0, 0, 0), (0, -0.45 * ll, (0 if front else 0.08) * ll), 0.16 * tw, 0.13 * tw)]
        if hoof:
            lwr.append(cap((0, -0.4 * ll, 0.02 * tw), (0, -0.5 * ll, 0.03 * tw), 0.16 * tw, 0.17 * tw))
            fn_ = (lambda p, n, ll=ll: hoof if p.y < -0.42 * ll else lsk(p, n))
        else:
            lwr.append(ell((0, -0.47 * ll, 0.08 * tw), (0.19 * tw, 0.08 * ll + 0.03, 0.26 * tw)))
            fn_ = (lambda p, n, ll=ll: paw_col if p.y < -0.4 * ll else lsk(p, n)) if paw_col else lsk
        if P.get("socks"):
            sc_, fr_ = P["socks"]
            fn0 = fn_
            fn_ = (lambda p, n, ll=ll, fn0=fn0: (sc_ if p.y < -(1 - fr_) * 0.5 * ll and not (hoof and p.y < -0.42 * ll) else fn0(p, n)))
        voxelize(m, lo_, lwr, v * 0.85, fn_)
        if claws:
            for k in (-1, 0, 1):
                m.box(lo_, (k * 0.09 * tw, -0.5 * ll, 0.3 * tw), (0.05 * tw, 0.06 * tw, 0.12 * tw), claws, r=(25, 0, 0))
        if P.get("anklet"):
            m.box(lo_, (0, -0.32 * ll, 0), (0.36 * tw, 0.08 * ll, 0.36 * tw), P["anklet"], metal=1)

    # cola(s)
    tk = P.get("tail", "long")
    ntails = P.get("tails", 1)
    info["tails"] = []
    for ti in range(ntails):
        pre = "tail" if ti == 0 else f"tl{ti}_"
        yaw = 0 if ntails == 1 else (ti - (ntails - 1) / 2) * (100 / max(ntails - 1, 1))
        n = tail(m, "body", (0, 0.25 * H, -0.5 * L), tk, ctx, n=P.get("tailN", 6), seg=P.get("tailSeg", 0.3), w=P.get("tailW", 0.14),
                 lift=P.get("tailLift", -25) - (abs(yaw) * 0.3 if ntails > 1 else 0), curve=P.get("tailCurve", 6), sk=tsk,
                 tuft=P.get("tuftCol"), prefix=pre, v=v, yaw=yaw)
        info["tails"].append((pre, n))
    info["tail_n"] = info["tails"][0][1]
    return info


def _head(m, hn, P, ctx, hs, sn, hsk, v, ex, info, suffix=""):
    S = ctx.S * P.get("size", 1.0)
    skullW, skullH, skullL = P.get("skullW", 1.0), P.get("skullH", 1.0), P.get("skullL", 1.0)
    skull = ell((0, 0.05 * hs, 0.1 * hs), (0.5 * hs * skullW, 0.46 * hs * skullH, 0.55 * hs * skullL))
    hp = [skull, ell((0, 0.27 * hs * skullH, 0.38 * hs), (0.44 * hs * skullW, 0.14 * hs, 0.22 * hs))]
    if P.get("cheeks", 1.0) > 0:
        ck = P.get("cheeks", 1.0)
        hp += [ell((sx * 0.33 * hs * skullW, -0.12 * hs, 0.25 * hs), (0.24 * hs * ck, 0.26 * hs * ck, 0.3 * hs)) for sx in (1, -1)]
    mw, mh = P.get("muzzleW", 1.0), P.get("muzzleH", 1.0)
    drop = P.get("snDrop", 0.0)
    tipz = 0.45 * hs + sn
    tipy = -0.14 * hs - drop * sn
    if sn > 0:
        hp.append(cap((0, -0.1 * hs, 0.45 * hs), (0, tipy, tipz), 0.3 * hs * mw * mh, 0.24 * hs * mw * mh * P.get("snTaper", 1.0)))
    if "pignose" in ex:
        hp.append(cap((0, tipy, tipz), (0, tipy, tipz + 0.1 * hs), 0.2 * hs, 0.2 * hs))
    hp += P.get("head_extra", [])
    nose_col = P.get("nose", "#2a1a1a")
    region = P.get("hregion")

    def head_col(p, n):
        if region:
            r = region(p, n, hs, sn)
            if r is not None:
                return r
        if nose_col and p.z > tipz - 0.05 * hs and abs(p.x - 0) < 0.14 * hs * mw and abs(p.y - tipy) < 0.12 * hs and n.z > 0.3:
            return nose_col
        return hsk(p, n)

    voxelize(m, hn, hp, v * 0.85, head_col)
    if "pignose" in ex:
        for sx in (1, -1):
            m.box(hn, (sx * 0.07 * hs, tipy, tipz + 0.21 * hs), (0.06 * hs, 0.09 * hs, 0.02), "#5a2a2a")
    E = P.get("eye", {})
    ex_, ey_ = E.get("x", 0.26), E.get("y", 0.14)
    sp = surface_point(skull, ex_ * hs * skullW, ey_ * hs)
    iris = E.get("col", "#3a2a1a")
    glow = ctx.eye_glow if E.get("glow", True) else 0
    if ctx.L >= 3 and E.get("themed", True):
        iris = ctx.en
    eyes(m, hn, (0, sp.y, sp.z + 0.01), ex_ * hs * skullW, hs * 0.2 * E.get("size", 1.0), iris, glow=glow, slit=E.get("slit", False),
         yaw=E.get("yaw", 18), lid=E.get("lid"), style=E.get("style", "round"))
    # mandíbula
    jn = "jaw" + suffix
    m.part(jn, hn, (0, -0.3 * hs, 0.32 * hs))
    jl = max(sn, 0.2 * hs) + 0.12 * hs
    jp = [cap((0, 0, 0), (0, -0.02 * hs - drop * sn * 0.8, jl), 0.2 * hs * mw, 0.16 * hs * mw)]
    voxelize(m, jn, jp, v * 0.8, lambda p, n: "#5a1a22" if n.y > 0.6 else hsk(p, n))
    if P.get("teeth"):
        for sx in (1, -1):
            m.box(hn, (sx * 0.14 * hs * mw, tipy - 0.2 * hs, tipz - 0.08 * hs), (0.05 * hs, 0.16 * hs, 0.05 * hs), "#f6f0e2")
            m.box(jn, (sx * 0.12 * hs * mw, 0.08 * hs, jl * 0.85), (0.04 * hs, 0.1 * hs, 0.04 * hs), "#f6f0e2")
    if P.get("sabers"):
        for sx in (1, -1):
            segment(m, hn, (sx * 0.14 * hs, tipy - 0.1 * hs, tipz - 0.1 * hs), (sx * 0.16 * hs, tipy - 0.75 * hs, tipz - 0.05 * hs), 0.08 * hs, "#f6f0e2")
    if P.get("tusks"):
        tk = P["tusks"]
        tc = P.get("tuskCol", "#f2ead6")
        for sx in (1, -1):
            if tk == "elephant":
                pts = [Vector((sx * 0.2 * hs, tipy - 0.05 * hs + 0.0 * u, 0.6 * hs)) + Vector((sx * 0.08 * u * hs, -0.6 * u * hs + 0.5 * u * u * hs, 0.7 * u * hs))
                       for u in (j / 5 for j in range(6))]
                polyline(m, hn, pts, 0.11 * hs, tc)
            elif tk == "mammoth":
                pts = [Vector((sx * 0.22 * hs, tipy, 0.6 * hs)) + Vector((sx * 0.5 * math.sin(u * 2.2) * hs, -0.7 * math.sin(u * 2.6) * hs + 0.9 * u * u * hs, 0.9 * u * hs))
                       for u in (j / 8 for j in range(9))]
                polyline(m, hn, pts, 0.13 * hs, tc)
            elif tk == "boar":
                segment(m, jn, (sx * 0.16 * hs, 0.05 * hs, jl * 0.8), (sx * 0.28 * hs, 0.35 * hs, jl * 0.85), 0.07 * hs, tc)
            elif tk == "walrus":
                segment(m, hn, (sx * 0.12 * hs, tipy - 0.1 * hs, tipz - 0.05 * hs), (sx * 0.14 * hs, tipy - 1.0 * hs, tipz + 0.05 * hs), 0.09 * hs, tc)
            elif tk == "fang":
                segment(m, hn, (sx * 0.12 * hs, tipy - 0.1 * hs, tipz - 0.1 * hs), (sx * 0.12 * hs, tipy - 0.35 * hs, tipz - 0.08 * hs), 0.05 * hs, tc)
    if P.get("trunk"):
        tn = P["trunk"]
        tcol = P.get("trunkCol")
        prev = hn
        piv = (0, tipy, tipz)
        for j in range(tn):
            nm = f"trunk{j}" + suffix
            m.part(nm, prev, piv, (28 if j else 15, 0, 0))
            r0 = 0.2 * hs * (1 - 0.1 * j) * P.get("trunkW", 1.0)
            ln = 0.3 * hs * P.get("trunkLen", 1.0)
            voxelize(m, nm, [cap((0, 0, 0), (0, 0, ln * 1.1), r0, r0 * 0.9)], v * 0.8,
                     (lambda p, n: tcol) if tcol else (lambda p, n: hsk(p, n) if (int(-p.z / (0.06 * hs)) % 3) else mix(hsk(p, n) if not isinstance(hsk(p, n), tuple) else "#888888", "#000000", 0.12)))
            prev, piv = nm, (0, 0, ln)
        info.setdefault("trunks", []).append((f"trunk{{}}{suffix}", tn))
    if P.get("beak"):  # hipogrifo / grifo: pico ganchudo de águila
        bcol = P.get("beakCol", "#f2c14e")
        voxelize(m, hn, [cap((0, 0.0, 0.45 * hs), (0, -0.08 * hs, 0.95 * hs), 0.26 * hs, 0.14 * hs)], v * 0.7, solid(bcol))
        segment(m, hn, (0, -0.08 * hs, 0.9 * hs), (0, -0.35 * hs, 1.02 * hs), (0.14 * hs, 0.12 * hs), bcol)
    if P.get("bill"):  # ornitorrinco
        bc = P.get("billCol", "#3a3a40")
        m.box(hn, (0, tipy - 0.02 * hs, tipz + 0.25 * hs), (0.55 * hs, 0.1 * hs, 0.6 * hs), bc)
        m.box(hn, (0, tipy - 0.04 * hs, tipz + 0.52 * hs), (0.5 * hs, 0.09 * hs, 0.14 * hs), mix(bc, "#ffffff", 0.1))
    if P.get("starnose"):
        for k in range(11):
            a = k / 11 * TAU
            segment(m, hn, (0, tipy, tipz + 0.05 * hs), (math.cos(a) * 0.2 * hs, tipy + math.sin(a) * 0.2 * hs, tipz + 0.14 * hs), 0.06 * hs, "#ff8aa8")
    if "whiskers" in ex:
        wc = P.get("whiskerCol", "#f6f0e2")
        for sx in (1, -1):
            for k in (-1, 0, 1):
                segment(m, hn, (sx * 0.15 * hs, tipy - 0.02 * hs + k * 0.04 * hs, tipz - 0.05 * hs),
                        (sx * 0.65 * hs, tipy + k * 0.12 * hs, tipz - 0.15 * hs), (0.02 * hs + 0.01, 0.02 * hs + 0.01), wc)
    if "beard" in ex:
        bc = P.get("beardCol", "#e8e0d0")
        voxelize(m, jn, [cap((0, -0.05 * hs, jl * 0.6), (0, -0.45 * hs, jl * 0.4), 0.1 * hs, 0.05 * hs, 0.15, 4)], v * 0.7, solid(bc))
    if "frill" in ex:
        fc = P.get("frillCol", ctx.acc)
        for k in range(11):
            a = math.radians(-100 + k * 20)
            d = Vector((math.sin(a), math.cos(a) * 0.9 + 0.2, -0.25))
            segment(m, hn, (0, 0.1 * hs, -0.1 * hs), Vector((0, 0.1 * hs, -0.1 * hs)) + d * 0.9 * hs, (0.24 * hs, 0.06 * hs), fc if k % 2 else mix(fc, "#000000", 0.15))
    if "cheekpouch" in ex:
        for sx in (1, -1):
            voxelize(m, hn, [ell((sx * 0.4 * hs, -0.15 * hs, 0.25 * hs), (0.3 * hs, 0.26 * hs, 0.28 * hs))], v * 0.8, hsk)
    if "gills" in ex:  # ajolote
        gc = P.get("gillCol", "#ff6a9a")
        for sx in (1, -1):
            for k in range(3):
                a = Vector((sx * 0.4 * hs, (0.15 - 0.15 * k) * hs, -0.1 * hs))
                b = a + Vector((sx * 0.45 * hs, (0.35 - 0.25 * k) * hs, -0.25 * hs))
                segment(m, hn, a, b, 0.08 * hs, gc)
                for j in range(4):
                    pp = a.lerp(b, 0.25 + j * 0.22)
                    m.box(hn, pp + Vector((0, 0.06 * hs, 0)), (0.06 * hs, 0.14 * hs, 0.06 * hs), mix(gc, "#ffffff", 0.2))
    hk = P.get("horns")
    if hk:
        horns(m, hn, hk, hs, P.get("hornCol", "#e8dcc0"), ctx, size=P.get("hornSize", 1.0), tip=P.get("hornTip"))
    ears(m, hn, P.get("ear", "pointy"), hs, hsk, P.get("earIn", "#e8a0a8"), ctx, size=P.get("earS", 1.0), tilt=P.get("earTilt", -10),
         x=P.get("earX", 0.3), y=P.get("earY", 0.38), tuft=P.get("earTuft"), v=v)
    if suffix:
        for side in ("L", "R"):
            if f"ear_{side}" in m.parts and m.parts[f"ear_{side}"].parent == hn:
                m.parts[f"ear_{side}{suffix}"] = m.parts.pop(f"ear_{side}")
                m.parts[f"ear_{side}{suffix}"].name = f"ear_{side}{suffix}"


# ----------------------------------------------------------------------------- lagartos (patas abiertas)
def lizard(m, P, ctx):
    S, v = ctx.S * P.get("size", 1.0), ctx.v * P.get("size", 1.0) ** 0.5
    L, W, H = P.get("L", 1.6) * S, P.get("W", 0.8) * S, P.get("H", 0.55) * S
    hs = P.get("hs", 0.75) * S
    sn = P.get("sn", 0.35) * S
    bsk = _sk(ctx, P.get("skin", "#6a9a3a"))
    hsk = _sk(ctx, P.get("hskin"), bsk)
    lsk = _sk(ctx, P.get("lskin"), bsk)
    ex = set(P.get("ex", ()))
    leg = P.get("leg", 0.5) * S
    m.part("body", "root", (0, leg * 0.75 + H * 0.45, 0))
    voxelize(m, "body", [ell((0, 0, 0.12 * L), (0.5 * W, 0.5 * H, 0.32 * L), 0.04, 3), ell((0, 0.02 * H, -0.2 * L), (0.46 * W, 0.46 * H, 0.3 * L), 0.04, 3),
                         cap((0, 0.05 * H, 0.3 * L), (0, 0.1 * H, 0.5 * L), 0.36 * W, 0.3 * W)], v, bsk)
    m.part("head", "body", (0, 0.12 * H, 0.52 * L))
    flat = P.get("flat", 0.75)
    skull = ell((0, 0.05 * hs, 0.15 * hs), (0.45 * hs, 0.38 * hs * flat, 0.5 * hs))
    hp = [skull, cap((0, -0.02 * hs, 0.4 * hs), (0, -0.06 * hs, 0.4 * hs + sn), 0.32 * hs * flat, 0.2 * hs * flat * P.get("snW", 1.0))]
    hp += P.get("head_extra", [])
    voxelize(m, "head", hp, v * 0.85, hsk)
    E = P.get("eye", {})
    iris = ctx.en if ctx.L >= 3 else E.get("col", "#e8b020")
    if "turret" in ex:  # camaleón: ojos cónicos
        for sx in (1, -1):
            voxelize(m, "head", [ell((sx * 0.36 * hs, 0.15 * hs, 0.2 * hs), (0.17 * hs, 0.17 * hs, 0.17 * hs))], v * 0.7, hsk)
            m.box("head", (sx * 0.52 * hs, 0.15 * hs, 0.24 * hs), (0.06, 0.1 * hs, 0.1 * hs), "#101010")
            m.box("head", (sx * 0.54 * hs, 0.17 * hs, 0.25 * hs), (0.04, 0.04 * hs, 0.04 * hs), iris, emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
    else:
        sp_ = surface_point(skull, 0.3 * hs, 0.16 * hs * flat)
        eyes(m, "head", (0, sp_.y + 0.04 * hs, sp_.z - 0.05 * hs), 0.32 * hs, hs * 0.22 * E.get("size", 1.0), iris, glow=ctx.eye_glow, slit=E.get("slit", True),
             yaw=55, style=E.get("style", "round"))
    m.part("jaw", "head", (0, -0.15 * hs, 0.3 * hs))
    voxelize(m, "jaw", [cap((0, 0, 0), (0, -0.02 * hs, sn + 0.1 * hs), 0.26 * hs * flat, 0.16 * hs * flat * P.get("snW", 1.0))], v * 0.8,
             lambda p, n: "#c85a6a" if n.y > 0.6 else hsk(p, n))
    if P.get("teeth"):
        for k in range(6):
            for sx in (1, -1):
                m.box("head", (sx * 0.17 * hs * P.get("snW", 1.0), -0.13 * hs, 0.45 * hs + k * sn / 6), (0.04 * hs, 0.1 * hs, 0.04 * hs), "#f6f0e2")
    if "tongue" in ex:
        tcol = P.get("tongueCol", "#3a5aff")
        m.box("jaw", (0, 0.05 * hs, sn + 0.25 * hs), (0.15 * hs, 0.05 * hs, 0.3 * hs), tcol)
    if "frill" in ex:
        fc = P.get("frillCol", "#e8762a")
        for k in range(13):
            a = math.radians(-120 + k * 20)
            d = Vector((math.sin(a), math.cos(a), -0.15))
            segment(m, "head", (0, 0, 0.05 * hs), Vector((0, 0, 0.05 * hs)) + d * 1.0 * hs, (0.26 * hs, 0.05 * hs), fc if k % 2 else mix(fc, "#a01010", 0.4))
    if "beard" in ex:
        for k in range(9):
            a = math.radians(-80 + k * 20)
            p0 = Vector((math.sin(a) * 0.38 * hs, -0.2 * hs + math.cos(a) * 0.05 * hs, 0.2 * hs - abs(math.sin(a)) * 0.1 * hs))
            crystal(m, "head", p0, 0.08 * hs, 0.25 * hs, P.get("beardCol", "#4a3a20"), rot=(80 + k * 2, 0, math.degrees(a)))
    if "dewlap" in ex:
        voxelize(m, "head", [ell((0, -0.35 * hs, 0.15 * hs), (0.06 * hs, 0.3 * hs, 0.3 * hs))], v * 0.7, solid(P.get("dewCol", "#e8a030")))
    if "casque" in ex:
        voxelize(m, "head", [ell((0, 0.35 * hs, -0.1 * hs), (0.18 * hs, 0.45 * hs, 0.35 * hs))], v * 0.8, hsk)
    if "headhorns" in ex:  # lagarto cornudo / diablo espinoso
        for k, (dx, dy) in enumerate(((0.25, 0.25), (-0.25, 0.25), (0.4, 0.1), (-0.4, 0.1), (0.12, 0.32), (-0.12, 0.32))):
            crystal(m, "head", (dx * hs, dy * hs, -0.1 * hs), 0.1 * hs, 0.38 * hs, P.get("hornCol", "#c8a070"), rot=(-55, 0, -dx * 40))
    if "gills" in ex:
        gc = P.get("gillCol", "#ff6a9a")
        for sx in (1, -1):
            for k in range(3):
                a = Vector((sx * 0.38 * hs, (0.12 - 0.13 * k) * hs, -0.05 * hs))
                b = a + Vector((sx * 0.4 * hs, (0.32 - 0.24 * k) * hs, -0.25 * hs))
                segment(m, "head", a, b, 0.07 * hs, gc)
                for j in range(4):
                    m.box("head", a.lerp(b, 0.25 + j * 0.22) + Vector((0, 0.05 * hs, 0)), (0.05 * hs, 0.13 * hs, 0.05 * hs), mix(gc, "#ffffff", 0.25))
    if "crest" in ex or "sailback" in ex:  # cresta de púas (iguana) o vela (basilisco)
        cc = P.get("crestCol", mix(P.get("skin", {}).get("base", "#6a9a3a") if isinstance(P.get("skin"), dict) else "#6a9a3a", "#000000", 0.2))
        n_ = 14
        for j in range(n_):
            k = j / (n_ - 1)
            z = (0.5 - 1.0 * k) * L
            h_ = (0.12 + (0.5 if "sailback" in ex else 0.18) * math.sin(k * math.pi)) * S
            if "sailback" in ex:
                m.box("body", (0, 0.45 * H + h_ / 2, z), (0.04 * S, h_, L / n_ + 0.02), cc if j % 2 else mix(cc, "#ffffff", 0.15))
            else:
                crystal(m, "body", (0, 0.45 * H + h_ * 0.35, z), 0.09 * S, h_, cc, rot=(-20, 0, 0))
    if "scutes" in ex:  # cocodrilo: filas de escudos
        sc = P.get("scuteCol", mix("#3a4a2a", "#000000", 0.2))
        for j in range(12):
            z = (0.45 - 0.9 * j / 11) * L
            for sx in (-1, 0, 1):
                m.box("body", (sx * 0.18 * W, 0.48 * H, z), (0.1 * S, 0.08 * S, 0.1 * S), sc, r=(0, 45, 0))
    if "spines" in ex:  # tuátara / lagarto cornudo: púas por el cuerpo
        for j in range(30):
            a = j * 2.39996
            z = (0.45 - 0.9 * ((j * 0.618) % 1)) * L
            x = math.cos(a) * 0.45 * W
            y = abs(math.sin(a)) * 0.45 * H
            crystal(m, "body", (x, y, z), 0.06 * S, 0.18 * S, P.get("spineCol", "#c8a070"), rot=(-30, 0, -math.degrees(math.atan2(x, y + 0.01))))
    if "ribwings" in ex:  # dragón volador: alas de costillas
        wc = P.get("wingCol", "#e8702a")
        for side, sx in (("L", 1), ("R", -1)):
            w = f"wing_{side}"
            m.part(w, "body", (sx * 0.45 * W, 0.2 * H, 0.0))
            for k in range(6):
                a = math.radians(-40 + k * 16)
                d = Vector((sx * math.cos(a), 0.05, math.sin(a))) * 0.75 * S
                segment(m, w, (0, 0, 0), d, (0.05 * S, 0.04 * S), mix(wc, "#000000", 0.35))
                if k < 5:
                    a2 = math.radians(-40 + (k + 1) * 16)
                    d2 = Vector((sx * math.cos(a2), 0.05, math.sin(a2))) * 0.75 * S
                    for j in range(4):
                        u = (j + 1) / 5
                        segment(m, w, d * u, d2 * u, (0.17 * S, 0.03 * S), wc if (k + j) % 2 else mix(wc, "#ffd23a", 0.3))
    # patas abiertas
    toe = P.get("toe")
    for name, sx, sz in (("FL", 1, 1), ("FR", -1, 1), ("BL", 1, -1), ("BR", -1, -1)):
        up, lo_ = f"leg_{name}", f"low_{name}"
        m.part(up, "body", (sx * 0.4 * W, -0.1 * H, (0.3 if sz > 0 else -0.25) * L))
        a = Vector((sx * leg * 0.7, leg * 0.05, sz * 0.1 * leg))
        voxelize(m, up, [cap((0, 0, 0), a, 0.13 * S * P.get("legW", 1), 0.11 * S * P.get("legW", 1))], v * 0.85, lsk)
        m.part(lo_, up, tuple(a))
        voxelize(m, lo_, [cap((0, 0, 0), (sx * 0.05 * leg, -leg * 0.75, sz * 0.05 * leg), 0.11 * S * P.get("legW", 1), 0.09 * S * P.get("legW", 1))],
                 v * 0.8, lsk)
        for k in (-1, 0, 1):  # dedos
            d = Vector((sx * 0.1 + k * 0.12, 0, 0.18 * sz + 0.08)).normalized()
            pp = Vector((sx * 0.05 * leg, -leg * 0.75, sz * 0.05 * leg))
            segment(m, lo_, pp, pp + d * 0.2 * S, 0.05 * S, P.get("toeCol", lsk(pp, Vector((0, 1, 0))) if not isinstance(lsk(pp, Vector((0, 1, 0))), tuple) else "#555"))
            if toe == "pads":
                m.box(lo_, pp + d * 0.22 * S, (0.09 * S, 0.04 * S, 0.09 * S), P.get("padCol", "#e8d8a0"))
    # cola
    tk = P.get("tail", "thick")
    if "curltail" in ex:  # camaleón: cola enrollada
        m.part("tail0", "body", (0, 0.05 * H, -0.48 * L))
        pts = []
        for j in range(16):
            a = j / 15 * 1.7 * math.pi
            r = 0.35 * S * (1 - j / 22)
            pts.append(Vector((0, -r * math.sin(a) + 0.0, -r * (1 - math.cos(a)) * 0.0 - 0.5 * S * min(1, j / 5) - r * math.sin(min(a, math.pi / 2)) * 0)))
        pts = [Vector((0, -0.15 * S - 0.3 * S * math.sin(a) * (1 - j / 25), -0.35 * S - 0.3 * S * math.cos(a) * (1 - j / 25) + 0.3 * S))
               for j, a in ((j, j / 15 * 1.8 * math.pi) for j in range(16))]
        pts.insert(0, Vector((0, 0, 0)))
        for j in range(len(pts) - 1):
            r = 0.14 * S * (1 - j / (len(pts) + 2))
            voxelize(m, "tail0", [cap(pts[j], pts[j + 1], r, r * 0.95)], v * 0.8, bsk)
        n_t = 1
    else:
        n_t = tail(m, "body", (0, 0.0, -0.48 * L), tk, ctx, n=P.get("tailN", 7), seg=P.get("tailSeg", 0.3), w=P.get("tailW", 0.2), lift=P.get("tailLift", 8),
                   curve=P.get("tailCurve", 3), sk=bsk, v=v, tuft=P.get("ringCol"))
    if "tailfin" in ex:  # tritón: cresta en la cola
        for i in range(n_t):
            m.box(f"tail{i}", (0, 0.12 * S, -0.15 * S), (0.03 * S, 0.18 * S, 0.32 * S), P.get("finCol", mix("#6a9a3a", "#ffffff", 0.2)))
    return dict(L=L, W=W, H=H, hs=hs, S=S, v=v, body="body", head="head", tail_n=n_t, heads=["head"], tails=[("tail", n_t)])


# ----------------------------------------------------------------------------- terópodos (dinosaurios y criaturas bípedas con cola)
def theropod(m, P, ctx):
    S, v = ctx.S * P.get("size", 1.0), ctx.v * P.get("size", 1.0) ** 0.5
    L, W, H = P.get("L", 1.6) * S, P.get("W", 0.85) * S, P.get("H", 0.9) * S
    hs, sn = P.get("hs", 0.95) * S, P.get("sn", 0.5) * S
    leg = P.get("leg", 1.1) * S
    bsk = _sk(ctx, P.get("skin", "#5a7a3a"))
    hsk = _sk(ctx, P.get("hskin"), bsk)
    ex = set(P.get("ex", ()))
    tilt = P.get("tilt", -12)
    m.part("body", "root", (0, leg * 0.92 + H * 0.35, 0), (tilt, 0, 0))
    voxelize(m, "body", [ell((0, 0, 0.05 * L), (0.5 * W, 0.5 * H, 0.42 * L), 0.04, 3), ell((0, 0.05 * H, 0.35 * L), (0.42 * W, 0.45 * H, 0.25 * L), 0.04, 3),
                         cap((0, 0.15 * H, 0.4 * L), (0, 0.55 * H + P.get("neck", 0.2) * S, 0.62 * L), 0.3 * W, 0.24 * W)], v, bsk)
    m.part("head", "body", (0, 0.6 * H + P.get("neck", 0.2) * S, 0.66 * L), (-tilt * 0.8, 0, 0))
    skull = ell((0, 0.05 * hs, 0.12 * hs), (0.42 * hs, 0.42 * hs, 0.5 * hs))
    voxelize(m, "head", [skull, cap((0, 0.0, 0.35 * hs), (0, -0.05 * hs, 0.35 * hs + sn), 0.34 * hs, 0.26 * hs)] + P.get("head_extra", []), v * 0.85, hsk)
    E = P.get("eye", {})
    sp_ = surface_point(skull, 0.3 * hs, 0.2 * hs)
    eyes(m, "head", (0, sp_.y, sp_.z - 0.05 * hs), 0.3 * hs, hs * 0.2, ctx.en if ctx.L >= 3 else E.get("col", "#e8b020"), glow=ctx.eye_glow, slit=True, yaw=45,
         lid=mix(P.get("browCol", "#3a4a2a"), "#000000", 0.1))
    m.part("jaw", "head", (0, -0.2 * hs, 0.25 * hs))
    voxelize(m, "jaw", [cap((0, 0, 0), (0, -0.04 * hs, sn + 0.12 * hs), 0.28 * hs, 0.2 * hs)], v * 0.8, lambda p, n: "#8a2a3a" if n.y > 0.6 else hsk(p, n))
    for k in range(7):
        for sx in (1, -1):
            m.box("head", (sx * 0.22 * hs, -0.25 * hs, 0.4 * hs + k * sn / 7), (0.05 * hs, 0.12 * hs, 0.05 * hs), "#f6f0e2")
    if "crest" in ex:  # parasaurolofo
        segment(m, "head", (0, 0.35 * hs, 0.2 * hs), (0, 0.75 * hs, -0.9 * hs), (0.2 * hs, 0.3 * hs), P.get("crestCol", "#c8603a"))
    if "dome" in ex:  # paquicefalosaurio
        voxelize(m, "head", [ell((0, 0.38 * hs, 0.0), (0.42 * hs, 0.32 * hs, 0.42 * hs))], v * 0.8, solid(P.get("domeCol", "#c8a070")))
        for k in range(10):
            a = k / 10 * TAU
            crystal(m, "head", (math.cos(a) * 0.4 * hs, 0.25 * hs, math.sin(a) * 0.4 * hs - 0.05 * hs), 0.06 * hs, 0.18 * hs, "#e8d8b0",
                    rot=(math.degrees(math.sin(a)) * 50, 0, -math.degrees(math.cos(a)) * 50))
    if "sail" in ex:
        for j in range(12):
            k = j / 11
            z = (0.45 - 0.8 * k) * L
            h_ = (0.2 + 1.1 * math.sin(k * math.pi)) * S
            segment(m, "body", (0, 0.4 * H, z), (0, 0.4 * H + h_, z - 0.05 * S), 0.05 * S, "#5a2a1a")
            m.box("body", (0, 0.4 * H + h_ * 0.5, z - 0.03 * S), (0.04 * S, h_, 0.8 * L / 11 + 0.02), P.get("sailCol", "#c84a3a") if j % 2 else mix(P.get("sailCol", "#c84a3a"), "#ffffff", 0.15))
    if "feathers" in ex:  # raptor emplumado
        fc = P.get("featherCol", ctx.acc)
        for j in range(10):
            z = (0.4 - 0.8 * j / 9) * L
            m.box("body", (0, 0.48 * H, z), (0.08 * S, 0.22 * S, 0.3 * S), fc, r=(-35, 0, 0))
    for side, sx in (("L", 1), ("R", -1)):  # brazos cortos
        a = f"arm_{side}"
        m.part(a, "body", (sx * 0.38 * W, 0.0, 0.48 * L))
        ln = P.get("arm", 0.35) * S
        voxelize(m, a, [cap((0, 0, 0), (sx * 0.05 * S, -ln, 0.15 * ln), 0.09 * S, 0.06 * S)], v * 0.8, bsk)
        for k in (-1, 1):
            segment(m, a, (sx * 0.05 * S, -ln, 0.15 * ln), (sx * 0.05 * S + k * 0.03 * S, -ln - 0.1 * S, 0.25 * ln), 0.04 * S, "#f6f0e2")
        if "feathers" in ex:
            for k in range(4):
                m.box(a, (sx * 0.08 * S, -ln * (0.3 + 0.2 * k), -0.05 * S), (0.04 * S, 0.12 * S, 0.3 * S), P.get("featherCol", ctx.acc))
        lg, lo_ = f"leg_{side}", f"low_{side}"
        m.part(lg, "body", (sx * 0.4 * W, -0.2 * H, -0.05 * L), (-tilt, 0, 0))
        voxelize(m, lg, [ell((0, -0.15 * leg, 0.05 * leg), (0.28 * W, 0.4 * leg, 0.32 * W), 0.04, 3), cap((0, -0.2 * leg, 0.05 * leg), (0, -0.5 * leg, -0.08 * leg), 0.2 * W, 0.14 * W)],
                 v, bsk)
        m.part(lo_, lg, (0, -0.5 * leg, -0.08 * leg))
        voxelize(m, lo_, [cap((0, 0, 0), (0, -0.45 * leg, -0.08 * leg), 0.12 * W, 0.1 * W)], v * 0.85, bsk)
        for k in (-1, 0, 1):
            segment(m, lo_, (0, -0.45 * leg, -0.08 * leg), (k * 0.14 * S, -0.48 * leg, 0.2 * S), 0.08 * S, P.get("clawCol", "#3a3020"))
        if "sickle" in ex:
            segment(m, lo_, (0, -0.4 * leg, -0.02 * leg), (sx * 0.02 * S, -0.3 * leg, 0.2 * S), 0.06 * S, "#f6f0e2")
    if P.get("wings"):  # wyvern
        wings(m, "body", P["wings"], ctx, (0.4 * W, 0.4 * H, 0.3 * L), span=P.get("wingSpan", 0.9), cols=P.get("wingCols"), prefix="qwing")
    n_t = tail(m, "body", (0, 0.05 * H, -0.45 * L), "thick", ctx, n=P.get("tailN", 7), seg=P.get("tailSeg", 0.32), w=P.get("tailW", 0.24), lift=-tilt + 4, curve=-2,
               sk=bsk, v=v)
    return dict(L=L, W=W, H=H, hs=hs, S=S, v=v, body="body", head="head", tail_n=n_t, heads=["head"], tails=[("tail", n_t)], biped=True)
