"""Aves, peces (y mamíferos marinos), insectos/arácnidos y crustáceos."""

import math

from mathutils import Vector

from eggs import _wing
from eggs_themes import membrane_wing, vnoise
from pk_common import TAU, eyes, mix, shades, skin, solid
from pk_quad import _sk
from sculpt import cap, ell, surface_point, voxelize
from voxel import crystal, polyline, quat, ring, segment


# ============================================================================= AVES
def _beak(m, part, kind, hr, ln, col, col2, S):
    """Pico superior en la cabeza; devuelve el punto de la punta. El inferior va en la parte 'jaw'."""
    z0 = 0.82 * hr
    if kind == "cone":
        voxelize(m, part, [cap((0, -0.08 * hr, z0), (0, -0.14 * hr, z0 + ln), 0.3 * hr, 0.04 * hr)], 0.05 * S + 0.02, solid(col))
    elif kind == "tiny":
        voxelize(m, part, [cap((0, -0.1 * hr, z0), (0, -0.16 * hr, z0 + ln * 0.6), 0.18 * hr, 0.03 * hr)], 0.04 * S + 0.02, solid(col))
    elif kind in ("long", "dagger"):
        segment(m, part, (0, -0.08 * hr, z0 - 0.05 * hr), (0, -0.12 * hr, z0 + ln), (0.16 * hr, 0.12 * hr), col)
        segment(m, part, (0, -0.1 * hr, z0 + ln * 0.6), (0, -0.13 * hr, z0 + ln), (0.08 * hr, 0.07 * hr), col2 or mix(col, "#000000", 0.3))
    elif kind == "curved":  # ibis
        pts = [Vector((0, -0.1 * hr - 0.55 * ln * u * u, z0 + ln * math.sin(u * 1.2) / math.sin(1.2))) for u in (j / 6 for j in range(7))]
        polyline(m, part, pts, 0.12 * hr, col)
    elif kind in ("hook", "parrot"):
        deep = 1.5 if kind == "parrot" else 1.0
        voxelize(m, part, [cap((0, -0.02 * hr, z0 - 0.05 * hr), (0, -0.1 * hr, z0 + ln * 0.7), 0.3 * hr * deep, 0.18 * hr * deep)], 0.04 * S + 0.02, solid(col))
        segment(m, part, (0, -0.1 * hr, z0 + ln * 0.65), (0, -0.1 * hr - ln * 0.5, z0 + ln * 0.8), (0.14 * hr * deep, 0.12 * hr), col)
    elif kind == "duck":
        m.box(part, (0, -0.15 * hr, z0 + ln * 0.5), (0.5 * hr, 0.14 * hr, ln), col)
        m.box(part, (0, -0.14 * hr, z0 + ln * 0.95), (0.42 * hr, 0.13 * hr, 0.12 * hr), col2 or mix(col, "#000000", 0.2))
    elif kind == "toucan":
        voxelize(m, part, [ell((0, -0.05 * hr, z0 + ln * 0.5), (0.28 * hr, 0.42 * hr, ln * 0.55))], 0.05 * S + 0.02,
                 lambda p, n: col2 if p.z > z0 + ln * 0.75 else (mix(col, "#ffffff", 0.2) if p.y > 0.15 * hr else col))
    elif kind == "pelican":
        segment(m, part, (0, -0.05 * hr, z0), (0, -0.1 * hr, z0 + ln), (0.3 * hr, 0.12 * hr), col)
        voxelize(m, part, [ell((0, -0.4 * hr, z0 + ln * 0.45), (0.24 * hr, 0.3 * hr, ln * 0.45))], 0.05 * S + 0.02, solid(col2 or mix(col, "#ff8a6a", 0.4)))
    elif kind == "spoon":
        segment(m, part, (0, -0.08 * hr, z0), (0, -0.1 * hr, z0 + ln), (0.12 * hr, 0.08 * hr), col)
        m.box(part, (0, -0.1 * hr, z0 + ln), (0.38 * hr, 0.06 * hr, 0.3 * hr), col)
    elif kind == "hornbill":
        voxelize(m, part, [cap((0, -0.05 * hr, z0), (0, -0.4 * hr, z0 + ln), 0.3 * hr, 0.06 * hr)], 0.05 * S + 0.02, solid(col))
        voxelize(m, part, [ell((0, 0.3 * hr, z0 + ln * 0.25), (0.18 * hr, 0.2 * hr, ln * 0.4))], 0.05 * S + 0.02, solid(col2 or "#f2c14e"))
    elif kind == "flamingo":
        pts = [Vector((0, -0.1 * hr - 0.6 * ln * max(0, u - 0.45) ** 1.2, z0 + ln * min(u, 0.75))) for u in (j / 6 for j in range(7))]
        polyline(m, part, pts, 0.18 * hr, col)
        segment(m, part, pts[-3], pts[-1], 0.16 * hr, col2 or "#1a1a1a")


def _crest(m, part, kind, hr, col, col2, S):
    if kind == "tuft":  # cardenal, arrendajo
        for k in range(4):
            segment(m, part, (0, 0.4 * hr, (0.15 - 0.15 * k) * hr), (0, (0.95 - 0.08 * k) * hr, (-0.15 - 0.2 * k) * hr), (0.14 * hr, 0.08 * hr), col if k % 2 else col2 or col)
    elif kind == "fan":  # cacatúa
        for k in range(7):
            a = math.radians(-40 + k * 18)
            segment(m, part, (0, 0.35 * hr, 0.1 * hr), (0, 0.35 * hr + math.cos(a) * 0.9 * hr, 0.1 * hr - math.sin(a) * 0.9 * hr - 0.2 * hr),
                    (0.12 * hr, 0.07 * hr), col2 if k % 2 else col)
    elif kind == "comb":  # gallo
        for k in range(5):
            m.box(part, (0, (0.5 + 0.12 * math.sin(k * 1.4)) * hr, (0.45 - 0.2 * k) * hr), (0.08 * hr, 0.35 * hr, 0.18 * hr), col)
        m.box(part, (0, -0.55 * hr, 0.7 * hr), (0.08 * hr, 0.35 * hr, 0.15 * hr), col)  # barbilla
    elif kind == "crown":  # pavo real / grulla coronada: plumas con punta
        for k in range(7):
            a = math.radians(-36 + k * 12)
            tip = Vector((math.sin(a) * 0.35 * hr, 1.05 * hr, -0.1 * hr))
            segment(m, part, (0, 0.4 * hr, 0), tip, 0.04 * hr + 0.01, col)
            m.box(part, tip, (0.14 * hr, 0.14 * hr, 0.1 * hr), col2 or col)
    elif kind == "spray":  # grulla coronada: abanico dorado
        for k in range(14):
            a = k / 14 * math.pi
            tip = Vector((math.cos(a) * 0.6 * hr, 0.9 * hr + math.sin(a) * 0.4 * hr, -0.1 * hr))
            segment(m, part, (0, 0.4 * hr, 0), tip, 0.04 * hr + 0.01, col if k % 2 else col2 or col)
    elif kind == "mohawk":  # pájaro secretario: plumas negras hacia atrás
        for k in range(8):
            sx = (k % 2) * 2 - 1
            segment(m, part, (sx * 0.15 * hr, 0.2 * hr, -0.3 * hr), (sx * 0.3 * hr, (0.1 + 0.08 * k) * hr, -1.1 * hr), (0.08 * hr, 0.08 * hr), col)
            m.box(part, (sx * 0.3 * hr, (0.1 + 0.08 * k) * hr, -1.1 * hr), (0.12 * hr, 0.12 * hr, 0.18 * hr), col2 or col)
    elif kind == "plume":  # codorniz
        pts = [Vector((0, 0.4 * hr + 0.5 * hr * math.sin(u * 2.2), 0.25 * hr + 0.4 * hr * math.cos(u * 2.2) - 0.1 * hr)) for u in (j / 5 for j in range(6))]
        polyline(m, part, pts, 0.1 * hr, col)
    elif kind == "horns":  # búho: penachos
        for sx in (1, -1):
            segment(m, part, (sx * 0.3 * hr, 0.55 * hr, 0), (sx * 0.5 * hr, 1.0 * hr, -0.1 * hr), (0.16 * hr, 0.1 * hr), col)
    elif kind == "casque":
        voxelize(m, part, [ell((0, 0.55 * hr, 0.05 * hr), (0.18 * hr, 0.38 * hr, 0.3 * hr))], 0.05 * S + 0.02, solid(col))
    elif kind == "redcap":
        m.box(part, (0, 0.45 * hr, 0.15 * hr), (0.4 * hr, 0.1 * hr, 0.4 * hr), col)
    elif kind == "ruff":  # cuello de plumas (buitre, cóndor)
        voxelize(m, part, [ell((0, -0.75 * hr, -0.2 * hr), (0.85 * hr, 0.35 * hr, 0.7 * hr), 0.25, 4 / S)], 0.06 * S + 0.02, solid(col))


def _bird_tail(m, part, kind, S, cols, ctx):
    c0, c1 = cols[0], cols[1] if len(cols) > 1 else cols[0]
    if kind == "short":
        for k in range(5):
            a = math.radians(-30 + k * 15)
            q = quat((15, math.degrees(a) * 0.6, 0))
            m.box(part, q @ Vector((0, 0, -0.25 * S)), (0.13 * S, 0.05 * S, 0.5 * S), c0 if k % 2 else c1, r=q)
    elif kind == "upright":
        for k in range(4):
            q = quat((-60 + k * 4, (k - 1.5) * 8, 0))
            m.box(part, q @ Vector((0, 0, -0.3 * S)), (0.12 * S, 0.05 * S, 0.6 * S), c0 if k % 2 else c1, r=q)
    elif kind == "fork":
        for sx in (1, -1):
            q = quat((10, sx * 18, 0))
            m.box(part, q @ Vector((0, 0, -0.45 * S)), (0.1 * S, 0.04 * S, 0.9 * S), c0, r=q)
        m.box(part, (0, 0, -0.2 * S), (0.3 * S, 0.05 * S, 0.4 * S), c1)
    elif kind == "long":  # faisán, quetzal
        for k in range(3):
            q = quat((12 - k * 4, (k - 1) * 6, 0))
            ln = (2.0 - 0.4 * abs(k - 1)) * S
            for j in range(8):
                m.box(part, q @ Vector((0, 0, -(j + 0.5) * ln / 8)), (0.14 * S * (1 - j / 12), 0.04 * S, ln / 8 + 0.02),
                      c0 if (j + k) % 2 else c1, r=q)
    elif kind == "streamers":  # quetzal: dos plumas larguísimas
        for sx in (1, -1):
            pts = [Vector((sx * 0.05 * S, -0.3 * S * u * u, -2.6 * S * u)) for u in (j / 7 for j in range(8))]
            polyline(m, part, pts, (0.12 * S, 0.04 * S), c0)
        m.box(part, (0, 0, -0.25 * S), (0.3 * S, 0.05 * S, 0.5 * S), c1)
    elif kind == "fan":  # pavo real: abanico con ocelos
        n = 21
        for k in range(n):
            a = math.radians(-80 + k * 160 / (n - 1))
            d = Vector((math.sin(a), math.cos(a) * 0.95 + 0.15, -0.35)).normalized()
            ln = 2.0 * S
            for j in range(7):
                p = d * (0.25 * S + ln * (j + 0.5) / 7)
                m.box(part, p, (0.16 * S * (0.6 + j / 10), 0.05 * S, ln / 7 + 0.03), c0 if j < 6 else c1, r=Vector((0, 0, 1)).rotation_difference(d))
            tip = d * (0.25 * S + ln * 0.92)
            m.box(part, tip, (0.3 * S, 0.3 * S, 0.06 * S), cols[2] if len(cols) > 2 else c1, r=Vector((0, 0, 1)).rotation_difference(d),
                  emit=0.8 if ctx.L >= 3 else 0, tag="glow" if ctx.L >= 3 else None)
            m.box(part, tip + d * 0.02, (0.14 * S, 0.14 * S, 0.06 * S), "#1a2a5a", r=Vector((0, 0, 1)).rotation_difference(d))
    elif kind == "cock":  # gallo: plumas en hoz
        for k in range(5):
            pts = [Vector(((k - 2) * 0.06 * S, 0.9 * S * math.sin(u * 2.4) * (1 - k * 0.08), -0.25 * S - 0.75 * S * u)) for u in (j / 6 for j in range(7))]
            polyline(m, part, pts, (0.14 * S, 0.05 * S), c0 if k % 2 else c1)
    elif kind == "lyre":  # ave lira
        for sx in (1, -1):
            pts = [Vector((sx * (0.15 + 0.5 * math.sin(u * 3.0)) * S, 1.8 * S * u, -0.3 * S - 0.4 * S * math.sin(u * 2))) for u in (j / 9 for j in range(10))]
            polyline(m, part, pts, (0.16 * S, 0.05 * S), c0)
        for k in range(9):
            a = math.radians(-30 + k * 7.5)
            segment(m, part, (0, 0, -0.2 * S), (math.sin(a) * 0.8 * S, 1.6 * S, -0.3 * S), 0.03 * S + 0.01, c1)
    elif kind == "stiff":
        m.box(part, (0, -0.2 * S, -0.3 * S), (0.24 * S, 0.06 * S, 0.6 * S), c0, r=(40, 0, 0))


