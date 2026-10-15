"""Mascotas de los huevos: 4 por huevo, cada una diseñada a mano en pet_roster.py.

Cada entrada del catálogo es (nombre, plano de cuerpo, rasgos). El plano
(cuadrúpedo, lagarto, terópodo, ave, pez, insecto, crustáceo, cefalópodo,
serpiente, anfibio, primate/bípedo, criatura...) construye el cuerpo y los rasgos
pedidos; aquí se añaden la calidad según la rareza (tamaño de vóxel, ojos y marcas
brillantes, auras, orbes, halos, llamas), la animación, la base y el escenario.

Las mascotas de los huevos secretos y hacker son gigantes y con el máximo detalle.
"""

import math

from mathutils import Vector

import pk_quad
import pk_more
import sculpt
from animals import P_, add_base, stage_for
from eggs_themes import flame
from pet_roster import EGG_TINT, ROSTER
from pk_common import TAU, Ctx, mix
from tiers import RARITIES, SPECS, _mix
from voxel import Model, crystal, quat, ring

FEATURED_SPECS = {
    "egg_celestial": dict(shell=["#3b74ff", "#4985ff", "#2f63f5"], accent="#f6c64a", energy="#33ffd0", metal="#f6c64a", pattern="spots", wings="feather", rarity="legendario", name="Huevo Celestial"),
    "egg_ice": dict(shell=["#223e88", "#2a4ea3", "#1b3170"], accent="#5ff4ff", energy="#5ff4ff", metal="#bfe8ff", pattern="scales", wings="crystal", rarity="mitico", name="Huevo de Hielo"),
    "egg_inferno": dict(shell=["#25110f", "#2f1612", "#1b0e10"], accent="#ff6a14", energy="#ff7a1a", metal="#3a3c42", pattern="crack", wings="bat", rarity="mitico", name="Huevo Infernal"),
    "egg_swamp": dict(shell=["#4b6b30", "#5a7a35", "#3d5a2a"], accent="#8bbd40", energy="#b6ff5a", metal="#6a4424", pattern="spots", wings="leaf", rarity="epico", name="Huevo del Pantano"),
    "egg_galaxy": dict(shell=["#1d0f52", "#24125f", "#140a3a"], accent="#d14ee8", energy="#d14ee8", metal="#ffe08a", pattern="void", wings="crystal", rarity="legendario", name="Huevo Galaxia"),
    "egg_storm": dict(shell=["#46546f", "#52617d", "#3a4660"], accent="#ffe14a", energy="#ffe14a", metal="#c0c8d8", pattern="crack", wings="feather", rarity="mitico", name="Huevo Tormenta"),
    "egg_sakura": dict(shell=["#fbeef2", "#f7e3ea", "#f3d6e0"], accent="#f59ab8", energy="#ff8fb8", metal="#e8b84a", pattern="spots", wings="feather", rarity="legendario", name="Huevo Sakura"),
}

GLOW_OF = {"crack": "cracks", "runes": "runes", "void": "stars", "prism": "stars", "code": "code", "scanlines": "code", "circuit_red": "circuit",
           "hexgrid": "circuit", "glitch": "circuit", "flamefeather": "veins", "sunrays": "veins", "swirl": "veins", "facets": "cracks",
           "craters": "spots", "suckers": "spots", "rainbow": "stripes", "rainbow_scales": "stripes", "plates": "circuit", "scales": "spots",
           "tiger": "stripes", "spots": "spots", "stripes": "stripes", "hex": "cracks"}

LEVEL_V = [0.15, 0.135, 0.12, 0.11, 0.1, 0.092, 0.085]
TIER = [1, 2, 4, 6, 9, 12, 16]
BUILD = {"quad": pk_quad.quad, "lizard": pk_quad.lizard, "theropod": pk_quad.theropod, **pk_more.BUILD}


def egg_spec(egg_id):
    if egg_id in FEATURED_SPECS:
        return FEATURED_SPECS[egg_id]
    for sp in SPECS:
        if "egg_" + sp["id"] == egg_id:
            return sp
    raise KeyError(egg_id)


