"""Cefalópodos y bichos marinos blandos, cuerpos en cadena (serpiente, gusanos,
orugas, dragón oriental), tortugas y caracoles, ranas, primates y bípedos
(incluidos gólems y robots), criaturas mágicas (slime, fantasma, ojo...),
murciélagos y accesorios.
"""

import math

from mathutils import Vector

from eggs import _wing
from eggs_themes import flame, membrane_wing, vnoise
from pk_common import TAU, eyes, mix, shades, skin, solid
from pk_quad import _sk, ears, horns, tail, wings
from sculpt import cap, ell, surface_point, voxelize
from voxel import crystal, polyline, quat, ring, segment


def _ac():
    from pets import anim_common
    return anim_common


# ============================================================================= CEFALÓPODOS Y BLANDOS
def ceph(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#c84a6a")
    kind = P.get("kind", "octopus")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, pat=P.get("pat"), pc=C.get("pc"), pc2=C.get("pc2"), ps=P.get("ps", 0.5), belly=C.get("belly")))
    info = dict(S=S, v=v, body="body", head="body", hover=P.get("hover", 0.5), tails=[], heads=[], kind=kind, arms=[])
    glow_soft = P.get("glowBody", 0.0)
    if glow_soft:
        base_fn = bsk
        bsk = lambda p, n: (base_fn(p, n), glow_soft, "glow") if not isinstance(base_fn(p, n), tuple) else base_fn(p, n)
    if kind in ("octopus", "dumbo", "kraken", "vampire", "cables"):
        m.part("body", "root", (0, 1.3 * S, 0))
        mh = P.get("mantle", 0.8)
        voxelize(m, "body", [ell((0, 0.35 * S * mh, -0.1 * S), (0.62 * S, 0.8 * S * mh, 0.65 * S), 0.04, 3), ell((0, -0.1 * S, 0.05 * S), (0.55 * S, 0.45 * S, 0.55 * S))], v, bsk)
        eyes(m, "body", (0, 0.05 * S, 0.55 * S), 0.3 * S, 0.3 * S, ctx.en if ctx.L >= 3 else C.get("eye", "#f2c14e"), glow=ctx.eye_glow, yaw=30, slit=True,
             lid=mix(base, "#000000", 0.2))
        if kind == "dumbo":
            for side, sx in (("L", 1), ("R", -1)):
                m.part(f"ear_{side}", "body", (sx * 0.55 * S, 0.6 * S, -0.1 * S))
                voxelize(m, f"ear_{side}", [ell((sx * 0.3 * S, 0.1 * S, 0), (0.35 * S, 0.25 * S, 0.06 * S))], v * 0.8, bsk)
        n = P.get("arms", 8)
        for k in range(n):
            a = k / n * TAU + 0.2
            tn = f"arm{k}"
            m.part(tn, "body", (math.cos(a) * 0.4 * S, -0.35 * S, math.sin(a) * 0.4 * S), (0, -math.degrees(a) + 90, 0))
            ln = P.get("armL", 1.0) * S
            pts = []
            for j in range(8):
                u = j / 7
                pts.append(Vector((0, -0.3 * u * ln + 0.35 * ln * max(0, u - 0.55) ** 2 * 4, (0.15 + 1.0 * u) * ln)))
            curl_end = P.get("curl", True)
            if curl_end:
                c = pts[-1]
                for j in range(4):
                    a2 = (j + 1) * 0.9
                    pts.append(c + Vector((0, 0.18 * ln * math.sin(a2), 0.18 * ln * (1 - math.cos(a2)) * -0.6 + 0.12 * ln * math.sin(a2) * 0.4)))
            for j in range(len(pts) - 1):
                r0 = (0.2 * S) * (1 - j / (len(pts) + 1)) + 0.02
                if kind == "cables":
                    segment(m, tn, pts[j], pts[j + 1], (r0 * 1.2, r0 * 1.2), "#2a2a30" if j % 3 else ctx.en, emit=1.4 if j % 3 == 0 else 0, tag="glow" if j % 3 == 0 else None)
                else:
                    voxelize(m, tn, [cap(tuple(pts[j]), tuple(pts[j + 1]), r0, r0 * 0.92)], v * 0.8, bsk)
                    if j % 2 == 0 and kind != "vampire":
                        m.box(tn, pts[j] + Vector((0, -r0 * 0.9, 0)), (r0 * 0.7, 0.05 * S, r0 * 0.7), C.get("sucker", mix(base, "#ffffff", 0.55)))
            info["arms"].append(tn)
        if kind == "vampire":  # membrana entre brazos
            for k in range(n):
                a, b = k / n * TAU + 0.2, (k + 1) / n * TAU + 0.2
                for j in range(4):
                    r = (0.5 + j * 0.25) * S
                    pa = Vector((math.cos(a) * r, -0.45 * S - j * 0.18 * S, math.sin(a) * r))
                    pb = Vector((math.cos(b) * r, -0.45 * S - j * 0.18 * S, math.sin(b) * r))
                    segment(m, "body", pa, pb, (0.2 * S, 0.04 * S), C.get("web", mix(base, "#000000", 0.35)))
    elif kind == "squid":
        m.part("body", "root", (0, 1.4 * S, 0), (-12, 0, 0))
        voxelize(m, "body", [cap((0, 0, 0), (0, 0, -1.3 * S), 0.46 * S, 0.14 * S), ell((0, 0, 0.1 * S), (0.42 * S, 0.42 * S, 0.34 * S))], v, bsk)
        for sx in (1, -1):
            voxelize(m, "body", [ell((sx * 0.3 * S, 0, -1.15 * S), (0.3 * S, 0.06 * S, 0.25 * S))], v * 0.8, bsk)
        eyes(m, "body", (0, 0.0, 0.35 * S), 0.32 * S, 0.24 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=70)
        for k in range(10):
            a = k / 10 * TAU
            tn = f"arm{k}"
            m.part(tn, "body", (math.cos(a) * 0.2 * S, math.sin(a) * 0.2 * S, 0.35 * S))
            ln = (2.0 if k in (2, 7) else 0.9) * S * P.get("armL", 1.0)
            segment(m, tn, (0, 0, 0), (math.cos(a) * 0.15 * S, math.sin(a) * 0.15 * S, ln), 0.09 * S, base)
            if k in (2, 7):
                voxelize(m, tn, [ell((math.cos(a) * 0.15 * S, math.sin(a) * 0.15 * S, ln), (0.13 * S, 0.13 * S, 0.25 * S))], v * 0.8, bsk)
            info["arms"].append(tn)
    elif kind == "cuttlefish":
        m.part("body", "root", (0, 1.2 * S, 0))
        voxelize(m, "body", [ell((0, 0, -0.1 * S), (0.5 * S, 0.38 * S, 0.8 * S), 0.02, 3)], v, bsk)
        for sx in (1, -1):
            for j in range(10):
                z = (0.55 - j * 0.13) * S
                m.box("body", (sx * 0.52 * S, -0.08 * S + 0.04 * S * math.sin(j), z), (0.22 * S, 0.04 * S, 0.14 * S), C.get("fin", mix(base, "#ffffff", 0.25)), r=(0, 0, sx * -15))
        eyes(m, "body", (0, 0.18 * S, 0.62 * S), 0.32 * S, 0.24 * S, ctx.en if ctx.L >= 3 else "#f2c14e", glow=ctx.eye_glow, yaw=50, slit=True)
        for k in range(8):
            a = math.radians(-60 + k * 17)
            tn = f"arm{k}"
            m.part(tn, "body", (math.sin(a) * 0.25 * S, -0.1 * S + math.cos(a) * 0.05 * S, 0.7 * S))
            segment(m, tn, (0, 0, 0), (math.sin(a) * 0.15 * S, -0.1 * S, 0.5 * S), 0.09 * S, base)
            info["arms"].append(tn)
    elif kind == "nautilus":
        m.part("body", "root", (0, 1.3 * S, 0))
        sc = C.get("shell", "#f2e8d8")
        stripe = C.get("stripe", "#b85a2a")
        for j in range(30):
            a = j * 0.35
            r = 0.75 * S * math.exp(-0.055 * j)
            p = Vector((0, math.sin(a) * r * 0.9, -math.cos(a) * r * 0.9 - 0.1 * S))
            voxelize(m, "body", [ell(tuple(p), (0.42 * S * (1 - j / 45), r * 0.55, r * 0.55))], v, lambda p_, n, j=j: stripe if (j % 4 == 0 and p_.y > -0.2 * S) else sc)
        m.part("head", "body", (0, -0.25 * S, 0.55 * S))
        voxelize(m, "head", [ell((0, 0, 0), (0.35 * S, 0.3 * S, 0.25 * S))], v, solid(C.get("body", "#d8a888")))
        eyes(m, "head", (0, 0.05 * S, 0.2 * S), 0.28 * S, 0.18 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=60, style="bead")
        for k in range(14):
            a = math.radians(-70 + k * 10)
            tn = f"arm{k}"
            m.part(tn, "head", (math.sin(a) * 0.2 * S, -0.1 * S, 0.2 * S))
            segment(m, tn, (0, 0, 0), (math.sin(a) * 0.25 * S, -0.3 * S, 0.45 * S), 0.05 * S, "#e8c8a8")
            info["arms"].append(tn)
        info["head"] = "head"
    elif kind in ("jelly", "siphon", "comb"):
        m.part("body", "root", (0, 1.9 * S, 0))
        if kind == "jelly":
            voxelize(m, "body", [ell((0, 0.2 * S, 0), (0.85 * S, 0.6 * S, 0.85 * S))], v,
                     lambda p, n: (C.get("rim", base) if p.y < 0.0 else (mix(base, "#ffffff", 0.35) if vnoise(p.x * 4, p.y * 4, p.z * 4) > 0.62 else base), 0.35 + 0.08 * ctx.L, "glow"),
                     carve=[ell((0, -0.25 * S, 0), (0.78 * S, 0.45 * S, 0.78 * S))])
            for k in range(4):  # gónadas en trébol (medusa luna)
                a = k / 4 * TAU
                m.box("body", (math.cos(a) * 0.25 * S, 0.55 * S, math.sin(a) * 0.25 * S), (0.2 * S, 0.06 * S, 0.2 * S), C.get("gonad", "#ff9ad8"), emit=0.8, tag="glow")
            for k in range(4):  # brazos orales
                tn = f"arm{k}"
                a = k / 4 * TAU + 0.4
                m.part(tn, "body", (math.cos(a) * 0.15 * S, -0.1 * S, math.sin(a) * 0.15 * S))
                for j in range(6):
                    m.box(tn, (0.05 * S * math.sin(j), -(0.15 + j * 0.25) * S, 0.05 * S * math.cos(j)), (0.18 * S, 0.28 * S, 0.1 * S), C.get("oral", mix(base, "#ffffff", 0.3)),
                          r=(0, j * 40, 0), emit=0.4, tag="glow")
                info["arms"].append(tn)
            for k in range(16):  # tentáculos finos del borde
                a = k / 16 * TAU
                tn = f"tent{k}"
                m.part(tn, "body", (math.cos(a) * 0.78 * S, -0.1 * S, math.sin(a) * 0.78 * S))
                segment(m, tn, (0, 0, 0), (0, -1.6 * S, 0), 0.04 * S + 0.01, C.get("tent", mix(base, "#ffffff", 0.4)), emit=0.5, tag="glow")
                info["arms"].append(tn)
        elif kind == "siphon":  # carabela portuguesa
            voxelize(m, "body", [ell((0, 0.2 * S, 0), (0.45 * S, 0.45 * S, 0.85 * S))], v, lambda p, n: (mix(base, "#ffffff", 0.3) if p.y > 0.4 * S else base, 0.35, "glow"))
            for j in range(8):
                m.box("body", (0, 0.62 * S + 0.06 * S * math.sin(j), (0.6 - j * 0.17) * S), (0.06 * S, 0.22 * S, 0.17 * S), C.get("crest", "#ff6ad8"), emit=0.6, tag="glow")
            for k in range(10):
                tn = f"tent{k}"
                m.part(tn, "body", ((k % 3 - 1) * 0.2 * S, -0.2 * S, (0.5 - k * 0.1) * S))
                pts = [Vector((0.08 * S * math.sin(j * 1.3 + k), -(j * 0.3) * S, 0)) for j in range(8)]
                polyline(m, tn, pts, 0.05 * S + 0.01, C.get("tent", "#5a6aff") if k % 2 else "#a85aff", emit=0.5, tag="glow")
                info["arms"].append(tn)
        else:  # ctenóforo
            voxelize(m, "body", [ell((0, 0, 0), (0.55 * S, 0.85 * S, 0.55 * S))], v, lambda p, n: ("#e8f4ff", 0.25, "glow"))
            bands = ["#ff5a7a", "#ffd23a", "#5aff8a", "#5ad8ff", "#a85aff", "#ff8a3a", "#5affe0", "#ff5ad8"]
            for k in range(8):
                a = k / 8 * TAU
                for j in range(9):
                    b = math.radians(-70 + j * 17.5)
                    p = Vector((math.cos(a) * math.cos(b) * 0.57 * S, math.sin(b) * 0.87 * S, math.sin(a) * math.cos(b) * 0.57 * S))
                    m.box("body", p, (0.08 * S, 0.12 * S, 0.08 * S), bands[(k + j) % 8], emit=1.6, tag="twinkle")
    elif kind == "starfish":
        m.part("body", "root", (0, 0.25 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.35 * S, 0.18 * S, 0.35 * S))], v, bsk)
        for k in range(5):
            a = k / 5 * TAU + math.pi / 2
            tn = f"arm{k}"
            m.part(tn, "body", (math.cos(a) * 0.25 * S, 0, math.sin(a) * 0.25 * S), (0, -math.degrees(a) + 90, 0))
            voxelize(m, tn, [cap((0, 0, 0), (0, 0.05 * S, 0.9 * S), 0.25 * S, 0.07 * S)], v * 0.85, bsk)
            for j in range(5):
                m.box(tn, (0, 0.18 * S - j * 0.02 * S, (0.1 + j * 0.17) * S), (0.07 * S,) * 3, C.get("pc", mix(base, "#ffffff", 0.4)))
            info["arms"].append(tn)
        eyes(m, "body", (0, 0.17 * S, 0.12 * S), 0.12 * S, 0.14 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=0, style="bead")
        info["hover"] = 0
    elif kind == "urchin":
        m.part("body", "root", (0, 0.55 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.5 * S, 0.42 * S, 0.5 * S))], v, bsk)
        for j in range(70):
            a, b = j * 2.39996, math.acos(1 - 2 * ((j + 0.5) / 70))
            d = Vector((math.sin(b) * math.cos(a), math.cos(b), math.sin(b) * math.sin(a)))
            if d.y < -0.6:
                continue
            p0 = Vector((d.x * 0.5 * S, d.y * 0.42 * S, d.z * 0.5 * S))
            segment(m, "body", p0, p0 + d * 0.65 * S, 0.05 * S, C.get("spine", base) if j % 3 else C.get("spine2", mix(base, "#ffffff", 0.3)),
                    emit=0.8 if (ctx.L >= 3 and j % 5 == 0) else 0, tag="glow" if (ctx.L >= 3 and j % 5 == 0) else None)
        eyes(m, "body", (0, 0.05 * S, 0.5 * S), 0.18 * S, 0.18 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=15)
        info["hover"] = 0
    elif kind == "anemone":
        m.part("body", "root", (0, 0.5 * S, 0))
        voxelize(m, "body", [cap((0, -0.45 * S, 0), (0, 0.3 * S, 0), 0.45 * S, 0.38 * S)], v, bsk)
        for k in range(18):
            a = k / 18 * TAU
            r = 0.3 * S if k % 2 else 0.18 * S
            tn = f"tent{k}"
            m.part(tn, "body", (math.cos(a) * r, 0.32 * S, math.sin(a) * r), (math.sin(a) * 25, 0, -math.cos(a) * 25))
            for j in range(5):
                m.box(tn, (0, (0.1 + j * 0.13) * S, 0), (0.12 * S * (1 - j / 8), 0.15 * S, 0.12 * S * (1 - j / 8)),
                      C.get("tent", "#ff6a9a") if j < 4 else C.get("tip", "#fff0f6"), emit=0.5 if ctx.L >= 2 else 0, tag="glow" if ctx.L >= 2 else None)
            info["arms"].append(tn)
        eyes(m, "body", (0, 0.0, 0.42 * S), 0.16 * S, 0.17 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=15)
        info["hover"] = 0
    elif kind == "nudibranch":
        m.part("body", "root", (0, 0.25 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.35 * S, 0.22 * S, 0.9 * S))], v, bsk)
        for k in range(16):
            sx = 1 if k % 2 else -1
            z = (0.6 - (k // 2) * 0.16) * S
            for j in range(3):
                m.box("body", (sx * 0.35 * S + sx * j * 0.08 * S, 0.12 * S + j * 0.1 * S, z), (0.09 * S, 0.12 * S, 0.09 * S),
                      [C.get("cerata", "#ff8a3a"), C.get("cerata2", "#ffd23a"), "#ffffff"][j], r=(0, 0, -sx * 25))
        for sx in (1, -1):
            segment(m, "body", (sx * 0.1 * S, 0.18 * S, 0.75 * S), (sx * 0.15 * S, 0.5 * S, 0.85 * S), 0.07 * S, C.get("rhino", "#ff8a3a"))
        eyes(m, "body", (0, 0.18 * S, 0.82 * S), 0.12 * S, 0.12 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=10, style="bead")
        info["hover"] = 0
    elif kind == "tardigrade":
        m.part("body", "root", (0, 0.65 * S, 0))
        for j in range(4):
            voxelize(m, "body", [ell((0, 0, (0.45 - j * 0.32) * S), (0.42 * S, 0.4 * S, 0.24 * S), 0.04, 4)], v, bsk)
        voxelize(m, "body", [ell((0, -0.05 * S, 0.68 * S), (0.3 * S, 0.28 * S, 0.22 * S))], v, bsk)
        m.box("body", (0, -0.08 * S, 0.9 * S), (0.18 * S, 0.18 * S, 0.06 * S), "#3a2030")
        eyes(m, "body", (0, 0.1 * S, 0.85 * S), 0.14 * S, 0.1 * S, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=30, style="bead")
        for j in range(4):
            for side, sx in (("L", 1), ("R", -1)):
                tn = f"leg{j}_{side}"
                m.part(tn, "body", (sx * 0.3 * S, -0.25 * S, (0.45 - j * 0.32) * S))
                voxelize(m, tn, [cap((0, 0, 0), (sx * 0.12 * S, -0.3 * S, 0.02 * S), 0.12 * S, 0.1 * S)], v * 0.85, bsk)
                for k in (-1, 1):
                    segment(m, tn, (sx * 0.12 * S, -0.35 * S, 0), (sx * 0.12 * S + k * 0.05 * S, -0.42 * S, 0.08 * S), 0.03 * S + 0.01, "#2a1a1a")
                info["arms"].append(tn)
        info["hover"] = 0
    return info


def anim_ceph(m, info, P, L):
    has = m.parts
    S = info["S"]
    kind = info["kind"]

    def f(t):
        a = t * TAU
        pose = {"body": {"p": (0, (0.18 if info["hover"] else 0.0) * S * math.sin(a * 2), 0), "r": quat((0, 8 * math.sin(a), 0))}}
        if kind in ("jelly", "siphon"):
            k = math.sin(a * 2)
            pose["body"]["s"] = (1 + 0.06 * k, 1 - 0.07 * k, 1 + 0.06 * k)
        if kind == "tardigrade":
            pose["body"] = {"p": (0, 0.02 * S * abs(math.sin(a * 4)), 0), "r": quat((0, 5 * math.sin(a), 0))}
        for i, nm in enumerate(info["arms"]):
            if nm in has:
                if kind == "starfish":
                    pose[nm] = {"r": quat((6 * math.sin(a * 2 + i), 0, 0))}
                elif kind == "tardigrade":
                    pose[nm] = {"r": quat((20 * math.sin(a * 4 + i * 1.7), 0, 0))}
                elif kind == "anemone":
                    pose[nm] = {"r": quat((10 * math.sin(a * 2 + i * 0.7), 0, 8 * math.sin(a * 2 + i)))}
                else:
                    pose[nm] = {"r": quat((14 * math.sin(a * 2 - i * 0.8), 6 * math.sin(a + i), 0))}
        for side, sx in (("L", 1), ("R", -1)):
            if f"ear_{side}" in has:
                pose[f"ear_{side}"] = {"r": quat((0, 0, sx * 25 * math.sin(a * 4)))}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= CADENAS (serpiente, gusanos, orugas, dragón oriental)
def chain(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#3a8a3a")
    kind = P.get("kind", "snake")
    n = P.get("segs", 10)
    r0 = P.get("r", 0.3) * S
    seg = P.get("seg", 0.36) * S
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly", mix(base, "#ffffff", 0.45)), pat=P.get("pat"), pc=C.get("pc"), pc2=C.get("pc2"),
                                        ps=P.get("ps", 0.5), belly_k=-0.4))
    raise_ = P.get("raise", 0.0)
    wav = P.get("wave", 0.35)

    def path(i):  # reposo: cuerpo ondulado en el suelo, cabeza levantada
        u = i / n
        y = r0 + max(0.0, raise_ * (1 - i / 3.0)) * S
        return Vector((math.sin(u * math.pi * 2.2) * wav * S * (0.3 + u), y, -i * seg))
    pts = [path(i) for i in range(n + 1)]
    m.part("body", "root", tuple(pts[0]))
    prev = "body"
    names = ["body"]
    for i in range(1, n):
        nm = f"s{i}"
        m.part(nm, prev, tuple(pts[i] - pts[i - 1]))
        names.append(nm)
        prev = nm
    for i, nm in enumerate(names):
        a = Vector((0, 0, 0))
        b = pts[i + 1] - pts[i]
        taper = P.get("taper", 0.6)
        ra = r0 * (1 - taper * (i / n) ** 1.6)
        rb = r0 * (1 - taper * ((i + 1) / n) ** 1.6)
        if kind in ("caterpillar", "millipede", "worm", "gummy", "sandworm", "larva", "glitch"):
            voxelize(m, nm, [ell(tuple(b * 0.5), (ra * 1.05, ra, seg * 0.62), 0.03 * (kind != "gummy"), 4)], v,
                     (lambda p, n_, i=i: (C.get("pc", base) if i % 2 else base, 0.4 if kind == "gummy" else 0, "glow")) if kind in ("gummy",) else
                     (lambda p, n_, i=i: bsk(p, n_) if i % 2 or not C.get("ring") else C["ring"]))
        else:  # serpiente/anguila/dragón: cápsulas que se solapan (sin huecos)
            voxelize(m, nm, [cap(tuple(a - b.normalized() * ra * 0.4), tuple(b + b.normalized() * rb * 0.3), ra, rb)], v, bsk)
        if kind == "caterpillar":
            if C.get("dots"):
                for sx in (1, -1):
                    m.box(nm, (sx * ra * 0.85, ra * 0.35, b.z * 0.5), (0.06 * S, ra * 0.35, ra * 0.35), C["dots"])
            if P.get("tufts"):
                m.box(nm, (0, ra * 1.05, b.z * 0.5), (0.08 * S, 0.25 * S, 0.08 * S), P["tufts"])
            for sx in (1, -1):  # patitas
                m.box(nm, (sx * ra * 0.6, -ra * 0.85, b.z * 0.5), (0.1 * S, 0.12 * S, 0.1 * S), C.get("feet", mix(base, "#000000", 0.25)))
        if kind == "millipede":
            for sx in (1, -1):
                for k in (0.3, 0.7):
                    segment(m, nm, (sx * ra * 0.7, -ra * 0.4, b.z * k), (sx * ra * 1.3, -ra * 1.0, b.z * k), 0.04 * S + 0.01, C.get("legs", "#e8c890"))
        if kind in ("eel", "oarfish") and i > 0:
            m.box(nm, (0, ra * 0.95 + 0.1 * S, b.z * 0.5), (0.04 * S, 0.22 * S, abs(b.z) * 0.95), C.get("fin", mix(base, "#000000", 0.2)))
            if kind == "oarfish":
                m.box(nm, (0, ra * 0.95 + 0.12 * S, b.z * 0.5), (0.03 * S, 0.24 * S, abs(b.z) * 0.95), "#e83a3a")
        if kind == "dragon" and i > 0:  # cresta y crin
            crystal(m, nm, (0, ra * 1.05, b.z * 0.5), 0.1 * S, 0.3 * S, C.get("crest", ctx.acc), rot=(-30, 0, 0))
            for sx in (1, -1):
                m.box(nm, (sx * ra * 0.5, ra * 0.9, b.z * 0.3), (0.06 * S, 0.18 * S, 0.22 * S), C.get("mane", "#f2ead6"), r=(-40, 0, sx * 25))
        if kind == "glitch" and i % 2:
            for k in range(3):
                m.box(nm, ((k - 1) * ra * 0.7, ra * 0.9, b.z * 0.5), (ra * 0.4, ra * 0.4, ra * 0.4), ctx.en if k % 2 else ctx.acc, emit=1.5, tag="glow")
    # cabeza
    hr = P.get("hr", 1.15) * r0
    m.part("head", "body", (0, 0.02 * S, 0.05 * S), (P.get("headPitch", 0), 0, 0))
    hsk = _sk(ctx, P.get("hskin"), bsk)
    if kind in ("snake", "eel", "dragon", "oarfish"):
        skull = ell((0, 0.05 * hr, 0.55 * hr), (hr * 0.95, hr * 0.7, hr * 1.1))
        hp = [skull, cap((0, 0, -0.4 * hr), (0, 0.02 * hr, 0.4 * hr), r0 * 0.95, r0 * 0.95)]  # cuello dentro del cuerpo: no hay hueco
        voxelize(m, "head", hp, v * 0.85, hsk)
        eyes(m, "head", (0, 0.35 * hr, 1.05 * hr), 0.55 * hr, hr * 0.38, ctx.en if ctx.L >= 3 else C.get("eye", "#f2c14e"), glow=ctx.eye_glow, slit=kind == "snake",
             yaw=50, lid=mix(base, "#000000", 0.15) if kind != "eel" else None)
        m.part("jaw", "head", (0, -0.35 * hr, 0.3 * hr))
        voxelize(m, "jaw", [cap((0, 0, 0), (0, -0.05 * hr, 1.1 * hr), 0.55 * hr, 0.35 * hr)], v * 0.8, lambda p, n_: "#c84a5a" if n_.y > 0.5 else hsk(p, n_))
        if kind == "snake":
            pts_t = [Vector((0, -0.25 * hr, 1.5 * hr)), Vector((0, -0.25 * hr, 2.0 * hr))]
            segment(m, "jaw", (0, 0.05 * hr, 1.0 * hr), (0, 0.05 * hr, 1.55 * hr), (0.08 * hr, 0.03 * hr), "#e8304a")
            for sx in (1, -1):
                m.box("jaw", (sx * 0.06 * hr, 0.05 * hr, 1.65 * hr), (0.05 * hr, 0.03 * hr, 0.18 * hr), "#e8304a", r=(0, sx * 25, 0))
                m.box("head", (sx * 0.3 * hr, -0.35 * hr, 1.35 * hr), (0.06 * hr, 0.25 * hr, 0.06 * hr), "#f6f6f0")
        if kind == "dragon":
            horns(m, "head", "dragon", hr * 1.4, C.get("horn", "#f2d27a"), ctx, size=0.9, x=0.2, y=0.4, z=0.15)
            for sx in (1, -1):  # bigotes
                pts_w = [Vector((sx * (0.4 + 0.9 * u) * hr, -0.2 * hr - 0.4 * u * hr, 1.4 * hr - 0.5 * u * hr + 0.5 * u * u * hr)) for u in (j / 5 for j in range(6))]
                polyline(m, "head", pts_w, 0.08 * hr, C.get("whisker", "#f2d27a"))
            voxelize(m, "head", [ell((0, 0.4 * hr, -0.2 * hr), (hr * 0.9, hr * 0.5, hr * 0.7), 0.3, 3 / S)], v * 0.8, solid(C.get("mane", "#f2ead6")))
    else:
        skull = ell((0, 0.05 * hr, 0.3 * hr), (hr, hr * 0.95, hr * 0.85))
        voxelize(m, "head", [skull], v * 0.85, hsk if kind != "sandworm" else bsk, carve=[ell((0, 0.0, 1.0 * hr), (hr * 0.65, hr * 0.65, hr * 0.4))] if kind == "sandworm" else None)
        if kind == "sandworm":
            for k in range(12):
                a = k / 12 * TAU
                m.box("head", (math.cos(a) * 0.55 * hr, math.sin(a) * 0.55 * hr, 0.85 * hr), (0.08 * hr, 0.25 * hr, 0.08 * hr), "#f6f0e2",
                      r=(0, 0, math.degrees(a) + 90))
            if ctx.L >= 3:
                m.box("head", (0, 0, 0.45 * hr), (0.5 * hr, 0.5 * hr, 0.1 * hr), ctx.en, emit=2.0, tag="glow")
        else:
            st = "bead" if kind in ("worm", "larva") else "round"
            eyes(m, "head", (0, 0.25 * hr, 1.05 * hr), 0.4 * hr, hr * 0.35, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=20, style=st)
            m.box("head", (0, -0.3 * hr, 1.08 * hr), (0.35 * hr, 0.08 * hr, 0.04 * hr), "#3a1a1a")
            if kind == "caterpillar":
                for sx in (1, -1):
                    segment(m, "head", (sx * 0.3 * hr, 0.7 * hr, 0.4 * hr), (sx * 0.45 * hr, 1.3 * hr, 0.6 * hr), 0.06 * S, C.get("antenna", "#1a1a1a"))
                    m.box("head", (sx * 0.45 * hr, 1.32 * hr, 0.6 * hr), (0.1 * S,) * 3, C.get("antTip", "#ffd23a"))
            if kind == "millipede":
                for sx in (1, -1):
                    segment(m, "head", (sx * 0.3 * hr, 0.4 * hr, 0.8 * hr), (sx * 0.6 * hr, 0.9 * hr, 1.4 * hr), 0.05 * S, C.get("legs", "#e8c890"))
    if kind == "dragon":  # patas
        for j, i in enumerate((1, n - 3)):
            for side, sx in (("L", 1), ("R", -1)):
                lg = f"leg{j}_{side}"
                m.part(lg, names[i], (sx * r0 * 0.8, -r0 * 0.3, 0))
                voxelize(m, lg, [cap((0, 0, 0), (sx * 0.35 * S, -0.45 * S, 0.1 * S), 0.14 * S, 0.11 * S)], v * 0.85, bsk)
                for k in (-1, 0, 1):
                    segment(m, lg, (sx * 0.35 * S, -0.45 * S, 0.1 * S), (sx * 0.35 * S + k * 0.08 * S, -0.5 * S, 0.3 * S), 0.05 * S, C.get("claw", "#f2d27a"))
    if P.get("rattle"):
        for k in range(3):
            m.box(names[-1], (0, 0, pts[n].z - pts[n - 1].z - k * 0.1 * S), (r0 * 0.6, r0 * 0.5, 0.1 * S), "#c8b890")
    hover = P.get("hover", 0)
    return dict(S=S, v=v, body="body", head="head", hover=hover, tails=[], heads=["head"], chain=names, kind=kind)


def anim_chain(m, info, P, L):
    has = m.parts
    kind = info["kind"]
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {}
        for i, nm in enumerate(info["chain"]):
            if kind in ("caterpillar", "worm", "larva", "gummy"):  # oruga: ola vertical
                pose[nm] = {"r": quat((10 * math.sin(a * 2 - i * 0.9), 4 * math.sin(a - i * 0.5), 0))}
            else:
                pose[nm] = {"r": quat((0, (9 + L) * math.sin(a * 2 - i * 0.7), 0))}
        if kind in ("dragon", "eel", "oarfish"):
            pose["body"] = {"p": (0, 0.15 * S * math.sin(a * 2), 0), "r": pose["body"]["r"]}
        pose["head"] = {"r": quat((-5 * math.sin(a * 2), -(6 + L) * math.sin(a * 2 + 0.6), 0))}
        if "jaw" in has:
            pose["jaw"] = {"r": quat((18 * max(0.0, math.sin(a + 1)) ** 6, 0, 0))}
        for j in range(2):
            for side, sx in (("L", 1), ("R", -1)):
                if f"leg{j}_{side}" in has:
                    pose[f"leg{j}_{side}"] = {"r": quat((22 * math.sin(a * 2 + j * math.pi + (0 if sx > 0 else math.pi)), 0, 0))}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= TORTUGAS Y CARACOLES
def shellback(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    kind = P.get("kind", "tortoise")
    shell_c = C.get("shell", "#7a5a34")
    skin_c = C.get("skin", "#8a9a5a")
    ssk = _sk(ctx, dict(base=skin_c, belly=C.get("belly")))
    tails = []
    if kind in ("snail", "slug"):
        m.part("body", "root", (0, 0.25 * S, 0))
        voxelize(m, "body", [cap((0, 0, -0.65 * S), (0, 0.05 * S, 0.45 * S), 0.22 * S, 0.3 * S), ell((0, 0.25 * S, 0.55 * S), (0.26 * S, 0.3 * S, 0.24 * S))], v, ssk)
        m.part("head", "body", (0, 0.45 * S, 0.62 * S))
        for side, sx in (("L", 1), ("R", -1)):
            segment(m, "head", (sx * 0.1 * S, 0, 0), (sx * 0.2 * S, 0.5 * S, 0.12 * S), 0.07 * S, skin_c)
            m.box("head", (sx * 0.2 * S, 0.55 * S, 0.12 * S), (0.13 * S,) * 3, ctx.en if ctx.L >= 3 else "#101010", emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
            segment(m, "head", (sx * 0.12 * S, -0.15 * S, 0.12 * S), (sx * 0.18 * S, -0.1 * S, 0.35 * S), 0.05 * S, skin_c)
        m.box("head", (0, -0.12 * S, 0.24 * S), (0.18 * S, 0.04 * S, 0.04 * S), "#3a1a1a")
        if kind == "snail":
            m.part("shell", "body", (0, 0.3 * S, -0.2 * S))
            sc2 = C.get("shell2", mix(shell_c, "#000000", 0.3))
            for j in range(28):
                a = j * 0.42
                r = 0.6 * S * math.exp(-0.06 * j)
                p = Vector((0, 0.35 * S + math.sin(a) * r * 0.85, -math.cos(a) * r * 0.85))
                voxelize(m, "shell", [ell(tuple(p), (0.35 * S * (1 - j / 40), r * 0.5, r * 0.5))], v,
                         lambda p_, n, j=j: (sc2 if j % 3 == 0 else shell_c) if not P.get("geode") else ((ctx.en, 1.5, "glow") if j % 3 == 0 else shell_c))
        return dict(S=S, v=v, body="body", head="head", hover=0, tails=[], heads=["head"], kind=kind)
    # tortugas
    sea = kind == "sea"
    sh = Vector(P.get("shellR", (0.9, 0.55 if not sea else 0.35, 1.05))) * S
    leg = P.get("leg", 0.35) * S
    m.part("body", "root", (0, leg * 0.8 + sh.y * 0.2, 0))

    def scute(p, n):
        if n.y < -0.3:
            return C.get("plastron", "#e8d8a0")
        cx, cz = (p.x / (0.36 * S)) % 1, (p.z / (0.36 * S) + (0.5 if int(p.x / (0.36 * S) + 50) % 2 else 0)) % 1
        if n.y > 0 and (cx < 0.12 or cz < 0.12):
            return C.get("seam", mix(shell_c, "#000000", 0.4))
        h = vnoise(p.x * 4, p.y * 4, p.z * 4)
        return C.get("shell2", mix(shell_c, "#ffffff", 0.15)) if h > 0.6 else shell_c
    carve = [ell((0, -sh.y * 0.75, 0), (sh.x * 1.1, sh.y * 0.65, sh.z * 1.1))]
    voxelize(m, "body", [ell((0, sh.y * 0.35, 0), tuple(sh), 0.03, 3)], v, scute, carve=carve)
    voxelize(m, "body", [ell((0, -sh.y * 0.12, 0), (sh.x * 0.95, sh.y * 0.25, sh.z * 0.95))], v, ssk)
    if P.get("ridges"):  # tortuga caimán: crestas
        for sx in (-1, 0, 1):
            for j in range(6):
                crystal(m, "body", (sx * 0.35 * S, sh.y * (1.25 - 0.12 * abs(sx)) - abs(j - 2.5) * 0.05 * S, (0.6 - j * 0.24) * S), 0.15 * S, 0.3 * S, mix(shell_c, "#000000", 0.25), rot=(-25, 0, 0))
    if P.get("volcano"):
        m.part("volcano", "body", (0, sh.y * 1.25, -0.05 * S))
        voxelize(m, "volcano", [cap((0, 0, 0), (0, 0.6 * S, 0), 0.55 * S, 0.25 * S)], v, skin(["#4a3a34", "#3a2e2a", "#5a4a40"], ctx=ctx),
                 carve=[cap((0, 0.35 * S, 0), (0, 0.8 * S, 0), 0.1 * S, 0.2 * S)])
        m.box("volcano", (0, 0.55 * S, 0), (0.3 * S, 0.06 * S, 0.3 * S), "#ff6a1a", emit=2.5, tag="fire")
        for k in range(5):
            a = k / 5 * TAU
            m.box("volcano", (math.cos(a) * 0.32 * S, 0.35 * S - k * 0.05 * S, math.sin(a) * 0.32 * S), (0.08 * S, 0.3 * S, 0.08 * S), "#ff8a2a", emit=2.0, tag="fire")
    if P.get("tree"):  # árbol o montaña encima
        m.part("tree", "body", (0, sh.y * 1.25, 0))
        polyline(m, "tree", [Vector((0, 0, 0)), Vector((0.05 * S, 0.6 * S, 0)), Vector((-0.05 * S, 1.0 * S, 0.05 * S))], 0.16 * S, "#5a3a24")
        voxelize(m, "tree", [ell((0, 1.25 * S, 0), (0.6 * S, 0.45 * S, 0.6 * S), 0.2, 3 / S), ell((0.35 * S, 1.0 * S, 0.2 * S), (0.35 * S, 0.3 * S, 0.35 * S), 0.2, 3 / S)], v,
                 lambda p, n: C.get("leaf2", "#5ab04a") if vnoise(p.x * 3, p.y * 3, p.z * 3) > 0.55 else C.get("leaf", "#3a8a3a"))
    if P.get("mountain"):
        m.part("tree", "body", (0, sh.y * 1.1, 0))
        voxelize(m, "tree", [cap((0, 0, 0), (0, 0.9 * S, 0), 0.7 * S, 0.1 * S, 0.15, 3 / S), cap((0.4 * S, 0, 0.2 * S), (0.45 * S, 0.55 * S, 0.25 * S), 0.4 * S, 0.08 * S, 0.15, 3 / S)], v,
                 lambda p, n: "#f2f6fa" if p.y > 0.6 * S else ("#5a7a3a" if p.y < 0.2 * S and n.y > 0.3 else "#7a7a80"))
    if P.get("world"):  # tortuga cósmica: planeta encima
        m.part("tree", "body", (0, sh.y * 1.3 + 0.6 * S, 0))
        voxelize(m, "tree", [ell((0, 0, 0), (0.75 * S,) * 3)], v,
                 lambda p, n: ("#2a7ad8", 0.2, "glow") if vnoise(p.x * 2, p.y * 2, p.z * 2) < 0.5 else ("#3aa84a" if p.y < 0.55 * S else "#f2f6fa"))
        ring(m, "tree", 1.1 * S, 40, (0.08 * S, 0.04 * S), ctx.en, rot=(20, 0, 10), emit=1.6, tag="neon")
    if P.get("mech"):
        for k in range(6):
            a = k / 6 * TAU
            m.box("body", (math.cos(a) * sh.x * 0.6, sh.y * 1.05, math.sin(a) * sh.z * 0.6), (0.12 * S, 0.12 * S, 0.12 * S), ctx.en, emit=1.6, tag="glow")
        m.box("body", (0, sh.y * 1.32, 0), (0.25 * S, 0.12 * S, 0.25 * S), ctx.metal, metal=1)
    if P.get("crystalShell"):
        for k in range(7):
            a = k / 7 * TAU
            crystal(m, "body", (math.cos(a) * 0.45 * S, sh.y * 1.05, math.sin(a) * 0.5 * S), 0.2 * S, 0.55 * S, ctx.en if k % 2 else ctx.acc, rot=(math.sin(a) * 25, 0, -math.cos(a) * 25),
                    emit=1.0, tag="glow")
    m.part("head", "body", (0, 0.05 * S, sh.z * 0.9))
    hs = P.get("hs", 0.32) * S
    skull = ell((0, 0.05 * hs, 0.5 * hs), (hs, hs * 0.9, hs * 1.1))
    voxelize(m, "head", [skull, cap((0, 0, -0.3 * hs), (0, 0.02 * hs, 0.3 * hs), hs * 0.75, hs * 0.75)], v * 0.85, ssk)
    eyes(m, "head", (0, 0.3 * hs, 1.2 * hs), 0.55 * hs, hs * 0.38, ctx.en if ctx.L >= 3 else "#1a1a1a", glow=ctx.eye_glow, yaw=45, style="bead" if not P.get("bigEyes") else "round")
    m.box("head", (0, -0.25 * hs, 1.45 * hs), (0.6 * hs, 0.08 * hs, 0.08 * hs), "#2a1a14")
    if P.get("beak"):
        segment(m, "head", (0, 0.0, 1.4 * hs), (0, -0.4 * hs, 1.7 * hs), (0.3 * hs, 0.2 * hs), "#3a3020")
    for name, sx, sz in (("FL", 1, 1), ("FR", -1, 1), ("BL", 1, -1), ("BR", -1, -1)):
        lg = f"leg_{name}"
        m.part(lg, "body", (sx * sh.x * 0.7, -0.05 * S, sz * sh.z * 0.6))
        if sea:
            ln = (0.9 if sz > 0 else 0.45) * S
            voxelize(m, lg, [ell((sx * ln * 0.5, -0.05 * S, sz * 0.1 * S), (ln * 0.55, 0.06 * S, (0.28 if sz > 0 else 0.2) * S))], v * 0.85, ssk)
        else:
            voxelize(m, lg, [cap((0, 0, 0), (sx * 0.1 * S, -leg, 0), 0.2 * S * P.get("legW", 1.0), 0.22 * S * P.get("legW", 1.0))], v * 0.85, ssk)
            for k in (-1, 0, 1):
                m.box(lg, (sx * 0.1 * S + k * 0.08 * S, -leg, 0.17 * S), (0.06 * S, 0.06 * S, 0.06 * S), "#e8dcc0")
    m.part("tail0", "body", (0, 0, -sh.z * 0.95))
    voxelize(m, "tail0", [cap((0, 0, 0), (0, -0.05 * S, -0.3 * S * P.get("tailL", 1.0)), 0.12 * S, 0.04 * S)], v * 0.8, ssk)
    tails = [("tail", 1)]
    return dict(S=S, v=v, body="body", head="head", hover=P.get("hover", 0.0), tails=tails, heads=["head"], kind=kind)


def anim_shell(m, info, P, L):
    has = m.parts
    kind = info["kind"]
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {}
        if kind in ("snail", "slug"):
            k = math.sin(a * 2)
            pose["body"] = {"s": (1, 1, 1 + 0.06 * k)}
            pose["head"] = {"r": quat((6 * math.sin(a * 2), 12 * math.sin(a), 0))}
            if "shell" in has:
                pose["shell"] = {"r": quat((0, 0, 3 * math.sin(a * 2)))}
        else:
            sea = kind == "sea"
            pose["body"] = {"p": (0, (0.15 * S * math.sin(a * 2)) if sea else 0.02 * S * abs(math.sin(a * 2)), 0), "r": quat((0, 4 * math.sin(a), 2 * math.sin(a * 2)))}
            pose["head"] = {"r": quat((5 * math.sin(a * 2), 15 * math.sin(a), 0)), "p": (0, 0, 0.05 * S * max(0.0, math.sin(a)))}
            for k, ph in (("FL", 0), ("BR", 0), ("FR", math.pi), ("BL", math.pi)):
                if sea:
                    sx = 1 if k[1] == "L" else -1
                    pose[f"leg_{k}"] = {"r": quat((0, 0, sx * 25 * math.sin(a * 2)))}
                else:
                    pose[f"leg_{k}"] = {"r": quat((16 * math.sin(a * 2 + ph), 0, 0))}
        if "tree" in has:
            pose["tree"] = {"r": quat((0, math.degrees(a) * (1 if P.get("world") else 0), 2 * math.sin(a * 2)))}
        if "volcano" in has:
            pose["volcano"] = {"s": (1, 1 + 0.03 * math.sin(a * 4), 1)}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= RANAS
def frog(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#5aa83a")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly", mix(base, "#ffffff", 0.5)), pat=P.get("pat"), pc=C.get("pc"), pc2=C.get("pc2"), ps=P.get("ps", 0.5),
                                        belly_k=-0.25))
    bw, bh, bl = Vector(P.get("body", (0.7, 0.5, 0.7))) * S
    m.part("body", "root", (0, bh * 0.9, 0), (-15, 0, 0))
    voxelize(m, "body", [ell((0, 0, -0.05 * S), (bw, bh, bl), 0.03, 3)], v, bsk)
    m.part("head", "body", (0, bh * 0.4, bl * 0.65), (15, 0, 0))
    hw = P.get("hw", 1.0)
    voxelize(m, "head", [ell((0, 0, 0.1 * S), (bw * 0.95 * hw, bh * 0.6, bl * 0.55))], v * 0.9, bsk)
    es = P.get("eyeS", 1.0) * 0.22 * S
    iris = ctx.en if ctx.L >= 3 else C.get("eye", "#1a1a1a")
    for sx in (1, -1):
        e = ell((sx * bw * 0.55 * hw, bh * 0.45, 0.15 * S), (es, es, es))
        voxelize(m, "head", [e], v * 0.75, bsk)
        p = Vector((sx * bw * 0.55 * hw, bh * 0.5, 0.15 * S + es * 0.85))
        m.box("head", p, (es * 1.2, es * 1.0, 0.06 * S), C.get("eyeWhite", "#fbfbf6") if not C.get("eye") else C["eye"], emit=ctx.eye_glow if ctx.L >= 3 else 0,
              tag="eyes" if ctx.L >= 3 else None)
        m.box("head", p + Vector((0, 0, 0.04 * S)), (es * (0.9 if C.get("eye") else 0.5), es * 0.4 if C.get("eye") else es * 0.6, 0.04 * S), "#050505")
        m.box("head", p + Vector((sx * es * 0.2, es * 0.25, 0.06 * S)), (es * 0.25,) * 2 + (0.02,), "#ffffff")
    m.box("head", (0, -0.1 * S, bl * 0.62), (bw * 1.3 * hw, 0.04 * S, 0.06 * S), C.get("mouth", "#3a1a2a"))
    if P.get("horns"):
        for sx in (1, -1):
            crystal(m, "head", (sx * bw * 0.55 * hw, bh * 0.45 + es * 1.1, 0.1 * S), 0.12 * S, 0.3 * S, C.get("horn", base), rot=(-20, 0, sx * -15))
    if P.get("sac"):
        m.part("sac", "head", (0, -0.25 * S, 0.3 * S))
        voxelize(m, "sac", [ell((0, 0, 0), (0.3 * S, 0.22 * S, 0.25 * S))], v * 0.8, solid(P["sac"]))
    if P.get("coin"):  # rana de la fortuna: moneda en la boca
        m.box("head", (0, -0.12 * S, bl * 0.7), (0.4 * S, 0.4 * S, 0.06 * S), "#f2c14e", metal=1, r=(10, 0, 0))
        m.box("head", (0, -0.12 * S, bl * 0.74), (0.14 * S, 0.14 * S, 0.04 * S), "#8a5a10")
    pads = P.get("pads")
    lc = C.get("legs", base)
    for side, sx in (("L", 1), ("R", -1)):
        fl = f"leg_F{side}"
        m.part(fl, "body", (sx * bw * 0.6, -bh * 0.4, bl * 0.45), (15, 0, 0))
        segment(m, fl, (0, 0, 0), (sx * 0.12 * S, -0.4 * S, 0.12 * S), 0.12 * S, lc)
        for k in (-1, 0, 1):
            segment(m, fl, (sx * 0.12 * S, -0.4 * S, 0.12 * S), (sx * 0.12 * S + k * 0.1 * S, -0.42 * S, 0.3 * S), 0.05 * S, lc)
            if pads:
                m.box(fl, (sx * 0.12 * S + k * 0.1 * S, -0.42 * S, 0.32 * S), (0.09 * S,) * 3, pads)
        bl_ = f"leg_B{side}"
        m.part(bl_, "body", (sx * bw * 0.75, -bh * 0.3, -bl * 0.55), (15, 0, 0))
        voxelize(m, bl_, [ell((sx * 0.15 * S, 0, 0.1 * S), (0.2 * S, 0.22 * S, 0.4 * S))], v * 0.85, lambda p, n: C.get("thigh", lc) if not callable(C.get("thigh")) else C["thigh"](p, n))
        segment(m, bl_, (sx * 0.2 * S, -0.15 * S, 0.4 * S), (sx * 0.3 * S, -0.35 * S, 0.0), 0.1 * S, lc)
        for k in (-1, 0, 1):
            segment(m, bl_, (sx * 0.3 * S, -0.35 * S, 0.0), (sx * 0.3 * S + k * 0.12 * S, -0.38 * S, 0.35 * S), 0.05 * S, lc)
            if pads:
                m.box(bl_, (sx * 0.3 * S + k * 0.12 * S, -0.38 * S, 0.37 * S), (0.09 * S,) * 3, pads)
    return dict(S=S, v=v, body="body", head="head", hover=0, tails=[], heads=["head"])


def anim_frog(m, info, P, L):
    has = m.parts
    S = info["S"]

    def f(t):
        a = t * TAU
        j = max(0.0, math.sin(a)) ** 2
        pose = {"body": {"p": (0, 0.45 * S * j * P.get("jump", 1.0), 0), "r": quat((-12 * j, 0, 0))}}
        for side in ("L", "R"):
            pose[f"leg_B{side}"] = {"r": quat((-40 * j, 0, 0))}
            pose[f"leg_F{side}"] = {"r": quat((-25 * j, 0, 0))}
        if "sac" in has:
            k = max(0.0, math.sin(a * 3)) ** 2
            pose["sac"] = {"s": (1 + 0.5 * k, 1 + 0.5 * k, 1 + 0.4 * k)}
        pose["head"] = {"r": quat((0, 8 * math.sin(a * 2), 0))}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= PRIMATES Y BÍPEDOS (gólems, robots, hadas...)
def biped(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#6a4a2a")
    mat = P.get("mat", "fur")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly"), pat=P.get("pat"), pc=C.get("pc"), pc2=C.get("pc2"), ps=P.get("ps", 0.5), belly_k=-0.6))
    face = C.get("face")
    tw, th_, td = Vector(P.get("torso", (0.5, 0.6, 0.4))) * S
    leg = P.get("leg", 0.6) * S
    lean = P.get("lean", 0)
    gait = P.get("gait", "walk")
    noise = {"fur": 0.06, "stone": 0.18, "wood": 0.1, "metal": 0.0, "jelly": 0.0, "cloth": 0.03}.get(mat, 0.05)
    m.part("body", "root", (0, leg + th_ * 0.75, 0), (lean, 0, 0))
    if mat == "metal":
        m.box("body", (0, 0, 0), (tw * 2, th_ * 1.8, td * 2), base, metal=1)
        m.box("body", (0, 0.1 * th_, td + 0.02), (tw * 1.2, th_ * 0.9, 0.05 * S), C.get("panel", "#0a0e14"))
        for k in range(3):
            m.box("body", ((k - 1) * 0.15 * S, 0.1 * th_, td + 0.05), (0.08 * S, 0.08 * S, 0.04 * S), ctx.en, emit=2, tag="glow")
    else:
        prims = [ell((0, 0, 0), (tw, th_, td), noise, 3 / S), ell((0, 0.45 * th_, 0.02 * S), (tw * 1.1 * P.get("shoulders", 1.0), th_ * 0.55, td * 0.9), noise, 3 / S)]
        if P.get("belly_round"):
            prims.append(ell((0, -0.25 * th_, 0.15 * td), (tw * 0.9, th_ * 0.7, td * 1.0), noise, 3 / S))
        fn = bsk
        if C.get("belly") and mat in ("fur", "cloth"):
            bc = C["belly"]
            fn = lambda p, n: bc if (n.z > 0.45 and abs(p.x) < tw * 0.6 and p.y < 0.4 * th_) else bsk(p, n)
        voxelize(m, "body", prims, v, fn)
    # cabeza
    hs = P.get("hs", 0.5) * S
    m.part("head", "body", (0, th_ * 0.95 + hs * 0.55, 0.05 * S), (-lean, 0, 0))
    hsk = _sk(ctx, P.get("hskin"), bsk)
    if mat == "metal":
        hshape = P.get("headShape", "box")
        if hshape == "crt":
            m.box("head", (0, 0.1 * hs, -0.1 * hs), (hs * 1.7, hs * 1.4, hs * 1.4), C.get("case", "#c8c0a8"))
            m.box("head", (0, 0.1 * hs, 0.62 * hs), (hs * 1.3, hs * 1.0, 0.06 * S), "#0a140a")
            for k in range(4):
                m.box("head", (-0.25 * hs + (k % 2) * 0.1 * hs, (0.35 - k * 0.15) * hs, 0.66 * hs), (0.7 * hs * (1 - 0.15 * k), 0.06 * hs, 0.03 * S), ctx.en, emit=2.0, tag="glow")
            m.box("head", (0, -0.25 * hs, 0.66 * hs), (0.12 * hs, 0.12 * hs, 0.03 * S), ctx.en, emit=2.5, tag="eyes")
        else:
            m.box("head", (0, 0.1 * hs, 0), (hs * 1.5, hs * 1.15, hs * 1.3), C.get("head", base), metal=1)
            m.box("head", (0, 0.12 * hs, 0.66 * hs), (hs * 1.2, hs * 0.55, 0.05 * S), "#0a0e14")
            if P.get("visor"):
                m.box("head", (0, 0.12 * hs, 0.69 * hs), (hs * 1.1, hs * 0.18, 0.04 * S), ctx.en, emit=2.5, tag="eyes")
            else:
                for sx in (1, -1):
                    m.box("head", (sx * 0.28 * hs, 0.14 * hs, 0.7 * hs), (0.22 * hs, 0.22 * hs, 0.04 * S), ctx.en, emit=2.5, tag="eyes")
            if P.get("antenna", True):
                segment(m, "head", (0, 0.7 * hs, 0), (0, 1.2 * hs, 0), 0.05 * S, ctx.metal, metal=1)
                m.box("head", (0, 1.25 * hs, 0), (0.15 * S,) * 3, ctx.en, emit=3, tag="eyes")
    else:
        skull = ell((0, 0, 0), (hs * P.get("hw", 1.0), hs * 0.92, hs * 0.9), noise * 0.6, 3 / S)
        hp = [skull]
        mz = P.get("muzzle", 0.3)
        if mz > 0:
            hp.append(ell((0, -0.3 * hs, 0.65 * hs), (hs * 0.55 * P.get("muzzleW", 1.0), hs * 0.4, hs * mz)))
        if P.get("brow"):
            hp.append(ell((0, 0.25 * hs, 0.55 * hs), (hs * 0.85, hs * 0.2, hs * 0.3)))
        fc = face

        def hcol(p, n):
            if fc and n.z > 0.3 and p.z > 0.15 * hs and (p.y < 0.35 * hs or not P.get("faceTop")):
                return fc
            return hsk(p, n)
        voxelize(m, "head", hp, v * 0.85, hcol)
        if P.get("faceStripe"):  # mandril
            for sx in (1, -1):
                m.box("head", (sx * 0.18 * hs, -0.2 * hs, 0.75 * hs + mz * hs * 0.3), (0.12 * hs, 0.35 * hs, 0.2 * hs), P["faceStripe"])
            m.box("head", (0, -0.15 * hs, 0.85 * hs + mz * hs * 0.4), (0.15 * hs, 0.5 * hs, 0.15 * hs), C.get("nose", "#e83a3a"))
        E = P.get("eye", {})
        sp_ = surface_point(skull, 0.32 * hs, 0.12 * hs)
        eyes(m, "head", (0, sp_.y, sp_.z + 0.01), 0.32 * hs * E.get("sep", 1.0), hs * 0.32 * E.get("size", 1.0), ctx.en if ctx.L >= 3 else E.get("col", "#3a2a1a"),
             glow=ctx.eye_glow, yaw=12, style=E.get("style", "round"), lid=E.get("lid"))
        if mz > 0:
            m.box("head", (0, -0.2 * hs, 0.65 * hs + mz * hs * 0.95), (0.25 * hs, 0.12 * hs, 0.05 * S), C.get("nose", "#2a1a1a"))
            m.box("head", (0, -0.5 * hs, 0.6 * hs + mz * hs * 0.8), (0.35 * hs, 0.05 * hs, 0.05 * S), "#2a1a1a")
        if P.get("bignose"):
            m.box("head", (0, -0.12 * hs, 0.85 * hs), (0.32 * hs, 0.42 * hs, 0.2 * hs), P["bignose"])
        ek = P.get("ear", "round")
        if ek != "none":
            ears(m, "head", ek, hs * 1.4, hsk, C.get("earIn", mix(face or base, "#ffb8c8", 0.3)), ctx, size=P.get("earS", 1.0), tilt=P.get("earTilt", -60 if ek == "round" else -15),
                 x=P.get("earX", 0.55), y=P.get("earY", 0.15), v=v)
        if P.get("horns"):
            horns(m, "head", P["horns"], hs * 1.3, C.get("horn", "#e8dcc0"), ctx, size=P.get("hornSize", 1.0), y=0.45)
        if P.get("mane"):  # tití león / gorila plateado / yeti
            voxelize(m, "head", [ell((0, 0.05 * hs, -0.2 * hs), (hs * 1.35, hs * 1.3, hs * 1.0), 0.22, 3 / S)], v, solid(C.get("mane", base)),
                     carve=[ell((0, 0.0, 0.7 * hs), (hs * 0.85, hs * 0.85, hs * 0.75))])
        if P.get("leafHair"):
            for k in range(7):
                a = math.radians(-60 + k * 20)
                crystal(m, "head", (math.sin(a) * 0.5 * hs, 0.75 * hs, -0.1 * hs), 0.2 * hs, 0.6 * hs, C.get("leaf", "#4aa83a"), rot=(-20, 0, -math.degrees(a)))
    # brazos
    arm = P.get("arm", 0.7) * S
    aw = P.get("armW", 1.0)
    for side, sx in (("L", 1), ("R", -1)):
        a = f"arm_{side}"
        m.part(a, "body", (sx * (tw + 0.08 * S), th_ * 0.6, 0), (0, 0, sx * P.get("armSpread", 8)))
        if mat == "metal":
            m.box(a, (sx * 0.05 * S, -arm * 0.45, 0), (0.28 * S * aw, arm * 0.9, 0.28 * S * aw), C.get("limb", base), metal=1)
            m.box(a, (sx * 0.05 * S, -arm * 0.95, 0.03 * S), (0.36 * S * aw, 0.28 * S, 0.36 * S * aw), ctx.metal, metal=1)
            m.box(a, (sx * 0.05 * S, -arm * 0.45, 0.15 * S * aw), (0.06 * S, arm * 0.6, 0.02 * S), ctx.en, emit=1.6, tag="glow")
        else:
            voxelize(m, a, [cap((0, 0, 0), (sx * 0.05 * S, -arm, 0.12 * S), 0.16 * S * aw, 0.13 * S * aw, noise, 3 / S)], v * 0.85, bsk)
            voxelize(m, a, [ell((sx * 0.05 * S, -arm - 0.05 * S, 0.14 * S), (0.15 * S * aw, 0.12 * S * aw, 0.15 * S * aw))], v * 0.8,
                     solid(C.get("hand", face or base)) if mat in ("fur", "cloth") else bsk)
            if P.get("claws"):
                for k in (-1, 0, 1):
                    segment(m, a, (sx * 0.05 * S + k * 0.06 * S, -arm - 0.1 * S, 0.22 * S), (sx * 0.05 * S + k * 0.06 * S, -arm - 0.2 * S, 0.3 * S), 0.04 * S, P["claws"])
        if P.get("weapon") and sx < 0:
            wk = P["weapon"]
            if wk == "staff":
                segment(m, a, (sx * 0.05 * S, -arm - 0.05 * S, -0.6 * S), (sx * 0.05 * S, -arm - 0.05 * S, 0.9 * S), 0.08 * S, "#c83a2a")
                for zz in (-0.62, 0.92):
                    m.box(a, (sx * 0.05 * S, -arm - 0.05 * S, zz * S), (0.13 * S, 0.13 * S, 0.12 * S), "#f2c14e", metal=1)
            elif wk == "axe":
                segment(m, a, (sx * 0.05 * S, -arm - 0.05 * S, -0.3 * S), (sx * 0.05 * S, -arm + 0.9 * S, -0.1 * S), 0.07 * S, "#5a3a24")
                m.box(a, (sx * 0.05 * S, -arm + 0.8 * S, 0.12 * S), (0.06 * S, 0.45 * S, 0.4 * S), "#c8ccd4", metal=1)
            elif wk == "shield":
                m.box(a, (sx * 0.25 * S, -arm * 0.6, 0.1 * S), (0.06 * S, 0.8 * S, 0.7 * S), ctx.metal, metal=1)
                m.box(a, (sx * 0.29 * S, -arm * 0.6, 0.1 * S), (0.04 * S, 0.5 * S, 0.4 * S), ctx.en, emit=1.8, tag="glow")
            elif wk == "wand":
                segment(m, a, (sx * 0.05 * S, -arm - 0.05 * S, 0.1 * S), (sx * 0.05 * S, -arm + 0.3 * S, 0.5 * S), 0.04 * S, "#f6f0e2")
                m.box(a, (sx * 0.05 * S, -arm + 0.32 * S, 0.52 * S), (0.12 * S,) * 3, ctx.en, r=(45, 0, 45), emit=2.0, tag="glow")
    # piernas
    lw = P.get("legW", 1.0)
    foot = P.get("foot", 1.0)
    for side, sx in (("L", 1), ("R", -1)):
        lg = f"leg_{side}"
        m.part(lg, "body", (sx * tw * 0.5, -th_ * 0.75, 0), (-lean, 0, 0))
        if mat == "metal":
            m.box(lg, (0, -leg * 0.5, 0), (0.3 * S * lw, leg, 0.3 * S * lw), C.get("limb", base), metal=1)
            m.box(lg, (0, -leg + 0.06 * S, 0.08 * S), (0.36 * S * lw, 0.14 * S, 0.5 * S * foot), ctx.metal, metal=1)
        else:
            voxelize(m, lg, [cap((0, 0, 0), (0, -leg * 0.95, 0.02 * S), 0.19 * S * lw, 0.15 * S * lw, noise, 3 / S)], v * 0.85, bsk)
            voxelize(m, lg, [ell((0, -leg + 0.03 * S, 0.1 * S * foot), (0.15 * S * lw, 0.08 * S, 0.24 * S * foot))], v * 0.8,
                     solid(C.get("foot", C.get("hand", face or base))) if mat in ("fur", "cloth") else bsk)
    # cola
    tk = P.get("tail", "none")
    tails = []
    if tk != "none":
        n = tail(m, "body", (0, -th_ * 0.6, -td * 0.85), tk, ctx, n=P.get("tailN", 7), seg=P.get("tailSeg", 0.25), w=P.get("tailW", 0.08), lift=P.get("tailLift", 40),
                 curve=P.get("tailCurve", -12), sk=_sk(ctx, P.get("tskin"), bsk), tuft=P.get("ringCol", P.get("tuftCol")), v=v)
        tails = [("tail", n)]
    if P.get("wings"):
        wings(m, "body", P["wings"], ctx, (tw * 0.6, th_ * 0.55, -td * 0.7), span=P.get("wingSpan", 0.6), cols=P.get("wingCols"), prefix="bwing")
    if P.get("pouch"):
        m.box("body", (0, -0.35 * th_, td * 0.95), (tw * 1.0, th_ * 0.45, 0.06 * S), mix(base, "#000000", 0.15))
    if P.get("chestGem"):
        m.box("body", (0, 0.25 * th_, td + 0.03 * S), (0.2 * S, 0.2 * S, 0.06 * S), ctx.en, r=(0, 0, 45), emit=2.0, tag="glow")
    if mat == "stone" and P.get("crystals", True):
        for k in range(3 + ctx.L):
            crystal(m, "body", ((k % 3 - 1) * 0.3 * S, th_ * (0.5 + 0.12 * (k // 3)), -td * 0.6), 0.16 * S, 0.4 * S, ctx.en, rot=(-30, 0, (k - 1) * 20), emit=1.0, tag="glow")
    return dict(S=S, v=v, body="body", head="head", hover=P.get("hover", 0), tails=tails, heads=["head"], gait=gait, hs=P.get("hs", 0.5) * S * 1.3)


def anim_biped(m, info, P, L):
    has = m.parts
    S = info["S"]
    gait = info["gait"]

    def f(t):
        a = t * TAU
        pose = {}
        if gait == "hop":  # canguro
            j = max(0.0, math.sin(a * 2)) ** 1.4
            pose["body"] = {"p": (0, 0.45 * S * j, 0), "r": quat((-10 * j, 0, 0))}
            for side in ("L", "R"):
                pose[f"leg_{side}"] = {"r": quat((35 * j - 10, 0, 0))}
                pose[f"arm_{side}"] = {"r": quat((-20 * j, 0, 0))}
        elif gait == "float":
            pose["body"] = {"p": (0, 0.2 * S * math.sin(a * 2), 0), "r": quat((0, 8 * math.sin(a), 3 * math.sin(a * 2)))}
            for side, sx in (("L", 1), ("R", -1)):
                pose[f"arm_{side}"] = {"r": quat((15 * math.sin(a * 2), 0, sx * 10 * math.sin(a * 2)))}
                pose[f"leg_{side}"] = {"r": quat((8 * math.sin(a * 2 + 1), 0, 0))}
        elif gait == "knuckle":
            for side, ph in (("L", 0), ("R", math.pi)):
                pose[f"arm_{side}"] = {"r": quat((-50 + 20 * math.sin(a + ph), 0, 0))}
                pose[f"leg_{side}"] = {"r": quat((18 * math.sin(a + ph + math.pi), 0, 0))}
            pose["body"] = {"p": (0, 0.04 * S * abs(math.sin(a)), 0), "r": quat((5 * math.sin(a * 2), 5 * math.sin(a), 0))}
        elif gait == "stomp":
            s = math.sin(a)
            pose["body"] = {"p": (0, 0.05 * S * abs(s), 0), "r": quat((0, 7 * s, 3 * s))}
            pose["leg_L"] = {"r": quat((-22 * max(0, s), 0, 0))}
            pose["leg_R"] = {"r": quat((-22 * max(0, -s), 0, 0))}
            pose["arm_L"] = {"r": quat((20 * s, 0, 0))}
            pose["arm_R"] = {"r": quat((-20 * s, 0, 0))}
        else:  # walk / idle
            amp = 22 if gait == "walk" else 6
            for side, ph in (("L", 0), ("R", math.pi)):
                pose[f"leg_{side}"] = {"r": quat((amp * math.sin(a + ph), 0, 0))}
                pose[f"arm_{side}"] = {"r": quat((-amp * 0.8 * math.sin(a + ph), 0, 0))}
            pose["body"] = {"p": (0, 0.04 * S * abs(math.sin(a)), 0), "r": quat((0, 5 * math.sin(a), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 2), 14 * math.sin(a), 0))}
        _ac()(pose, m, info, t, L)
        for side, sx in (("L", 1), ("R", -1)):
            if f"bwing_{side}" in has:
                pose[f"bwing_{side}"] = {"r": quat((0, sx * 8 * math.sin(a * 2), sx * 22 * math.sin(a * 2 if gait != "float" else a * 4)))}
        return pose
    return f


# ============================================================================= CRIATURAS MÁGICAS
def blob(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#7ad86a")
    kind = P.get("kind", "slime")
    info = dict(S=S, v=v, body="body", head="body", hover=0, tails=[], heads=[], kind=kind, arms=[])
    soft = P.get("emit", 0.0)
    bsk = _sk(ctx, P.get("skin") or dict(base=base, pat=P.get("pat"), pc=C.get("pc"), ps=P.get("ps", 0.5)))
    if soft:
        b0 = bsk
        bsk = lambda p, n: (b0(p, n), soft, "glow") if not isinstance(b0(p, n), tuple) else b0(p, n)
    if kind == "slime":
        m.part("body", "root", (0, 0.65 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.8 * S, 0.62 * S, 0.75 * S), 0.04, 2)], v,
                 lambda p, n: (mix(base, "#ffffff", 0.45) if n.y > 0.75 and vnoise(p.x * 3, 0, p.z * 3) > 0.62 else bsk(p, n)))
        for k, item in enumerate(P.get("inside", [])):  # cosas dentro del slime (monedas, píxeles)
            a = k * 2.4
            m.box("body", (math.cos(a) * 0.35 * S, -0.1 * S + (k % 3) * 0.15 * S, math.sin(a) * 0.3 * S), (0.2 * S, 0.2 * S, 0.06 * S), item, r=(k * 30, k * 50, 0),
                  emit=0.8, tag="glow")
        ey, ez = 0.05 * S, 0.7 * S
    elif kind == "ghost":
        m.part("body", "root", (0, 1.5 * S, 0))
        voxelize(m, "body", [ell((0, 0.2 * S, 0), (0.62 * S, 0.72 * S, 0.62 * S)), cap((0, 0, 0), (0, -0.75 * S, 0), 0.58 * S, 0.45 * S, 0.25, 4 / S)], v,
                 lambda p, n: (bsk(p, n) if not isinstance(bsk(p, n), tuple) else bsk(p, n)[0], 0.3 + 0.1 * ctx.L, "glow"))
        for side, sx in (("L", 1), ("R", -1)):
            m.part(f"arm_{side}", "body", (sx * 0.55 * S, 0.0, 0.1 * S))
            voxelize(m, f"arm_{side}", [cap((0, 0, 0), (sx * 0.4 * S, -0.2 * S, 0.15 * S), 0.14 * S, 0.1 * S)], v, lambda p, n: (base, 0.35, "glow"))
            info["arms"].append(f"arm_{side}")
        ey, ez = 0.35 * S, 0.6 * S
        info["hover"] = 0.6
    elif kind == "kodama":
        m.part("body", "root", (0, 0.75 * S, 0))
        voxelize(m, "body", [cap((0, -0.45 * S, 0), (0, 0.2 * S, 0), 0.38 * S, 0.32 * S)], v, bsk)
        m.part("head", "body", (0, 0.55 * S, 0))
        voxelize(m, "head", [ell((0, 0, 0), (0.42 * S, 0.5 * S, 0.4 * S))], v, bsk)
        for sx in (1, -1):
            m.box("head", (sx * 0.15 * S, 0.05 * S, 0.38 * S), (0.12 * S, 0.14 * S, 0.06 * S), "#101010" if ctx.L < 3 else ctx.en, emit=ctx.eye_glow, tag="eyes" if ctx.eye_glow else None)
        m.box("head", (0, -0.18 * S, 0.38 * S), (0.1 * S, 0.12 * S, 0.06 * S), "#101010")
        for side, sx in (("L", 1), ("R", -1)):
            m.part(f"arm_{side}", "body", (sx * 0.35 * S, 0.05 * S, 0))
            segment(m, f"arm_{side}", (0, 0, 0), (sx * 0.25 * S, -0.3 * S, 0.05 * S), 0.1 * S, base)
            info["arms"].append(f"arm_{side}")
            segment(m, "body", (sx * 0.15 * S, -0.45 * S, 0), (sx * 0.18 * S, -0.75 * S, 0.02 * S), 0.12 * S, base)
        info["head"] = "head"
        info["heads"] = ["head"]
        return info
    elif kind == "mushroom":
        m.part("body", "root", (0, 0.7 * S, 0))
        voxelize(m, "body", [cap((0, -0.55 * S, 0), (0, 0.15 * S, 0), 0.4 * S, 0.34 * S)], v, solid(C.get("stem", "#f2ead6")))
        m.part("cap", "body", (0, 0.25 * S, 0))
        cc = C.get("cap", "#e8423a")
        voxelize(m, "cap", [ell((0, 0.15 * S, 0), (0.9 * S, 0.5 * S, 0.9 * S))], v,
                 lambda p, n: C.get("spot", "#ffffff") if vnoise(p.x * 3, p.y * 3, p.z * 3) > 0.64 else cc, carve=[ell((0, -0.15 * S, 0), (0.85 * S, 0.28 * S, 0.85 * S))])
        for sx in (1, -1):
            m.box("body", (sx * 0.2 * S, -0.75 * S, 0.05 * S), (0.2 * S, 0.12 * S, 0.28 * S), "#c8b890")
            m.part(f"arm_{side}" if False else f"arm_{'L' if sx > 0 else 'R'}", "body", (sx * 0.4 * S, -0.2 * S, 0))
            segment(m, f"arm_{'L' if sx > 0 else 'R'}", (0, 0, 0), (sx * 0.25 * S, -0.25 * S, 0.05 * S), 0.1 * S, C.get("stem", "#f2ead6"))
            info["arms"].append(f"arm_{'L' if sx > 0 else 'R'}")
        ey, ez = -0.12 * S, 0.38 * S
    elif kind == "beholder":  # ojo flotante con tentáculos-ojo
        m.part("body", "root", (0, 2.0 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.9 * S, 0.85 * S, 0.9 * S), 0.03, 3)], v, bsk)
        m.box("body", (0, 0.05 * S, 0.88 * S), (0.85 * S, 0.85 * S, 0.1 * S), "#f6f0e2")
        m.box("body", (0, 0.05 * S, 0.94 * S), (0.55 * S, 0.55 * S, 0.06 * S), ctx.en, emit=2.0, tag="eyes")
        m.box("body", (0, 0.05 * S, 0.98 * S), (0.18 * S, 0.4 * S, 0.04 * S), "#050505")
        m.box("body", (0, -0.55 * S, 0.7 * S), (0.9 * S, 0.12 * S, 0.1 * S), "#3a0a14")
        for k in range(8):
            m.box("body", ((k - 3.5) * 0.11 * S, -0.48 * S, 0.76 * S), (0.06 * S, 0.12 * S, 0.06 * S), "#f6f0e2")
        for k in range(8):
            a = k / 8 * TAU
            tn = f"stalk{k}"
            m.part(tn, "body", (math.cos(a) * 0.4 * S, 0.65 * S, math.sin(a) * 0.4 * S - 0.1 * S))
            pts = [Vector((math.cos(a) * 0.5 * S * u, 0.9 * S * math.sin(u * 1.4) + 0.1 * S, math.sin(a) * 0.5 * S * u - 0.2 * S * u)) for u in (j / 4 for j in range(5))]
            polyline(m, tn, pts, 0.09 * S, mix(base, "#000000", 0.15))
            m.box(tn, pts[-1], (0.25 * S, 0.25 * S, 0.25 * S), "#f6f0e2")
            m.box(tn, pts[-1] + Vector((0, 0, 0.12 * S)), (0.14 * S, 0.14 * S, 0.04 * S), ctx.en, emit=1.6, tag="eyes")
            info["arms"].append(tn)
        info["hover"] = 0.3
        return info
    elif kind == "mimic":  # cofre del tesoro vivo
        wood, wood2 = C.get("wood", "#8a5430"), C.get("wood2", "#6a3e22")
        metal = C.get("metal", "#f2c14e")
        W_, H_, D_ = 1.4 * S, 0.75 * S, 0.95 * S
        m.part("body", "root", (0, 0.35 * S + H_ / 2, 0))
        for k in range(5):  # tablas
            m.box("body", (0, -H_ / 2 + (k + 0.5) * H_ / 5, 0), (W_, H_ / 5 - 0.015 * S, D_), wood if k % 2 else wood2)
        m.box("body", (0, 0, 0), (W_ * 0.96, H_ * 0.98, D_ * 0.96), "#2a140a")
        for sx in (1, -1):  # herrajes de las esquinas y bandas
            for sz in (1, -1):
                m.box("body", (sx * W_ / 2, 0, sz * D_ / 2), (0.14 * S, H_ + 0.04 * S, 0.14 * S), metal, metal=1)
                m.box("body", (sx * W_ / 2, -H_ / 2, sz * D_ / 2), (0.2 * S, 0.12 * S, 0.2 * S), metal, metal=1)
            m.box("body", (sx * W_ * 0.28, 0, 0), (0.1 * S, H_ + 0.03 * S, D_ + 0.03 * S), metal, metal=1)
        for k in range(6):  # remaches
            m.box("body", ((k - 2.5) * 0.22 * S, -H_ / 2 + 0.06 * S, D_ / 2 + 0.02 * S), (0.05 * S,) * 3, mix(metal, "#ffffff", 0.3), metal=1)
        m.box("body", (0, H_ * 0.18, D_ / 2 + 0.05 * S), (0.3 * S, 0.34 * S, 0.08 * S), metal, metal=1)  # cerradura
        m.box("body", (0, H_ * 0.2, D_ / 2 + 0.1 * S), (0.07 * S, 0.12 * S, 0.03 * S), "#1a0a04")
        # interior oscuro con monedas y dientes de abajo
        m.box("body", (0, H_ / 2 - 0.02 * S, 0), (W_ * 0.9, 0.04 * S, D_ * 0.88), "#140604")
        for k in range(9):
            a = k * 2.4
            m.box("body", (math.cos(a) * 0.4 * S, H_ / 2 + 0.03 * S, math.sin(a) * 0.25 * S - 0.1 * S), (0.18 * S, 0.05 * S, 0.18 * S), metal, r=(0, k * 25, 0), metal=1)
        for k in range(10):
            m.box("body", ((k - 4.5) * 0.13 * S, H_ / 2 + 0.1 * S, D_ / 2 - 0.08 * S), (0.08 * S, 0.2 * S, 0.08 * S), "#f6f0e2", r=(0, 0, 45))
        for sx in (1, -1):
            m.box("body", (sx * W_ * 0.44, H_ / 2 + 0.05 * S, 0), (0.08 * S, 0.14 * S, D_ * 0.8), "#f6f0e2", r=(45, 0, 0))
        # tapa curva que se abre
        m.part("lid", "body", (0, H_ / 2, -D_ / 2), (-48, 0, 0))
        for k in range(7):
            a = math.radians(-80 + k * 160 / 6)
            y, z = 0.08 * S + math.cos(a) * 0.28 * S, D_ / 2 + math.sin(a) * D_ / 2
            m.box("lid", (0, y, z), (W_, 0.12 * S, D_ / 7 + 0.04 * S), wood if k % 2 else wood2, r=(math.degrees(-a), 0, 0))
        m.box("lid", (0, 0.04 * S, D_ / 2), (W_ * 0.94, 0.06 * S, D_ * 0.94), "#1a0804")
        for sx in (1, -1):
            for k in range(7):
                a = math.radians(-80 + k * 160 / 6)
                m.box("lid", (sx * W_ / 2, 0.08 * S + math.cos(a) * 0.29 * S, D_ / 2 + math.sin(a) * D_ / 2), (0.14 * S, 0.14 * S, D_ / 7 + 0.05 * S), metal,
                      r=(math.degrees(-a), 0, 0), metal=1)
            m.box("lid", (sx * W_ * 0.28, 0.36 * S, D_ / 2), (0.1 * S, 0.06 * S, D_ * 0.9), metal, metal=1)
        for k in range(10):  # dientes de arriba
            m.box("lid", ((k - 4.5) * 0.13 * S + 0.065 * S, -0.08 * S, D_ - 0.1 * S), (0.08 * S, 0.22 * S, 0.08 * S), "#f6f0e2", r=(0, 0, 45))
        for sx in (1, -1):  # ojos brillando bajo la tapa
            m.box("lid", (sx * 0.3 * S, -0.02 * S, D_ * 0.55), (0.24 * S, 0.06 * S, 0.16 * S), "#fff6dc", emit=1.0, tag="eyes")
            m.box("lid", (sx * 0.3 * S, -0.04 * S, D_ * 0.55), (0.1 * S, 0.06 * S, 0.14 * S), ctx.en, emit=2.5, tag="eyes")
        # lengua larga
        m.part("tongue", "body", (0, H_ / 2 + 0.05 * S, 0.0))
        pts = [Vector((0, 0.05 * S * math.sin(u * 3), 0.1 * S + 0.9 * S * u)) + Vector((0, -0.55 * S * max(0, u - 0.45) ** 1.5, 0)) for u in (j / 6 for j in range(7))]
        for j in range(6):
            segment(m, "tongue", pts[j], pts[j + 1], (0.32 * S * (1 - j / 10), 0.07 * S), "#c8304a" if j % 2 else "#d8405a")
        m.box("tongue", pts[-1], (0.24 * S, 0.08 * S, 0.12 * S), "#e8506a")
        # patitas con garras
        for sx in (1, -1):
            for sz in (1, -1):
                nm = f"foot_{'L' if sx > 0 else 'R'}{'F' if sz > 0 else 'B'}"
                m.part(nm, "body", (sx * W_ * 0.38, -H_ / 2, sz * D_ * 0.3))
                voxelize(m, nm, [cap((0, 0, 0), (sx * 0.08 * S, -0.25 * S, sz * 0.05 * S), 0.12 * S, 0.1 * S)], v * 0.8, solid("#5a3420"))
                for k in (-1, 0, 1):
                    segment(m, nm, (sx * 0.08 * S, -0.28 * S, sz * 0.05 * S), (sx * 0.08 * S + k * 0.07 * S, -0.32 * S, sz * 0.05 * S + 0.16 * S), 0.04 * S, "#f6f0e2")
                info["arms"].append(nm)
        info["lid"] = True
        return info
    elif kind == "seraph":  # orbe con seis alas
        m.part("body", "root", (0, 2.0 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.55 * S,) * 3)], v, lambda p, n: (C.get("body", "#fff6dc"), 0.6, "glow"))
        m.box("body", (0, 0, 0.55 * S), (0.4 * S, 0.4 * S, 0.06 * S), ctx.en, emit=2.5, tag="eyes")
        m.box("body", (0, 0, 0.59 * S), (0.12 * S, 0.3 * S, 0.04 * S), "#2a1a0a")
        ring(m, "body", 0.9 * S, 32, (0.06 * S, 0.06 * S), ctx.metal, rot=(70, 0, 0), metal=1)
        ring(m, "body", 1.05 * S, 36, (0.05 * S, 0.05 * S), ctx.metal, rot=(-60, 30, 0), metal=1)
        for j, (y, sz) in enumerate(((0.45, 0.7), (0.0, 1.0), (-0.45, 0.6))):
            for side, sx in (("L", 1), ("R", -1)):
                w = f"swing{j}_{side}"
                m.part(w, "body", (sx * 0.4 * S, y * S, -0.1 * S), (0, 0, sx * (35 - j * 35)))
                sc = sz * S
                _wing(m, w, sx, [(9, 0.45 * sc, 1.4 * sc, 0.3 * sc, 0, ["#ffffff", "#fff6dc", C.get("tip", "#f2c14e")])],
                      [(0, 0), (0.45 * sc, 0.25 * sc), (0.9 * sc, 0.55 * sc), (1.3 * sc, 0.95 * sc)], ctx.metal, ctx.metal)
                info["arms"].append(w)
        info["hover"] = 0.2
        return info
    elif kind == "devourer":  # boca cósmica gigante
        m.part("body", "root", (0, 1.4 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (1.0 * S, 0.95 * S, 1.0 * S), 0.12, 2 / S)], v, bsk, carve=[ell((0, -0.05 * S, 0.9 * S), (0.75 * S, 0.55 * S, 0.5 * S))])
        voxelize(m, "body", [ell((0, -0.05 * S, 0.35 * S), (0.5 * S, 0.35 * S, 0.1 * S))], v, solid("#000000"))
        m.box("body", (0, -0.05 * S, 0.42 * S), (0.3 * S, 0.3 * S, 0.06 * S), ctx.en, emit=3.0, tag="glow")
        for k in range(16):
            a = k / 16 * TAU
            m.box("body", (math.cos(a) * 0.72 * S, -0.05 * S + math.sin(a) * 0.52 * S, 0.62 * S), (0.1 * S, 0.3 * S, 0.1 * S), "#f6f0e2", r=(0, 0, math.degrees(a) + 90))
        for k in range(5):
            a = k / 5 * math.pi * 0.8 + 0.3
            m.box("body", (math.cos(a) * 0.5 * S, 0.7 * S + math.sin(a) * 0.1 * S, 0.55 * S), (0.2 * S, 0.2 * S, 0.06 * S), "#f6f0e2")
            m.box("body", (math.cos(a) * 0.5 * S, 0.7 * S + math.sin(a) * 0.1 * S, 0.59 * S), (0.1 * S, 0.1 * S, 0.04 * S), ctx.en, emit=2.0, tag="eyes")
        for k in range(8):
            a = k / 8 * TAU
            tn = f"tent{k}"
            m.part(tn, "body", (math.cos(a) * 0.8 * S, -0.5 * S, math.sin(a) * 0.8 * S - 0.1 * S))
            pts = [Vector((math.cos(a) * 0.6 * S * u, -1.0 * S * u + 0.3 * S * u * u, math.sin(a) * 0.6 * S * u)) for u in (j / 5 for j in range(6))]
            for j in range(5):
                segment(m, tn, pts[j], pts[j + 1], 0.22 * S * (1 - j / 7), mix(base, "#000000", 0.2))
            info["arms"].append(tn)
        info["hover"] = 0.5
        return info
    elif kind == "cloud":
        m.part("body", "root", (0, 1.4 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.7 * S, 0.45 * S, 0.5 * S), 0.15, 3 / S), ell((0.55 * S, -0.1 * S, 0), (0.45 * S, 0.35 * S, 0.4 * S), 0.15, 3 / S),
                             ell((-0.55 * S, -0.1 * S, 0), (0.45 * S, 0.35 * S, 0.4 * S), 0.15, 3 / S), ell((0.1 * S, 0.35 * S, 0), (0.4 * S, 0.35 * S, 0.38 * S), 0.15, 3 / S)], v, bsk)
        ey, ez = 0.05 * S, 0.52 * S
        info["hover"] = 0.5
    elif kind == "wisp":
        m.part("body", "root", (0, 1.4 * S, 0))
        voxelize(m, "body", [ell((0, 0, 0), (0.5 * S, 0.55 * S, 0.5 * S))], v, lambda p, n: (base, 0.8, "glow"))
        m.part("flame", "body", (0, 0.35 * S, 0))
        flame(m, "flame", (0, 0, 0), 0.9 * S, 0.35 * S, seed=3, tag="fire")
        for b in m.parts["flame"].boxes:
            b["col"] = mix(base, "#ffffff", min(0.8, b["c"].y / (1.0 * S)))
        ey, ez = 0.0, 0.48 * S
        info["hover"] = 0.6
    if kind in ("slime", "ghost", "mushroom", "cloud", "wisp"):
        for sx in (1, -1):
            m.box("body", (sx * 0.22 * S, ey, ez), (0.2 * S, 0.24 * S, 0.05), "#ffffff")
            m.box("body", (sx * 0.22 * S, ey - 0.02 * S, ez + 0.03), (0.12 * S, 0.16 * S, 0.04), ctx.en if ctx.L >= 2 else "#1a1a1a",
                  emit=0.6 + 0.3 * ctx.L if ctx.L >= 2 else 0, tag="eyes" if ctx.L >= 2 else None)
            m.box("body", (sx * 0.25 * S, ey + 0.06 * S, ez + 0.05), (0.05 * S, 0.05 * S, 0.02), "#ffffff")
        m.box("body", (0, ey - 0.22 * S, ez - 0.02), (0.2 * S, 0.06 * S, 0.04), "#3a1a2a")
    return info