def bird(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    body_c = C.get("body", "#8a6a4a")
    bw, bh, bl = P.get("bw", 0.5) * S, P.get("bh", 0.55) * S, P.get("bl", 0.7) * S
    leg = P.get("leg", 0.45) * S
    bsk = _sk(ctx, P.get("skin") or dict(base=body_c, belly=C.get("belly"), pat=P.get("pat"), pc=C.get("pc"), ps=P.get("ps", 1.0), belly_k=-0.2))
    hsk = _sk(ctx, P.get("hskin") or dict(base=C.get("head", body_c)))
    lean = P.get("lean", -10)
    gait = P.get("gait", "stand")
    m.part("body", "root", (0, leg + bh * 0.85, 0), (lean, 0, 0))
    prims = [ell((0, 0, 0), (bw, bh, bl), P.get("fluff", 0.05), 3)]
    if P.get("chest", 0):
        prims.append(ell((0, 0.15 * bh, 0.45 * bl), (bw * 0.92, bh * 0.75, bl * 0.55), P.get("fluff", 0.05), 3))
    voxelize(m, "body", prims, v, bsk)
    info = dict(S=S, v=v, body="body", head="head", hover=P.get("hover", 0), tails=[], heads=["head"])
    # cuello y cabeza
    hr = P.get("hr", 0.36) * S
    info["hs"] = hr * 1.4
    neck = P.get("neck", 0.0) * S
    base = Vector((0, 0.55 * bh, 0.65 * bl))
    parent, piv = "body", base
    if neck > 0:
        dirs = P.get("neckDirs", [(0, 1, 0.3), (0, 1, 0.1), (0, 0.8, 0.4)])
        ncol = C.get("neck", C.get("head", body_c))
        nsk = _sk(ctx, dict(base=ncol))
        for j, d in enumerate(dirs):
            nm = f"neck{j}"
            m.part(nm, parent, tuple(piv), (-lean if j == 0 else 0, 0, 0))
            d = Vector(d).normalized() * neck / len(dirs)
            r0 = P.get("neckR", 0.16) * S * (1 - 0.15 * j)
            voxelize(m, nm, [cap((0, 0, 0), tuple(d * 1.08), r0, r0 * 0.9)], v * 0.85, nsk)
            parent, piv = nm, d
        m.part("head", parent, tuple(piv))
    else:
        m.part("head", "body", tuple(base + Vector((0, hr * 0.4, 0))), (-lean, 0, 0))
    skull = ell((0, 0, 0), (hr * P.get("hw", 1.0), hr * 0.95, hr))
    region = None
    if P.get("disk"):  # disco facial de búho/lechuza
        dc, rim = P["disk"]

        def region(p, n, dc=dc, rim=rim):
            if n.z > 0.35 and p.z > 0.25 * hr:
                rr = math.hypot(p.x * 0.85, p.y)
                return rim if rr > 0.78 * hr else dc
            return None
    hfn = (lambda p, n: region(p, n) or hsk(p, n)) if region else hsk
    if P.get("mask"):  # antifaz o cara de otro color
        mc = P["mask"]
        base_h = hfn
        hfn = lambda p, n, base_h=base_h: mc if (n.z > 0.2 and abs(p.y) < 0.3 * hr and p.z > 0.2 * hr) else base_h(p, n)
    if P.get("capCol"):
        cc = P["capCol"]
        base_h2 = hfn
        hfn = lambda p, n, base_h2=base_h2: cc if p.y > 0.35 * hr else base_h2(p, n)
    if P.get("throat"):
        tc = P["throat"]
        base_h3 = hfn
        hfn = lambda p, n, base_h3=base_h3: tc if (p.y < -0.35 * hr and p.z > -0.1 * hr) else base_h3(p, n)
    voxelize(m, "head", [skull] + P.get("head_extra", []), v * 0.8, hfn)
    E = P.get("eye", {})
    owl = P.get("disk") is not None or E.get("front")
    ex_ = E.get("x", 0.32 if owl else 0.5)
    sp_ = surface_point(skull, ex_ * hr * P.get("hw", 1.0), E.get("y", 0.12) * hr)
    iris = ctx.en if ctx.L >= 3 else E.get("col", "#ffb020" if owl else "#1a1a1a")
    eyes(m, "head", (0, sp_.y, sp_.z - (0 if owl else 0.08 * hr)), ex_ * hr * P.get("hw", 1.0), hr * E.get("size", 0.42 if owl else 0.3), iris,
         glow=ctx.eye_glow, yaw=18 if owl else 60, style=E.get("style", "round" if owl else "bead"))
    bk, bln = P.get("beak", "cone"), P.get("beakLen", 0.35) * S
    _beak(m, "head", bk, hr, bln, C.get("beak", "#f2a02a"), C.get("beak2"), S)
    m.part("jaw", "head", (0, -0.2 * hr, 0.75 * hr))
    if bk not in ("toucan", "pelican", "hornbill", "flamingo", "curved"):
        segment(m, "jaw", (0, 0, 0), (0, -0.04 * hr, bln * (0.8 if bk != "duck" else 0.9)), (0.2 * hr if bk != "duck" else 0.45 * hr, 0.08 * hr), mix(C.get("beak", "#f2a02a"), "#000000", 0.15))
    if P.get("crest"):
        _crest(m, "head", P["crest"], hr, C.get("crest", C.get("head", body_c)), C.get("crest2"), S)
    if P.get("wattle"):
        m.box("head", (0, -0.6 * hr, 0.55 * hr), (0.14 * hr, 0.4 * hr, 0.12 * hr), P["wattle"])
    # alas
    wk = P.get("wings", "folded")
    wc = [C.get("wing", body_c), C.get("wing2", mix(C.get("wing", body_c), "#000000", 0.3)), C.get("wing3", C.get("belly") or mix(body_c, "#ffffff", 0.3))]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        if wk == "none":
            continue
        if wk == "folded":
            m.part(w, "body", (sx * bw * 0.85, 0.25 * bh, 0.25 * bl))
            wl = P.get("wingLen", 1.0)
            voxelize(m, w, [ell((sx * 0.04 * S, -0.2 * bh, -0.45 * bl * wl), (0.11 * S, 0.55 * bh, 0.8 * bl * wl))], v * 0.8,
                     lambda p, n, wl=wl: wc[1] if p.z < -0.75 * bl * wl else (wc[0] if p.y > -0.35 * bh else wc[1] if (int(-p.z / (0.12 * S)) % 2) else wc[0]))
        elif wk == "flipper":
            m.part(w, "body", (sx * bw * 0.9, 0.2 * bh, 0.05 * bl), (0, 0, sx * 12))
            voxelize(m, w, [ell((sx * 0.06 * S, -0.5 * bh, 0), (0.08 * S, 0.65 * bh, 0.3 * bl))], v * 0.8, lambda p, n: wc[0] if n.x * sx > 0 else wc[2])
        elif wk in ("open", "hover"):
            m.part(w, "body", (sx * bw * 0.7, 0.3 * bh, 0.1 * bl), (0, sx * -10, sx * (20 if wk == "open" else 55)))
            sc = P.get("span", 1.0) * S * (0.6 if wk == "hover" else 1.0)
            _wing(m, w, sx, [(10, 0.5 * sc, 1.5 * sc, 0.3 * sc, 0, [wc[1], wc[0], wc[1]]), (8, 0.35 * sc, 0.9 * sc, 0.26 * sc, 0.15 * sc, [wc[0], wc[0], wc[2]])],
                  [(0, 0), (0.45 * sc, 0.25 * sc), (0.9 * sc, 0.55 * sc), (1.3 * sc, 0.95 * sc)], wc[0], wc[0])
        elif wk == "membrane":  # pterosaurio
            m.part(w, "body", (sx * bw * 0.7, 0.3 * bh, 0.2 * bl), (0, 0, sx * 15))
            sc = P.get("span", 1.0) * S
            membrane_wing(m, w, sx, (0.9 * sc, 0.4 * sc), [(2.4 * sc, 0.6 * sc), (2.0 * sc, -0.2 * sc), (1.2 * sc, -0.5 * sc)], wc[1], wc[0], wc[2], step=0.11 * S)
    # cola
    tk = P.get("tail", "short")
    if tk != "none":
        m.part("tail0", "body", (0, 0.05 * bh, -0.9 * bl), (P.get("tailLift", -8), 0, 0))
        _bird_tail(m, "tail0", tk, S * P.get("tailS", 1.0), P.get("tailCols", [C.get("tail", body_c), mix(C.get("tail", body_c), "#000000", 0.25)]), ctx)
        info["tails"] = [("tail", 1)]
    # patas
    lc = C.get("leg", "#e8a040")
    if leg > 0.05 and gait != "hover":
        for side, sx in (("L", 1), ("R", -1)):
            lg = f"leg_{side}"
            m.part(lg, "body", (sx * 0.4 * bw, -0.75 * bh, 0.05 * bl), (-lean, 0, 0))
            th = P.get("legW", 1.0)
            if P.get("thigh", True):
                voxelize(m, lg, [ell((0, 0.05 * S, 0), (0.18 * S * th, 0.22 * S, 0.2 * S * th))], v * 0.8, bsk)
            segment(m, lg, (0, 0, 0), (0, -leg, 0.02 * S), (0.09 * S * th, 0.09 * S * th), lc)
            if P.get("webbed"):
                m.box(lg, (0, -leg, 0.15 * S), (0.36 * S, 0.05 * S, 0.34 * S), lc)
            else:
                for k in (-1, 0, 1):
                    segment(m, lg, (0, -leg, 0), (k * 0.14 * S, -leg, 0.28 * S), (0.06 * S, 0.05 * S), lc)
                segment(m, lg, (0, -leg, 0), (0, -leg, -0.15 * S), (0.06 * S, 0.05 * S), lc)
    info["gait"] = gait
    return info


def anim_bird(m, info, P, L):
    from pets import anim_common
    gait = info["gait"]
    has = m.parts
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {}
        if gait in ("hover", "fly"):
            fast = 8 if gait == "hover" else 2
            for side, sx in (("L", 1), ("R", -1)):
                if f"wing_{side}" in has:
                    pose[f"wing_{side}"] = {"r": quat((0, 0, sx * (40 if gait == "hover" else 28) * math.sin(a * fast)))}
            pose["body"] = {"p": (0, 0.15 * S * math.sin(a * 2), 0), "r": quat((0, 6 * math.sin(a), 0))}
        elif gait == "waddle":
            pose["body"] = {"r": quat((0, 4 * math.sin(a * 2), 8 * math.sin(a * 2))), "p": (0, 0.03 * S * abs(math.sin(a * 2)), 0)}
            for side, sx in (("L", 1), ("R", -1)):
                if f"wing_{side}" in has:
                    pose[f"wing_{side}"] = {"r": quat((0, 0, sx * (10 + 8 * math.sin(a * 2))))}
                if f"leg_{side}" in has:
                    pose[f"leg_{side}"] = {"r": quat((18 * math.sin(a * 2 + (0 if sx > 0 else math.pi)), 0, 0))}
        elif gait == "strut":
            for side, ph in (("L", 0), ("R", math.pi)):
                if f"leg_{side}" in has:
                    pose[f"leg_{side}"] = {"r": quat((25 * math.sin(a * 2 + ph), 0, 0))}
            pose["body"] = {"p": (0, 0.04 * S * abs(math.sin(a * 2)), 0)}
        else:  # stand: picotea y mira
            pk = max(0.0, math.sin(a)) ** 6
            pose["body"] = {"r": quat((0, 0, 0))}
            for side, sx in (("L", 1), ("R", -1)):
                if f"wing_{side}" in has:
                    pose[f"wing_{side}"] = {"r": quat((0, 0, sx * 6 * max(0.0, math.sin(a * 2 + 1)) ** 4))}
            if "neck0" in has:
                pose["neck0"] = {"r": quat((25 * pk, 0, 0))}
        hr = quat((-8 * max(0.0, math.sin(a * 1.5)) ** 4 + (20 * max(0.0, math.sin(a)) ** 6 if gait == "stand" and "neck0" not in has else 0), 25 * math.sin(a), 0))
        pose["head"] = {"r": hr}
        if "jaw" in has:
            pose["jaw"] = {"r": quat((14 * max(0.0, math.sin(a * 2 + 2)) ** 8, 0, 0))}
        if "tail0" in has:
            pose["tail0"] = {"r": quat((5 * math.sin(a * 2), 4 * math.sin(a), 0))}
        anim_common(pose, m, info, t, L)
        pose.pop("tail0", None) if False else None
        return pose
    return f


# ============================================================================= PECES Y MAMÍFEROS MARINOS
def fish(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    shape = P.get("shape", "torpedo")
    if shape == "seahorse":
        return seahorse(m, P, ctx, S, v)
    if shape == "ray":
        return ray(m, P, ctx, S, v)
    C = P.get("cols", {})
    base = C.get("body", "#4a8ad8")
    bl, bh, bw = P.get("bl", 1.0) * S, P.get("bh", 0.55) * S, P.get("bw", 0.4) * S
    mammal = P.get("mammal", False)
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly", mix(base, "#ffffff", 0.55)), pat=P.get("pat"), pc=C.get("pc"), pc2=C.get("pc2"),
                                        ps=P.get("ps", 1.0), belly_k=-0.25, back=C.get("back")))
    m.part("body", "root", (0, 1.0 * S, 0))
    prims = [ell((0, 0, 0.1 * bl), (bw, bh, bl * 0.75), 0.02, 3), cap((0, 0, -0.2 * bl), (0, 0.02 * bh, -0.95 * bl), bh * 0.7 * P.get("stalk", 1.0) * min(1, bw / bh * 1.6),
                                                                      bh * 0.18 * P.get("stalk", 1.0))]
    if P.get("head", 1.0) != 1.0:
        hk = P["head"]
        prims.append(ell((0, 0.02 * bh, 0.55 * bl), (bw * hk, bh * hk * 0.9, bl * 0.4 * hk)))
    if shape == "round":
        prims = [ell((0, 0, 0), (bw, bh, bl * 0.8), 0.03, 3), cap((0, 0, -0.5 * bl), (0, 0, -0.85 * bl), bh * 0.25, bh * 0.15)]
    if shape == "disc":  # pez ángel, disco: alto y plano
        prims = [ell((0, 0, 0.05 * bl), (bw * 0.7, bh, bl * 0.65), 0.02, 3), cap((0, 0, -0.4 * bl), (0, 0, -0.8 * bl), bh * 0.2, bh * 0.12)]
    if shape == "box":
        prims = [ell((0, 0, 0), (bw, bh, bl * 0.75), 0.0, 3), ell((0, 0, 0), (bw * 0.85, bh * 0.85, bl * 0.8))]
    if shape == "mola":
        prims = [ell((0, 0, 0), (bw * 0.6, bh, bl * 0.6), 0.02, 3)]
    if shape == "long":  # barracuda, pez espada, pez remo
        prims = [ell((0, 0, 0.3 * bl), (bw, bh, bl * 0.6), 0.02, 3), cap((0, 0, 0), (0, 0, -1.0 * bl), bh * 0.85, bh * 0.25)]
    carve = None
    if P.get("mouth") == "maw":  # boca enorme (rape, pez víbora)
        carve = [ell((0, -0.15 * bh, 0.85 * bl), (bw * 0.8, bh * 0.45, bl * 0.25))]
    voxelize(m, "body", prims, v, bsk, carve=carve)
    front = {"round": 0.8, "disc": 0.7, "box": 0.75, "mola": 0.6, "long": 0.9}.get(shape, 0.85) * bl
    E = P.get("eye", {})
    ey, ex_ = E.get("y", 0.2) * bh, E.get("x", 0.65) * bw
    ez = front * E.get("z", 0.72)
    iris = ctx.en if ctx.L >= 3 else E.get("col", "#1a1a1a" if mammal else "#f2c14e")
    es = E.get("size", 0.3) * min(bh, bw * 1.5)
    for sx in ((1, -1) if not P.get("neck") else ()):
        p = Vector((sx * ex_, ey, ez))
        m.box("body", p, (0.06 * S, es, es), "#f6f6f0", r=(0, sx * 90 - sx * 20, 0))
        m.box("body", p + Vector((sx * 0.03 * S, 0, 0)), (0.05 * S, es * 0.7, es * 0.7), iris, r=(0, sx * 70, 0), emit=ctx.eye_glow,
              tag="eyes" if ctx.eye_glow else None)
        m.box("body", p + Vector((sx * 0.05 * S, 0, 0.01)), (0.04 * S, es * 0.35, es * 0.35), "#050505", r=(0, sx * 70, 0))
    fc = C.get("fin", mix(base, "#000000", 0.2))
    fc2 = C.get("fin2", fc)
    # aleta dorsal
    dk = P.get("dorsal", "tri")
    if dk == "tri":
        for j in range(5):
            m.box("body", (0, bh * 0.85 + j * 0.1 * S * P.get("dorsalH", 1), (0.05 - j * 0.07) * bl), (0.06 * S, 0.12 * S * P.get("dorsalH", 1), (0.5 - j * 0.09) * bl), fc)
    elif dk == "sail":
        for j in range(12):
            k = j / 11
            h_ = (0.4 + 1.3 * math.sin(k * math.pi * 0.9 + 0.2)) * S
            m.box("body", (0, bh * 0.75 + h_ / 2, (0.55 - 1.1 * k) * bl), (0.05 * S, h_, 1.1 * bl / 12 + 0.02), fc if j % 2 else fc2)
            segment(m, "body", (0, bh * 0.75, (0.55 - 1.1 * k) * bl), (0, bh * 0.75 + h_, (0.5 - 1.1 * k) * bl), 0.05 * S, mix(fc, "#000000", 0.3))
    elif dk == "long":
        for j in range(12):
            k = j / 11
            m.box("body", (0, bh * (0.85 - 0.5 * k) + 0.12 * S, (0.6 - 1.4 * k) * bl), (0.05 * S, 0.3 * S, 1.4 * bl / 12 + 0.02), fc if j % 2 else fc2)
    elif dk == "spiny":
        for j in range(9):
            k = j / 8
            h_ = (0.35 + 0.35 * math.sin(k * math.pi)) * S * P.get("dorsalH", 1)
            segment(m, "body", (0, bh * 0.8, (0.45 - 0.9 * k) * bl), (0, bh * 0.8 + h_, (0.4 - 0.9 * k) * bl), 0.05 * S, fc)
            if j < 8:
                m.box("body", (0, bh * 0.8 + h_ * 0.35, (0.4 - 0.9 * k) * bl - 0.05 * bl), (0.03 * S, h_ * 0.7, 0.9 * bl / 8), fc2)
    elif dk == "small":
        m.box("body", (0, bh * 0.95, -0.1 * bl), (0.06 * S, 0.2 * S, 0.3 * bl), fc, r=(-20, 0, 0))
    elif dk == "flowing":  # betta: aleta enorme ondulada
        voxelize(m, "body", [ell((0, bh * 0.8 + 0.35 * S, -0.35 * bl), (0.04 * S, 0.5 * S, 0.65 * bl))], v * 0.7,
                 lambda p, n: fc2 if (p.z * 6 / S) % 1 < 0.25 else fc)
    # aletas pectorales
    pk = P.get("pecs", 0.5) * S
    for side, sx in (("L", 1), ("R", -1)):
        fn = f"fin_{side}"
        m.part(fn, "body", (sx * bw * 0.9, -0.25 * bh, 0.35 * bl), (0, 0, sx * -25))
        if mammal:
            voxelize(m, fn, [ell((sx * pk * 0.6, -0.1 * S, -0.1 * S), (pk * 0.7, 0.08 * S, pk * 0.35))], v * 0.8, solid(fc))
        else:
            for j in range(4):
                m.box(fn, (sx * (0.1 + j * 0.12) * S, 0, -j * 0.06 * S), (0.16 * S, 0.04 * S, pk * (1 - j * 0.18)), fc if j % 2 else fc2, r=(0, sx * -30, 0))
    if P.get("pelvic"):
        for sx in (1, -1):
            m.box("body", (sx * 0.2 * bw, -0.95 * bh, 0.1 * bl), (0.05 * S, 0.3 * S, 0.2 * S), fc, r=(-30, 0, 0))
    if P.get("anal"):
        m.box("body", (0, -0.85 * bh, -0.45 * bl), (0.05 * S, 0.25 * S, 0.35 * bl), fc, r=(20, 0, 0))
    # cola
    tk = P.get("tail", "fork")
    m.part("tail0", "body", (0, 0.02 * bh, -0.95 * bl if shape not in ("round", "disc", "mola") else -0.82 * bl))
    ts = P.get("tailS", 1.0) * S
    if tk == "fork":
        for sx in (1, -1):
            for j in range(4):
                m.box("tail0", (0, sx * (0.12 + j * 0.12) * ts, -(0.12 + j * 0.1) * ts), (0.05 * S, 0.16 * ts, 0.3 * ts), fc if j % 2 else fc2)
    elif tk == "round":
        voxelize(m, "tail0", [ell((0, 0, -0.35 * ts), (0.05 * S, 0.45 * ts, 0.4 * ts))], v * 0.7, solid(fc))
    elif tk == "crescent":  # tiburón, atún
        for j in range(6):
            k = j / 5
            m.box("tail0", (0, (0.12 + 0.55 * k) * ts * (1.0 if P.get("hetero", True) else 0.8), -(0.15 + 0.45 * k) * ts), (0.06 * S, 0.16 * ts, 0.3 * ts), fc)
            m.box("tail0", (0, -(0.1 + 0.35 * k) * ts, -(0.15 + 0.3 * k) * ts), (0.06 * S, 0.14 * ts, 0.26 * ts), fc)
    elif tk == "fan":  # betta / carpín: cola enorme con radios
        voxelize(m, "tail0", [ell((0, 0, -0.55 * ts), (0.05 * S, 0.75 * ts, 0.6 * ts)), ell((0, 0.35 * ts, -0.75 * ts), (0.05 * S, 0.4 * ts, 0.4 * ts)),
                              ell((0, -0.35 * ts, -0.75 * ts), (0.05 * S, 0.4 * ts, 0.4 * ts))], v * 0.7,
                 lambda p, n: fc2 if (math.atan2(p.y, -p.z) * 5) % 1 < 0.22 else fc)
    elif tk == "fluke":  # mamíferos: horizontal
        for sx in (1, -1):
            for j in range(4):
                m.box("tail0", (sx * (0.15 + j * 0.13) * ts, 0, -(0.1 + j * 0.08) * ts), (0.18 * ts, 0.06 * S, 0.32 * ts * (1 - 0.15 * j)), fc)
    elif tk == "whip":  # raya: cola fina
        segment(m, "tail0", (0, 0, 0), (0, 0, -1.4 * ts), 0.06 * S, fc)
    elif tk == "clavus":  # pez luna
        voxelize(m, "tail0", [ell((0, 0, -0.05 * ts), (0.06 * S, 0.8 * bh / S * ts, 0.2 * ts))], v * 0.7, solid(fc))
    # boca y rasgos
    mo = P.get("mouth", "small")
    mz = front * 1.05
    mcol = C.get("mouth", "#2a1418")
    if mo == "small":
        m.box("body", (0, -0.15 * bh, mz - 0.05 * S), (0.18 * bw, 0.06 * S, 0.08 * S), mcol)
    elif mo in ("big", "teeth", "maw", "underbite"):
        m.part("jaw", "body", (0, -0.3 * bh, mz - 0.25 * bl))
        voxelize(m, "jaw", [cap((0, 0, 0), (0, -0.05 * bh, 0.3 * bl), 0.45 * bw, 0.3 * bw)], v * 0.8, lambda p, n: "#5a1a2a" if n.y > 0.5 else bsk(p, n))
        if mo in ("teeth", "maw", "underbite"):
            n_t = 9 if mo == "maw" else 6
            for k in range(n_t):
                a = math.radians(-70 + k * 140 / (n_t - 1))
                ln = (0.35 if mo == "maw" else 0.15) * S
                m.box("body", (math.sin(a) * 0.4 * bw, -0.15 * bh, mz - 0.1 * bl + math.cos(a) * 0.12 * bl), (0.05 * S, ln, 0.05 * S), "#f6f6f0")
                m.box("jaw", (math.sin(a) * 0.35 * bw, 0.05 * bh + ln * 0.4, 0.22 * bl + math.cos(a) * 0.05 * bl), (0.04 * S, ln * 0.8, 0.04 * S), "#f6f6f0")
    elif mo == "bottle":  # delfín
        voxelize(m, "body", [cap((0, -0.1 * bh, front * 0.9), (0, -0.15 * bh, front * 0.9 + 0.35 * S), 0.18 * S, 0.13 * S)], v * 0.8, bsk)
    elif mo == "beak":  # pez loro
        m.box("body", (0, -0.1 * bh, mz), (0.3 * bw, 0.25 * bh, 0.15 * S), C.get("beak", "#f2ead6"))
    elif mo == "tube":
        segment(m, "body", (0, 0, front * 0.9), (0, -0.05 * S, front * 0.9 + 0.4 * S), 0.12 * S, base)
    elif mo == "whiskers":
        for sx in (1, -1):
            for k in range(2):
                pts = [Vector((sx * (0.15 + 0.3 * u) * S, -0.2 * bh - 0.25 * u * S - k * 0.1 * S, mz - 0.1 * S - 0.15 * u * S)) for u in (j / 4 for j in range(5))]
                polyline(m, "body", pts, 0.04 * S, mix(base, "#000000", 0.3))
    if P.get("noseHorn"):  # pez unicornio
        crystal(m, "body", (0, bh * 0.55, front * 0.8), 0.14 * S, P["noseHorn"] * S, C.get("horn", mix(base, "#ffffff", 0.3)), rot=(-50, 0, 0))
    if P.get("neck"):  # plesiosaurio: cuello largo con cabeza
        parent, piv = "body", Vector((0, 0.1 * bh, front * 0.9))
        nn = 5
        for j in range(nn):
            nm = f"neck{j}"
            m.part(nm, parent, tuple(piv), (-12 if j == 0 else 4, 0, 0))
            d = Vector((0, 0, P["neck"] * S / nn))
            r = bh * (0.42 - 0.04 * j)
            voxelize(m, nm, [cap((0, 0, -0.05 * S), tuple(d * 1.1), r, r * 0.9)], v * 0.85, bsk)
            parent, piv = nm, d
        m.part("head", parent, tuple(piv))
        voxelize(m, "head", [ell((0, 0, 0.15 * S), (bh * 0.4, bh * 0.32, bh * 0.6)), cap((0, -0.05 * S, 0.3 * S), (0, -0.07 * S, 0.65 * S), bh * 0.22, bh * 0.15)], v * 0.8, bsk)
        eyes(m, "head", (0, bh * 0.15, 0.3 * S), bh * 0.3, 0.12 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=55)
        for k in range(5):
            for sx in (1, -1):
                m.box("head", (sx * bh * 0.16, -0.12 * S, 0.35 * S + k * 0.07 * S), (0.03 * S, 0.08 * S, 0.03 * S), "#f6f6f0")
    if P.get("sword"):
        segment(m, "body", (0, 0.05 * bh, front * 0.9), (0, 0.06 * bh, front + P["sword"] * S), (0.1 * S, 0.06 * S), C.get("sword", mix(base, "#000000", 0.3)))
    if P.get("saw"):
        segment(m, "body", (0, 0.0, front * 0.9), (0, 0.0, front + P["saw"] * S), (0.22 * S, 0.06 * S), C.get("sword", "#8a8070"))
        for k in range(8):
            for sx in (1, -1):
                m.box("body", (sx * 0.13 * S, 0, front + (0.1 + k * 0.11) * P["saw"] * S / 0.9), (0.08 * S, 0.04 * S, 0.04 * S), "#f6f0e2")
    if P.get("hammer"):
        voxelize(m, "body", [ell((0, 0.05 * bh, front * 0.95), (bw * 2.3, bh * 0.25, bl * 0.15))], v * 0.8, bsk)
        for sx in (1, -1):
            m.box("body", (sx * bw * 2.25, 0.05 * bh, front * 0.95), (0.08 * S, 0.14 * S, 0.14 * S), "#101010")
    if P.get("lure"):  # rape
        pts = [Vector((0, bh * 0.8 + 0.6 * S * math.sin(u * 2.2), front * 0.5 + 0.7 * S * u)) for u in (j / 5 for j in range(6))]
        polyline(m, "body", pts, 0.05 * S, mix(base, "#000000", 0.3))
        m.box("body", pts[-1] + Vector((0, -0.05 * S, 0)), (0.2 * S, 0.2 * S, 0.2 * S), C.get("lure", ctx.en if ctx.L >= 1 else "#ffe88a"), emit=2.0, tag="glow")
    if P.get("spikes"):  # pez globo
        for j in range(60):
            a, b = j * 2.39996, math.acos(1 - 2 * ((j + 0.5) / 60))
            d = Vector((math.sin(b) * math.cos(a), math.cos(b), math.sin(b) * math.sin(a)))
            if d.z > 0.85:
                continue
            p0 = Vector((d.x * bw, d.y * bh, d.z * bl * 0.8))
            segment(m, "body", p0, p0 + d * 0.22 * S, 0.04 * S, C.get("spike", "#f2ead6"))
    if P.get("lantern"):  # puntos luminosos (pez linterna)
        for k in range(10):
            m.box("body", ((1 if k % 2 else -1) * bw * 0.9, -0.5 * bh + (k % 3) * 0.08 * S, (0.5 - k * 0.09) * bl), (0.04 * S, 0.08 * S, 0.08 * S),
                  P["lantern"], emit=2.0, tag="glow")
    if P.get("tusk"):  # narval
        pos = Vector((0, 0.05 * bh, front * 0.95))
        for j in range(10):
            m.box("body", pos + Vector((0, 0, j * P["tusk"] * S / 10)), (0.08 * S * (1 - j / 14), 0.08 * S * (1 - j / 14), P["tusk"] * S / 10 + 0.01),
                  "#f2ead6" if j % 2 else "#d8ccb0", r=(0, 0, 30 * j))
    if P.get("walrusTusks"):
        for sx in (1, -1):
            segment(m, "body", (sx * 0.15 * bw, -0.35 * bh, front * 0.95), (sx * 0.2 * bw, -1.35 * bh, front * 1.0), 0.1 * S, "#f2ead6")
        voxelize(m, "body", [ell((0, -0.25 * bh, front * 0.92), (bw * 0.55, bh * 0.35, 0.25 * S))], v * 0.8, bsk)
    if P.get("blowhole"):
        m.box("body", (0, bh * 0.98, front * 0.45), (0.1 * S, 0.03 * S, 0.06 * S), "#1a1a1a")
    if P.get("crestRed"):  # pez remo
        for j in range(8):
            segment(m, "body", (0, bh * 0.8, front - j * 0.08 * S), (0, bh * 0.8 + (0.9 - j * 0.08) * S, front - 0.1 * S - j * 0.1 * S), 0.05 * S, "#e83a3a")
    if P.get("bumps"):  # ballena jorobada / tiburón ballena
        for k in range(10):
            m.box("body", (((k % 3) - 1) * 0.18 * bw, bh * 0.75, front * 0.85 - k * 0.04 * S), (0.08 * S, 0.06 * S, 0.08 * S), mix(base, "#000000", 0.25))
    if P.get("gills"):
        for sx in (1, -1):
            for k in range(P["gills"]):
                m.box("body", (sx * bw * 0.92, -0.05 * bh, front * 0.45 - k * 0.07 * S), (0.03 * S, bh * 0.6, 0.03 * S), mix(base, "#000000", 0.35))
    if P.get("whitePatch"):  # orca: mancha blanca tras el ojo
        for sx in (1, -1):
            voxelize(m, "body", [ell((sx * bw * 0.75, bh * 0.35, front * 0.5), (bw * 0.3, bh * 0.2, bl * 0.18))], v * 0.8, solid("#f6f6f0"))
    if P.get("whiskersMan"):  # manatí: hocico redondo
        voxelize(m, "body", [ell((0, -0.2 * bh, front * 0.95), (bw * 0.6, bh * 0.45, 0.3 * S))], v * 0.8, bsk)
    return dict(S=S, v=v, body="body", head="body", hover=P.get("hover", 0.55), tails=[], heads=[], swim="mammal" if mammal else "fish",
                shape=shape)


