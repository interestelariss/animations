"""Mascotas de los huevos: 4 por huevo, con la estética del huevo.

El nivel de rareza del huevo (0 común … 6 secreto) decide el detalle:
tamaño de vóxel, accesorios (collar, gema, alas, aura, orbes, halo, corona),
animaciones y VFX del visor.
"""

import math

from mathutils import Vector

import sculpt
from animals import P_, add_base, cosmic_col, stage_for
from eggs import _hash, _wing
from eggs_themes import flame, horn, membrane_wing, vnoise
from pet_names import PETS
from rebirth import beast, fur, put_eyes, walk
from sculpt import cap, ell, voxelize
from tiers import RARITIES, SPECS, _mix
from voxel import Model, crystal, polyline, quat, ring, segment, star

TAU = math.tau

FEATURED_SPECS = {
    "egg_celestial": dict(shell=["#3b74ff", "#4985ff", "#2f63f5"], accent="#f6c64a", energy="#33ffd0", metal="#f6c64a", pattern="spots", wings="feather", rarity="legendario", name="Huevo Celestial"),
    "egg_ice": dict(shell=["#223e88", "#2a4ea3", "#1b3170"], accent="#5ff4ff", energy="#5ff4ff", metal="#bfe8ff", pattern="scales", wings="crystal", rarity="mitico", name="Huevo de Hielo"),
    "egg_inferno": dict(shell=["#25110f", "#2f1612", "#1b0e10"], accent="#ff6a14", energy="#ff7a1a", metal="#3a3c42", pattern="crack", wings="bat", rarity="mitico", name="Huevo Infernal"),
    "egg_swamp": dict(shell=["#4b6b30", "#5a7a35", "#3d5a2a"], accent="#8bbd40", energy="#b6ff5a", metal="#6a4424", pattern="spots", wings="leaf", rarity="epico", name="Huevo del Pantano"),
    "egg_galaxy": dict(shell=["#1d0f52", "#24125f", "#140a3a"], accent="#d14ee8", energy="#d14ee8", metal="#ffe08a", pattern="void", wings="crystal", rarity="legendario", name="Huevo Galaxia"),
    "egg_storm": dict(shell=["#46546f", "#52617d", "#3a4660"], accent="#ffe14a", energy="#ffe14a", metal="#c0c8d8", pattern="crack", wings="feather", rarity="mitico", name="Huevo Tormenta"),
    "egg_sakura": dict(shell=["#fbeef2", "#f7e3ea", "#f3d6e0"], accent="#f59ab8", energy="#ff8fb8", metal="#e8b84a", pattern="spots", wings="feather", rarity="legendario", name="Huevo Sakura"),
}


def egg_spec(egg_id):
    if egg_id in FEATURED_SPECS:
        return FEATURED_SPECS[egg_id]
    for sp in SPECS:
        if "egg_" + sp["id"] == egg_id:
            return sp
    raise KeyError(egg_id)


# ----------------------------------------------------------------------------- colores
def pet_fur(sp, L, shade=0):
    c = list(sp["shell"])
    if shade:  # variación por mascota: un tono más claro u oscuro
        c = [_mix(x, "#ffffff" if shade > 0 else "#000000", 0.18 * abs(shade)) for x in c]
    acc, en = sp["accent"], sp["energy"]
    belly = _mix(c[0], "#ffffff", 0.45)
    pat = sp["pattern"]
    if pat in ("void", "prism"):
        return lambda p, n: cosmic_col(p, pal=tuple(c) + (_mix(c[0], "#000000", 0.3),), neb=(en, acc if acc != "#ffffff" else "#7fe8ff"))
    if pat in ("rainbow", "rainbow_scales"):
        bands = ["#ff9ab8", "#ffd27a", "#fff3a0", "#a8f0b8", "#9ad8ff", "#c8a8ff"]
        base = fur(c, belly=belly)
        return lambda p, n: bands[int((p.y + p.z * 0.5 + 20) / 0.3) % 6] if vnoise(p.x * 2, p.y * 2, p.z * 2) > 0.62 else base(p, n)
    if pat in ("spots", "flowers", "craters", "suckers", "hex", "hexgrid" if L < 1 else "_"):
        return fur(c, belly=belly, pattern="spots", pcol=acc, freq=1.8)
    if pat in ("stripes", "tiger", "zigzag", "ribs", "candy", "diag", "sunrays", "scanlines" if L < 1 else "_"):
        return fur(c, belly=belly, pattern="stripes", pcol=acc, freq=2.0)
    if pat in ("crack", "runes", "circuit_red", "scanlines", "hexgrid", "code", "glitch", "swirl", "flamefeather"):
        if L >= 1:
            return fur(c, belly=belly, pattern="runes", pcol=en, pemit=1.5 + 0.2 * L)
        return fur(c, belly=belly, pattern="stripes", pcol=acc)
    if pat in ("scales", "facets", "plates"):
        def sc(p, n):
            h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
            if n.y < -0.4:
                return belly
            row = int((p.y + 20) / 0.18)
            return c[(row + int((p.z + 20) / 0.18 + (row % 2) * 0.5)) % 3] if h > 0.08 else acc
        return sc
    return fur(c, belly=belly)


# ----------------------------------------------------------------------------- arquetipos
QUAD = {
    "cat": dict(L=1.6, W=0.95, H=0.9, legF=0.7, hs=1.0, snout=0.12, ear="pointy", tail="long", tail_n=6, tail_seg=0.24, tail_w=0.1, tail_lift=-45, slit=True),
    "dog": dict(L=1.8, W=1.05, H=1.0, legF=0.75, hs=1.05, snout=0.4, ear="floppy", tail="bushy", tail_n=4, tail_seg=0.22, tail_w=0.1, tail_lift=-55),
    "fox": dict(L=1.7, W=0.9, H=0.88, legF=0.72, hs=1.0, snout=0.45, ear="pointy", tail="bushy", tail_n=6, tail_seg=0.28, tail_w=0.14, tail_lift=-30),
    "bunny": dict(L=1.25, W=1.05, H=1.0, legF=0.35, legB=0.5, hs=1.1, snout=0.1, ear="long", tail="puff", tail_w=0.14),
    "bear": dict(L=2.0, W=1.45, H=1.35, legF=0.75, hs=1.2, snout=0.35, ear="round", tail="puff", tail_w=0.12),
    "panda": dict(L=2.0, W=1.45, H=1.35, legF=0.75, hs=1.25, snout=0.3, ear="round", tail="puff", tail_w=0.12),
    "deer": dict(L=2.0, W=0.95, H=1.0, legF=1.25, hs=0.9, snout=0.4, ear="pointy", tail="puff", tail_w=0.1, neckUp=0.6, neckFwd=0.35),
    "horse": dict(L=2.3, W=1.0, H=1.05, legF=1.35, hs=0.9, snout=0.65, ear="pointy", tail="long", tail_n=6, tail_seg=0.28, tail_w=0.12, tail_lift=-30, neckUp=0.9, neckFwd=0.45),
    "unicorn": dict(L=2.3, W=1.0, H=1.05, legF=1.35, hs=0.9, snout=0.65, ear="pointy", tail="long", tail_n=6, tail_seg=0.28, tail_w=0.12, tail_lift=-30, neckUp=0.9, neckFwd=0.45),
    "tiger": dict(L=2.2, W=1.1, H=1.05, legF=0.9, hs=1.05, snout=0.3, ear="round", tail="long", tail_n=7, tail_seg=0.28, tail_w=0.11, tail_lift=-25),
    "lion": dict(L=2.2, W=1.15, H=1.1, legF=0.9, hs=1.1, snout=0.35, ear="round", tail="tuft", tail_n=6, tail_seg=0.28, tail_w=0.09, tail_lift=-20),
    "wolf": dict(L=2.1, W=1.0, H=1.0, legF=1.0, hs=0.98, snout=0.55, ear="pointy", tail="bushy", tail_n=5, tail_seg=0.28, tail_w=0.13, tail_lift=-30),
    "pig": dict(L=1.8, W=1.25, H=1.15, legF=0.5, hs=1.05, snout=0.22, ear="floppy", tail="long", tail_n=2, tail_seg=0.15, tail_w=0.06, tail_lift=-60, muzzleW=1.3),
    "mouse": dict(L=1.15, W=0.85, H=0.8, legF=0.35, hs=0.9, snout=0.3, ear="round", tail="long", tail_n=7, tail_seg=0.22, tail_w=0.05, tail_lift=-5),
}