def anim_blob(m, info, P, L):
    has = m.parts
    S = info["S"]
    kind = info["kind"]

    def f(t):
        a = t * TAU
        sq = math.sin(a * 2)
        pose = {}
        if kind == "slime":
            pose["body"] = {"s": (1 + 0.08 * sq, 1 - 0.1 * sq, 1 + 0.08 * sq), "p": (0, 0.15 * S * max(0.0, -sq), 0)}
        elif kind in ("kodama", "mushroom"):
            pose["body"] = {"p": (0, 0.05 * S * abs(sq), 0), "r": quat((0, 0, 6 * math.sin(a)))}
            if "head" in has:
                pose["head"] = {"r": quat((0, 0, 20 * math.sin(a * 2)))}
            if "cap" in has:
                pose["cap"] = {"r": quat((0, 0, 6 * sq))}
        elif kind == "mimic":
            pose["body"] = {"p": (0, 0.08 * S * max(0.0, sq), 0), "r": quat((0, 6 * math.sin(a), 0))}
            pose["lid"] = {"r": quat((-14 * max(0.0, sq), 0, 0))}
            pose["tongue"] = {"r": quat((8 * math.sin(a * 4), 10 * math.sin(a * 2), 0))}
        else:
            pose["body"] = {"p": (0, 0.22 * S * sq, 0), "r": quat((0, 8 * math.sin(a), 4 * sq))}
        for i, nm in enumerate(info["arms"]):
            if nm in has:
                if nm.startswith("swing"):
                    sx = 1 if nm.endswith("L") else -1
                    pose[nm] = {"r": quat((0, 0, sx * 20 * math.sin(a * 2 + i * 0.3)))}
                else:
                    pose[nm] = {"r": quat((15 * math.sin(a * 2 - i), 0, 10 * math.sin(a * 2 + i)))}
        if "flame" in has:
            k = 1 + 0.15 * math.sin(a * 8)
            pose["flame"] = {"s": (1 / k ** 0.5, k, 1 / k ** 0.5)}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= MURCIÉLAGOS