def seahorse(m, P, ctx, S, v):
    C = P.get("cols", {})
    base = C.get("body", "#f2a03a")
    bsk = _sk(ctx, dict(base=base, belly=C.get("belly", mix(base, "#ffffff", 0.4)), belly_k=-0.9, pat="bands_y", pc=mix(base, "#000000", 0.12), ps=0.35))
    m.part("body", "root", (0, 1.6 * S, 0))
    voxelize(m, "body", [ell((0, 0, 0.08 * S), (0.32 * S, 0.55 * S, 0.38 * S), 0.02, 3)], v, bsk)
    m.part("head", "body", (0, 0.6 * S, 0.12 * S), (35, 0, 0))
    voxelize(m, "head", [ell((0, 0, 0), (0.25 * S, 0.3 * S, 0.28 * S)), cap((0, -0.05 * S, 0.1 * S), (0, -0.1 * S, 0.65 * S), 0.11 * S, 0.08 * S)], v * 0.8, bsk)
    for k in range(4):
        crystal(m, "head", ((k - 1.5) * 0.06 * S, 0.3 * S, -0.05 * S - 0.04 * S * k), 0.06 * S, 0.2 * S, mix(base, "#ffffff", 0.2), rot=(-20, 0, 0))
    eyes(m, "head", (0, 0.05 * S, 0.12 * S), 0.22 * S, 0.12 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=60, style="bead")
    parent, piv = "body", Vector((0, -0.45 * S, -0.05 * S))
    n = 7
    for j in range(n):
        nm = f"tail{j}"
        a = j / (n - 1)
        m.part(nm, parent, tuple(piv), (-18 - 10 * a, 0, 0))
        r = 0.2 * S * (1 - 0.8 * a) + 0.03
        d = Vector((0, -0.22 * S * (1 - 0.3 * a), 0))
        voxelize(m, nm, [cap((0, 0, 0), tuple(d * 1.1), r, r * 0.85)], v * 0.8, bsk)
        parent, piv = nm, d
    m.part("fin_D", "body", (0, 0.0, -0.35 * S))
    for j in range(5):
        m.box("fin_D", (0, -0.2 * S + j * 0.1 * S, -0.08 * S), (0.04 * S, 0.12 * S, 0.22 * S), C.get("fin", mix(base, "#ffffff", 0.35)))
    for k in range(6):
        crystal(m, "body", (0, 0.4 * S - k * 0.15 * S, -0.3 * S), 0.06 * S, 0.16 * S, mix(base, "#000000", 0.15), rot=(-80, 0, 0))
    if P.get("leafy"):  # dragón de mar foliado: apéndices de hoja
        lc = C.get("leaf", "#c8a03a")
        for part_, pts in (("body", [(0.3, 0.3, 0.1), (-0.3, 0.2, 0.0), (0.32, -0.2, 0.0), (-0.3, -0.35, 0.05), (0, 0.45, -0.3), (0, -0.1, -0.35)]),
                           ("head", [(0, 0.3, -0.1), (0.2, 0.0, 0.3), (-0.2, 0.0, 0.3)])):
            for (x, y, z) in pts:
                d = Vector((x, y * 0.5 + 0.3, z)).normalized()
                for j in range(4):
                    m.box(part_, Vector((x, y, z)) * S + d * (0.1 + j * 0.12) * S, (0.2 * S * (1 - j / 5), 0.05 * S, 0.14 * S), lc if j % 2 else mix(lc, "#4a8a2a", 0.4),
                          r=Vector((0, 0, 1)).rotation_difference(d))
        for j in range(7):
            for sx in (1, -1):
                m.box(f"tail{j}", (sx * 0.15 * S, 0, 0), (0.2 * S, 0.05 * S, 0.12 * S), lc, r=(0, 0, sx * 30))
    return dict(S=S, v=v, body="body", head="head", hover=0.4, tails=[("tail", n)], heads=["head"], swim="seahorse", shape="seahorse")