def quad_pet(m, arch, sp, L, S, v, f):
    P = dict(QUAD[arch])
    tw = sp.get("wings")
    B = dict(S=S, v=v, fur=f, eye="#2a1a1a" if L < 2 else sp["energy"], eye_glow=0 if L < 2 else 0.6 + 0.3 * L, eye_size=1.3,
             nose="#3a2020", ear_inner=_mix(sp["shell"][0], "#ff9ab8", 0.5), paw=_mix(sp["shell"][0], "#ffffff", 0.5),
             claws="#f6f0e2" if L >= 2 else None, teeth=L >= 3 and arch in ("tiger", "lion", "wolf", "dog", "fox", "bear"),
             brow=_mix(sp["shell"][0], "#000000", 0.35) if L >= 3 else None, fur_noise=0.07)
    B.update(P)
    if arch == "panda":
        base = f
        B["fur"] = lambda p, n: "#161616" if (abs(p.x) > 0.35 and p.y < 0.2) or n.y < -0.5 else base(p, n)
        B["head_fur"] = lambda p, n: "#161616" if (abs(p.x) > 0.15 and 0.0 < p.y < 0.35 and p.z > 0.3) else base(p, n)
    d = beast(m, B)
    hs = d["hs"]
    if arch in ("lion",):
        m.part("mane", "head", (0, 0, -0.05))
        voxelize(m, "mane", [ell((0, 0.05 * hs, -0.12 * hs), (0.95 * hs, 0.95 * hs, 0.55 * hs), 0.25, 2.6)], v,
                 lambda p, n: _mix(sp["accent"], "#000000", 0.2) if _hash(round(p.x, 3), round(p.y, 3)) > 0.5 else sp["accent"],
                 carve=[ell((0, 0.02 * hs, 0.4 * hs), (0.6 * hs, 0.58 * hs, 0.5 * hs))])
    if arch == "deer":
        for sx in (1, -1):
            pts = [Vector((sx * (0.25 + 0.3 * u), hs * 0.4 + 0.9 * u, -0.1 * u)) for u in (j / 4 for j in range(5))]
            polyline(m, "head", pts, 0.08, "#c8a878" if L < 4 else sp["metal"], metal=1 if L >= 4 else 0)
            segment(m, "head", pts[2], pts[2] + Vector((sx * 0.25, 0.25, 0.1)), 0.06, "#c8a878" if L < 4 else sp["metal"])
    if arch == "unicorn":
        crystal(m, "head", (0, 0.6 * hs, 0.45 * hs), 0.18, 0.9, sp["energy"] if L >= 2 else "#f2c14e", rot=(-30, 0, 0), emit=1.2 if L >= 2 else 0,
                tag="glow" if L >= 2 else None)
    if arch == "pig":
        m.box("head", (0, -0.1 * hs, 0.62 * hs + P["snout"]), (0.3 * hs, 0.22 * hs, 0.06), _mix(sp["shell"][0], "#ff9ab8", 0.4))
    return d, "body", "head"


def avian_pet(m, kind, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 1.4 * s, 0))
    if kind == "penguin":
        prims = [ell((0, 0, 0), (0.6 * s, 0.85 * s, 0.55 * s), 0.05, 3)]
    elif kind in ("owl", "chick"):
        prims = [ell((0, 0, 0), (0.62 * s, 0.68 * s, 0.6 * s), 0.06, 3)]
    else:
        prims = [ell((0, 0, 0), (0.5 * s, 0.5 * s, 0.75 * s), 0.05, 3)]
    belly = _mix(sp["shell"][0], "#ffffff", 0.55)
    voxelize(m, "body", prims, v, lambda p, n: (belly if (n.z > 0.4 and kind in ("penguin", "owl")) else f(p, n)))
    hy = {"penguin": 0.95, "owl": 0.75, "chick": 0.55}.get(kind, 0.55)
    m.part("head", "body", (0, hy * s, 0.25 * s if kind not in ("penguin", "owl", "chick") else 0.05 * s))
    hr = 0.42 * s if kind != "chick" else 0.5 * s
    skull = ell((0, 0, 0.05 * s), (hr, hr * 0.95, hr))
    voxelize(m, "head", [skull], v * 0.85, f)
    beak = "#ffb020" if kind in ("chick", "duck", "penguin", "bird") else "#e8c070"
    if kind == "duck":
        m.box("head", (0, -0.08 * s, hr + 0.15 * s), (0.36 * s, 0.1 * s, 0.35 * s), beak)
    else:
        voxelize(m, "head", [cap((0, -0.05 * s, hr * 0.85), (0, -0.12 * s, hr + 0.3 * s), 0.12 * s, 0.03 * s)], v * 0.6, lambda p, n: beak)
    put_eyes(m, "head", skull, hr * 2.0, sp["energy"] if L >= 2 else "#1a1a1a", glow=0.6 + 0.3 * L if L >= 2 else 0,
             x=0.2, y=0.08, size=0.75 if kind != "owl" else 1.0)
    if kind == "owl":
        for sx in (1, -1):
            m.box("head", (sx * 0.28 * s, 0.4 * s, 0), (0.12 * s, 0.3 * s, 0.12 * s), _mix(sp["shell"][0], "#000000", 0.2), r=(0, 0, sx * -20))
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.45 * s, 0.15 * s, -0.05 * s), (0, 0, sx * 10))
        if kind == "penguin":
            m.box(w, (sx * 0.1 * s, -0.35 * s, 0), (0.12 * s, 0.75 * s, 0.35 * s), _mix(sp["shell"][0], "#000000", 0.2), r=(0, 0, sx * 15))
        elif L >= 3:
            n = 6 + L
            _wing(m, w, sx, [(n, 0.5 * s, (0.9 + 0.2 * L) * s, 0.32 * s, 0, [sp["shell"][0], sp["shell"][1], sp["accent"]])],
                  [(0, 0), (0.3 * s, 0.25 * s), (0.6 * s, 0.6 * s), (0.85 * s, 1.0 * s)], sp["metal"], sp["metal"])
        else:
            voxelize(m, w, [ell((sx * 0.12 * s, -0.15 * s, -0.1 * s), (0.12 * s, 0.38 * s, 0.45 * s))], v, f)
    if kind not in ("penguin", "chick"):
        for i in range(3 + (L >= 3) * 2):
            a = (i - (2 + (L >= 3)) / 2) * 14
            q = quat((25, a, 0))
            m.box("body", q @ Vector((0, 0, -0.85 * s)), (0.16 * s, 0.05 * s, 0.6 * s), sp["accent"] if i % 2 else sp["shell"][1], r=q)
    for sx in (1, -1):
        m.box("body", (sx * 0.2 * s, -0.75 * s if kind != "penguin" else -0.92 * s, 0.1 * s), (0.14 * s, 0.3 * s, 0.24 * s), "#ffb020")
    return {"hs": hr}, "body", "head"