def bat(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    v = ctx.v * P.get("size", 1.0) ** 0.5
    C = P.get("cols", {})
    base = C.get("body", "#4a3a34")
    bsk = _sk(ctx, P.get("skin") or dict(base=base, belly=C.get("belly")))
    m.part("body", "root", (0, 1.7 * S, 0))
    voxelize(m, "body", [ell((0, 0, 0), (0.4 * S, 0.5 * S, 0.36 * S), 0.08, 4 / S)], v, bsk)
    m.part("head", "body", (0, 0.55 * S, 0.05 * S))
    hs = P.get("hs", 0.34) * S
    skull = ell((0, 0, 0.05 * S), (hs, hs * 0.9, hs * 0.9))
    hp = [skull]
    if P.get("snout", 0):  # zorro volador: hocico de zorro
        hp.append(cap((0, -0.05 * hs, 0.5 * hs), (0, -0.12 * hs, 0.5 * hs + P["snout"] * S), 0.4 * hs, 0.25 * hs))
    voxelize(m, "head", hp, v * 0.8, _sk(ctx, dict(base=C.get("head", base))))
    eyes(m, "head", (0, 0.1 * hs, 0.85 * hs + 0.05 * S), 0.38 * hs, hs * 0.45, ctx.en if ctx.L >= 3 else C.get("eye", "#1a1a1a"), glow=ctx.eye_glow, yaw=20,
         style="bead" if not P.get("bigEyes") else "round")
    for sx in (1, -1):
        m.box("head", (sx * 0.12 * hs, -0.45 * hs, 0.8 * hs), (0.06 * hs, 0.2 * hs, 0.05 * hs), "#ffffff")
    ears(m, "head", "bat", hs * P.get("ear", 1.0), _sk(ctx, dict(base=C.get("head", base))), C.get("earIn", "#c88a8a"), ctx, size=1.0, tilt=-15, x=0.55, y=0.6, v=v)
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.3 * S, 0.2 * S, 0))
        sc = P.get("span", 0.55) * S
        membrane_wing(m, w, sx, (1.0 * sc, 0.8 * sc), [(0.9 * sc, 1.5 * sc), (2.0 * sc, 1.3 * sc), (2.4 * sc, 0.3 * sc), (1.6 * sc, -0.6 * sc)],
                      C.get("bone", mix(base, "#000000", 0.3)), C.get("wing", mix(base, "#000000", 0.15)), C.get("wing2", mix(base, "#000000", 0.25)), step=0.1 * S)
        m.part(f"foot_{side}", "body", (sx * 0.15 * S, -0.5 * S, 0))
        segment(m, f"foot_{side}", (0, 0, 0), (sx * 0.05 * S, -0.25 * S, 0.05 * S), 0.06 * S, mix(base, "#000000", 0.3))
    return dict(S=S, v=v, body="body", head="head", hover=0.4, tails=[], heads=["head"], gait="fly")