def ray(m, P, ctx, S, v):
    C = P.get("cols", {})
    base = C.get("body", "#2a3a5a")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly", "#f2f2ea"), belly_k=-0.3, pat=P.get("pat"), pc=C.get("pc"), ps=P.get("ps", 1)))
    m.part("body", "root", (0, 1.4 * S, 0))
    voxelize(m, "body", [ell((0, 0, 0.1 * S), (0.55 * S, 0.17 * S, 0.75 * S), 0.02, 3)], v, bsk)
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.4 * S, 0, 0.1 * S))
        voxelize(m, w, [ell((sx * 0.6 * S, 0, -0.1 * S), (0.85 * S, 0.13 * S, 0.6 * S), 0.0, 3),
                        ell((sx * 1.25 * S, 0, -0.35 * S), (0.4 * S, 0.07 * S, 0.25 * S))], v, bsk)
    if P.get("cephalic", True):  # manta: aletas cefálicas
        for sx in (1, -1):
            m.box("body", (sx * 0.38 * S, -0.05 * S, 0.9 * S), (0.12 * S, 0.08 * S, 0.4 * S), base, r=(0, sx * -10, 0))
    for sx in (1, -1):
        m.box("body", (sx * 0.42 * S, 0.06 * S, 0.65 * S), (0.06 * S, 0.12 * S, 0.12 * S), ctx.en if ctx.L >= 3 else "#1a1a1a", emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
    m.box("body", (0, -0.12 * S, 0.82 * S), (0.5 * S, 0.06 * S, 0.06 * S), "#1a1a1a")
    m.part("tail0", "body", (0, 0, -0.65 * S))
    segment(m, "tail0", (0, 0, 0), (0, 0.05 * S, -1.6 * S), 0.07 * S, mix(base, "#000000", 0.2))
    return dict(S=S, v=v, body="body", head="body", hover=0.7, tails=[], heads=[], swim="ray", shape="ray")


def anim_fish(m, info, P, L):
    from pets import anim_common
    sw = info["swim"]
    has = m.parts
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {"body": {"p": (0, 0.15 * S * math.sin(a * 2), 0), "r": quat((0, 8 * math.sin(a), 0))}}
        if sw == "fish":
            pose["tail0"] = {"r": quat((0, 28 * math.sin(a * 4), 0))}
            pose["body"]["r"] = quat((0, 8 * math.sin(a) - 4 * math.sin(a * 4), 0))
        elif sw == "mammal":
            pose["tail0"] = {"r": quat((22 * math.sin(a * 2), 0, 0))}
            pose["body"]["r"] = quat((5 * math.sin(a * 2 - 1), 8 * math.sin(a), 0))
        elif sw == "ray":
            for side, sx in (("L", 1), ("R", -1)):
                pose[f"wing_{side}"] = {"r": quat((0, 0, sx * 22 * math.sin(a * 2)))}
            pose["tail0"] = {"r": quat((0, 10 * math.sin(a * 2), 0))}
        elif sw == "seahorse":
            pose["body"] = {"p": (0, 0.12 * S * math.sin(a * 2), 0), "r": quat((4 * math.sin(a * 2), 15 * math.sin(a), 0))}
            pose["fin_D"] = {"r": quat((0, 30 * math.sin(a * 10), 0))}
            for j in range(7):
                pose[f"tail{j}"] = {"r": quat((-6 * math.sin(a * 2 - j * 0.5), 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            if f"fin_{side}" in has:
                pose[f"fin_{side}"] = {"r": quat((0, sx * 15 * math.sin(a * 4), 0))}
        if "jaw" in has:
            pose["jaw"] = {"r": quat((12 * max(0.0, math.sin(a)) ** 4, 0, 0))}
        anim_common(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= INSECTOS Y ARÁCNIDOS
def bug(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5 * 0.85
    C = P.get("cols", {})
    base = C.get("body", "#3a2a1a")
    ab_c = C.get("abdomen", base)
    th_c = C.get("thorax", base)
    hd_c = C.get("head", th_c)
    leg_c = C.get("legs", "#1a1410")
    fly = P.get("fly", False)
    spider = P.get("spider", False)
    hov = P.get("hover", 0.6 if fly else 0.0)
    tr = Vector(P.get("thorax", (0.32, 0.3, 0.35))) * S
    m.part("body", "root", (0, (P.get("legL", 0.55) * 0.75 + tr.y) * S if not fly else 1.2 * S, 0))
    voxelize(m, "body", [ell((0, 0, 0), tuple(tr), P.get("fuzz", 0.03), 4)], v, _sk(ctx, dict(base=th_c, pat=P.get("thPat"), pc=C.get("thpc"))))
    # abdomen
    ar = Vector(P.get("abdomen", (0.42, 0.4, 0.62))) * S
    m.part("abdomen", "body", (0, 0.02 * S, -tr.z * 0.8), (P.get("abTilt", 8), 0, 0))
    apat = P.get("abPat")
    ab_fn = _sk(ctx, dict(base=ab_c, pat=apat, pc=C.get("pc"), pc2=C.get("pc2"), ps=P.get("ps", 0.35), belly=C.get("abBelly")))
    if P.get("abShape") == "segmented":  # hormiga: cintura fina y gáster
        voxelize(m, "abdomen", [ell((0, 0, -0.12 * S), (0.1 * S, 0.1 * S, 0.12 * S)), ell((0, 0.05 * S, -ar.z), tuple(ar), P.get("fuzz", 0.03), 4)], v, ab_fn)
    elif P.get("abShape") == "long":  # libélula, insecto palo
        voxelize(m, "abdomen", [cap((0, 0, 0), (0, 0.02 * S, -ar.z * 2), ar.x, ar.x * 0.7)], v * 0.8, ab_fn)
    elif P.get("abShape") == "dome":  # mariquita, escarabajo: élitros
        voxelize(m, "abdomen", [ell((0, 0.05 * S, -ar.z * 0.7), tuple(ar), 0.0, 3)], v, ab_fn)
    else:
        voxelize(m, "abdomen", [ell((0, 0, -ar.z * 0.9), tuple(ar), P.get("fuzz", 0.03), 4)], v, ab_fn)
    if P.get("elytra_line", P.get("abShape") == "dome"):
        segment(m, "abdomen", (0, 0.05 * S + ar.y * 1.0, -0.05 * S), (0, 0.05 * S + ar.y * 0.6, -ar.z * 1.6), 0.03 * S, C.get("line", "#101010"))
    if P.get("stinger"):
        segment(m, "abdomen", (0, 0, -ar.z * 1.8), (0, -0.05 * S, -ar.z * 1.8 - 0.3 * S), 0.05 * S, "#1a1a1a")
    if P.get("forceps"):  # tijereta: pinzas al final del abdomen
        for sx in (1, -1):
            pts = [Vector((sx * (0.06 + 0.12 * math.sin(u * 2.4)) * S, 0.02 * S, -ar.z * 1.9 - 0.45 * S * u)) for u in (j / 4 for j in range(5))]
            polyline(m, "abdomen", pts, 0.06 * S, C.get("forceps", "#5a2a14"))
    if P.get("lightTail"):  # luciérnaga
        voxelize(m, "abdomen", [ell((0, -0.05 * S, -ar.z * 1.5), (ar.x * 0.8, ar.y * 0.7, ar.z * 0.4))], v * 0.8, solid(P["lightTail"], 2.5, "glow"))
    if P.get("honey"):  # hormiga melífera: gáster lleno de miel translúcido
        pass
    # cabeza
    hr = P.get("hr", 0.26) * S
    m.part("head", "body", (0, 0.05 * S, tr.z * 0.85))
    hsk = _sk(ctx, dict(base=hd_c))
    voxelize(m, "head", [ell((0, 0, hr * 0.6), (hr * P.get("hw", 1.0), hr * 0.9, hr))], v * 0.85, hsk)
    E = P.get("eye", {})
    ecol = ctx.en if ctx.L >= 3 else E.get("col", "#1a1a1a")
    if E.get("style", "compound") == "compound":
        for sx in (1, -1):
            es = hr * E.get("size", 0.65)
            m.box("head", (sx * hr * 0.75, hr * 0.15, hr * 0.9), (es, es, es), ecol, emit=ctx.eye_glow or (0.0), tag="eyes" if ctx.eye_glow else None)
            m.box("head", (sx * hr * 0.82, hr * 0.25, hr * 1.0), (es * 0.3, es * 0.3, es * 0.3), "#ffffff")
    elif E.get("style") == "spider":  # 8 ojos
        for k, (x, y, s_) in enumerate(((0.25, 0.25, 0.5), (-0.25, 0.25, 0.5), (0.55, 0.35, 0.3), (-0.55, 0.35, 0.3), (0.12, 0.55, 0.22), (-0.12, 0.55, 0.22),
                                        (0.4, 0.6, 0.2), (-0.4, 0.6, 0.2))):
            m.box("head", (x * hr, y * hr, hr * 1.45 - abs(x) * 0.4 * hr), (s_ * hr,) * 3, ecol if ctx.L >= 3 else "#101010", emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
            m.box("head", (x * hr + 0.05 * hr, y * hr + 0.08 * hr, hr * 1.45 - abs(x) * 0.4 * hr + s_ * hr * 0.5), (s_ * hr * 0.3,) * 3, "#ffffff")
    else:
        eyes(m, "head", (0, hr * 0.2, hr * 1.5), hr * 0.45, hr * 0.5, ecol, glow=ctx.eye_glow, yaw=30)
    ant = P.get("antenna", "thin")
    acol = C.get("antenna", leg_c)
    for side, sx in (("L", 1), ("R", -1)):
        if ant == "none":
            break
        al = P.get("antL", 0.7) * S
        if ant == "feather":
            a0 = Vector((sx * 0.25 * hr, 0.7 * hr, 1.2 * hr))
            a1 = a0 + Vector((sx * 0.35 * al, 0.7 * al, 0.1 * al))
            segment(m, "head", a0, a1, 0.04 * S, acol)
            for k in range(6):
                p = a0.lerp(a1, 0.2 + k * 0.14)
                segment(m, "head", p, p + Vector((sx * 0.12 * S, 0.02 * S, 0.12 * S)), 0.025 * S + 0.01, acol)
                segment(m, "head", p, p + Vector((sx * 0.12 * S, 0.02 * S, -0.12 * S)), 0.025 * S + 0.01, acol)
        elif ant == "elbow":
            a0 = Vector((sx * 0.25 * hr, 0.7 * hr, 1.2 * hr))
            a1 = a0 + Vector((sx * 0.1 * al, 0.5 * al, 0))
            a2 = a1 + Vector((sx * 0.2 * al, 0.1 * al, 0.5 * al))
            polyline(m, "head", [a0, a1, a2], 0.04 * S, acol)
        else:
            curve = 0.4 if ant == "long" else 0.0
            pts = [Vector((sx * (0.25 * hr + 0.3 * al * u), 0.6 * hr + 0.8 * al * u, 1.1 * hr + (0.25 - curve * u) * al * u)) for u in (j / 4 for j in range(5))]
            polyline(m, "head", pts, 0.035 * S + 0.01, acol)
            if ant == "club":
                m.box("head", pts[-1], (0.1 * S, 0.1 * S, 0.1 * S), acol)
    if P.get("mandibles") == "stag":
        for sx in (1, -1):
            pts = [Vector((sx * (0.25 * hr + 0.25 * S * math.sin(u * 2)), 0.1 * hr, hr * 1.3 + 0.8 * S * u)) for u in (j / 5 for j in range(6))]
            polyline(m, "head", pts, 0.1 * S, C.get("mand", "#5a2a14"))
            segment(m, "head", pts[3], pts[3] + Vector((-sx * 0.15 * S, 0.12 * S, 0)), 0.06 * S, C.get("mand", "#5a2a14"))
    elif P.get("mandibles") == "small":
        for sx in (1, -1):
            segment(m, "head", (sx * 0.3 * hr, -0.4 * hr, hr * 1.4), (sx * 0.05 * hr, -0.45 * hr, hr * 1.9), 0.06 * S, C.get("mand", "#3a2014"))
    hk = P.get("horn")
    if hk == "rhino":
        pts = [Vector((0, 0.2 * hr + 0.9 * S * u * u + 0.2 * S * u, hr * 1.3 + 0.35 * S * u)) for u in (j / 5 for j in range(6))]
        polyline(m, "head", pts, 0.12 * S, C.get("horn", "#2a1a10"))
    elif hk == "hercules":
        pts = [Vector((0, 0.3 * hr + 0.1 * S * u, hr * 1.2 + 1.0 * S * u)) for u in (j / 5 for j in range(6))]
        polyline(m, "head", pts, 0.1 * S, C.get("horn", "#1a1410"))
        pts2 = [Vector((0, 0.3 * S + 0.4 * S * u, 0.2 * S + 1.1 * S * u)) for u in (j / 5 for j in range(6))]
        polyline(m, "body", pts2, 0.11 * S, C.get("horn", "#1a1410"))
    elif hk == "kabuto":
        polyline(m, "head", [Vector((0, 0.3 * hr, hr * 1.2)), Vector((0, 0.8 * S, hr * 1.3 + 0.35 * S))], 0.12 * S, C.get("horn", "#3a1a10"))
        for sx in (1, -1):
            segment(m, "head", (0, 0.65 * S, hr * 1.3 + 0.25 * S), (sx * 0.25 * S, 0.9 * S, hr * 1.3 + 0.45 * S), 0.08 * S, C.get("horn", "#3a1a10"))
    if P.get("proboscis"):
        segment(m, "head", (0, -0.3 * hr, hr * 1.3), (0, -0.4 * hr, hr * 1.3 + P["proboscis"] * S), 0.04 * S, "#2a1a1a")
    # patas
    npairs = 4 if spider else 3
    legL = P.get("legL", 0.55) * S
    lw = P.get("legW", 1.0)
    for i in range(npairs):
        for side, sx in (("L", 1), ("R", -1)):
            lg = f"leg{i}_{side}"
            z = (0.55 - i * (1.1 / max(npairs - 1, 1))) * tr.z
            m.part(lg, "body", (sx * tr.x * 0.8, -0.3 * tr.y, z))
            style = P.get("legStyle", "normal")
            k_out = 0.5 if not spider else 0.75
            spread = (i - (npairs - 1) / 2) * (0.35 if not spider else 0.5)
            knee = Vector((sx * k_out * legL, 0.35 * legL if spider else 0.2 * legL, spread * legL))
            foot = Vector((sx * (k_out + 0.25) * legL, -0.55 * legL if not fly else -0.45 * legL, spread * legL * 1.3))
            if style == "jump" and i == 2:  # saltamontes: muslo enorme
                knee = Vector((sx * 0.35 * legL, 0.55 * legL, -0.6 * legL))
                foot = Vector((sx * 0.45 * legL, -0.5 * legL, -0.2 * legL))
                voxelize(m, lg, [cap((0, 0, 0), tuple(knee), 0.14 * S * lw, 0.07 * S * lw)], v * 0.8, solid(C.get("femur", th_c)))
                segment(m, lg, knee, foot, 0.05 * S * lw, leg_c)
                continue
            if style == "raptor" and i == 0:  # mantis: patas delanteras plegadas
                knee = Vector((sx * 0.12 * legL, 0.15 * legL, 0.55 * legL))
                foot = Vector((sx * 0.12 * legL, -0.35 * legL, 0.35 * legL))
                segment(m, lg, (0, 0, 0), knee, 0.1 * S * lw, C.get("femur", th_c))
                segment(m, lg, knee, foot, 0.08 * S * lw, C.get("femur", th_c))
                for k in range(3):
                    m.box(lg, knee.lerp(foot, 0.25 + 0.25 * k) + Vector((0, 0, 0.05 * S)), (0.03 * S, 0.03 * S, 0.1 * S), "#f2ead6")
                continue
            th_ = 0.065 * S * lw * (1.5 if spider else 1.0)
            segment(m, lg, (0, 0, 0), knee, th_, leg_c)
            segment(m, lg, knee, foot, th_ * 0.8, leg_c)
            if P.get("hairyLegs"):
                for k in range(3):
                    pp = knee.lerp(foot, 0.2 + 0.3 * k)
                    m.box(lg, pp, (th_ * 1.8, th_ * 0.6, th_ * 1.8), mix(leg_c, "#ffffff", 0.15))
                if spider:
                    m.box(lg, knee, (th_ * 1.7,) * 3, C.get("knee", mix(leg_c, "#ff8a3a", 0.5)))
    # alas
    wk = P.get("wings")
    wc = P.get("wingCols", ["#e6f2ff", "#c8dcf0", "#1a1a1a"])
    if wk:
        for side, sx in (("L", 1), ("R", -1)):
            w = f"wing_{side}"
            m.part(w, "body", (sx * 0.12 * S, tr.y * 0.85, 0.0))
            if wk == "clear":
                voxelize(m, w, [ell((sx * 0.55 * S, 0.25 * S, -0.35 * S), (0.5 * S, 0.04 * S, 0.3 * S))], v * 0.8,
                         lambda p, n: (wc[0], 0.35, "glow") if ctx.L >= 3 else (wc[0] if (int(abs(p.x) / (0.12 * S)) + int(abs(p.z) / (0.12 * S))) % 3 else wc[1]))
            elif wk == "dragonfly":
                for j, zz in enumerate((0.15, -0.2)):
                    voxelize(m, w, [ell((sx * 0.8 * S, 0.05 * S, zz * S), (0.8 * S, 0.03 * S, 0.14 * S))], v * 0.7,
                             lambda p, n: wc[2] if abs(p.x) > 1.45 * S else ((wc[0], 0.35, "glow") if ctx.L >= 3 else wc[0] if (int(abs(p.x) / (0.1 * S)) % 3) else wc[1]))
            elif wk in ("butterfly", "moth", "swallowtail", "glass", "longwing"):
                pat = P.get("wingPat", "eyes")
                fore = (0.8, 0.25, 0.75, 0.55) if wk != "longwing" else (0.9, 0.15, 0.9, 0.28)
                hind = (0.55, -0.4, 0.5, 0.45) if wk != "longwing" else (0.7, -0.25, 0.65, 0.28)

                def wcol(p, n, pat=pat):
                    rr = math.hypot(p.x / S, p.z / S)
                    if wk == "glass":
                        return wc[1] if rr > 1.15 or abs((p.x / S) % 0.5) < 0.04 else (wc[0], 0.15, "glow")
                    if rr > 1.25:
                        return wc[2]
                    if pat == "eyes":
                        d = math.hypot(p.x / S - sx * 0.75, p.z / S - 0.35)
                        if d < 0.15:
                            return (ctx.en, 1.5, "glow") if ctx.L >= 2 else wc[2]
                        if d < 0.25:
                            return wc[1]
                    elif pat == "veins":
                        if abs(math.sin(math.atan2(p.z, abs(p.x)) * 6)) < 0.18 or rr > 1.1:
                            return wc[2]
                    elif pat == "spots":
                        if vnoise(p.x * 3 / S, 2, p.z * 3 / S) > 0.64:
                            return wc[1]
                    elif pat == "stripes":
                        if int((abs(p.x) + p.z * 0.5) / (0.2 * S)) % 2:
                            return wc[1]
                    elif pat == "skull":  # polilla calavera: dibujo en el tórax
                        pass
                    return wc[0] if rr < 0.7 else (wc[3] if len(wc) > 3 else wc[0])
                prims = [ell((sx * fore[0] * S, 0.02 * S, fore[1] * S), (fore[2] * S, 0.04 * S, fore[3] * S)),
                         ell((sx * hind[0] * S, 0, hind[1] * S), (hind[2] * S, 0.04 * S, hind[3] * S))]
                if wk == "swallowtail":
                    prims.append(cap((sx * 0.6 * S, 0, -0.6 * S), (sx * 0.75 * S, 0, -1.15 * S), 0.12 * S, 0.06 * S))
                if wk == "moth":
                    prims = [ell((sx * 0.75 * S, 0.02 * S, -0.05 * S), (0.75 * S, 0.05 * S, 0.5 * S)), ell((sx * 0.5 * S, 0, -0.45 * S), (0.45 * S, 0.05 * S, 0.35 * S))]
                voxelize(m, w, prims, v * 0.75, wcol)
            elif wk == "bee":
                voxelize(m, w, [ell((sx * 0.5 * S, 0.3 * S, -0.25 * S), (0.45 * S, 0.04 * S, 0.28 * S))], v * 0.75,
                         lambda p, n: (wc[0], 0.35, "glow") if ctx.L >= 3 else wc[0])
            elif wk == "elytra_open":  # escarabajo volando: élitros abiertos + alas
                voxelize(m, w, [ell((sx * 0.3 * S, 0.2 * S, -0.35 * S), (0.3 * S, 0.12 * S, 0.5 * S))], v * 0.8, solid(ab_c))
    # cola de escorpión y pinzas
    if P.get("scorpion"):
        parent, piv = "abdomen", Vector((0, 0.05 * S, -ar.z * 1.7))
        n = 6
        for j in range(n):
            nm = f"tail{j}"
            m.part(nm, parent, tuple(piv), (-32 if j else -40, 0, 0))
            r = 0.16 * S * (1 - 0.06 * j)
            voxelize(m, nm, [ell((0, 0, -0.14 * S), (r, r, 0.18 * S))], v * 0.8, ab_fn)
            parent, piv = nm, Vector((0, 0, -0.26 * S))
        voxelize(m, f"tail{n - 1}", [ell((0, 0, -0.4 * S), (0.16 * S, 0.16 * S, 0.2 * S))], v * 0.8, solid(C.get("sting", ab_c)))
        segment(m, f"tail{n - 1}", (0, -0.05 * S, -0.55 * S), (0, -0.25 * S, -0.45 * S), 0.06 * S, "#1a1a1a" if ctx.L < 3 else ctx.en,
                emit=1.5 if ctx.L >= 3 else 0, tag="glow" if ctx.L >= 3 else None)
        for side, sx in (("L", 1), ("R", -1)):
            cl = f"claw_{side}"
            m.part(cl, "head", (sx * 0.4 * hr, -0.2 * hr, hr * 1.1))
            segment(m, cl, (0, 0, 0), (sx * 0.35 * S, 0.05 * S, 0.3 * S), 0.1 * S, ab_c)
            voxelize(m, cl, [ell((sx * 0.45 * S, 0.05 * S, 0.65 * S), (0.17 * S, 0.12 * S, 0.28 * S))], v * 0.8, ab_fn)
            for k in (1, -1):
                segment(m, cl, (sx * 0.45 * S, 0.05 * S, 0.85 * S), (sx * (0.45 + 0.08 * k) * S, 0.05 * S, 1.1 * S), 0.07 * S, mix(ab_c, "#000000", 0.25))
        info_tails = [("tail", n)]
    else:
        info_tails = []
    if P.get("ball"):  # escarabajo pelotero
        m.part("ball", "root", (0, 0.45 * S * P["ball"], 0.9 * S + 0.45 * S * P["ball"]))
        voxelize(m, "ball", [ell((0, 0, 0), (0.45 * S * P["ball"],) * 3, 0.15, 4)], v, P.get("ballCol") and solid(P["ballCol"], *(P.get("ballEmit", ()))) or skin(["#6a4a2a", "#5a3a22", "#7a5434"]))
    if P.get("leaf"):  # hormiga cortadora: hoja en la boca
        m.part("leaf", "head", (0, 0.1 * S, hr * 1.4))
        for j in range(6):
            k = j / 5
            m.box("leaf", (0, 0.2 * S + 0.6 * S * k, 0.1 * S - 0.2 * S * k), (0.7 * S * math.sin(math.pi * (0.1 + 0.8 * k)), 0.12 * S, 0.04 * S),
                  "#4aa83a" if j % 2 else "#3a9030", r=(-20, 0, 0))
    if P.get("skullMark"):
        m.box("body", (0, tr.y * 0.95, 0), (0.25 * S, 0.04 * S, 0.25 * S), "#e8d8a0")
        for sx in (1, -1):
            m.box("body", (sx * 0.06 * S, tr.y * 0.98, 0.03 * S), (0.06 * S, 0.03 * S, 0.06 * S), "#1a1410")
    return dict(S=S, v=v, body="body", head="head", hover=hov, tails=info_tails, heads=["head"], fly=fly, spider=spider, npairs=npairs)


def anim_bug(m, info, P, L):
    from pets import anim_common
    has = m.parts
    S = info["S"]
    fly = info["fly"]
    wk = P.get("wings")
    fast = {"clear": 14, "bee": 14, "dragonfly": 10, "butterfly": 3, "moth": 4, "swallowtail": 3, "glass": 3, "longwing": 3, "elytra_open": 12}.get(wk, 3)

    def f(t):
        a = t * TAU
        pose = {}
        if fly:
            pose["body"] = {"p": (0, 0.18 * S * math.sin(a * 2), 0), "r": quat((5 * math.sin(a * 2), 10 * math.sin(a), 0))}
        else:
            pose["body"] = {"p": (0, 0.02 * S * abs(math.sin(a * 4)), 0), "r": quat((0, 6 * math.sin(a), 0))}
        for side, sx in (("L", 1), ("R", -1)):
            if f"wing_{side}" in has:
                amp = 40 if fast >= 10 else 35
                pose[f"wing_{side}"] = {"r": quat((0, 0, sx * amp * math.sin(a * fast)))}
            for i in range(info["npairs"]):
                nm = f"leg{i}_{side}"
                if nm in has:
                    ph = i * 2.1 + (0 if sx > 0 else math.pi)
                    pose[nm] = {"r": quat((8 * math.sin(a * 4 + ph), 15 * math.sin(a * 4 + ph), 0))} if not fly else {"r": quat((10 * math.sin(a * 2 + ph), 0, 0))}
            if f"claw_{side}" in has:
                pose[f"claw_{side}"] = {"r": quat((0, sx * 14 * math.sin(a * 2), 0))}
        pose["abdomen"] = {"r": quat((4 * math.sin(a * 2), 5 * math.sin(a * 2 + 1), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 3), 10 * math.sin(a), 0))}
        if "ball" in has:
            pose["ball"] = {"r": quat((math.degrees(a), 0, 0))}
        anim_common(pose, m, info, t, L)
        for j in range(6):
            if f"tail{j}" in has:
                pose[f"tail{j}"] = {"r": quat((6 * math.sin(a * 2 - j * 0.5), 0, 0))}
        return pose
    return f


# ============================================================================= CRUSTÁCEOS
def crust(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5 * 0.9
    C = P.get("cols", {})
    base = C.get("body", "#d8482a")
    kind = P.get("kind", "crab")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly", mix(base, "#ffffff", 0.45)), pat=P.get("pat"), pc=C.get("pc"), ps=P.get("ps", 0.6)))
    leg_c = C.get("legs", mix(base, "#000000", 0.1))
    tails = []
    if kind in ("crab", "fiddler", "hermit", "spider", "king", "ghost", "coconut"):
        cw, ch, cl = Vector(P.get("carapace", (0.75, 0.32, 0.55))) * S
        legL = P.get("legL", 0.65) * S
        m.part("body", "root", (0, legL * 0.6 + ch, 0))
        prims = [ell((0, 0, 0), (cw, ch, cl), 0.03, 3)]
        voxelize(m, "body", prims, v, bsk)
        if P.get("spiky"):
            for j in range(26):
                a, b = j * 2.39996, math.acos(1 - ((j + 0.5) / 26))
                d = Vector((math.sin(b) * math.cos(a), math.cos(b), math.sin(b) * math.sin(a)))
                p0 = Vector((d.x * cw, d.y * ch, d.z * cl))
                crystal(m, "body", p0 + d * 0.05 * S, 0.07 * S, 0.2 * S, C.get("spike", mix(base, "#ffffff", 0.2)), rot=(math.degrees(math.atan2(d.z, d.y)), 0, -math.degrees(math.atan2(d.x, d.y))))
        if P.get("crystals"):
            for k in range(5):
                crystal(m, "body", ((k - 2) * 0.2 * S, ch * 0.9, ((k % 2) - 0.5) * 0.3 * S), 0.16 * S, 0.45 * S, ctx.en if k % 2 else ctx.acc, emit=1.0, tag="glow")
        m.part("head", "body", (0, 0.1 * ch, cl * 0.8))
        stalk = P.get("stalk", 0.35) * S
        for sx in (1, -1):
            segment(m, "head", (sx * 0.2 * S, 0, 0), (sx * 0.25 * S, stalk, 0.05 * S), 0.07 * S, base)
            m.box("head", (sx * 0.25 * S, stalk + 0.06 * S, 0.06 * S), (0.16 * S,) * 3, ctx.en if ctx.L >= 3 else "#101010", emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
            m.box("head", (sx * 0.27 * S, stalk + 0.1 * S, 0.14 * S), (0.05 * S,) * 3, "#ffffff")
        m.box("head", (0, -0.12 * S, 0.05 * S), (0.3 * S, 0.06 * S, 0.06 * S), "#2a1010")
        # pinzas
        for side, sx in (("L", 1), ("R", -1)):
            cl_ = f"claw_{side}"
            big = P.get("clawL" if sx > 0 else "clawR", P.get("claw", 1.0))
            m.part(cl_, "body", (sx * cw * 0.85, 0.0, cl * 0.6))
            segment(m, cl_, (0, 0, 0), (sx * 0.3 * S * big, 0.08 * S, 0.3 * S * big), 0.12 * S * min(big, 1.6), base)
            voxelize(m, cl_, [ell((sx * 0.38 * S * big, 0.12 * S * big, 0.6 * S * big), (0.2 * S * big, 0.17 * S * big, 0.3 * S * big))], v * 0.85,
                     solid(C.get("claw", base)))
            m.part(cl_ + "f", cl_, (sx * 0.38 * S * big, 0.0, 0.8 * S * big))
            segment(m, cl_ + "f", (0, 0, 0), (sx * 0.02 * S, -0.02 * S, 0.35 * S * big), (0.1 * S * big, 0.08 * S * big), C.get("clawTip", mix(C.get("claw", base), "#000000", 0.3)))
        nl = P.get("legs", 4)
        for i in range(nl):
            for side, sx in (("L", 1), ("R", -1)):
                lg = f"leg{i}_{side}"
                z = (0.35 - i * 0.8 / max(nl - 1, 1)) * cl
                m.part(lg, "body", (sx * cw * 0.8, -0.1 * ch, z))
                kn = Vector((sx * legL * 0.6, legL * 0.35, (i - 1.5) * 0.12 * S))
                ft = Vector((sx * legL * 1.0, -legL * 0.55, (i - 1.5) * 0.2 * S))
                segment(m, lg, (0, 0, 0), kn, 0.08 * S, leg_c)
                segment(m, lg, kn, ft, 0.065 * S, leg_c)
                if kind == "spider":
                    m.box(lg, kn, (0.12 * S,) * 3, mix(leg_c, "#ffffff", 0.15))
        if kind == "hermit":  # caparazón de caracola
            m.part("shell", "body", (0, ch * 0.6, -cl * 0.6))
            sc = C.get("shell", "#e8c8a0")
            for j in range(22):
                a = j * 0.5
                r = 0.55 * S * math.exp(-0.06 * j)
                p = Vector((math.cos(a) * r * 0.5, 0.25 * S + j * 0.035 * S, math.sin(a) * r - 0.1 * S))
                voxelize(m, "shell", [ell(tuple(p), (r * 0.7, r * 0.6, r * 0.7))], v, lambda p_, n, j=j: sc if j % 3 else mix(sc, "#8a5a3a", 0.4))
    else:  # langosta, gamba, gamba mantis, cacerola de mar, isópodo
        L_ = P.get("len", 1.0) * S
        bw = P.get("bw", 0.32) * S
        m.part("body", "root", (0, 0.7 * S if kind != "isopod" else 0.4 * S, 0))
        if kind == "isopod":
            for j in range(8):
                z = (0.55 - j * 0.16) * L_
                w_ = bw * (1.1 - 0.4 * abs(j - 3.5) / 3.5)
                voxelize(m, "body", [ell((0, 0, z), (w_ * 1.6, 0.3 * S, 0.12 * L_), 0.0, 3)], v, (lambda p, n, j=j: base if j % 2 else mix(base, "#ffffff", 0.12)))
            head_z = 0.7 * L_
        elif kind == "horseshoe":
            voxelize(m, "body", [ell((0, 0, 0.1 * L_), (0.8 * S, 0.28 * S, 0.7 * S), 0.0, 3)], v, bsk, carve=[ell((0, -0.35 * S, 0.1 * L_), (0.85 * S, 0.3 * S, 0.75 * S))])
            m.part("tail0", "body", (0, 0, -0.55 * S))
            segment(m, "tail0", (0, 0, 0), (0, 0.05 * S, -1.1 * S), 0.08 * S, mix(base, "#000000", 0.2))
            tails = [("tail", 1)]
            head_z = 0.7 * S
        else:
            voxelize(m, "body", [ell((0, 0, 0.25 * L_), (bw, bw * 0.9, 0.4 * L_), 0.02, 3)], v, bsk)
            head_z = 0.62 * L_
            parent, piv = "body", Vector((0, 0, -0.1 * L_))
            n = 6
            for j in range(n):
                nm = f"tail{j}"
                curl = P.get("curl", 8)
                m.part(nm, parent, tuple(piv), (curl, 0, 0))
                r = bw * (0.95 - 0.08 * j)
                voxelize(m, nm, [ell((0, 0, -0.12 * L_), (r, r * 0.8, 0.13 * L_))], v * 0.85, (lambda p, n_, j=j: base if j % 2 else mix(base, "#ffffff", 0.15)) if kind != "mantis" else bsk)
                parent, piv = nm, Vector((0, 0, -0.2 * L_))
            fc = C.get("fan", mix(base, "#000000", 0.15))
            for k in range(5):
                a = math.radians(-50 + k * 25)
                m.box(f"tail{n - 1}", (math.sin(a) * 0.25 * S, 0, -0.25 * L_ - math.cos(a) * 0.15 * S), (0.16 * S, 0.04 * S, 0.3 * S), fc, r=(0, math.degrees(a), 0))
            tails = [("tail", n)]
        m.part("head", "body", (0, 0.05 * S, head_z))
        eyes(m, "head", (0, 0.15 * S, 0.1 * S), 0.16 * S, 0.14 * S, ctx.en if ctx.L >= 3 else "#101010", glow=ctx.eye_glow, yaw=40, style="bead")
        if kind != "isopod" and kind != "horseshoe":
            for sx in (1, -1):  # antenas largas
                pts = [Vector((sx * (0.08 + 0.4 * u) * S, 0.1 * S + 0.5 * u * S, 0.1 * S + 1.4 * u * S * P.get("antL", 1.0) - 0.6 * u * u * S)) for u in (j / 6 for j in range(7))]
                polyline(m, "head", pts, 0.035 * S + 0.01, C.get("antenna", base))
        if kind == "lobster":
            for side, sx in (("L", 1), ("R", -1)):
                cl_ = f"claw_{side}"
                m.part(cl_, "head", (sx * 0.2 * S, -0.05 * S, 0.0))
                segment(m, cl_, (0, 0, 0), (sx * 0.4 * S, 0.05 * S, 0.4 * S), 0.12 * S, base)
                voxelize(m, cl_, [ell((sx * 0.5 * S, 0.08 * S, 0.85 * S), (0.2 * S, 0.14 * S, 0.38 * S))], v * 0.85, solid(C.get("claw", base)))
                segment(m, cl_, (sx * 0.5 * S, 0.0, 1.15 * S), (sx * 0.5 * S, 0.0, 1.45 * S), (0.1 * S, 0.07 * S), mix(base, "#000000", 0.25))
        if kind == "mantis":  # gamba mantis: mazas
            for side, sx in (("L", 1), ("R", -1)):
                cl_ = f"claw_{side}"
                m.part(cl_, "head", (sx * 0.18 * S, -0.1 * S, 0.05 * S))
                segment(m, cl_, (0, 0, 0), (sx * 0.1 * S, -0.3 * S, 0.25 * S), 0.1 * S, C.get("claw", "#ff4a8a"))
                m.box(cl_, (sx * 0.1 * S, -0.32 * S, 0.3 * S), (0.16 * S, 0.16 * S, 0.16 * S), C.get("claw", "#ff4a8a"))
        nl = P.get("legs", 5)
        for i in range(nl):
            for side, sx in (("L", 1), ("R", -1)):
                lg = f"leg{i}_{side}"
                m.part(lg, "body", (sx * bw * 0.8, -0.2 * S, (0.45 - i * 0.12) * L_))
                k_ = 0.45 if kind == "isopod" else 1.0
                segment(m, lg, (0, 0, 0), (sx * 0.35 * S * k_, -0.1 * S, 0.05 * S), 0.05 * S, leg_c)
                segment(m, lg, (sx * 0.35 * S * k_, -0.1 * S, 0.05 * S), (sx * 0.45 * S * k_, -0.45 * S * k_, 0.1 * S), 0.04 * S, leg_c)
    return dict(S=S, v=v, body="body", head="head", hover=P.get("hover", 0), tails=tails, heads=["head"], kind=kind, nlegs=P.get("legs", 4))


def anim_crust(m, info, P, L):
    from pets import anim_common
    has = m.parts
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {"body": {"p": (0.08 * S * math.sin(a * 2) if info["kind"] in ("crab", "fiddler", "ghost", "spider", "king", "coconut") else 0, 0.02 * S * abs(math.sin(a * 4)), 0),
                         "r": quat((0, 0, 3 * math.sin(a * 4)))}}
        for side, sx in (("L", 1), ("R", -1)):
            if f"claw_{side}" in has:
                pose[f"claw_{side}"] = {"r": quat((10 * math.sin(a * 2), sx * 12 * math.sin(a * 2), 0))}
            if f"claw_{side}f" in has:
                pose[f"claw_{side}f"] = {"r": quat((0, sx * 18 * max(0.0, math.sin(a * 4)), 0))}
            for i in range(6):
                nm = f"leg{i}_{side}"
                if nm in has:
                    pose[nm] = {"r": quat((0, 0, 12 * math.sin(a * 4 + i * 1.7 + (0 if sx > 0 else math.pi))))}
        anim_common(pose, m, info, t, L)
        for j in range(6):
            if f"tail{j}" in has:
                pose[f"tail{j}"] = {"r": quat((6 * math.sin(a * 2 - j * 0.6), 0, 0))}
        return pose
    return f


BUILD = {"bird": bird, "fish": fish, "bug": bug, "crust": crust}
ANIM = {"bird": anim_bird, "fish": anim_fish, "bug": anim_bug, "crust": anim_crust}