def fish_pet(m, kind, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 1.6 * s, 0))
    big = kind == "shark"
    voxelize(m, "body", [ell((0, 0, 0), (0.45 * s, 0.6 * s, (1.1 if big else 0.85) * s), 0.04, 3)], v,
             lambda p, n: _mix(sp["shell"][0], "#ffffff", 0.5) if n.y < -0.3 else f(p, n))
    skull = ell((0, 0.05 * s, 0.55 * s), (0.4 * s, 0.45 * s, 0.4 * s))
    put_eyes(m, "body", skull, 0.9 * s, sp["energy"] if L >= 2 else "#1a1a1a", glow=0.5 + 0.3 * L if L >= 2 else 0, x=0.32, y=0.12, size=0.9)
    m.part("tail0", "body", (0, 0, -(1.0 if big else 0.75) * s))
    for j in range(5):
        k = j / 4
        m.box("tail0", (0, (k - 0.5) * 0.9 * s, -0.25 * s - abs(k - 0.5) * 0.3 * s), (0.08 * s, 0.22 * s, 0.5 * s), sp["accent"])
    fin_h = 0.7 if big else 0.45
    for j in range(4):
        m.box("body", (0, (0.55 + j * 0.15) * s, (0.1 - j * 0.12) * s), (0.08 * s, 0.17 * s, (0.6 - j * 0.13) * s), sp["accent"])
    for sx in (1, -1):
        m.box("body", (sx * 0.5 * s, -0.25 * s, 0.2 * s), (0.4 * s, 0.06 * s, 0.25 * s), sp["accent"], r=(0, sx * 30, sx * -25))
    if big:
        for k in range(5):
            m.box("body", ((k - 2) * 0.1 * s, -0.3 * s, 0.95 * s), (0.06 * s, 0.12 * s, 0.05 * s), "#ffffff", r=(0, 0, 45))
    return {"hs": 0.8 * s}, "body", "body"


def insect_pet(m, kind, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 1.3 * s if kind in ("bee", "butterfly") else 0.55 * s, 0))
    acc = sp["accent"]
    if kind == "bee":
        voxelize(m, "body", [ell((0, 0, -0.45 * s), (0.5 * s, 0.48 * s, 0.6 * s), 0.03, 3)], v,
                 lambda p, n: acc if int((p.z + 10) / (0.22 * s)) % 2 else f(p, n))
        voxelize(m, "body", [ell((0, 0.05 * s, 0.2 * s), (0.38 * s, 0.36 * s, 0.32 * s), 0.08, 4)], v, f)
        m.box("body", (0, -0.05 * s, -1.08 * s), (0.08 * s, 0.08 * s, 0.25 * s), "#1a1a1a")
    elif kind in ("beetle", "ladybug"):
        dome = "#d8282a" if kind == "ladybug" else None
        voxelize(m, "body", [ell((0, 0.15 * s, -0.1 * s), (0.6 * s, 0.45 * s, 0.75 * s))], v,
                 lambda p, n: ("#161616" if abs(p.x) < 0.04 * s or vnoise(p.x * 3, p.y * 3, p.z * 3) > 0.7 else dome) if dome else
                 (_mix(sp["shell"][0], "#000000", 0.4) if abs(p.x) < 0.05 * s else f(p, n)))
        if kind == "beetle" and L >= 2:
            horn(m, "body", (0, 0.35 * s, 0.6 * s), (0, 0.8, 0.6), 0.7 * s, 0.12 * s, 20, sp["metal"], sp["energy"], tip_emit=1.0, tag="glow")
    elif kind == "butterfly":
        voxelize(m, "body", [cap((0, 0, -0.6 * s), (0, 0, 0.3 * s), 0.12 * s, 0.1 * s)], v * 0.8, lambda p, n: "#2a1a2a")
    elif kind == "spider":
        voxelize(m, "body", [ell((0, 0.35 * s, -0.5 * s), (0.55 * s, 0.45 * s, 0.6 * s)), ell((0, 0.25 * s, 0.25 * s), (0.35 * s, 0.3 * s, 0.35 * s))], v, f)
    m.part("head", "body", (0, 0.1 * s if kind != "spider" else 0.3 * s, 0.55 * s))
    skull = ell((0, 0, 0.05 * s), (0.3 * s, 0.28 * s, 0.28 * s))
    voxelize(m, "head", [skull], v * 0.8, lambda p, n: _mix(sp["shell"][0], "#000000", 0.5))
    put_eyes(m, "head", skull, 0.7 * s, sp["energy"] if L >= 1 else "#1a1a1a", glow=0.6 + 0.3 * L if L >= 1 else 0, x=0.28, y=0.08, size=1.0)
    for side, sx in (("L", 1), ("R", -1)):  # antenas
        pts = [Vector((sx * (0.1 + 0.2 * u) * s, (0.2 + 0.5 * u) * s, (0.1 + 0.15 * u) * s)) for u in (j / 3 for j in range(4))]
        polyline(m, "head", pts, 0.04 * s, "#1a1a1a")
        m.box("head", pts[-1], (0.08 * s,) * 3, sp["energy"] if L >= 2 else acc, emit=1.2 if L >= 2 else 0, tag="glow" if L >= 2 else None)
    nlegs = 4 if kind == "spider" else 3
    for i in range(nlegs):
        for side, sx in (("L", 1), ("R", -1)):
            lg = f"leg{i}_{side}"
            z = (0.3 - i * 0.3) * s if kind != "spider" else (0.4 - i * 0.3) * s
            m.part(lg, "body", (sx * 0.35 * s, 0.05 * s if kind != "spider" else 0.3 * s, z))
            ln = 0.7 if kind == "spider" else 0.45
            segment(m, lg, (0, 0, 0), (sx * ln * s, 0.2 * s, 0), 0.06 * s, "#1a1a1a")
            segment(m, lg, (sx * ln * s, 0.2 * s, 0), (sx * (ln + 0.2) * s, -0.45 * s if kind != "bee" else -0.25 * s, 0.05 * s), 0.05 * s, "#1a1a1a")
    if kind in ("bee", "butterfly"):
        for side, sx in (("L", 1), ("R", -1)):
            w = f"wing_{side}"
            m.part(w, "body", (sx * 0.15 * s, 0.35 * s, 0.05 * s))
            if kind == "bee":
                voxelize(m, w, [ell((sx * 0.55 * s, 0.35 * s, -0.2 * s), (0.5 * s, 0.06 * s, 0.32 * s))], v * 0.8,
                         lambda p, n: ("#e6f6ff", 0.4, "glow") if L >= 3 else "#e6f6ff")
            else:
                c2 = sp["shell"]

                def wcol(p, n, c2=c2):
                    r = math.hypot(p.x, p.z)
                    if r > 1.0 * s:
                        return "#1a1a2a"
                    if vnoise(p.x * 3, 0, p.z * 3) > 0.65:
                        return (sp["energy"], 1.2, "glow") if L >= 2 else acc
                    return c2[int(r * 4) % 3]
                voxelize(m, w, [ell((sx * 0.7 * s, 0, 0.3 * s), (0.7 * s, 0.06 * s, 0.6 * s)), ell((sx * 0.55 * s, -0.05 * s, -0.5 * s), (0.5 * s, 0.06 * s, 0.45 * s))],
                         v * 0.8, wcol)
    if kind == "bee" and "Reina" in m.meta_name:
        for k in range(5):
            a = k / 5 * TAU
            m.box("head", (math.cos(a) * 0.2 * s, 0.35 * s, math.sin(a) * 0.2 * s), (0.06 * s, 0.18 * s, 0.06 * s), "#f2c14e", metal=1)
    return {"hs": 0.6 * s}, "body", "head"