def anim_bat(m, info, P, L):
    S = info["S"]

    def f(t):
        a = t * TAU
        flap = math.sin(a * 4)
        pose = {"body": {"p": (0, 0.25 * S * math.sin(a * 2) + 0.05 * S * flap, 0), "r": quat((0, 8 * math.sin(a), 0))}}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * flap, sx * 32 * flap))}
        pose["head"] = {"r": quat((5 * math.sin(a * 2), 12 * math.sin(a), 0))}
        _ac()(pose, m, info, t, L)
        return pose
    return f


# ============================================================================= ACCESORIOS
def accessories(m, info, acc, ctx):
    hd = info.get("head", info["body"])
    S = info["S"]
    hs = info.get("hs", 0.5 * S)
    for a in acc:
        name, kw = (a, {}) if isinstance(a, str) else (a[0], a[1])
        y = kw.get("y", 0.55) * hs
        z = kw.get("z", 0.0) * hs
        sc = kw.get("s", 1.0) * hs
        if name == "pirate_hat":
            m.box(hd, (0, y, z), (1.5 * sc, 0.1 * sc, 0.9 * sc), "#1a1418")
            m.box(hd, (0, y + 0.25 * sc, z), (0.9 * sc, 0.45 * sc, 0.6 * sc), "#1a1418")
            m.box(hd, (0, y + 0.3 * sc, z + 0.31 * sc), (0.2 * sc, 0.2 * sc, 0.04 * sc), "#f6f0e2")
            for sx in (1, -1):
                m.box(hd, (sx * 0.6 * sc, y + 0.15 * sc, z), (0.3 * sc, 0.3 * sc, 0.8 * sc), "#1a1418", r=(0, 0, sx * -30))
        elif name == "eyepatch":
            m.box(hd, (kw.get("x", 0.27) * hs, kw.get("ey", 0.15) * hs, kw.get("ez", 0.55) * hs), (0.3 * hs, 0.28 * hs, 0.06 * hs), "#101010")
            segment(m, hd, (-0.5 * hs, 0.35 * hs, 0.3 * hs), (0.5 * hs, 0.05 * hs, 0.45 * hs), 0.04 * hs, "#101010")
        elif name == "samurai_helmet":
            m.box(hd, (0, y, z - 0.05 * sc), (1.25 * sc, 0.35 * sc, 1.2 * sc), "#1a1a1a")
            for sx in (1, -1):
                m.box(hd, (sx * 0.65 * sc, y - 0.25 * sc, z - 0.15 * sc), (0.12 * sc, 0.45 * sc, 0.9 * sc), "#b81f24", r=(0, 0, sx * 20))
            crystal(m, hd, (0, y + 0.35 * sc, z + 0.4 * sc), 0.5 * sc, 0.5 * sc, "#f2c14e", rot=(90, 0, 0), metal=1)
            for sx in (1, -1):
                segment(m, hd, (sx * 0.15 * sc, y + 0.2 * sc, z + 0.45 * sc), (sx * 0.6 * sc, y + 0.9 * sc, z + 0.5 * sc), (0.12 * sc, 0.04 * sc), "#f2c14e", metal=1)
        elif name == "samurai_armor":
            body = info["body"]
            W = info.get("W", 1.0 * S)
            for k in range(4):
                for sx in (1, -1):
                    m.box(body, (sx * W * 0.5, 0.15 * S - k * 0.12 * S, 0.3 * info.get("L", S)), (0.06 * S, 0.12 * S, 0.5 * S), "#b81f24" if k % 2 else "#1a1a1a")
            m.box(body, (0, 0.5 * info.get("H", S), 0.1 * S), (W * 0.8, 0.08 * S, 0.9 * S), "#b81f24")
        elif name == "pharaoh":
            for k in range(7):
                for sx in (1, -1):
                    m.box(hd, (sx * 0.55 * sc, y - 0.2 * sc - k * 0.13 * sc, z - 0.05 * sc), (0.14 * sc, 0.13 * sc, 0.6 * sc), "#f2c14e" if k % 2 else "#2a5ad8",
                          metal=1 if k % 2 else 0)
            m.box(hd, (0, y + 0.05 * sc, z), (1.15 * sc, 0.15 * sc, 1.0 * sc), "#f2c14e", metal=1)
            m.box(hd, (0, y + 0.2 * sc, z + 0.5 * sc), (0.12 * sc, 0.3 * sc, 0.12 * sc), "#f2c14e", metal=1)
        elif name == "crown":
            ring(m, hd, 0.35 * sc, 12, (0.1 * sc, 0.14 * sc), "#f2c14e", center=(0, y, z), metal=1)
            for k in range(6):
                a = k / 6 * TAU
                m.box(hd, (math.cos(a) * 0.35 * sc, y + 0.15 * sc, z + math.sin(a) * 0.35 * sc), (0.08 * sc, 0.25 * sc, 0.08 * sc), "#f2c14e", metal=1)
                if k % 2 == 0:
                    m.box(hd, (math.cos(a) * 0.35 * sc, y + 0.3 * sc, z + math.sin(a) * 0.35 * sc), (0.1 * sc,) * 3, ctx.en, r=(45, 0, 45), emit=1.5, tag="glow")
        elif name == "collar":
            col = kw.get("col", "#c83a3a")
            ring(m, hd, 0.5 * hs, 14, (0.1 * hs, 0.12 * hs), col, center=(0, -0.45 * hs, -0.1 * hs), rot=(70, 0, 0))
            m.box(hd, (0, -0.62 * hs, 0.2 * hs), (0.16 * hs,) * 3, kw.get("tag", "#f2c14e"), metal=1, r=(45, 0, 45))
        elif name == "scarf":
            col = kw.get("col", "#c83a3a")
            ring(m, hd, 0.55 * hs, 14, (0.18 * hs, 0.2 * hs), col, center=(0, -0.5 * hs, -0.1 * hs), rot=(70, 0, 0))
            m.box(hd, (0.3 * hs, -0.75 * hs, -0.45 * hs), (0.22 * hs, 0.5 * hs, 0.08 * hs), col, r=(20, 0, 10))
        elif name == "bandana":
            col = kw.get("col", "#c83a3a")
            m.box(hd, (0, y - 0.1 * sc, z), (1.05 * sc, 0.25 * sc, 1.0 * sc), col)
            m.box(hd, (0, y - 0.15 * sc, z - 0.55 * sc), (0.2 * sc, 0.2 * sc, 0.25 * sc), col, r=(30, 0, 0))
        elif name == "headphones":
            for sx in (1, -1):
                m.box(hd, (sx * 0.52 * hs, 0.05 * hs, 0), (0.15 * hs, 0.35 * hs, 0.35 * hs), "#1a1a1a")
                m.box(hd, (sx * 0.6 * hs, 0.05 * hs, 0), (0.04 * hs, 0.2 * hs, 0.2 * hs), ctx.en, emit=1.6, tag="glow")
            ring(m, hd, 0.52 * hs, 12, (0.07 * hs, 0.07 * hs), "#1a1a1a", center=(0, 0.1 * hs, 0), rot=(0, 0, 90))
        elif name == "glasses":
            for sx in (1, -1):
                m.box(hd, (sx * 0.25 * hs, kw.get("ey", 0.15) * hs, kw.get("ez", 0.6) * hs), (0.32 * hs, 0.24 * hs, 0.04 * hs), ctx.en if kw.get("glow") else "#101010",
                      emit=1.8 if kw.get("glow") else 0, tag="glow" if kw.get("glow") else None)
            m.box(hd, (0, kw.get("ey", 0.15) * hs, kw.get("ez", 0.6) * hs), (0.2 * hs, 0.05 * hs, 0.04 * hs), "#101010")
        elif name == "wreath":
            for k in range(14):
                a = k / 14 * TAU
                m.box(hd, (math.cos(a) * 0.45 * sc, y, z + math.sin(a) * 0.45 * sc), (0.16 * sc, 0.1 * sc, 0.16 * sc), kw.get("col", "#ff9ac0") if k % 2 else "#5aa83a",
                      r=(0, -math.degrees(a), 0))
        elif name == "gem":
            m.box(hd, (0, kw.get("ey", 0.4) * hs, kw.get("ez", 0.45) * hs), (0.16 * hs, 0.16 * hs, 0.08 * hs), ctx.en, r=(0, 0, 45), emit=1.8, tag="glow")
        elif name == "saddle":
            body = info["body"]
            m.box(body, (0, 0.5 * info.get("H", S) + 0.03 * S, 0), (info.get("W", S) * 0.9, 0.08 * S, 0.6 * S), kw.get("col", "#7a3a1a"))
            for sx in (1, -1):
                m.box(body, (sx * info.get("W", S) * 0.48, 0.2 * S, 0), (0.05 * S, 0.5 * S, 0.5 * S), kw.get("col2", "#c83a3a"))
        elif name == "wheels":  # caballo de Troya
            body = info["body"]
            lo = m.parts[body]
            for sx in (1, -1):
                for sz in (1, -1):
                    m.part(f"wheel_{sx}_{sz}", body, (sx * info.get("W", S) * 0.55, -info.get("H", S) * 0.5 - info.get("lf", S) * 0.9, sz * info.get("L", S) * 0.32))
                    ring(m, f"wheel_{sx}_{sz}", 0.3 * S, 12, (0.12 * S, 0.1 * S), "#5a3a1a", rot=(0, 0, 90))
                    m.box(f"wheel_{sx}_{sz}", (0, 0, 0), (0.08 * S, 0.5 * S, 0.06 * S), "#5a3a1a")
                    m.box(f"wheel_{sx}_{sz}", (0, 0, 0), (0.08 * S, 0.06 * S, 0.5 * S), "#5a3a1a")
            m.box(body, (0, -info.get("H", S) * 0.5 - info.get("lf", S) * 0.75, 0), (info.get("W", S) * 1.3, 0.12 * S, info.get("L", S) * 0.9), "#6a4a2a")
        elif name == "bamboo":  # panda con bambú en la boca
            for k in range(6):
                m.box(hd, (0.1 * hs, -0.35 * hs + k * 0.22 * hs, 0.75 * hs), (0.12 * hs, 0.2 * hs, 0.12 * hs), "#7ab84a" if k % 2 else "#5a9a3a", r=(0, 0, 60))
            m.box(hd, (0.65 * hs, 0.35 * hs, 0.75 * hs), (0.35 * hs, 0.05 * hs, 0.15 * hs), "#6ac84a", r=(0, 0, 20))
        elif name == "face_ring":  # gibón: anillo blanco alrededor de la cara
            ring(m, hd, 0.42 * hs, 14, (0.08 * hs, 0.08 * hs), "#f2ead6", center=(0, 0.0, 0.62 * hs), rot=(90, 0, 0))
        elif name == "gears":
            for sx in (1, -1):
                c = Vector((sx * 0.62 * S, 0.9 * S, 0.0))
                ring(m, info["body"], 0.18 * S, 10, (0.06 * S, 0.06 * S), "#c8a050", center=tuple(c), rot=(0, 0, 90), metal=1)
                for k in range(8):
                    a = k / 8 * TAU
                    m.box(info["body"], c + Vector((0, math.cos(a) * 0.24 * S, math.sin(a) * 0.24 * S)), (0.06 * S, 0.07 * S, 0.07 * S), "#c8a050", metal=1)
        elif name == "windup":  # llave de cuerda
            segment(m, info["body"], (0, 0.2 * S, -0.1 * S), (0, 0.55 * S, -0.1 * S), 0.06 * S, "#c8a050", metal=1)
            for sx in (1, -1):
                m.box(info["body"], (sx * 0.14 * S, 0.62 * S, -0.1 * S), (0.22 * S, 0.16 * S, 0.05 * S), "#c8a050", metal=1)
        elif name == "smile":
            m.box(hd, (0, -0.32 * hs, 0.62 * hs), (0.22 * hs, 0.04 * hs, 0.04 * hs), "#2a1010")
            for sx in (1, -1):
                m.box(hd, (sx * 0.13 * hs, -0.28 * hs, 0.6 * hs), (0.06 * hs, 0.04 * hs, 0.04 * hs), "#2a1010")
        elif name == "antenna_ears":
            for sx in (1, -1):
                segment(m, hd, (sx * 0.25 * hs, 0.45 * hs, -0.1 * hs), (sx * 0.35 * hs, 0.95 * hs, -0.15 * hs), 0.05 * hs, "#5a6068")
                m.box(hd, (sx * 0.35 * hs, 0.98 * hs, -0.15 * hs), (0.1 * hs,) * 3, ctx.en, emit=2.0, tag="eyes")
        elif name == "leaf_head":
            for k in range(5):
                m.box(hd, (0, 0.5 * hs + k * 0.06 * hs, -0.1 * hs + k * 0.08 * hs), (0.4 * hs * math.sin(math.pi * (0.15 + 0.17 * k)), 0.04 * hs, 0.1 * hs), "#5ab83a", r=(-30, 0, 0))
        elif name == "nose_ring":
            ring(m, hd, 0.12 * hs, 10, (0.04 * hs, 0.04 * hs), "#f2c14e", center=(0, -0.45 * hs, 0.95 * hs), metal=1)
        elif name == "sun_disc":
            m.part("sun", info["body"], (0, 0.9 * S, 0.2 * S))
            ring(m, "sun", 0.4 * S, 18, (0.08 * S, 0.08 * S), "#f2c14e", rot=(90, 0, 0), metal=1)
            m.box("sun", (0, 0, 0), (0.55 * S, 0.55 * S, 0.06 * S), "#ff6a1a", r=(0, 0, 45), emit=1.6, tag="glow")
        elif name == "coin_slot":  # hucha
            m.box(info["body"], (0, info.get("H", S) * 0.55, 0), (0.1 * S, 0.06 * S, 0.5 * S), "#2a1010")
            m.box(info["body"], (0, info.get("H", S) * 0.6 + 0.15 * S, 0), (0.06 * S, 0.4 * S, 0.4 * S), "#f2c14e", metal=1)
        elif name == "accretion":  # disco de acreción alrededor
            m.part("disc", info["body"], (0, 0.3 * S, 0), (15, 0, 8))
            for k, (r, c) in enumerate(((1.6, "#ff9a3a"), (1.85, "#ffd27a"), (2.1, "#ff5a1a"))):
                ring(m, "disc", r * S, 56, (0.14 * S, 0.05 * S), c, emit=2.0, tag="neon")
        elif name == "glitch_cubes":
            for k in range(14):
                a = k * 2.399
                p_ = Vector((math.cos(a) * (0.6 + 0.3 * (k % 3)) * S, (0.3 + 0.12 * k) * S, math.sin(a) * (0.6 + 0.3 * (k % 3)) * S))
                m.box(info["body"], p_, (0.18 * S,) * 3, ctx.en if k % 2 else ctx.acc, emit=1.8, tag="twinkle")
        elif name == "eyes_body":  # ojos extra repartidos por el cuerpo
            for k in range(kw.get("n", 8)):
                a = k * 2.399
                p_ = Vector((math.cos(a) * 0.45 * S, (0.2 + 0.25 * math.sin(k)) * S, ((k / kw.get("n", 8)) - 0.5) * 1.2 * S))
                m.box(info["body"], p_, (0.18 * S, 0.18 * S, 0.18 * S), "#f6f0e2")
                m.box(info["body"], p_ * 1.04, (0.1 * S, 0.1 * S, 0.1 * S), ctx.en, emit=2.0, tag="eyes")
        elif name == "crescent_moon":
            m.part("moon", hd, (0, 0.9 * hs, -0.6 * hs))
            for k in range(9):
                a = math.radians(-120 + k * 30)
                m.box("moon", (math.cos(a) * 0.35 * hs, math.sin(a) * 0.35 * hs, 0), (0.14 * hs * (1 - abs(k - 4) / 6), 0.16 * hs, 0.06 * hs), "#fff6c8", emit=1.5, tag="glow")
        elif name == "portal_ring":
            m.part("portal", info["body"], (0, 0.4 * S, -0.6 * S), (0, 0, 0))
            ring(m, "portal", 1.3 * S, 48, (0.12 * S, 0.12 * S), ctx.en, rot=(90, 0, 0), emit=2.2, tag="neon")
            ring(m, "portal", 1.1 * S, 40, (0.06 * S, 0.06 * S), "#ffffff", rot=(90, 0, 0), emit=1.6, tag="neon")
        elif name == "barrel":  # San Bernardo: barrilito
            m.box(hd, (0, -0.75 * hs, 0.15 * hs), (0.38 * hs, 0.3 * hs, 0.3 * hs), "#8a5a2a")
            for zz in (-0.12, 0.12):
                m.box(hd, (0, -0.75 * hs, 0.15 * hs + zz * hs), (0.4 * hs, 0.32 * hs, 0.04 * hs), "#c8c8c8", metal=1)
        elif name == "warts":  # facóquero
            for sx in (1, -1):
                m.box(hd, (sx * 0.45 * hs, -0.05 * hs, 0.5 * hs), (0.12 * hs, 0.2 * hs, 0.12 * hs), "#6a5a4a")
        elif name == "snow_peak":
            for k, (dx, dz, h_) in enumerate(((0, 0, 0.7), (0.3, 0.1, 0.45), (-0.28, -0.1, 0.5))):
                for j in range(5):
                    w_ = (1 - j / 5) * 0.35 * S
                    m.box(hd, (dx * S, 0.55 * hs + j * h_ * S / 5, dz * S), (w_, h_ * S / 5, w_), "#f2f6fa" if j >= 3 else "#7a7e88")
        elif name == "money":  # monedas alrededor
            for k in range(6):
                a = k / 6 * TAU
                m.box(info["body"], (math.cos(a) * 0.9 * S, -0.3 * S + (k % 2) * 0.2 * S, math.sin(a) * 0.9 * S), (0.3 * S, 0.3 * S, 0.06 * S), "#f2c14e", metal=1, r=(0, -math.degrees(a), 0))