def level_of(sp):
    L = RARITIES[sp["rarity"]][1]
    if sp.get("rebirth"):
        L = min(6, 2 + sp["rebirth"] // 4)
    return L


# ----------------------------------------------------------------------------- calidad por rareza
def flair(m, ctx, info, P):
    """Auras, orbes, halos y llamas: alrededor de la mascota, sin tapar su silueta."""
    L, S, en, metal = ctx.L, ctx.S, ctx.en, ctx.metal
    lo, hi = m.bounds()
    R = max(hi.x - lo.x, hi.z - lo.z) * 0.55 + 0.3 * S
    top = hi.y
    if L >= 3:
        m.part("aura", "root", (0, 0.05, 0))
        ring(m, "aura", R, 40, (0.07 * S ** 0.5, 0.04), en, emit=1.3 + 0.2 * L, tag="neon")
        if L >= 5:
            ring(m, "aura", R * 1.18, 48, (0.05 * S ** 0.5, 0.04), en, emit=1.4, tag="neon")
            for k in range(8):
                a = k / 8 * TAU
                m.box("aura", (math.cos(a) * R * 1.09, 0, math.sin(a) * R * 1.09), (0.18 * S ** 0.5, 0.04, 0.07 * S ** 0.5), en,
                      r=(0, -math.degrees(a), 0), emit=1.8, tag="neon")
    if L >= 4 and not P.get("no_orbs"):
        n = 3 if L < 6 else 5
        for i in range(n):
            a = i / n * TAU
            o = f"orb{i}"
            m.part(o, "root", (math.cos(a) * R * 0.95, top * 0.75, math.sin(a) * R * 0.95))
            crystal(m, o, (0, 0, 0), 0.2 * S ** 0.7, 0.42 * S ** 0.7, en, emit=1.6, tag="glow")
    if P.get("halo"):
        hd = info.get("head", info["body"])
        hpos = m.world_point(hd, Vector((0, 0, 0)))
        m.part("halo", "root", (hpos.x, top + 0.35 * S, hpos.z), (8, 0, 0))
        r_ = 0.32 * S
        ring(m, "halo", r_, 22, (0.08 * S ** 0.6, 0.07 * S ** 0.6), metal, metal=1)
        ring(m, "halo", r_, 22, (0.035 * S ** 0.6, 0.09 * S ** 0.6), en, emit=1.5, tag="glow")
    if L >= 6:
        for i in range(4):
            fl = f"aflame{i}"
            a = i / 4 * TAU + 0.4
            m.part(fl, "root", (math.cos(a) * R * 0.85, 0.1, math.sin(a) * R * 0.85))
            flame(m, fl, (0, 0, 0), 0.65 * S ** 0.7, 0.24 * S ** 0.7, seed=i, tag="fire")
            for b in m.parts[fl].boxes:
                b["col"] = _mix(en, "#ffffff", min(0.8, b["c"].y / (0.9 * S ** 0.7)))


def focus_bounds(m):
    """Caja de la criatura sin la peana ni los efectos (para encuadrar la cámara)."""
    skip = ("root", "aura", "halo")
    lo = Vector((1e9, 1e9, 1e9))
    hi = -lo
    for name, part in m.parts.items():
        if name in skip or name.startswith(("orb", "aflame")):
            continue
        for b in part.boxes:
            for v in m.box_corners(name, b):
                lo = Vector(map(min, lo, v))
                hi = Vector(map(max, hi, v))
    lo.y = 0.0
    return [[round(x, 3) for x in lo], [round(x, 3) for x in hi]]


def pet_base(m, L, giant, sp, S):
    """Peana: hierba para común/poco común/raro, piedra oscura con anillo de energía para el resto."""
    lo, hi = m.bounds()
    span = max(hi.x - lo.x, hi.z - lo.z)
    R = span * 0.5 + 0.35 * S ** 0.5
    bh = 0.28 * S ** 0.5
    for n in m.parts.values():
        if n.parent == "root":
            n.pivot.y += bh
    en = sp["energy"]
    if L <= 2:
        g1, g2, dirt = ("#5fae3a", "#4f9a35", "#6a4a2a")
        m.box("root", (0, bh * 0.4, 0), (R * 1.9, bh * 0.8, R * 1.9), dirt)
        m.box("root", (0, bh * 0.4 - 0.005, 0), (R * 1.9, bh * 0.8 - 0.01, R * 1.9), dirt, r=(0, 45, 0))
        m.box("root", (0, bh * 0.9, 0), (R * 1.88, bh * 0.2, R * 1.88), g1)
        m.box("root", (0, bh * 0.9 - 0.004, 0), (R * 1.88, bh * 0.2 - 0.008, R * 1.88), g2, r=(0, 45, 0))
        for k in range(14):
            a = k * 2.39996
            r_ = R * (0.35 + 0.5 * ((k * 0.618) % 1))
            m.box("root", (math.cos(a) * r_, bh + 0.08, math.sin(a) * r_), (0.06, 0.18 + 0.08 * (k % 3), 0.06), "#3f8a2a" if k % 2 else "#6ac04a")
        if L == 2:
            for k in range(5):
                a = k / 5 * TAU + 0.3
                m.box("root", (math.cos(a) * R * 0.85, bh + 0.06, math.sin(a) * R * 0.85), (0.14, 0.14, 0.14), "#ffffff" if k % 2 else en, r=(0, 30 * k, 0))
        return bh
    base = "#262b38" if L < 5 else "#161a28"
    base2 = "#323848" if L < 5 else "#20263a"
    m.box("root", (0, bh * 0.35, 0), (R * 2, bh * 0.7, R * 2), base)
    m.box("root", (0, bh * 0.35 - 0.005, 0), (R * 2, bh * 0.7 - 0.01, R * 2), base, r=(0, 45, 0))
    m.box("root", (0, bh * 0.85, 0), (R * 1.6, bh * 0.3, R * 1.6), base2, r=(0, 22.5, 0))
    m.box("root", (0, bh * 0.85 - 0.005, 0), (R * 1.6, bh * 0.3 - 0.01, R * 1.6), base2, r=(0, 67.5, 0))
    ring(m, "root", R * 0.86, 48, (0.1 * S ** 0.5, 0.06), en, center=(0, bh + 0.01, 0), emit=1.5 + 0.1 * L, tag="neon")
    for k in range(8):
        a = k / 8 * TAU + TAU / 16
        m.box("root", (math.cos(a) * R * 1.02, bh * 0.75, math.sin(a) * R * 1.02), (0.3 * S ** 0.5, bh * 0.6, 0.3 * S ** 0.5), "#f2c14e" if L >= 5 else "#6c7178",
              r=(0, -math.degrees(a), 0), metal=1)
    if giant:
        for k in range(12):
            a = k / 12 * TAU
            m.box("root", (math.cos(a) * R * 1.12, bh * 0.1, math.sin(a) * R * 1.12), (0.25 * S ** 0.5, 0.05, 0.1 * S ** 0.5), en, r=(0, -math.degrees(a) + 45, 0),
                  emit=2.2, tag="neon")
    return bh


# ----------------------------------------------------------------------------- animación
def anim_common(pose, m, info, t, L):
    a = t * TAU
    has = m.parts
    for pre, n in info.get("tails", []):
        for i in range(n):
            nm = f"{pre}{i}"
            if nm in has:
                r = quat((0, (6 + 1.5 * L) * math.sin(a * 2 - i * 0.6), 0))
                pose[nm] = {"r": r} if nm not in pose else pose[nm]
    for tpl, n in info.get("trunks", []):
        for j in range(n):
            nm = tpl.format(j)
            if nm in has:
                pose[nm] = {"r": quat((7 * math.sin(a * 2 - j * 0.7), 6 * math.sin(a - j * 0.5), 0))}
    for side, sx in (("L", 1), ("R", -1)):
        for pre in ("qwing", "wing", "fwing"):
            nm = f"{pre}_{side}"
            if nm in has and nm not in pose:
                pose[nm] = {"r": quat((0, sx * 6 * math.sin(a * 2), sx * 16 * math.sin(a * 2)))}
    if "aura" in has:
        pose["aura"] = {"r": quat((0, math.degrees(a), 0))}
    for i in range(5):
        o = f"orb{i}"
        if o in has:
            piv = has[o].pivot
            n_ = 3 if L < 6 else 5
            ang = i / n_ * TAU + a
            r_ = math.hypot(piv.x, piv.z)
            pose[o] = {"p": (math.cos(ang) * r_ - piv.x, 0.2 * math.sin(a * 2 + i), math.sin(ang) * r_ - piv.z), "r": quat((0, math.degrees(a * 2), 0))}
    if "halo" in has:
        pose["halo"] = {"r": quat((0, math.degrees(a), 0)), "p": (0, 0.06 * math.sin(a * 2), 0)}
    for i in range(4):
        fl = f"aflame{i}"
        if fl in has:
            k = 1 + 0.15 * math.sin(a * 8 + i)
            pose[fl] = {"s": (1 / k ** 0.5, k, 1 / k ** 0.5)}


def anim_quad(m, info, P, L):
    gait = P.get("gait", "walk")
    has = m.parts
    S = info["S"]

    def f(t):
        a = t * TAU
        pose = {}
        if gait in ("walk", "trot", "stomp", "prowl", "gallop"):
            amp = {"walk": 16, "trot": 22, "stomp": 11, "prowl": 13, "gallop": 26}[gait]
            spd = 2 if gait in ("trot", "gallop") else 1
            ph = {"FL": 0, "BR": 0, "FR": math.pi, "BL": math.pi} if gait != "gallop" else {"FL": 0, "FR": 0.6, "BL": math.pi, "BR": math.pi + 0.6}
            for k, p in ph.items():
                s = math.sin(a * spd + p)
                pose[f"leg_{k}"] = {"r": quat((amp * s, 0, 0))}
                bend = (14 + amp) * max(0.0, math.cos(a * spd + p))
                pose[f"low_{k}"] = {"r": quat((bend if k[0] == "F" else -bend * 0.6, 0, 0))}
            sway = 3 if gait == "stomp" else 0
            pose["body"] = {"p": (0, 0.03 * S * abs(math.sin(a * spd)), 0), "r": quat((2 * math.sin(a * spd * 2) if gait == "gallop" else 0, 0, sway * math.sin(a)))}
        elif gait == "hop":
            j = max(0.0, math.sin(a * 2)) ** 1.3
            pose["body"] = {"p": (0, 0.35 * S * j, 0), "r": quat((-8 * j, 0, 0))}
            for k in ("FL", "FR"):
                pose[f"leg_{k}"] = {"r": quat((-25 * j, 0, 0))}
            for k in ("BL", "BR"):
                pose[f"leg_{k}"] = {"r": quat((35 * j, 0, 0))}
                pose[f"low_{k}"] = {"r": quat((-20 * j, 0, 0))}
        else:  # idle: respiración
            b = math.sin(a * 2)
            pose["body"] = {"s": (1 + 0.015 * b, 1 + 0.02 * b, 1)}
        for hn in info.get("heads", ["head"]):
            off = (hash(hn) % 7) * 0.4
            pose[hn] = {"r": quat((4 * math.sin(a * 2 + off), (8 + L) * math.sin(a + off), 0))}
        if L >= 2:
            tw = max(0.0, math.sin(a * 3)) ** 8
            for side in ("L", "R"):
                if f"ear_{side}" in has:
                    pose[f"ear_{side}"] = {"r": quat((-14 * tw, 0, 0))}
        for jn in ("jaw", "jaw1", "jaw2"):
            if jn in has:
                pose[jn] = {"r": quat(((10 + 2 * L) * max(0.0, math.sin(a + 0.5)) ** 6, 0, 0))}
        anim_common(pose, m, info, t, L)
        return pose
    return f


def anim_lizard(m, info, P, L):
    def f(t):
        a = t * TAU
        pose = {}
        ph = {"FL": 0, "BR": 0, "FR": math.pi, "BL": math.pi}
        for k, p in ph.items():
            s = math.sin(a * 2 + p)
            sx = 1 if k[1] == "L" else -1
            pose[f"leg_{k}"] = {"r": quat((0, sx * 25 * s, 10 * max(0.0, math.cos(a * 2 + p)) * sx))}
        pose["body"] = {"r": quat((0, 6 * math.sin(a * 2), 0))}
        pose["head"] = {"r": quat((3 * math.sin(a * 4), -6 * math.sin(a * 2), 0))}
        if "jaw" in m.parts:
            pose["jaw"] = {"r": quat((14 * max(0.0, math.sin(a)) ** 8, 0, 0))}
        anim_common(pose, m, info, t, L)
        for i in range(info.get("tail_n", 0)):
            if f"tail{i}" in m.parts:
                pose[f"tail{i}"] = {"r": quat((0, -(8 + L) * math.sin(a * 2 - i * 0.5), 0))}
        return pose
    return f


def anim_theropod(m, info, P, L):
    def f(t):
        a = t * TAU
        pose = {}
        for side, ph in (("L", 0), ("R", math.pi)):
            s = math.sin(a + ph)
            pose[f"leg_{side}"] = {"r": quat((22 * s, 0, 0))}
            pose[f"low_{side}"] = {"r": quat((-25 * max(0.0, math.cos(a + ph)), 0, 0))}
            pose[f"arm_{side}"] = {"r": quat((12 * math.sin(a * 2 + ph), 0, 0))}
        pose["body"] = {"p": (0, 0.05 * info["S"] * abs(math.sin(a)), 0), "r": quat((0, 4 * math.sin(a), 0))}
        pose["head"] = {"r": quat((-6 * max(0.0, math.sin(a * 0.5 + 1)) ** 4, 8 * math.sin(a), 0))}
        pose["jaw"] = {"r": quat((22 * max(0.0, math.sin(a + 1)) ** 6, 0, 0))}
        anim_common(pose, m, info, t, L)
        return pose
    return f


ANIM = {"quad": anim_quad, "lizard": anim_lizard, "theropod": anim_theropod, **pk_more.ANIM}


# ----------------------------------------------------------------------------- construcción
def build_pet(egg_id, idx):
    sculpt.VOXEL_SCALE = 1.0
    sculpt.MODE = "voxel"
    sp = egg_spec(egg_id)
    name, plan, P = ROSTER[egg_id][idx]
    rar = sp["rarity"]
    L = level_of(sp)
    giant = rar in ("secreto", "hacker")
    S = (0.85 + 0.06 * L) * (2.1 if giant else 1.0)
    v = LEVEL_V[L] * S * (0.7 if giant else 1.0)
    pat = sp.get("pattern", "")
    ctx = Ctx(S, v, L, sp, tint=P.get("tint", EGG_TINT.get(egg_id, 0.0)), glow=P.get("glow", GLOW_OF.get(pat, "veins")), giant=giant)
    m = Model(f"pet_{egg_id[4:]}_{idx + 1}", fps=24, frames=48)
    m.meta_name = name
    m.part("root")
    info = BUILD[plan](m, P, ctx)
    if P.get("acc"):
        pk_more.accessories(m, info, P["acc"], ctx)
    m.ground(info["body"])
    if info.get("hover"):
        m.parts[info["body"]].pivot.y += info["hover"] * info["S"]
    flair(m, ctx, info, P)
    m.animate = ANIM[plan](m, info, P, L)
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "neon": 0.8 + 0.2 * math.sin(t * TAU * 4),
                        "fire": 0.85 + 0.15 * math.sin(t * TAU * 8), "twinkle": 0.5 + 0.5 * math.sin(t * TAU * 4) ** 2, "nebula": 0.9}
    pet_base(m, L, giant, sp, S)
    rcol = RARITIES[rar][2]
    bg = sp.get("bg") or (_mix(rcol, "#000000", 0.78) if L >= 2 else "#7fbfe8")
    parts = []
    if L >= 1:
        parts.append(P_("float", 20 + 25 * L, "#ffffff" if L < 2 else sp["energy"], 0.12 + 0.02 * L, (2, 6 * S ** 0.5), (0.3, 6 * S ** 0.5), 0.5, "sparkle", 1.2 + 0.3 * L))
    if L >= 3:
        parts.append(P_("rise", 40 + 30 * L, sp["energy"], 0.18, (0.4, 3 * S ** 0.5), (0.3, 6 * S ** 0.5), 0.5, "square", 1.8 + 0.2 * L))
    if L >= 5:
        parts.append(P_("orbit", 100 + (80 if giant else 0), _mix(sp["energy"], "#ffffff", 0.4), 0.2, (2.5 * S ** 0.5, 5 * S ** 0.5), (0.5, 6 * S ** 0.5), 0.3, "sparkle", 2.4))
    m.stage = stage_for(TIER[L], sp["energy"], bg, parts, extra={"shakePart": info["body"], "dist": 2.3 if L < 3 else 1.6,
                                                                   "bloom": {"strength": [0.0, 0.05, 0.15, 0.3, 0.4, 0.5, 0.6][L], "threshold": 1.3, "radius": 1}})
    m.stage["focus"] = focus_bounds(m)
    m.stage["dist"] = 1.75 if not giant else 1.6
    m.meta = {"title": name, "rarity": rar, "rarityName": RARITIES[rar][0] if not sp.get("rebirth") else f"Renacimiento {sp['rebirth']}",
              "level": L, "egg": egg_id, "eggName": sp["name"], "arch": plan, "group": "mascotas", "giant": giant}
    return m


BUILDERS = {f"pet_{egg[4:]}_{i + 1}": (lambda egg=egg, i=i: build_pet(egg, i)) for egg in ROSTER for i in range(len(ROSTER[egg]))}