def snake_pet(m, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 0.35 * s, 0))
    n = 8
    prev = Vector((0, 0, 0))
    path = lambda k: Vector((math.sin(k * 6) * 0.6 * s, 0.0 + max(0, 0.25 - k) * 4 * s, 1.0 * s - k * 3.0 * s))
    prev = path(0)
    m.part("s0", "body", tuple(prev))
    for i in range(1, n):
        p = path(i / (n - 1))
        m.part(f"s{i}", f"s{i - 1}", tuple(p - prev))
        prev = p
    for i in range(1, n):
        r_ = (0.32 - 0.025 * i) * s
        nxt = path(min(1, (i + 1) / (n - 1))) - path(i / (n - 1))
        voxelize(m, f"s{i}", [cap((0, 0, 0), tuple(nxt * 1.05), r_, r_ * 0.9)], v, f)
    skull = ell((0, 0.05 * s, 0.2 * s), (0.36 * s, 0.3 * s, 0.45 * s))
    voxelize(m, "s0", [skull], v * 0.85, f)
    put_eyes(m, "s0", skull, 0.8 * s, sp["energy"] if L >= 1 else "#ffcf3a", glow=0.6 + 0.3 * L if L >= 1 else 0, x=0.3, y=0.12, slit=True)
    m.box("s0", (0, -0.1 * s, 0.68 * s), (0.04 * s, 0.03 * s, 0.25 * s), "#ff3a5a")
    return {"hs": 0.7 * s, "segs": n}, "body", "s0"


def blob_pet(m, kind, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 0.75 * s if kind == "slime" else 1.4 * s, 0))
    if kind == "slime":
        prims = [ell((0, 0, 0), (0.75 * s, 0.6 * s, 0.7 * s), 0.05, 2)]
        col = lambda p, n: (_mix(sp["shell"][0], "#ffffff", 0.5) if n.y > 0.75 and _hash(round(p.x, 3), round(p.z, 3)) > 0.7 else f(p, n))
    elif kind == "ghost":
        prims = [ell((0, 0.2 * s, 0), (0.6 * s, 0.7 * s, 0.6 * s)), cap((0, 0, 0), (0, -0.7 * s, 0), 0.55 * s, 0.45 * s, 0.25, 4)]
        col = lambda p, n: (f(p, n)[0], 0.3, "glow") if isinstance(f(p, n), tuple) else (f(p, n), 0.3 + 0.1 * L, "glow")
    elif kind == "jelly":
        prims = [ell((0, 0.2 * s, 0), (0.75 * s, 0.55 * s, 0.75 * s))]
        col = lambda p, n: (f(p, n) if not isinstance(f(p, n), tuple) else f(p, n)[0], 0.5 + 0.1 * L, "glow")
    else:  # shroom
        prims = [cap((0, -0.6 * s, 0), (0, 0.1 * s, 0), 0.38 * s, 0.32 * s)]
        col = lambda p, n: "#f2ead6"
    carve = [ell((0, -0.4 * s, 0), (0.7 * s, 0.35 * s, 0.7 * s))] if kind == "jelly" else None
    voxelize(m, "body", prims, v, col, carve=carve)
    if kind == "shroom":
        m.part("cap", "body", (0, 0.2 * s, 0))
        voxelize(m, "cap", [ell((0, 0.15 * s, 0), (0.85 * s, 0.45 * s, 0.85 * s))], v,
                 lambda p, n: "#ffffff" if vnoise(p.x * 3, p.y * 3, p.z * 3) > 0.66 else sp["shell"][0], carve=[ell((0, -0.15 * s, 0), (0.8 * s, 0.25 * s, 0.8 * s))])
    eye_z = {"slime": 0.62, "ghost": 0.55, "jelly": 0.6, "shroom": 0.33}[kind] * s
    ey = {"slime": 0.05, "ghost": 0.35, "jelly": 0.0, "shroom": -0.15}[kind] * s
    for sx in (1, -1):
        m.box("body", (sx * 0.22 * s, ey, eye_z), (0.2 * s, 0.24 * s, 0.05), "#ffffff")
        m.box("body", (sx * 0.22 * s, ey - 0.02 * s, eye_z + 0.03), (0.12 * s, 0.16 * s, 0.04), sp["energy"] if L >= 2 else "#1a1a1a",
              emit=0.6 + 0.3 * L if L >= 2 else 0, tag="eyes" if L >= 2 else None)
        m.box("body", (sx * 0.25 * s, ey + 0.06 * s, eye_z + 0.05), (0.05 * s, 0.05 * s, 0.02), "#ffffff")
    m.box("body", (0, ey - 0.22 * s, eye_z - 0.02), (0.2 * s, 0.06 * s, 0.04), "#3a1a2a")
    if kind == "jelly":
        for k in range(8):
            a = k / 8 * TAU
            tn = f"tent{k}"
            m.part(tn, "body", (math.cos(a) * 0.45 * s, -0.15 * s, math.sin(a) * 0.45 * s))
            for j in range(5):
                m.box(tn, (0, -(0.12 + j * 0.22) * s, 0), (0.08 * s, 0.24 * s, 0.08 * s), sp["accent"], emit=0.6 if L >= 2 else 0, tag="glow" if L >= 2 else None)
    if kind == "ghost":
        for side, sx in (("L", 1), ("R", -1)):
            m.part(f"arm_{side}", "body", (sx * 0.55 * s, 0.0, 0.1 * s))
            voxelize(m, f"arm_{side}", [cap((0, 0, 0), (sx * 0.4 * s, -0.2 * s, 0.15 * s), 0.14 * s, 0.1 * s)], v, col)
    if kind == "shroom":
        for sx in (1, -1):
            m.box("body", (sx * 0.2 * s, -0.72 * s, 0.05 * s), (0.18 * s, 0.12 * s, 0.26 * s), "#c8b890")
    return {"hs": 0.8 * s}, "body", "body"