BUILD = {"ceph": ceph, "chain": chain, "shell": shellback, "frog": frog, "biped": biped, "blob": blob, "bat": bat}
ANIM = {"ceph": anim_ceph, "chain": anim_chain, "shell": anim_shell, "frog": anim_frog, "biped": anim_biped, "blob": anim_blob, "bat": anim_bat}


# ============================================================================= ROBOTS (con articulaciones y blindaje)
def _rbox(m, part, c, s, col, layers=3, metal=0, shrink=0.12):
    """Caja 'redondeada': varias capas que se estrechan hacia arriba y abajo."""
    c = Vector(c)
    m.box(part, c, s, col, metal=metal)
    for k in range(1, layers):
        f = 1 - shrink * k
        m.box(part, c, (s[0] * f, s[1] + 0.001, s[2] * f + shrink * k * 0.0), col, metal=metal)
        m.box(part, c, (s[0] + 0.001 * k, s[1] * f, s[2] * f), col, metal=metal)


def robot(m, P, ctx):
    S = ctx.S * P.get("size", 1.0)
    C = P.get("cols", {})
    body, trim, dark = C.get("body", "#8a929e"), C.get("trim", ctx.metal), C.get("dark", "#22262e")
    en = ctx.en
    style = P.get("style", "guardian")
    G = 1.15 if style in ("guardian", "antivirus") else 1.0
    leg = 0.95 * S
    m.part("body", "root", (0, leg + 0.55 * S, 0))
    # pelvis y abdomen
    _rbox(m, "body", (0, -0.42 * S, 0), (0.72 * S * G, 0.26 * S, 0.5 * S), dark)
    m.box("body", (0, -0.28 * S, 0), (0.8 * S * G, 0.08 * S, 0.56 * S), trim, metal=1)  # cinturón
    m.box("body", (0, -0.28 * S, 0.29 * S), (0.18 * S, 0.12 * S, 0.04 * S), en, emit=2.0, tag="glow")
    for k in range(3):
        m.box("body", (0, (-0.16 + k * 0.1) * S, 0.02 * S), (0.58 * S * G - k * 0.02 * S, 0.08 * S, 0.44 * S), dark if k % 2 else mix(dark, "#ffffff", 0.08))
    # pecho blindado
    _rbox(m, "body", (0, 0.32 * S, 0), (1.05 * S * G, 0.62 * S, 0.66 * S), body)
    m.box("body", (0, 0.4 * S, 0.3 * S), (0.85 * S * G, 0.42 * S, 0.1 * S), mix(body, "#ffffff", 0.12))
    for sx in (1, -1):
        m.box("body", (sx * 0.32 * S * G, 0.38 * S, 0.36 * S), (0.3 * S, 0.3 * S, 0.04 * S), mix(body, "#000000", 0.12))
        m.box("body", (sx * 0.47 * S * G, 0.1 * S, 0.34 * S), (0.05 * S, 0.4 * S, 0.03 * S), en, emit=1.8, tag="glow")  # líneas de energía
        for k in range(3):  # rejillas laterales
            m.box("body", (sx * 0.535 * S * G, 0.2 * S + k * 0.1 * S, 0.0), (0.03 * S, 0.04 * S, 0.4 * S), dark)
    # núcleo
    ring(m, "body", 0.15 * S, 12, (0.05 * S, 0.05 * S), trim, center=(0, 0.38 * S, 0.37 * S), rot=(90, 0, 0), metal=1)
    m.part("core", "body", (0, 0.38 * S, 0.38 * S))
    m.box("core", (0, 0, 0), (0.18 * S, 0.18 * S, 0.06 * S), en, r=(0, 0, 45), emit=3.0, tag="glow")
    m.box("core", (0, 0, 0.02 * S), (0.08 * S, 0.08 * S, 0.05 * S), "#ffffff", r=(0, 0, 45), emit=3.0, tag="glow")
    # mochila / propulsores
    _rbox(m, "body", (0, 0.35 * S, -0.42 * S), (0.7 * S, 0.55 * S, 0.22 * S), dark)
    for sx in (1, -1):
        m.box("body", (sx * 0.22 * S, 0.3 * S, -0.58 * S), (0.18 * S, 0.5 * S, 0.18 * S), body)
        m.box("body", (sx * 0.22 * S, 0.02 * S, -0.58 * S), (0.13 * S, 0.06 * S, 0.13 * S), en, emit=2.5, tag="fire")
    # cuello y cabeza
    m.box("body", (0, 0.7 * S, 0), (0.24 * S, 0.14 * S, 0.24 * S), dark)
    m.part("head", "body", (0, 0.8 * S, 0.02 * S))
    hs = 0.5 * S
    if style == "crt":
        m.box("head", (0, 0.25 * S, -0.05 * S), (0.85 * S, 0.62 * S, 0.62 * S), C.get("case", "#c8c0a8"))
        m.box("head", (0, 0.25 * S, -0.4 * S), (0.6 * S, 0.45 * S, 0.2 * S), mix(C.get("case", "#c8c0a8"), "#000000", 0.15))
        m.box("head", (0, 0.27 * S, 0.27 * S), (0.68 * S, 0.48 * S, 0.04 * S), "#06140a")
        for k in range(5):
            w = 0.5 * S * (0.4 + 0.6 * ((k * 0.37) % 1))
            m.box("head", (-0.25 * S + w / 2, (0.43 - k * 0.075) * S, 0.3 * S), (w, 0.035 * S, 0.02 * S), en, emit=2.0, tag="glow")
        m.box("head", (0.22 * S, 0.13 * S, 0.3 * S), (0.05 * S, 0.06 * S, 0.02 * S), en, emit=3.0, tag="eyes")
        for k in range(3):
            m.box("head", ((k - 1) * 0.12 * S, -0.03 * S, 0.27 * S), (0.06 * S, 0.04 * S, 0.03 * S), "#6a6a5a")
    else:
        _rbox(m, "head", (0, 0.22 * S, 0), (0.62 * S, 0.5 * S, 0.58 * S), C.get("head", body))
        m.box("head", (0, 0.2 * S, 0.3 * S), (0.54 * S, 0.22 * S, 0.04 * S), dark)
        if style == "agent":
            for sx in (1, -1):
                m.box("head", (sx * 0.13 * S, 0.21 * S, 0.33 * S), (0.2 * S, 0.1 * S, 0.03 * S), en, emit=2.6, tag="eyes")
        else:
            m.box("head", (0, 0.21 * S, 0.33 * S), (0.48 * S, 0.07 * S, 0.03 * S), en, emit=2.8, tag="eyes")
        m.box("head", (0, 0.03 * S, 0.3 * S), (0.36 * S, 0.12 * S, 0.06 * S), mix(body, "#000000", 0.2))
        for k in range(4):
            m.box("head", ((k - 1.5) * 0.07 * S, 0.03 * S, 0.335 * S), (0.035 * S, 0.08 * S, 0.02 * S), dark)
        m.box("head", (0, 0.5 * S, -0.02 * S), (0.08 * S, 0.12 * S, 0.5 * S), trim, metal=1)  # cresta
        for sx in (1, -1):
            m.box("head", (sx * 0.33 * S, 0.22 * S, 0), (0.06 * S, 0.24 * S, 0.24 * S), trim, metal=1)
            ring(m, "head", 0.1 * S, 10, (0.03 * S, 0.03 * S), en, center=(sx * 0.37 * S, 0.22 * S, 0), rot=(0, 0, 90), emit=2.0, tag="glow")
        segment(m, "head", (0.22 * S, 0.45 * S, -0.1 * S), (0.3 * S, 0.85 * S, -0.15 * S), 0.04 * S, trim, metal=1)
        m.box("head", (0.3 * S, 0.88 * S, -0.15 * S), (0.09 * S,) * 3, en, emit=3.0, tag="eyes")
    if style == "banker":
        m.box("head", (0, 0.5 * S, 0), (0.8 * S, 0.05 * S, 0.7 * S), "#1a1a1a")
        m.box("head", (0, 0.72 * S, 0), (0.48 * S, 0.42 * S, 0.44 * S), "#1a1a1a")
        m.box("head", (0, 0.56 * S, 0), (0.5 * S, 0.07 * S, 0.46 * S), trim, metal=1)
        m.box("head", (0.13 * S, 0.21 * S, 0.34 * S), (0.16 * S, 0.16 * S, 0.02 * S), trim, metal=1)
    # brazos con codo y mano
    for side, sx in (("L", 1), ("R", -1)):
        sh = f"arm_{side}"
        m.part(sh, "body", (sx * 0.62 * S * G, 0.48 * S, 0), (0, 0, sx * 6))
        _rbox(m, sh, (sx * 0.08 * S, 0.08 * S, 0), (0.42 * S * G, 0.32 * S, 0.46 * S), body)  # hombrera
        m.box(sh, (sx * 0.08 * S, 0.0, 0.0), (0.44 * S * G, 0.06 * S, 0.48 * S), trim, metal=1)
        m.box(sh, (sx * 0.12 * S, 0.12 * S, 0.24 * S), (0.2 * S, 0.06 * S, 0.02 * S), en, emit=1.8, tag="glow")
        m.box(sh, (sx * 0.08 * S, -0.3 * S, 0), (0.18 * S, 0.42 * S, 0.18 * S), dark)
        fo = f"fore_{side}"
        m.part(fo, sh, (sx * 0.08 * S, -0.55 * S, 0))
        m.box(fo, (0, 0, 0), (0.2 * S, 0.2 * S, 0.2 * S), trim, metal=1, r=(45, 0, 0))
        _rbox(m, fo, (0, -0.25 * S, 0.02 * S), (0.28 * S * G, 0.42 * S, 0.3 * S * G), body)
        m.box(fo, (sx * 0.15 * S * G, -0.25 * S, 0.02 * S), (0.03 * S, 0.3 * S, 0.06 * S), en, emit=1.8, tag="glow")
        m.box(fo, (0, -0.52 * S, 0.03 * S), (0.2 * S, 0.14 * S, 0.18 * S), dark)
        for k in range(3):
            m.box(fo, ((k - 1) * 0.06 * S, -0.64 * S, 0.06 * S), (0.05 * S, 0.12 * S, 0.06 * S), dark)
        m.box(fo, (-sx * 0.1 * S, -0.58 * S, 0.06 * S), (0.05 * S, 0.1 * S, 0.06 * S), dark)
        if style == "antivirus" and sx < 0:
            m.box(fo, (sx * 0.22 * S, -0.3 * S, 0.1 * S), (0.06 * S, 0.9 * S, 0.75 * S), trim, metal=1)
            m.box(fo, (sx * 0.26 * S, -0.3 * S, 0.1 * S), (0.04 * S, 0.55 * S, 0.12 * S), en, emit=2.2, tag="glow")
            m.box(fo, (sx * 0.26 * S, -0.3 * S, 0.1 * S), (0.04 * S, 0.12 * S, 0.45 * S), en, emit=2.2, tag="glow")
        if style == "guardian" and sx < 0:  # espada de energía
            m.box(fo, (0, -0.66 * S, 0.1 * S), (0.08 * S, 0.08 * S, 0.3 * S), dark)
            m.box(fo, (0, -0.66 * S, 0.75 * S), (0.05 * S, 0.14 * S, 1.0 * S), en, emit=2.5, tag="glow")
    # piernas con rodilla
    for side, sx in (("L", 1), ("R", -1)):
        th = f"leg_{side}"
        m.part(th, "body", (sx * 0.26 * S * G, -0.55 * S, 0))
        m.box(th, (0, 0, 0), (0.22 * S, 0.2 * S, 0.22 * S), trim, metal=1, r=(45, 0, 0))
        _rbox(m, th, (0, -0.25 * S, 0), (0.3 * S * G, 0.42 * S, 0.32 * S), body)
        sn = f"shin_{side}"
        m.part(sn, th, (0, -0.48 * S, 0))
        _rbox(m, sn, (0, 0.02 * S, 0.12 * S), (0.24 * S, 0.2 * S, 0.12 * S), trim)  # rodillera
        _rbox(m, sn, (0, -0.22 * S, 0), (0.34 * S * G, 0.42 * S, 0.36 * S), body)
        m.box(sn, (0, -0.2 * S, 0.19 * S), (0.08 * S, 0.26 * S, 0.02 * S), en, emit=1.8, tag="glow")
        _rbox(m, sn, (0, -0.45 * S, 0.1 * S), (0.36 * S * G, 0.12 * S, 0.56 * S), dark)
        m.box(sn, (0, -0.45 * S, 0.39 * S), (0.3 * S, 0.08 * S, 0.04 * S), trim, metal=1)
    return dict(S=S, v=ctx.v, body="body", head="head", hover=0, tails=[], heads=["head"], hs=hs * 1.4)


def anim_robot(m, info, P, L):
    S = info["S"]

    def f(t):
        a = t * TAU
        s = math.sin(a)
        pose = {"body": {"p": (0, 0.04 * S * abs(s), 0), "r": quat((0, 8 * s, 2 * s))}}
        for side, ph in (("L", 0), ("R", math.pi)):
            k = math.sin(a + ph)
            pose[f"leg_{side}"] = {"r": quat((-24 * k, 0, 0))}
            pose[f"shin_{side}"] = {"r": quat((30 * max(0.0, k), 0, 0))}
            pose[f"arm_{side}"] = {"r": quat((18 * k, 0, 0))}
            pose[f"fore_{side}"] = {"r": quat((-25 - 10 * k, 0, 0))}
        pose["head"] = {"r": quat((3 * math.sin(a * 2), 20 * math.sin(a * 0.5 + 1), 0))}
        k = 1 + 0.15 * math.sin(a * 4)
        pose["core"] = {"s": (k, k, 1)}
        _ac()(pose, m, info, t, L)
        return pose
    return f


BUILD["robot"] = robot
ANIM["robot"] = anim_robot