def golem_pet(m, kind, sp, L, S, v, f):
    s = S
    robot = kind == "robot"
    metal = sp["metal"]
    m.part("body", "root", (0, 1.2 * s, 0))
    if robot:
        m.box("body", (0, 0, 0), (1.1 * s, 1.0 * s, 0.8 * s), sp["shell"][0], metal=1)
        m.box("body", (0, 0.05 * s, 0.41 * s), (0.6 * s, 0.4 * s, 0.04), "#0a0e14")
        for k in range(3):
            m.box("body", ((k - 1) * 0.15 * s, 0.05 * s, 0.44 * s), (0.08 * s, 0.08 * s, 0.03), sp["energy"], emit=2, tag="glow")
    else:
        voxelize(m, "body", [ell((0, 0, 0), (0.7 * s, 0.65 * s, 0.55 * s), 0.18, 2)], v, f)
        for k in range(3 + L):
            crystal(m, "body", ((k % 3 - 1) * 0.35 * s, 0.4 * s + 0.1 * (k // 3), 0.3 * s), 0.18 * s, 0.4 * s, sp["energy"], rot=(30, 0, (k - 1) * 20),
                    emit=0.8 + 0.2 * L, tag="glow")
    m.part("head", "body", (0, 0.75 * s, 0.05 * s))
    if robot:
        m.box("head", (0, 0.2 * s, 0), (0.75 * s, 0.55 * s, 0.6 * s), sp["shell"][1], metal=1)
        m.box("head", (0, 0.2 * s, 0.31 * s), (0.6 * s, 0.35 * s, 0.03), "#0a0e14")
        for sx in (1, -1):
            m.box("head", (sx * 0.15 * s, 0.22 * s, 0.33 * s), (0.12 * s, 0.12 * s, 0.03), sp["energy"], emit=2.5, tag="eyes")
        segment(m, "head", (0, 0.47 * s, 0), (0, 0.85 * s, 0), 0.05 * s, metal, metal=1)
        m.box("head", (0, 0.9 * s, 0), (0.14 * s,) * 3, sp["energy"], emit=3, tag="eyes")
    else:
        skull = ell((0, 0.15 * s, 0), (0.42 * s, 0.38 * s, 0.4 * s), 0.12, 2)
        voxelize(m, "head", [skull], v, f)
        for sx in (1, -1):
            m.box("head", (sx * 0.15 * s, 0.2 * s, 0.38 * s), (0.12 * s, 0.08 * s, 0.05), sp["energy"], emit=1.5 + 0.3 * L, tag="eyes")
    for side, sx in (("L", 1), ("R", -1)):
        a = f"arm_{side}"
        m.part(a, "body", (sx * 0.8 * s, 0.25 * s, 0))
        if robot:
            m.box(a, (0, -0.35 * s, 0), (0.3 * s, 0.8 * s, 0.3 * s), sp["shell"][1], metal=1)
            m.box(a, (0, -0.85 * s, 0.05 * s), (0.4 * s, 0.3 * s, 0.4 * s), metal, metal=1)
        else:
            voxelize(m, a, [cap((0, 0, 0), (0, -0.7 * s, 0.1 * s), 0.25 * s, 0.3 * s, 0.15, 2)], v, f)
        lg = f"leg_{side}"
        m.part(lg, "body", (sx * 0.35 * s, -0.55 * s, 0))
        if robot:
            m.box(lg, (0, -0.3 * s, 0), (0.32 * s, 0.6 * s, 0.32 * s), sp["shell"][1], metal=1)
        else:
            voxelize(m, lg, [cap((0, 0, 0), (0, -0.55 * s, 0.05 * s), 0.25 * s, 0.27 * s, 0.12, 2)], v, f)
    return {"hs": 0.8 * s}, "body", "head"


def octo_pet(m, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 1.2 * s, 0))
    skull = ell((0, 0.25 * s, 0), (0.65 * s, 0.75 * s, 0.6 * s), 0.04, 3)
    voxelize(m, "body", [skull], v, f)
    put_eyes(m, "body", ell((0, 0.05 * s, 0), (0.6 * s, 0.6 * s, 0.6 * s)), 1.0 * s, sp["energy"] if L >= 2 else "#1a1a1a",
             glow=0.6 + 0.3 * L if L >= 2 else 0, x=0.28, y=0.0, size=1.0)
    for k in range(8):
        a = k / 8 * TAU
        tn = f"tent{k}"
        m.part(tn, "body", (math.cos(a) * 0.4 * s, -0.35 * s, math.sin(a) * 0.4 * s), (0, -math.degrees(a) + 90, 0))
        pts = [Vector((0, -0.25 * u * s, (0.2 + 0.9 * u) * s + 0.3 * u * u * s)) for u in (j / 5 for j in range(6))]
        pts = [Vector((p.x, p.y + (0.6 * (p.z / s - 0.6) ** 2 - 0.2) * s * 0.5, p.z)) for p in pts]
        for j in range(5):
            segment(m, tn, pts[j], pts[j + 1], (0.2 - 0.03 * j) * s, sp["shell"][j % 2])
            if j % 2 == 0:
                m.box(tn, (pts[j] + pts[j + 1]) / 2 + Vector((0, -0.08 * s, 0)), (0.07 * s,) * 3, _mix(sp["shell"][0], "#ffffff", 0.5))
    return {"hs": 0.9 * s}, "body", "body"


def frog_turtle_crab(m, kind, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 0.55 * s, 0))
    if kind == "frog":
        voxelize(m, "body", [ell((0, 0.1 * s, 0), (0.75 * s, 0.45 * s, 0.7 * s), 0.04, 3)], v,
                 lambda p, n: _mix(sp["shell"][0], "#ffffff", 0.5) if n.y < -0.3 else f(p, n))
        m.part("head", "body", (0, 0.35 * s, 0.35 * s))
        for sx in (1, -1):
            e = ell((sx * 0.32 * s, 0.25 * s, 0.1 * s), (0.2 * s, 0.2 * s, 0.2 * s))
            voxelize(m, "head", [e], v * 0.8, f)
            put_eyes(m, "head", e, 0.8 * s, sp["energy"] if L >= 2 else "#1a1a1a", glow=0.6 + 0.3 * L if L >= 2 else 0, x=0.0, y=0.0, size=0.9)
        m.box("head", (0, -0.05 * s, 0.62 * s), (0.7 * s, 0.04 * s, 0.05), "#3a1a2a")
    elif kind == "turtle":
        def shell(p, n):
            h = _hash(round(p.x, 3), round(p.z, 3))
            cx, cz = (p.x / (0.35 * s)) % 1, (p.z / (0.35 * s)) % 1
            if n.y > 0 and (cx < 0.12 or cz < 0.12):
                return _mix(sp["shell"][0], "#000000", 0.45)
            return sp["shell"][int(h * 3) % 3] if n.y > -0.2 else _mix(sp["shell"][0], "#ffffff", 0.5)
        voxelize(m, "body", [ell((0, 0.2 * s, 0), (0.85 * s, 0.5 * s, 0.95 * s))], v, shell, carve=[ell((0, -0.35 * s, 0), (1.0 * s, 0.4 * s, 1.1 * s))])
        m.part("head", "body", (0, 0.15 * s, 0.95 * s))
        skin = _mix(sp["accent"], "#7fa85a", 0.4)
        skull = ell((0, 0.05 * s, 0.15 * s), (0.3 * s, 0.28 * s, 0.32 * s))
        voxelize(m, "head", [skull], v * 0.8, lambda p, n: skin)
        put_eyes(m, "head", skull, 0.7 * s, sp["energy"] if L >= 2 else "#1a1a1a", glow=0.6 + 0.3 * L if L >= 2 else 0, x=0.3, y=0.1)
        if L >= 3:
            for k in range(4):
                crystal(m, "body", ((k % 2 - 0.5) * 0.6 * s, 0.75 * s, (k // 2 - 0.5) * 0.7 * s), 0.18 * s, 0.4 * s, sp["energy"], emit=1.2, tag="glow")
    else:  # crab
        voxelize(m, "body", [ell((0, 0.15 * s, 0), (0.75 * s, 0.35 * s, 0.55 * s), 0.04, 3)], v, f)
        m.part("head", "body", (0, 0.35 * s, 0.4 * s))
        for sx in (1, -1):
            segment(m, "head", (sx * 0.2 * s, 0, 0), (sx * 0.25 * s, 0.35 * s, 0.05 * s), 0.06 * s, sp["shell"][0])
            e = ell((sx * 0.25 * s, 0.42 * s, 0.05 * s), (0.11 * s, 0.11 * s, 0.11 * s))
            put_eyes(m, "head", e, 0.45 * s, sp["energy"] if L >= 2 else "#1a1a1a", glow=0.8 if L >= 2 else 0, x=0, y=0, size=1.0)
            cl = f"claw_{'L' if sx > 0 else 'R'}"
            m.part(cl, "body", (sx * 0.75 * s, 0.15 * s, 0.35 * s))
            segment(m, cl, (0, 0, 0), (sx * 0.25 * s, 0.1 * s, 0.35 * s), 0.12 * s, sp["shell"][1])
            voxelize(m, cl, [ell((sx * 0.3 * s, 0.15 * s, 0.6 * s), (0.22 * s, 0.18 * s, 0.25 * s))], v * 0.8, f)
    legs = [] if kind == "crab" else [("FL", 1, 1), ("FR", -1, 1), ("BL", 1, -1), ("BR", -1, -1)]
    for nm, sx, sz in legs:
        lg = f"leg_{nm}"
        m.part(lg, "body", (sx * 0.55 * s, -0.05 * s, sz * 0.45 * s))
        voxelize(m, lg, [cap((0, 0, 0), (sx * 0.2 * s, -0.4 * s, sz * 0.15 * s), 0.17 * s, 0.14 * s)], v,
                 (lambda p, n: _mix(sp["accent"], "#7fa85a", 0.4)) if kind == "turtle" else f)
    if kind == "crab":
        for i in range(3):
            for sx in (1, -1):
                lg = f"leg{i}_{'L' if sx > 0 else 'R'}"
                m.part(lg, "body", (sx * 0.6 * s, 0.05 * s, (0.1 - i * 0.25) * s))
                segment(m, lg, (0, 0, 0), (sx * 0.45 * s, 0.15 * s, 0), 0.07 * s, sp["shell"][1])
                segment(m, lg, (sx * 0.45 * s, 0.15 * s, 0), (sx * 0.6 * s, -0.5 * s, 0), 0.06 * s, sp["shell"][1])
    return {"hs": 0.7 * s}, "body", "head"


def bat_pet(m, sp, L, S, v, f):
    s = S
    m.part("body", "root", (0, 1.6 * s, 0))
    voxelize(m, "body", [ell((0, 0, 0), (0.42 * s, 0.5 * s, 0.38 * s), 0.08, 4)], v, f)
    m.part("head", "body", (0, 0.55 * s, 0.05 * s))
    skull = ell((0, 0, 0.05 * s), (0.36 * s, 0.32 * s, 0.32 * s))
    voxelize(m, "head", [skull, cap((0.18 * s, 0.2 * s, 0), (0.3 * s, 0.6 * s, -0.05 * s), 0.12 * s, 0.02 * s),
                         cap((-0.18 * s, 0.2 * s, 0), (-0.3 * s, 0.6 * s, -0.05 * s), 0.12 * s, 0.02 * s)], v * 0.8, f)
    put_eyes(m, "head", skull, 0.75 * s, sp["energy"] if L >= 1 else "#ff3a3a", glow=0.8 + 0.3 * L, x=0.3, y=0.08)
    for sx in (1, -1):
        m.box("head", (sx * 0.07 * s, -0.18 * s, 0.33 * s), (0.04 * s, 0.1 * s, 0.03), "#ffffff")
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.3 * s, 0.2 * s, 0))
        sc = (0.45 + 0.06 * L) * s
        membrane_wing(m, w, sx, (1.0 * sc, 0.8 * sc), [(0.9 * sc, 1.5 * sc), (2.0 * sc, 1.3 * sc), (2.4 * sc, 0.3 * sc), (1.6 * sc, -0.6 * sc)],
                      _mix(sp["shell"][0], "#000000", 0.4), sp["shell"][1], sp["shell"][2], step=0.12 * s)
    return {"hs": 0.7 * s}, "body", "head"


def dragon_pet(m, sp, L, S, v, f):
    d, body, head = quad_pet(m, "tiger", sp, L, S, v, f)
    hs = d["hs"]
    for sx in (1, -1):
        horn(m, "head", (sx * hs * 0.28, hs * 0.36, -hs * 0.05), (sx * 0.3, 0.6, -0.7), (0.6 + 0.12 * L) * S, hs * 0.14, -14,
             sp["metal"], sp["energy"], tip_emit=0.8 * (L >= 2), tag="glow" if L >= 2 else None)
    for i in range(6):
        m.box("body", (0, 0.58 * d["H"] + 0.05, 0.4 * d["L"] - i * d["L"] / 6), (0.08 * S, 0.3 * S, 0.3 * S), sp["accent"], r=(45, 0, 0))
    wt = sp.get("wings", "bat")
    for side, sx in (("L", 1), ("R", -1)):
        w = f"dwing_{side}"
        m.part(w, "body", (sx * d["W"] * 0.4, d["H"] * 0.4, d["L"] * 0.15), (0, sx * -20, sx * 10))
        sc = (0.45 + 0.08 * L) * S
        if wt == "feather":
            _wing(m, w, sx, [(7 + L, 0.6 * sc, 1.7 * sc, 0.4 * sc, 0, [sp["shell"][0], sp["accent"], sp["energy"]])],
                  [(0, 0), (0.6 * sc, 0.5 * sc), (1.2 * sc, 1.1 * sc), (1.7 * sc, 1.8 * sc)], sp["metal"], sp["metal"])
        elif wt == "crystal":
            for i in range(5 + L):
                k = i / (4 + L)
                th = math.radians(-20 + k * 110)
                Lw = (0.9 + 0.8 * math.sin(k * math.pi)) * sc
                dd = Vector((sx * math.cos(th), math.sin(th), 0))
                crystal(m, w, dd * (0.2 + Lw / 2), 0.3 * sc, Lw, sp["energy"] if i % 2 else sp["accent"],
                        rot=(0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th)), emit=0.6, tag="glow")
        else:
            membrane_wing(m, w, sx, (1.1 * sc, 1.3 * sc), [(1.0 * sc, 2.1 * sc), (2.2 * sc, 2.1 * sc), (3.0 * sc, 1.0 * sc), (2.9 * sc, -0.3 * sc)],
                          _mix(sp["shell"][0], "#000000", 0.4), sp["shell"][1], sp["accent"], step=0.12 * S)
    return d, body, head


# ----------------------------------------------------------------------------- accesorios por rareza
def flair(m, sp, L, body, head, hs, S, arch):
    en, metal = sp["energy"], sp["metal"]
    quad = arch in QUAD or arch == "dragon"
    if L >= 1 and quad:
        ring(m, head, hs * 0.5, 14, (0.08 * S, 0.12 * S), metal, center=(0, -hs * 0.45, -hs * 0.1), rot=(70, 0, 0), metal=1)
        m.box(head, (0, -hs * 0.62, hs * 0.18), (0.1 * S, 0.1 * S, 0.1 * S), en if L >= 2 else metal, r=(45, 0, 45), metal=0 if L >= 2 else 1,
              emit=1.5 if L >= 2 else 0, tag="glow" if L >= 2 else None)
    if L >= 2:
        m.box(head, (0, hs * 0.38, hs * 0.48), (0.12 * S, 0.12 * S, 0.06 * S), en, r=(0, 0, 45), emit=1.5 + 0.2 * L, tag="glow")
    if L >= 3:
        m.part("aura", "root", (0, 0.05, 0))
        ring(m, "aura", 1.4 * S, 32, (0.07, 0.04), en, emit=1.5 + 0.2 * L, tag="neon")
        if L >= 5:
            ring(m, "aura", 1.7 * S, 40, (0.05, 0.04), en, emit=1.5, tag="neon")
        if quad and arch != "dragon" and arch not in ("unicorn",):
            wt = sp.get("wings", "feather")
            for side, sx in (("L", 1), ("R", -1)):
                w = f"fwing_{side}"
                m.part(w, body, (sx * 0.35 * S, 0.45 * S, 0.25 * S), (0, sx * -20, sx * 10))
                sc = (0.3 + 0.08 * L) * S
                if wt == "bat":
                    membrane_wing(m, w, sx, (1.1 * sc, 1.3 * sc), [(1.0 * sc, 2.1 * sc), (2.2 * sc, 2.1 * sc), (3.0 * sc, 1.0 * sc), (2.9 * sc, -0.3 * sc)],
                                  _mix(sp["shell"][0], "#000000", 0.4), sp["shell"][1], sp["accent"], step=0.1 * S)
                elif wt in ("crystal", "mech", "fin", "leaf"):
                    for i in range(4 + L):
                        k = i / (3 + L)
                        th = math.radians(-15 + k * 105)
                        Lw = (0.9 + 0.7 * math.sin(k * math.pi)) * sc * 1.5
                        dd = Vector((sx * math.cos(th), math.sin(th), 0))
                        rot = (0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th))
                        if wt == "mech":
                            m.box(w, dd * (0.2 + Lw / 2), (0.16 * sc * 2, Lw, 0.05), sp["shell"][1], r=rot)
                            m.box(w, dd * (0.2 + Lw / 2) + Vector((0, 0, 0.04)), (0.04, Lw * 0.9, 0.03), en, r=rot, emit=1.5, tag="glow")
                        else:
                            crystal(m, w, dd * (0.2 + Lw / 2), 0.28 * sc * 2, Lw, en if i % 2 else sp["accent"], rot=rot, emit=0.6, tag="glow")
                else:
                    _wing(m, w, sx, [(6 + L, 0.5 * sc * 2, 1.4 * sc * 2, 0.35 * sc * 2, 0, ["#ffffff", sp["shell"][0], sp["accent"]])],
                          [(0, 0), (0.5 * sc, 0.4 * sc), (1.0 * sc, 0.9 * sc), (1.4 * sc, 1.5 * sc)], metal, metal)
    if L >= 4:
        for i in range(3 if L < 6 else 5):
            o = f"orb{i}"
            a = i / (3 if L < 6 else 5) * TAU
            m.part(o, "root", (math.cos(a) * 1.8 * S, 1.8 * S, math.sin(a) * 1.8 * S))
            crystal(m, o, (0, 0, 0), 0.22 * S, 0.45 * S, en, emit=1.6, tag="glow")
    if L >= 4:
        m.part("crownp", head, (0, hs * 0.55, 0))
        ring(m, "crownp", hs * 0.3, 12, (0.08 * S, 0.12 * S), metal, metal=1)
        for k in range(6):
            a = k / 6 * TAU
            m.box("crownp", (math.cos(a) * hs * 0.3, 0.12 * S, math.sin(a) * hs * 0.3), (0.06 * S, 0.2 * S, 0.06 * S), metal, metal=1)
            if k % 2 == 0:
                m.box("crownp", (math.cos(a) * hs * 0.3, 0.26 * S, math.sin(a) * hs * 0.3), (0.08 * S,) * 3, en, r=(45, 0, 45), emit=1.5, tag="glow")
    if L >= 5:
        m.part("halo", head, (0, hs * 1.0, -0.1 * S), (10, 0, 0))
        ring(m, "halo", hs * 0.42, 20, (0.1 * S, 0.08 * S), metal, metal=1)
        ring(m, "halo", hs * 0.42, 20, (0.04 * S, 0.1 * S), en, emit=1.5, tag="glow")
    if L >= 6:
        for i in range(4):
            fl = f"aflame{i}"
            a = i / 4 * TAU + 0.4
            m.part(fl, "root", (math.cos(a) * 1.2 * S, 0.1, math.sin(a) * 1.2 * S))
            flame(m, fl, (0, 0, 0), 0.7 * S, 0.25 * S, seed=i, tag="fire")
            for b in m.parts[fl].boxes:
                b["col"] = _mix(en, "#ffffff", min(0.8, b["c"].y / (0.9 * S)))


# ----------------------------------------------------------------------------- construcción
LEVEL_V = [0.15, 0.135, 0.12, 0.11, 0.1, 0.092, 0.085]

# Mascotas con el estilo "studs" (superficie tipo LEGO/Roblox, colores saturados, formas más suaves)
_here = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
STUDS = set(open(__import__("os").path.join(_here, "studs_pets.txt")).read().split())


def _saturate(h, k=1.3, light=1.04):
    import colorsys
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    r, g, b = colorsys.hsv_to_rgb(hh, min(1.0, ss * k), min(1.0, vv * light))
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
TIER = [1, 2, 4, 6, 9, 12, 16]


def build_pet(egg_id, idx):
    sculpt.VOXEL_SCALE = 1.0
    studs = f"pet_{egg_id[4:]}_{idx + 1}" in STUDS
    sculpt.MODE = "smooth" if studs else "voxel"
    try:
        return _build_pet(egg_id, idx)
    finally:
        sculpt.MODE = "voxel"


def _build_pet(egg_id, idx):
    sp = egg_spec(egg_id)
    name, arch = PETS[egg_id][idx]
    studs = f"pet_{egg_id[4:]}_{idx + 1}" in STUDS
    if studs:
        sp = dict(sp, shell=[_saturate(c) for c in sp["shell"]], accent=_saturate(sp["accent"]), energy=_saturate(sp["energy"], 1.2))
    rar = sp["rarity"]
    L = RARITIES[rar][1]
    if sp.get("rebirth"):
        L = min(6, 2 + sp["rebirth"] // 4)
    S = 0.85 + 0.06 * L
    v = LEVEL_V[L] * S * (0.85 if studs else 1.0)
    m = Model(f"pet_{egg_id[4:]}_{idx + 1}", fps=24, frames=48)
    m.meta_name = name
    m.part("root")
    f = pet_fur(sp, L, shade=(idx - 1.5) * 0.6)
    if arch in QUAD:
        d, body, head = quad_pet(m, arch, sp, L, S, v, f)
        kind = "quad"
    elif arch in ("bird", "owl", "penguin", "duck", "chick"):
        d, body, head = avian_pet(m, arch, sp, L, S, v, f)
        kind = "avian"
    elif arch in ("fish", "shark"):
        d, body, head = fish_pet(m, arch, sp, L, S, v, f)
        kind = "fish"
    elif arch in ("bee", "beetle", "butterfly", "ladybug", "spider"):
        d, body, head = insect_pet(m, arch, sp, L, S, v, f)
        kind = "insect"
    elif arch == "snake":
        d, body, head = snake_pet(m, sp, L, S, v, f)
        kind = "snake"
    elif arch in ("slime", "ghost", "jelly", "shroom"):
        d, body, head = blob_pet(m, arch, sp, L, S, v, f)
        kind = "blob"
    elif arch in ("golem", "robot"):
        d, body, head = golem_pet(m, arch, sp, L, S, v, f)
        kind = "golem"
    elif arch == "octo":
        d, body, head = octo_pet(m, sp, L, S, v, f)
        kind = "octo"
    elif arch in ("frog", "turtle", "crab"):
        d, body, head = frog_turtle_crab(m, arch, sp, L, S, v, f)
        kind = "small"
    elif arch == "bat":
        d, body, head = bat_pet(m, sp, L, S, v, f)
        kind = "bat"
    elif arch == "dragon":
        d, body, head = dragon_pet(m, sp, L, S, v, f)
        kind = "quad"
    else:
        raise ValueError(arch)
    flair(m, sp, L, body, head, d["hs"], S, arch)
    has = set(m.parts)
    flying = kind in ("fish", "bat", "blob") and arch != "slime" and arch != "shroom" or arch in ("bee", "butterfly", "jelly", "ghost")

    def animate(t):
        a = t * TAU
        pose = {}
        if kind == "quad":
            if L >= 1 and arch not in ("bunny",):
                walk(pose, t, amp=10 + 3 * L, speed=1, bob=0.03, knee=15 + 3 * L)
            else:
                hop = max(0.0, math.sin(a)) * (0.4 if arch == "bunny" else 0.1)
                pose["body"] = {"p": (0, hop, 0)}
            for i in range(8):
                if f"tail{i}" in has and i > 0:
                    pose[f"tail{i}"] = {"r": quat((0, (8 + 3 * L) * math.sin(a * 2 - i * 0.6), 0))}
            pose["head"] = {"r": quat((3 * math.sin(a * 2), (6 + L) * math.sin(a), 0))}
            if L >= 2:
                tw = max(0.0, math.sin(a * 3)) ** 8
                for side in ("L", "R"):
                    if f"ear_{side}" in has:
                        pose[f"ear_{side}"] = {"r": quat((-15 * tw, 0, 0))}
            if L >= 3 and "jaw" in has:
                pose["jaw"] = {"r": quat((14 * max(0.0, math.sin(a)) ** 4, 0, 0))}
        elif kind in ("avian", "bat"):
            flap = math.sin(a * (4 if L >= 3 else 2))
            hover = kind == "bat" or arch in ("bird", "owl") and L >= 3
            pose["body"] = {"p": (0, (0.3 * math.sin(a * 2) + (0.6 if hover else 0)) if hover else 0.05 * abs(math.sin(a * 2)), 0)}
            for side, sx in (("L", 1), ("R", -1)):
                if f"wing_{side}" in has:
                    pose[f"wing_{side}"] = {"r": quat((0, 0, sx * (25 if hover else 12) * flap))}
            pose["head"] = {"r": quat((5 * math.sin(a * 2), 12 * math.sin(a), 0))}
        elif kind == "fish":
            pose["body"] = {"p": (0, 0.2 * math.sin(a * 2), 0), "r": quat((0, 10 * math.sin(a), 0))}
            pose["tail0"] = {"r": quat((0, 25 * math.sin(a * 4), 0))}
        elif kind == "insect":
            pose["body"] = {"p": (0, 0.2 * math.sin(a * 2) if flying else 0.02 * abs(math.sin(a * 4)), 0), "r": quat((0, 8 * math.sin(a), 0))}
            for side, sx in (("L", 1), ("R", -1)):
                if f"wing_{side}" in has:
                    pose[f"wing_{side}"] = {"r": quat((0, 0, sx * (35 if arch == "bee" else 25) * math.sin(a * (12 if arch == "bee" else 3))))}
                for i in range(4):
                    if f"leg{i}_{side}" in has:
                        pose[f"leg{i}_{side}"] = {"r": quat((0, 15 * math.sin(a * 4 + i * 2 + (0 if sx > 0 else math.pi)), 0))}
        elif kind == "snake":
            for i in range(d["segs"]):
                pose[f"s{i}"] = {"r": quat((0, (10 + 2 * L) * math.sin(a * 2 - i * 0.7), 0))}
        elif kind == "blob":
            sq = math.sin(a * 2)
            if arch == "slime":
                pose["body"] = {"s": (1 + 0.08 * sq, 1 - 0.1 * sq, 1 + 0.08 * sq), "p": (0, 0.15 * max(0.0, -sq), 0)}
            else:
                pose["body"] = {"p": (0, 0.25 * sq, 0), "r": quat((0, 8 * math.sin(a), 4 * math.sin(a * 2)))}
            for k in range(8):
                if f"tent{k}" in has:
                    pose[f"tent{k}"] = {"r": quat((12 * math.sin(a * 2 - k), 0, 8 * math.sin(a * 2 + k)))}
            for side, sx in (("L", 1), ("R", -1)):
                if f"arm_{side}" in has:
                    pose[f"arm_{side}"] = {"r": quat((20 * math.sin(a * 2), 0, sx * 10 * math.sin(a * 2)))}
            if "cap" in has:
                pose["cap"] = {"r": quat((0, 0, 6 * math.sin(a * 2)))}
        elif kind == "golem":
            step = math.sin(a)
            pose["body"] = {"p": (0, 0.06 * abs(step), 0), "r": quat((0, 6 * step, 2 * step))}
            pose["leg_L"] = {"r": quat((-20 * max(0, step), 0, 0))}
            pose["leg_R"] = {"r": quat((-20 * max(0, -step), 0, 0))}
            pose["arm_L"] = {"r": quat((18 * step, 0, 0))}
            pose["arm_R"] = {"r": quat((-18 * step, 0, 0))}
            pose["head"] = {"r": quat((0, 10 * math.sin(a), 0))}
        elif kind == "octo":
            pose["body"] = {"p": (0, 0.2 * math.sin(a * 2), 0)}
            for k in range(8):
                pose[f"tent{k}"] = {"r": quat((15 * math.sin(a * 2 - k * 0.8), 0, 0))}
        elif kind == "small":
            pose["body"] = {"p": (0, (0.35 if arch == "frog" else 0.04) * max(0.0, math.sin(a)) ** 2, 0)}
            pose["head"] = {"r": quat((0, 10 * math.sin(a), 0))}
            for side, sx in (("L", 1), ("R", -1)):
                if f"claw_{side}" in has:
                    pose[f"claw_{side}"] = {"r": quat((0, sx * 15 * math.sin(a * 2), 0))}
        for side, sx in (("L", 1), ("R", -1)):
            for w in ("fwing", "dwing"):
                if f"{w}_{side}" in has:
                    pose[f"{w}_{side}"] = {"r": quat((0, sx * 8 * math.sin(a * 2), sx * 20 * math.sin(a * 2)))}
        if "aura" in has:
            pose["aura"] = {"r": quat((0, math.degrees(a), 0))}
        for i in range(5):
            if f"orb{i}" in has:
                piv = m.parts[f"orb{i}"].pivot
                n_ = 3 if L < 6 else 5
                ang = i / n_ * TAU + a
                r_ = math.hypot(piv.x, piv.z)
                pose[f"orb{i}"] = {"p": (math.cos(ang) * r_ - piv.x, 0.25 * math.sin(a * 2 + i), math.sin(ang) * r_ - piv.z), "r": quat((0, math.degrees(a * 2), 0))}
        if "halo" in has:
            pose["halo"] = {"r": quat((0, math.degrees(a), 0)), "p": (0, 0.06 * math.sin(a * 2), 0)}
        if "crownp" in has:
            pose["crownp"] = {"r": quat((0, math.degrees(a) * 0.5, 0))}
        for i in range(4):
            if f"aflame{i}" in has:
                fl = 1 + 0.15 * math.sin(a * 8 + i)
                pose[f"aflame{i}"] = {"s": (1 / fl ** 0.5, fl, 1 / fl ** 0.5)}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "neon": 0.8 + 0.2 * math.sin(t * TAU * 4),
                        "fire": 0.85 + 0.15 * math.sin(t * TAU * 8), "twinkle": 0.5 + 0.5 * math.sin(t * TAU * 4) ** 2, "nebula": 0.9}
    m.ground(body)
    add_base(m, TIER[L], sp["energy"], *({0: ("#5fae3a", "#4f9a35"), 1: ("#5fae3a", "#4f9a35")}.get(L, ("#5fae3a", "#4f9a35"))))
    rcol = RARITIES[rar][2]
    bg = sp.get("bg") or (_mix(rcol, "#000000", 0.78) if L >= 2 else "#7fbfe8")
    parts = []
    if L >= 1:
        parts.append(P_("float", 20 + 25 * L, "#ffffff" if L < 2 else sp["energy"], 0.12 + 0.02 * L, (2, 6), (0.3, 6), 0.5, "sparkle", 1.2 + 0.3 * L))
    if L >= 3:
        parts.append(P_("rise", 40 + 30 * L, sp["energy"], 0.18, (0.4, 3), (0.3, 6), 0.5, "square", 1.8 + 0.2 * L))
    if L >= 5:
        parts.append(P_("orbit", 100, _mix(sp["energy"], "#ffffff", 0.4), 0.2, (2.5, 5), (0.5, 6), 0.3, "sparkle", 2.4))
    m.stage = stage_for(TIER[L], sp["energy"], bg, parts, extra={"shakePart": body, "dist": 2.3 if L < 3 else 1.6,
                                                                   "bloom": {"strength": [0.0, 0.05, 0.15, 0.3, 0.4, 0.5, 0.6][L], "threshold": 1.3, "radius": 1}})
    if studs:
        m.stage.update(studs=True, studSize=round(v * 1.05, 3), studBump=0.7)
    m.meta = {"title": name, "rarity": rar, "rarityName": RARITIES[rar][0] if not sp.get("rebirth") else f"Renacimiento {sp['rebirth']}",
              "level": L, "egg": egg_id, "eggName": sp["name"], "arch": arch, "group": "mascotas"}
    return m


BUILDERS = {f"pet_{egg[4:]}_{i + 1}": (lambda egg=egg, i=i: build_pet(egg, i)) for egg in PETS for i in range(4)}
