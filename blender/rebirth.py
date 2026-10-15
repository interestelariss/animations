"""Los 20 animales de renacimiento, esculpidos con vóxeles (versión detallada).

Cada animal está hecho de miles de cubitos: cuerpo con pecho, costillas,
cintura, cadera y omóplatos; cabeza con cráneo, cejas, mofletes, hocico y
mandíbula; patas de dos segmentos con zarpas; colas articuladas. Todos llevan
el máximo detalle (ojos con brillo, colmillos, garras, armaduras, runas, alas,
llamas, cristales…) y VFX que crecen con el renacimiento.
"""

import math

from mathutils import Vector

from animals import ANIMALS, P_, add_base, cosmic_col, stage_for
from eggs import _hash, _wing
from eggs_themes import flame, fbm, horn, membrane_wing, vnoise
import sculpt
from mathutils import Quaternion
from sculpt import cap, ell, surface_point, voxelize

sculpt.VOXEL_SCALE = 1.45  # vóxeles algo más grandes: menos cubos, misma forma
from voxel import Model, crystal, polyline, quat, ring, segment, star

TAU = math.tau


# ----------------------------------------------------------------------------- pelaje
def fur(cols, belly=None, dorsal=None, pattern=None, pcol=None, pemit=0.0, freq=1.6, H=1.0, glow_tag="glow", extra=None):
    """Función de color de pelaje: 3 tonos, lomo más oscuro, vientre claro y patrón."""
    def fn(p, n):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if extra:
            r = extra(p, n, h)
            if r is not None:
                return r
        if pattern == "stripes":
            v = math.sin(p.z * freq * 3 + vnoise(p.x * 2, p.y * 2, p.z * 2) * 3 + abs(p.x) * 1.5)
            if v > 0.72 and n.y > -0.5:
                return (pcol, pemit, glow_tag) if pemit else pcol
        elif pattern == "spots":
            if vnoise(p.x * freq * 2 + 5, p.y * freq * 2, p.z * freq * 2) > 0.68 and n.y > -0.4:
                return pcol
        elif pattern == "runes":
            fx = (p.z * 2.2) % 1
            fy = (p.y * 2.2 + 0.3) % 1
            if abs(n.x) > 0.5 and ((abs(fx - 0.5) < 0.07 and 0.15 < fy < 0.85) or (abs(fy - 0.5) < 0.07 and 0.3 < fx < 0.7)):
                return (pcol, pemit or 2.5, glow_tag)
        if belly and n.y < -0.35:
            return belly
        if dorsal and n.y > 0.6:
            return dorsal if h > 0.3 else cols[0]
        return cols[int(h * 97) % len(cols)]
    return fn


def rock(cols, crystal_col=None):
    def fn(p, n):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if crystal_col and abs(fbm(p, 0.9, 3.0) - 0.5) < 0.012:
            return (crystal_col, 2.0, "glow")
        if n.y > 0.7 and vnoise(p.x * 1.5, p.y, p.z * 1.5) > 0.55:
            return "#4f7a3a" if h > 0.4 else "#5f8a44"  # musgo
        return cols[int(h * 97) % len(cols)]
    return fn


def put_eyes(m, part, skull, hs, iris, glow=0.0, x=0.24, y=0.12, size=1.0, brow=None, slit=False):
    for sx in (1, -1):
        p = surface_point(skull, sx * hs * x, hs * y) + Vector((0, 0, 0.01))
        s = hs * size
        m.box(part, p, (s * 0.2, s * 0.15, 0.05), "#fbfbf6", r=(0, sx * 18, 0))
        m.box(part, p + Vector((0, -s * 0.005, 0.02)), (s * 0.13, s * 0.13, 0.04), iris, r=(0, sx * 18, 0), emit=glow, tag="eyes" if glow else None)
        m.box(part, p + Vector((0, -s * 0.01, 0.04)), (s * (0.03 if slit else 0.06), s * 0.11, 0.03), "#050505", r=(0, sx * 18, 0))
        m.box(part, p + Vector((sx * s * 0.03, s * 0.04, 0.05)), (s * 0.035, s * 0.035, 0.02), "#ffffff", r=(0, sx * 18, 0))
        if brow:
            m.box(part, p + Vector((sx * -s * 0.01, s * 0.11, 0.0)), (s * 0.26, s * 0.06, s * 0.12), brow, r=(0, sx * 18, sx * -14))


# ----------------------------------------------------------------------------- bestia esculpida
def beast(m, B):
    S = B.get("S", 1.0)
    L, W, H = B["L"] * S, B["W"] * S, B["H"] * S
    lf, lb = B["legF"] * S, B.get("legB", B["legF"]) * S
    hs, sn = B["hs"] * S, B["snout"] * S
    v = B["v"]
    body_fn = B["fur"]
    head_fn = B.get("head_fur", body_fn)
    leg_fn = B.get("leg_fur", body_fn)
    nz = B.get("fur_noise", 0.06)
    m.part("body", "root", (0, lf * 0.95 + H * 0.5, 0))
    prims = [
        ell((0, 0.08 * H, 0.3 * L), (0.52 * W, 0.55 * H, 0.3 * L), nz, 3),
        ell((0, 0.02 * H, 0.05 * L), (0.48 * W, 0.5 * H, 0.32 * L), nz, 3),
        ell((0, 0.06 * H, -0.18 * L), (0.4 * W * B.get("waist", 1), 0.42 * H * B.get("waist", 1), 0.25 * L), nz, 3),
        ell((0, 0.1 * H, -0.33 * L), (0.46 * W, 0.5 * H, 0.2 * L), nz, 3),
        ell((0.3 * W, 0.32 * H, 0.3 * L), (0.22 * W, 0.28 * H, 0.16 * L), nz, 3),
        ell((-0.3 * W, 0.32 * H, 0.3 * L), (0.22 * W, 0.28 * H, 0.16 * L), nz, 3),
    ]
    nu, nf = B.get("neckUp", 0.35) * S, B.get("neckFwd", 0.3) * S
    neck_end = Vector((0, 0.25 * H + nu, 0.42 * L + nf))
    prims.append(cap((0, 0.2 * H, 0.36 * L), neck_end, 0.36 * W * B.get("neckW", 1), 0.3 * W * B.get("neckW", 1), nz, 3))
    prims += B.get("body_extra", [])
    voxelize(m, "body", prims, v, body_fn)
    # cabeza
    m.part("head", "body", tuple(neck_end + Vector((0, 0.08 * hs, 0.05 * hs))))
    skull = ell((0, 0.05 * hs, 0.1 * hs), (0.5 * hs * B.get("skullW", 1), 0.46 * hs, 0.55 * hs))
    hp = [skull, ell((0, 0.27 * hs, 0.38 * hs), (0.44 * hs, 0.14 * hs, 0.22 * hs)),
          ell((0.33 * hs, -0.12 * hs, 0.25 * hs), (0.24 * hs, 0.26 * hs, 0.3 * hs)),
          ell((-0.33 * hs, -0.12 * hs, 0.25 * hs), (0.24 * hs, 0.26 * hs, 0.3 * hs))]
    if sn > 0:
        hp.append(cap((0, -0.1 * hs, 0.45 * hs), (0, -0.14 * hs, 0.45 * hs + sn), 0.3 * hs * B.get("muzzleW", 1), 0.24 * hs * B.get("muzzleW", 1)))
    hp += B.get("head_extra", [])
    nose_col = B.get("nose", "#2a1a1a")

    def head_col(p, n):
        if p.z > 0.4 * hs + sn and abs(p.x) < 0.13 * hs and -0.12 * hs < p.y < 0.06 * hs and n.z > 0.3:
            return nose_col
        return head_fn(p, n)

    voxelize(m, "head", hp, v * 0.85, head_col)
    put_eyes(m, "head", skull, hs, B.get("eye", "#3a2a2a"), glow=B.get("eye_glow", 0.0), x=B.get("eye_x", 0.26), y=B.get("eye_y", 0.14),
             size=B.get("eye_size", 1.0), brow=B.get("brow"), slit=B.get("slit", False))
    # mandíbula
    m.part("jaw", "head", (0, -0.3 * hs, 0.32 * hs))
    jp = [cap((0, 0, 0), (0, -0.02 * hs, max(sn, 0.2 * hs) + 0.12 * hs), 0.2 * hs * B.get("muzzleW", 1), 0.16 * hs * B.get("muzzleW", 1))]
    voxelize(m, "jaw", jp, v * 0.8, lambda p, n: "#5a1a22" if n.y > 0.6 else head_fn(p, n))
    if B.get("teeth"):
        for sx in (1, -1):
            tz = 0.45 * hs + sn * 0.85
            m.box("head", (sx * 0.14 * hs, -0.33 * hs, tz), (0.05 * hs, 0.16 * hs, 0.05 * hs), "#f6f0e2")
            m.box("jaw", (sx * 0.12 * hs, 0.08 * hs, max(sn, 0.2 * hs) * 0.9), (0.04 * hs, 0.1 * hs, 0.04 * hs), "#f6f0e2")
    # orejas
    ear = B.get("ear", "pointy")
    for side, sx in (("L", 1), ("R", -1)):
        e = f"ear_{side}"
        m.part(e, "head", (sx * 0.3 * hs, 0.38 * hs, 0.0), (0, 0, sx * B.get("ear_tilt", -10)))
        if ear == "pointy":
            ep = [cap((0, 0, 0), (sx * 0.06 * hs, 0.45 * hs, -0.05 * hs), 0.17 * hs, 0.03 * hs)]
        elif ear == "long":
            ep = [ell((0, 0.55 * hs, 0), (0.13 * hs, 0.6 * hs, 0.07 * hs))]
        elif ear == "round":
            ep = [ell((0, 0.1 * hs, 0), (0.15 * hs, 0.14 * hs, 0.07 * hs))]
        elif ear == "floppy":
            ep = [ell((sx * 0.12 * hs, -0.2 * hs, 0.05 * hs), (0.1 * hs, 0.32 * hs, 0.17 * hs))]
        else:
            ep = []
        if ep:
            inner = B.get("ear_inner", "#ffb8c8")
            voxelize(m, e, ep, v * 0.75, lambda p, n, inner=inner: inner if n.z > 0.6 and ear in ("pointy", "long") else head_fn(p, n))
    # patas de dos segmentos
    claws = B.get("claws")
    for name, sx, sz, ll in (("FL", 1, 1, lf), ("FR", -1, 1, lf), ("BL", 1, -1, lb), ("BR", -1, -1, lb)):
        up, lo_ = f"leg_{name}", f"low_{name}"
        front = sz > 0
        m.part(up, "body", (sx * 0.33 * W, -0.12 * H, (0.3 if front else -0.33) * L))
        if front:
            upr = [cap((0, 0, 0), (0, -0.5 * ll, 0.05 * ll), 0.24 * W, 0.17 * W), ell((0, -0.05 * ll, 0.02 * ll), (0.25 * W, 0.28 * ll, 0.24 * W))]
        else:
            upr = [ell((0, -0.08 * ll, 0.02), (0.28 * W, 0.34 * ll, 0.32 * W)), cap((0, 0, 0), (0, -0.5 * ll, -0.1 * ll), 0.22 * W, 0.16 * W)]
        voxelize(m, up, upr, v, leg_fn)
        knee = Vector((0, -0.5 * ll, (0.05 if front else -0.1) * ll))
        m.part(lo_, up, tuple(knee))
        lwr = [cap((0, 0, 0), (0, -0.45 * ll, (0 if front else 0.08) * ll), 0.16 * W, 0.13 * W),
               ell((0, -0.47 * ll, 0.08 * W), (0.19 * W, 0.08 * ll + 0.03, 0.26 * W))]
        paw_col = B.get("paw")
        voxelize(m, lo_, lwr, v * 0.85, (lambda p, n, ll=ll: paw_col if p.y < -0.4 * ll else leg_fn(p, n)) if paw_col else leg_fn)
        if claws:
            for k in (-1, 0, 1):
                m.box(lo_, (k * 0.09 * W, -0.5 * ll, 0.3 * W), (0.05 * W, 0.06 * W, 0.12 * W), claws, r=(25, 0, 0))
        if B.get("anklet"):
            m.box(lo_, (0, -0.32 * ll, 0), (0.36 * W, 0.08 * ll, 0.36 * W), B["anklet"], metal=1)
    # cola
    tail = B.get("tail", "long")
    tn = B.get("tail_n", 6)
    parent, piv = "body", (0, 0.25 * H, -0.5 * L)
    seg = B.get("tail_seg", 0.3) * S
    tw = B.get("tail_w", 0.14) * S
    tfn = B.get("tail_fur", body_fn)
    if tail != "none":
        for i in range(tn):
            k = i / max(tn - 1, 1)
            n = f"tail{i}"
            m.part(n, parent, piv, (B.get("tail_lift", -25) if i == 0 else B.get("tail_curve", 6), 0, 0))
            if tail == "bushy":
                r_ = tw * (1.0 + 1.3 * math.sin(k * math.pi * 0.9 + 0.15))
                tp = [ell((0, 0, -seg / 2), (r_, r_, seg * 0.7), 0.15, 4)]
            elif tail == "puff":
                tp = [ell((0, 0, -0.05), (tw * 2.2, tw * 2.2, tw * 2.0), 0.15, 5)]
            else:
                r_ = tw * (1 - 0.45 * k)
                tp = [cap((0, 0, 0), (0, 0, -seg), r_, r_ * 0.9)]
            if tail == "tuft" and i == tn - 1:
                tp.append(ell((0, 0, -seg), (tw * 1.8, tw * 1.8, tw * 2.4), 0.25, 5))
            voxelize(m, n, tp, v * 0.8, tfn if not (tail == "tuft" and i == tn - 1) else (lambda p, n: B.get("tuft_col", "#5a2a10")))
            parent, piv = n, (0, 0, -seg)
            if tail == "puff":
                break
    return dict(L=L, W=W, H=H, lf=lf, lb=lb, hs=hs, sn=sn, skull=skull, tail_n=0 if tail == "none" else (1 if tail == "puff" else tn), neck_end=neck_end)


# ----------------------------------------------------------------------------- animación
def walk(pose, t, amp=24, speed=2, gallop=False, bob=0.05, knee=30):
    a = t * TAU * speed
    ph = {"FL": 0, "BR": 0, "FR": math.pi, "BL": math.pi} if not gallop else {"FL": 0, "FR": 0.5, "BL": math.pi, "BR": math.pi + 0.5}
    for k, p in ph.items():
        s = math.sin(a + p)
        pose[f"leg_{k}"] = {"r": quat((amp * s, 0, 0))}
        bend = knee * max(0.0, math.cos(a + p))
        pose[f"low_{k}"] = {"r": quat((bend if k[0] == "F" else -bend * 0.6, 0, 0))}
    pose["body"] = {"p": (0, bob * abs(math.sin(a)), 0), "r": quat((2.5 * math.sin(a * 2) if gallop else 0, 0, 0))}
    return pose


def tail_sway(pose, t, n, amp=10, speed=1, axis="y", start=1, prefix="tail"):
    a = t * TAU * speed
    for i in range(start, n):
        ang = amp * math.sin(a - i * 0.55)
        pose[f"{prefix}{i}"] = {"r": quat((0, ang, 0) if axis == "y" else (ang, 0, 0))}
    return pose


def finish(m, n, energy, bg, particles, extra=None, ground=("#5fae3a", "#4f9a35")):
    main = [k for k in ("body", "bird", "worm", "titan") if k in m.parts][0]
    m.ground(main)
    add_base(m, max(n, 5), energy, *ground)
    meta = ANIMALS[n - 1]
    m.meta = {"title": meta[2], "subtitle": meta[3], "rarity": "renacimiento", "rarityName": f"Renacimiento {n}", "level": n,
              "requirement": meta[4], "bonus": meta[5], "rebirth": n}
    ex = {"shakePart": main, "dist": 1.35}
    ex.update(extra or {})
    m.stage = stage_for(max(n, 6), energy, bg, particles, extra=ex)
    return m


def new(id_, frames=72):
    m = Model("animal_" + id_, fps=24, frames=frames)
    m.part("root")
    return m


# ======================================================================================
# 1-4
# ======================================================================================
def build_rabbit():
    m = new("rabbit", 48)
    f = fur(["#f6f0e8", "#efe7dc", "#fbf7f0"], belly="#ffffff")
    d = beast(m, dict(S=1.0, L=1.6, W=1.2, H=1.15, legF=0.42, legB=0.55, hs=1.15, snout=0.12, v=0.075, fur=f, ear="long", ear_tilt=-6,
                      tail="puff", tail_w=0.16, eye="#5a3a2a", eye_size=1.25, eye_y=0.1, nose="#ff8aa8", ear_inner="#ffb8c8", fur_noise=0.08,
                      paw="#ffffff", waist=1.05))
    hs = d["hs"]
    for sx in (1, -1):  # mofletes y bigotes
        m.box("head", (sx * 0.36 * hs, -0.12 * hs, 0.52 * hs), (0.14 * hs, 0.08 * hs, 0.04), "#ffc8d6")
        for j in (-1, 1):
            m.box("head", (sx * 0.5 * hs, -0.15 * hs + j * 0.03, 0.6 * hs), (0.35 * hs, 0.012, 0.012), "#ffffff", r=(0, 0, sx * j * 8))
    m.box("head", (0, -0.24 * hs, 0.66 * hs), (0.1 * hs, 0.08 * hs, 0.04), "#f6f0e2")  # dientecitos
    # bufanda de recién nacido y flor
    segment(m, "body", (-0.55, 0.45, 0.55), (0.55, 0.45, 0.55), (0.18, 0.2), "#7fc8ff")
    segment(m, "body", (0.4, 0.4, 0.62), (0.55, 0.05, 0.75), (0.16, 0.06), "#7fc8ff")

    def animate(t):
        a = t * TAU
        hop = max(0.0, math.sin(a))
        pose = {"body": {"p": (0, 0.9 * hop, 0.0), "r": quat((-12 * hop, 0, 0))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-40 * hop, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((20 * hop, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((55 * hop, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((-30 * hop, 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((-30 * hop + 5 * math.sin(a * 3), 0, sx * (8 * math.sin(a * 2) - 6)))}
        pose["head"] = {"r": quat((6 * math.sin(a * 2), 10 * math.sin(a), 0))}
        pose["tail0"] = {"s": (1 + 0.12 * math.sin(a * 4),) * 3}
        return pose

    m.animate = animate
    return finish(m, 1, "#9fe0a0", "#7fbfe8", [P_("float", 40, "#ffffff", 0.12, (2, 6), (0.3, 5), 0.5, "sparkle", 1.6)],
                  extra={"bloom": {"strength": 0.15, "threshold": 1.4, "radius": 1}})


def build_cat():
    m = new("cat", 48)
    f = fur(["#f2a24a", "#eb983e", "#f6ad58"], belly="#fff2e0", dorsal="#d9822e", pattern="stripes", pcol="#b85a14", freq=1.8)
    d = beast(m, dict(S=1.0, L=2.4, W=1.05, H=1.0, legF=1.0, hs=1.05, snout=0.14, v=0.07, fur=f, ear="pointy", tail="long", tail_n=9, tail_seg=0.28,
                      tail_w=0.12, tail_lift=-50, tail_curve=10, eye="#8fe05a", eye_glow=0.8, slit=True, nose="#ff9aa8", paw="#fff2e0",
                      claws="#f6f0e2", waist=0.9))
    hs = d["hs"]
    for sx in (1, -1):
        for j in (-1, 0, 1):
            m.box("head", (sx * 0.55 * hs, -0.14 * hs + j * 0.035, 0.62 * hs), (0.45 * hs, 0.012, 0.012), "#ffffff", r=(0, 0, sx * j * 9))
    ring(m, "body", 0.42, 16, (0.08, 0.1), "#d8322a", center=(0, 0.42, 0.95), rot=(70, 0, 0))  # collar
    m.box("body", (0, 0.12, 1.12), (0.12, 0.12, 0.12), "#f2c14e", r=(45, 0, 45), metal=1)

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=20, speed=2, bob=0.04, knee=25)
        tail_sway(pose, t, 9, amp=14)
        tw = max(0.0, math.sin(a * 3)) ** 8
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((-25 * tw, sx * 30 * tw, 0))}
        pose["head"] = {"r": quat((3 * math.sin(a * 4), 14 * math.sin(a), 0))}
        return pose

    m.animate = animate
    return finish(m, 2, "#ffd27a", "#8ac4ec", [P_("float", 50, "#ffe9b0", 0.14, (2, 6), (0.3, 5), 0.5, "sparkle", 1.8)],
                  extra={"bloom": {"strength": 0.15, "threshold": 1.4, "radius": 1}})


def build_dog():
    m = new("dog", 48)
    f = fur(["#c07a3a", "#b87234", "#c88444"], belly="#f6e2c6", dorsal="#8a5226")
    d = beast(m, dict(S=1.0, L=2.7, W=1.4, H=1.35, legF=1.05, hs=1.3, snout=0.55, v=0.08, fur=f, ear="floppy", tail="bushy", tail_n=4, tail_seg=0.26,
                      tail_w=0.12, tail_lift=-60, eye="#3a2414", eye_size=1.1, nose="#1a1210", paw="#f6e2c6", brow="#8a5226",
                      head_fur=fur(["#c07a3a", "#b87234"], belly="#f6e2c6", extra=lambda p, n, h: "#f6e2c6" if p.z > 0.55 and p.y < 0 else None)))
    hs = d["hs"]
    m.box("jaw", (0, 0.08 * hs, 0.62 * hs), (0.22 * hs, 0.04, 0.32 * hs), "#ff6a8a", r=(-25, 0, 0))  # lengua
    ring(m, "body", 0.6, 18, (0.14, 0.16), "#2a6ad8", center=(0, 0.5, 1.15), rot=(65, 0, 0))  # collar con placa
    for k in range(6):
        a = k / 6 * TAU
        m.box("body", (math.cos(a) * 0.6, 0.5 + math.sin(a) * 0.25, 1.15 + math.sin(a) * 0.15), (0.08, 0.08, 0.08), "#c0c8d8", metal=1)
    m.box("body", (0, 0.1, 1.42), (0.22, 0.22, 0.06), "#f2c14e", r=(0, 0, 45), metal=1)

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=24, speed=2, bob=0.06, knee=30)
        for i in range(4):
            pose[f"tail{i}"] = {"r": quat((0, 32 * math.sin(a * 6 - i * 0.5), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 4), 6 * math.sin(a), 0))}
        pose["jaw"] = {"r": quat((14 + 5 * math.sin(a * 8), 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"ear_{side}"] = {"r": quat((10 * math.sin(a * 4), 0, sx * 10 * math.sin(a * 4)))}
        return pose

    m.animate = animate
    return finish(m, 3, "#ffb36a", "#86c0e8", [P_("float", 60, "#fff0d0", 0.14, (2, 7), (0.3, 5), 0.5, "sparkle", 1.8)],
                  extra={"bloom": {"strength": 0.2, "threshold": 1.4, "radius": 1}})


def build_cheetah():
    m = new("cheetah", 36)
    f = fur(["#f0c060", "#e8b652", "#f4ca70"], belly="#fff4dc", pattern="spots", pcol="#22140c", freq=2.4)
    d = beast(m, dict(S=1.0, L=3.4, W=1.05, H=1.05, legF=1.45, hs=1.0, snout=0.3, v=0.075, fur=f, ear="round", tail="long", tail_n=10, tail_seg=0.32,
                      tail_w=0.11, tail_lift=-12, tail_curve=-3, eye="#ffb020", eye_glow=1.2, nose="#22140c", paw="#f0c060", claws="#2a2a2a",
                      waist=0.75, ear_inner="#22140c", brow="#22140c",
                      tail_fur=fur(["#f0c060"], extra=lambda p, n, h: "#1a1210" if int(-p.z / 0.25) % 2 else None)))
    hs = d["hs"]
    for sx in (1, -1):  # lágrimas negras
        m.box("head", (sx * 0.2 * hs, -0.06 * hs, 0.62 * hs), (0.05 * hs, 0.34 * hs, 0.04), "#1a1210")

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=45, speed=2, gallop=True, bob=0.16, knee=50)
        tail_sway(pose, t, 10, amp=8, speed=2, axis="x")
        pose["head"] = {"r": quat((-5 * math.sin(a * 4), 0, 0))}
        return pose

    m.animate = animate
    return finish(m, 4, "#ffcf6a", "#e8c48a", [P_("rise", 90, "#d8b88a", 0.24, (0.5, 3.5), (0, 1.4), 1.4, "square", 1.4),
                                              P_("float", 40, "#fff0c0", 0.12, (3, 8), (0.3, 5), 0.6, "sparkle", 1.6)],
                  extra={"bloom": {"strength": 0.2, "threshold": 1.4, "radius": 1}}, ground=("#d8b878", "#c8a868"))


# ======================================================================================
# 5-10
# ======================================================================================
def wolf_beast(m, white=False):
    if white:
        f = fur(["#f4f8ff", "#eef4ff", "#ffffff"], belly="#ffffff", dorsal="#dce8ff", pattern="runes", pcol="#5fb8ff", pemit=2.5)
        cols = dict(eye="#5fd8ff", nose="#3a5a8a", inner="#9fc8ff")
    else:
        f = fur(["#c8ccd4", "#bcc1ca", "#d4d8de"], belly="#eef0f4", dorsal="#7a808c")
        cols = dict(eye="#7fd0ff", nose="#1a1a1e", inner="#4a4e58")
    hf = fur(["#c8ccd4", "#bcc1ca"] if not white else ["#f4f8ff", "#ffffff"], belly="#eef0f4",
             extra=lambda p, n, h: ("#eef0f4" if not white else "#ffffff") if p.z > 0.6 and p.y < -0.05 else None)
    d = beast(m, dict(S=1.25, L=2.9, W=1.15, H=1.2, legF=1.3, hs=1.05, snout=0.7, v=0.085, fur=f, head_fur=hf, ear="pointy", tail="none" if white else "bushy",
                      tail_n=6, tail_seg=0.32, tail_w=0.14, tail_lift=-35, eye=cols["eye"], eye_glow=2.0, nose=cols["nose"], ear_inner=cols["inner"],
                      teeth=True, claws="#2a2a2a", brow="#5a606c" if not white else "#bcd4ff", fur_noise=0.1, waist=0.85,
                      body_extra=[ell((0, 0.35, 1.25), (0.85, 0.75, 0.55), 0.25, 4)]))  # gorguera de pelo
    return d


def build_wolf():
    m = new("wolf", 72)
    d = wolf_beast(m)
    for i in range(5):  # cicatriz y collar de garras
        m.box("body", ((i - 2) * 0.18, 0.05 - abs(i - 2) * 0.05, 1.62), (0.07, 0.18, 0.07), "#f6f0e2", r=(0, 0, (i - 2) * 12))

    def animate(t):
        a = t * TAU
        howl = max(0.0, math.sin(a)) ** 2
        pose = {"body": {"r": quat((-8 * howl, 0, 0))}, "head": {"r": quat((-50 * howl + 3 * math.sin(a * 6), 0, 0))},
                "jaw": {"r": quat((32 * howl, 0, 0))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-6 * howl, 0, 0))}
        tail_sway(pose, t, 6, amp=10)
        for side in ("L", "R"):
            pose[f"ear_{side}"] = {"r": quat((-12 * howl, 0, 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"eyes": 0.7 + 0.6 * max(0.0, math.sin(t * TAU)) ** 2, "neon": 0.8 + 0.2 * math.sin(t * TAU * 2)}
    return finish(m, 5, "#7fd0ff", "#1a2a44", [P_("float", 90, "#bfe8ff", 0.14, (3, 10), (0.3, 8), 0.5, "dot", 1.8, True),
                                              P_("rise", 50, "#7fd0ff", 0.2, (0.5, 3), (0.3, 3), 0.6, "sparkle", 2.0)])


def build_lion():
    m = new("lion", 72)
    f = fur(["#e2aa4c", "#d9a044", "#e8b458"], belly="#f6dca0", dorsal="#c8903a")
    d = beast(m, dict(S=1.35, L=3.0, W=1.4, H=1.35, legF=1.25, hs=1.25, snout=0.55, v=0.09, fur=f, ear="round", tail="tuft", tail_n=7, tail_seg=0.34,
                      tail_w=0.1, tail_lift=-20, tail_curve=8, eye="#ffb020", eye_glow=1.4, nose="#5a2a1a", ear_inner="#7a3a14", teeth=True,
                      claws="#e8dcc0", tuft_col="#6e3812", brow="#8a4a1a", muzzleW=1.15, fur_noise=0.07,
                      head_fur=fur(["#e2aa4c", "#e8b458"], extra=lambda p, n, h: "#f6e2b8" if p.z > 0.7 and p.y < 0 else None)))
    hs = d["hs"]
    # melena voluminosa esculpida
    m.part("mane", "head", (0, -0.05 * hs, -0.05 * hs))
    mp = [ell((0, 0.05 * hs, -0.12 * hs), (1.05 * hs, 1.05 * hs, 0.62 * hs), 0.28, 2.6, 4.0),
          ell((0, -0.6 * hs, 0.05 * hs), (0.6 * hs, 0.5 * hs, 0.45 * hs), 0.3, 3, 2.0),
          ell((0, 0.2 * hs, -0.75 * hs), (0.9 * hs, 0.95 * hs, 0.5 * hs), 0.25, 2.5, 7.0)]
    carve = [ell((0, 0.02 * hs, 0.4 * hs), (0.62 * hs, 0.6 * hs, 0.5 * hs))]
    mane_cols = ["#8a4a1a", "#a85a20", "#6e3812", "#b8682a", "#7a3e16"]
    voxelize(m, "mane", mp, 0.1, lambda p, n: mane_cols[int(_hash(round(p.x, 3), round(p.y, 3), round(p.z, 3)) * 97) % 5], carve=carve)
    # corona dorada con gemas
    m.part("crown_l", "head", (0, 1.12 * hs, -0.1))
    ring(m, "crown_l", 0.42, 16, (0.14, 0.18), "#f2c14e", metal=1)
    for k in range(8):
        a = k / 8 * TAU
        m.box("crown_l", (math.cos(a) * 0.42, 0.22, math.sin(a) * 0.42), (0.12, 0.34, 0.12), "#f2c14e", metal=1)
        m.box("crown_l", (math.cos(a) * 0.42, 0.44, math.sin(a) * 0.42), (0.14, 0.14, 0.14), "#ff3a4a" if k % 2 else "#3a8aff", r=(45, 0, 45), emit=1.5, tag="glow")

    def animate(t):
        a = t * TAU
        roar = max(0.0, math.sin(a)) ** 3
        pose = walk({}, t, amp=12 * (1 - roar), speed=1, bob=0.05, knee=20)
        pose["head"] = {"r": quat((-10 * roar, 0, 0)), "p": (0, 0, 0.12 * roar)}
        pose["jaw"] = {"r": quat((40 * roar, 0, 0))}
        pose["mane"] = {"s": (1 + 0.1 * roar,) * 3}
        tail_sway(pose, t, 7, amp=12)
        return pose

    m.animate = animate
    m.glow = lambda t: {"eyes": 0.8 + 0.5 * max(0.0, math.sin(t * TAU)) ** 3, "glow": 1.0, "neon": 0.9}
    return finish(m, 6, "#ffcf5a", "#3a2a14", [P_("rise", 110, "#ffd27a", 0.2, (1, 6), (0.3, 7), 0.4, "sparkle", 2.4),
                                              P_("float", 60, "#fff0c0", 0.12, (5, 14), (0.3, 9), 0.5, "square", 1.4)])


def build_frost_tiger():
    m = new("frost_tiger", 72)
    f = fur(["#e8f6ff", "#dff0ff", "#f2faff"], belly="#ffffff", pattern="stripes", pcol="#3fa8e8", pemit=1.6, freq=1.6)
    hf = fur(["#f2faff", "#e8f6ff"], belly="#ffffff", extra=lambda p, n, h: "#ffffff" if p.z > 0.55 and p.y < 0 else
             (("#3fa8e8", 1.2, "glow") if n.y > 0.5 and abs(p.x) > 0.12 and int((p.z + 5) / 0.22) % 2 else None))
    d = beast(m, dict(S=1.75, L=3.1, W=1.35, H=1.3, legF=1.25, hs=1.25, snout=0.45, v=0.09, fur=f, head_fur=hf, ear="round", tail="long", tail_n=9,
                      tail_seg=0.34, tail_w=0.12, tail_lift=-25, eye="#5fd8ff", eye_glow=2.5, slit=True, nose="#2a4a6a", ear_inner="#7fc8ff", teeth=True,
                      claws="#bff3ff", muzzleW=1.15, skullW=1.1, fur_noise=0.08,
                      body_extra=[ell((0, 0.2, 1.6), (1.0, 0.85, 0.6), 0.2, 4)],
                      tail_fur=fur(["#e8f6ff"], extra=lambda p, n, h: ("#3fa8e8", 1.5, "glow") if int(-p.z / 0.3) % 2 else None)))
    hs = d["hs"]
    for sx in (1, -1):  # bigotes de escarcha y patillas
        m.box("head", (sx * 0.62 * hs, -0.12 * hs, 0.5 * hs), (0.3 * hs, 0.25 * hs, 0.2 * hs), "#ffffff", r=(0, sx * 20, sx * -20))
        for j in (-1, 0, 1):
            m.box("head", (sx * 0.6 * hs, -0.2 * hs + j * 0.05, 0.85 * hs), (0.55 * hs, 0.02, 0.02), "#bff3ff", r=(0, 0, sx * j * 9), emit=0.8, tag="glow")
    for i in range(7):  # cristales de hielo en el lomo
        crystal(m, "body", (0, 1.25 + 0.12 * (i % 2), 1.6 - i * 0.7), 0.45, 1.1 + 0.35 * (i % 2), "#9fe8ff", rot=(-25, 0, 0), emit=1.2, tag="glow")
    for side in ("FL", "FR", "BL", "BR"):  # zarpas congeladas
        crystal(m, f"low_{side}", (0, -0.95, 0.0), 0.36, 0.5, "#bff3ff", rot=(0, 45, 0), emit=1.2, tag="glow")

    def animate(t):
        a = t * TAU
        leap = max(0.0, math.sin(a)) ** 1.5
        pose = {"body": {"p": (0, 1.5 * leap, 0), "r": quat((-14 * math.sin(a) * leap, 0, 0))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-65 * leap, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((30 * leap, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((55 * leap, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((-20 * leap, 0, 0))}
        pose["head"] = {"r": quat((10 * leap, 0, 0))}
        pose["jaw"] = {"r": quat((30 * leap, 0, 0))}
        tail_sway(pose, t, 9, amp=10, axis="x")
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 1.0, "neon": 0.9}
    m = finish(m, 7, "#7fe8ff", "#0e2440", [P_("snow", 260, "#e6fbff", 0.14, (0.5, 13), (0, 15), 0.9, "square", 1.8),
                                           P_("rise", 80, "#9fe8ff", 0.22, (0.5, 3.5), (0.3, 3), 0.8, "sparkle", 2.4)],
               ground=("#cfeaf7", "#e6f7ff"))
    for k in range(8):
        m.box("root", ((0.5 if k % 2 else -0.5), 0.52, -2.4 + k * 0.65), (0.36, 0.04, 0.42), "#9fe8ff", emit=1.5, tag="glow")
    return m


def bird_sculpt(m, s, cols, wing_rows, tail_cols, crest="flames", eye="#ffe14a", eye_glow=2.0, bone="#f2c14e", tail_feathers=9, fire=True):
    f = cols["fur"]
    m.part("bird", "root", (0, 3.6 * s, 0))
    voxelize(m, "bird", [ell((0, 0, 0), (0.75 * s, 0.85 * s, 1.15 * s), 0.08, 3), ell((0, -0.15 * s, 0.55 * s), (0.62 * s, 0.7 * s, 0.6 * s), 0.08, 3),
                         cap((0, 0.45 * s, 0.7 * s), (0, 1.35 * s, 1.05 * s), 0.42 * s, 0.32 * s, 0.08, 3)], 0.09, f)
    m.part("head", "bird", (0, 1.5 * s, 1.1 * s))
    skull = ell((0, 0, 0.1 * s), (0.42 * s, 0.4 * s, 0.48 * s))
    voxelize(m, "head", [skull, ell((0, 0.18 * s, 0.25 * s), (0.36 * s, 0.14 * s, 0.25 * s))], 0.075, cols.get("head_fur", f))
    voxelize(m, "head", [cap((0, -0.02 * s, 0.45 * s), (0, -0.2 * s, 1.0 * s), 0.17 * s, 0.03 * s)], 0.06,
             lambda p, n: (cols["beak"], 0, None))
    for b in m.parts["head"].boxes[-200:]:
        if b["col"] == cols["beak"]:
            b["metal"] = 1
    put_eyes(m, "head", skull, 0.8 * s, eye, glow=eye_glow, x=0.36, y=0.12, size=0.9, brow=cols.get("brow"))
    m.part("crest", "head", (0, 0.35 * s, -0.05 * s))
    for i in range(6):
        if crest == "flames":
            flame(m, "crest", (0, 0, -i * 0.18 * s), (1.1 - i * 0.14) * s, 0.3 * s, seed=i)
        else:
            m.box("crest", (0, (0.35 + 0.1 * i) * s, -i * 0.15 * s), (0.12 * s, (0.7 - 0.08 * i) * s, 0.12 * s), cols["accent"], r=(-25, 0, 0))
    bonep = [(0, 0), (1.0, 0.8), (2.0, 1.9), (2.9, 3.1)]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "bird", (sx * 0.6 * s, 0.4 * s, 0.15 * s), (0, sx * -15, 0))
        _wing(m, w, sx, [(n, a * s, b * s, wd * s, z * s, c) for (n, a, b, wd, z, c) in wing_rows], [(x * s, y * s) for x, y in bonep], bone, bone)
    m.part("tailfan", "bird", (0, 0.1 * s, -1.0 * s))
    for i in range(tail_feathers):
        k = i / (tail_feathers - 1) - 0.5
        ang = k * 80
        Lf = (2.8 - abs(k) * 1.4) * s
        rq = quat((25, ang, 0))
        for j, col in enumerate(tail_cols):
            p = rq @ Vector((0, 0, -(0.3 + j * 0.33) * Lf))
            m.box("tailfan", p, (0.34 * s * (1 - j * 0.15), 0.08 * s, 0.36 * Lf), col, r=rq, emit=(1.2 * (j + 1) / 3) if fire else 0,
                  tag="glow" if fire else None)
        if fire:
            flame(m, "tailfan", rq @ Vector((0, 0, -1.05 * Lf)), 0.5 * s, 0.2 * s, seed=i)
    for sx in (1, -1):
        segment(m, "bird", (sx * 0.3 * s, -0.6 * s, 0), (sx * 0.32 * s, -1.4 * s, 0.1 * s), 0.13 * s, cols["leg"], metal=1)
        for k in (-1, 0, 1):
            segment(m, "bird", (sx * 0.32 * s, -1.4 * s, 0.1 * s), (sx * 0.32 * s + k * 0.16 * s, -1.45 * s, 0.45 * s), 0.07 * s, cols["leg"], metal=1)


def build_phoenix():
    m = new("phoenix", 48)
    firecols = ["#ff8a1a", "#ffb020", "#ffe14a"]

    def plumage(p, n):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if n.y < -0.4:
            return ("#ffd23a", 1.0, "glow")
        k = (p.y * 2 + math.sin(p.x * 6) * 0.3) % 1
        if k < 0.15:
            return ("#ffe14a", 1.2, "glow")
        return ["#ff5a1a", "#ff6a1a", "#e8481a"][int(h * 97) % 3]

    bird_sculpt(m, 1.15, dict(fur=plumage, beak="#ffe08a", leg="#c8401a", accent="#ffe14a", brow="#c8301a"),
                [(13, 1.9, 3.6, 0.66, -0.12, firecols), (11, 1.2, 2.2, 0.62, 0.0, ["#ff6a1a", "#ff9a2a", "#ffd23a"]),
                 (8, 0.6, 1.1, 0.58, 0.12, ["#ff4a1a", "#ff7a1a", "#ffb020"])], ["#ff4a1a", "#ff8a1a", "#ffd23a"])
    for i in range(10):  # plumas que se desprenden (orbitan)
        n = f"plume{i}"
        a = i / 10 * TAU
        m.part(n, "root", (math.cos(a) * 3.2, 3 + 2.5 * _hash(i, 4), math.sin(a) * 3.2), (20 * i, 30 * i, 40))
        m.box(n, (0, 0, 0), (0.18, 0.04, 0.5), "#ffb020", emit=1.5, tag="glow")
        m.box(n, (0, 0, -0.3), (0.1, 0.04, 0.2), "#ffe14a", emit=2, tag="glow")

    def animate(t):
        a = t * TAU
        flap = math.sin(a * 2)
        pose = {"bird": {"p": (0, 0.4 * math.sin(a * 2 - 1), 0), "r": quat((-6 * flap, 0, 0))}}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 15 * flap, sx * 38 * flap))}
        pose["tailfan"] = {"r": quat((8 * math.sin(a * 2 + 1), 6 * math.sin(a), 0))}
        pose["head"] = {"r": quat((4 * math.sin(a * 2), 12 * math.sin(a), 0))}
        pose["crest"] = {"s": (1, 1 + 0.15 * math.sin(a * 8), 1)}
        for i in range(10):
            base = i / 10 * TAU
            pv = m.parts[f"plume{i}"].pivot
            ang = base + a
            pose[f"plume{i}"] = {"p": (math.cos(ang) * 3.2 - pv.x, -((t + i / 10) % 1) * 2.5 + 1.2, math.sin(ang) * 3.2 - pv.z),
                                 "r": quat((math.degrees(a * 2), math.degrees(a + i), 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.75 + 0.25 * math.sin(t * TAU * 4), "fire": 0.85 + 0.15 * math.sin(t * TAU * 12), "eyes": 1.0, "neon": 0.9}
    return finish(m, 8, "#ff8a1a", "#2a0e06", [P_("rise", 240, "#ff8a1a", 0.18, (0.5, 4.5), (0.5, 11), 0.8, "square", 2.4),
                                              P_("snow", 50, "#ffb020", 0.3, (1, 5), (0, 10), 0.4, "sparkle", 2.4)],
                  extra={"beam": {"color": "#ff8a1a", "top": 1.6, "bottom": 1.0, "height": 2.4, "y": 0.5, "intensity": 0.5}})


def dragon_sculpt(m, D):
    f = D["fur"]
    d = beast(m, dict(S=D.get("S", 1.5), L=3.2, W=1.5, H=1.35, legF=1.2, hs=1.15, snout=0.95, v=D.get("v", 0.1), fur=f, head_fur=D.get("head_fur", f),
                      ear="none", tail="long", tail_n=D.get("tail_n", 12), tail_seg=0.4, tail_w=0.22, tail_lift=-5, tail_curve=-3, neckUp=1.0, neckFwd=0.7,
                      neckW=0.9, eye=D["eye"], eye_glow=3.0, slit=True, nose=D.get("nose", "#1a1a1a"), teeth=True, claws=D["claw"], brow=D["spike"],
                      muzzleW=0.9, fur_noise=0.05, skullW=0.95))
    S = D.get("S", 1.5)
    hs = d["hs"]
    for i in range(9):  # crestas dorsales
        z = 0.5 * d["L"] - 0.3 - i * d["L"] / 9
        m.box("body", (0, 0.62 * d["H"] + 0.1, z), (0.14 * S, 0.5 * S, 0.5 * S), D["spike"], r=(45, 0, 0), emit=D.get("spine_emit", 0),
              tag="glow" if D.get("spine_emit") else None)
    for i in range(1, d["tail_n"], 2):
        m.box(f"tail{i}", (0, 0.25 * S, -0.2 * S), (0.1 * S, 0.34 * S, 0.34 * S), D["spike"], r=(45, 0, 0))
    m.box(f"tail{d['tail_n'] - 1}", (0, 0, -0.55 * S), (0.9 * S, 0.12 * S, 0.8 * S), D["spike"], r=(0, 45, 0))
    for sx in (1, -1):
        horn(m, "head", (sx * hs * 0.3, hs * 0.38, -hs * 0.05), (sx * 0.35, 0.65, -0.7), D["horn_len"], hs * 0.2, -14, D["horn"], D["horn_tip"],
             tip_emit=D.get("horn_emit", 0), tag="glow" if D.get("horn_emit") else None)
        horn(m, "head", (sx * hs * 0.42, hs * 0.1, -hs * 0.1), (sx * 0.7, 0.2, -0.6), D["horn_len"] * 0.5, hs * 0.12, -10, D["horn"], D["horn_tip"])
        m.box("head", (sx * hs * 0.5, -hs * 0.05, hs * 0.1), (0.08, hs * 0.35, hs * 0.55), D["spike"], r=(0, sx * 20, 0))
    if D.get("horn_metal"):
        for b in m.parts["head"].boxes:
            if b["col"] in (D["horn"], D["horn_tip"]):
                b["metal"] = 1
    pairs = D.get("wing_pairs", 1)
    for pi in range(pairs):
        for side, sx in (("L", 1), ("R", -1)):
            w = f"wing{pi}_{side}"
            m.part(w, "body", (sx * d["W"] * 0.4, d["H"] * 0.42, d["L"] * (0.22 - 0.22 * pi)), (0, sx * (-20 + 15 * pi), sx * (12 - 10 * pi)))
            sc = D["wing_scale"] * S * (1 - 0.18 * pi)
            tips = [(1.2 * sc, 2.6 * sc), (2.7 * sc, 2.7 * sc), (3.9 * sc, 1.4 * sc), (3.8 * sc, -0.3 * sc), (2.7 * sc, -1.3 * sc)]
            membrane_wing(m, w, sx, (1.3 * sc, 1.6 * sc), tips, D["wing_bone"], D["membrane"][0], D["membrane"][1], step=0.14 * S)
            for tx, ty in tips[:3]:
                m.box(w, (sx * tx, ty + 0.15 * S, 0), (0.1 * S, 0.35 * S, 0.1 * S), D["claw"], metal=1 if D["claw"] == "#f2c14e" else 0)
    return d


def scales(cols, belly, glow_col=None):
    def fn(p, n):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if n.y < -0.4:
            row = int((p.z + 10) / 0.22) % 2
            return belly[row]
        if glow_col and abs(fbm(p, 1.2, 4.0) - 0.5) < 0.022:
            return (glow_col, 2.0, "glow")
        row = int((p.y + 10) / 0.2)
        col = int((p.z + 10) / 0.2 + (row % 2) * 0.5)
        return cols[(row + col) % len(cols)] if h > 0.1 else cols[0]
    return fn


def build_ancient_dragon():
    m = new("ancient_dragon", 72)
    dragon_sculpt(m, dict(S=1.55, fur=scales(["#2f5a4a", "#3a6a58", "#24483a"], ["#d8c08a", "#c8ae76"]), eye="#ffb020", claw="#f2c14e",
                          spike="#c8a040", horn="#f2c14e", horn_tip="#fff0a0", horn_len=2.6, horn_metal=True, wing_scale=1.2, wing_bone="#24483a",
                          membrane=("#6a3a2a", "#8a4a32")))
    # armadura antigua de oro en el pecho
    for i in range(4):
        m.box("body", (0, 0.1 - i * 0.28, 2.45 - i * 0.05), (1.2 - i * 0.15, 0.2, 0.1), "#f2c14e", r=(-20, 0, 0), metal=1)
    m.box("body", (0, -0.2, 2.55), (0.3, 0.3, 0.12), "#3affd0", r=(0, 0, 45), emit=2, tag="glow")

    def animate(t):
        a = t * TAU
        roar = max(0.0, math.sin(a)) ** 3
        flap = math.sin(a * 2)
        pose = {"body": {"p": (0, 0.08 * math.sin(a * 2), 0), "r": quat((-5 * roar, 0, 0))}}
        pose["head"] = {"r": quat((-18 * roar + 3 * math.sin(a * 2), 8 * math.sin(a) * (1 - roar), 0))}
        pose["jaw"] = {"r": quat((42 * roar, 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing0_{side}"] = {"r": quat((0, sx * 10 * flap, sx * (25 * flap + 12 * roar)))}
        tail_sway(pose, t, 12, amp=6)
        return pose

    m.animate = animate
    m.glow = lambda t: {"eyes": 0.8 + 0.5 * max(0.0, math.sin(t * TAU)) ** 3, "neon": 0.9, "glow": 1.0}
    return finish(m, 9, "#ffb020", "#14201c", [P_("rise", 180, "#ffb020", 0.18, (0.5, 7), (0.3, 11), 0.6, "square", 2.2),
                                              P_("float", 100, "#bfe8c8", 0.12, (7, 20), (0.5, 13), 0.5, "square", 1.4)])


def serpent_chain(m, name, root, n, path, r0, r1, v, colfn, root_pivot):
    m.part(name, "root", root_pivot)
    prev = Vector(path(0))
    m.part(f"{name}_0", name, tuple(prev))
    for i in range(1, n):
        p = Vector(path(i / (n - 1)))
        m.part(f"{name}_{i}", f"{name}_{i - 1}", tuple(p - prev))
        prev = p
    for i in range(n):
        k = i / (n - 1)
        r_ = r0 + (r1 - r0) * k
        nxt = Vector(path(min(1, (i + 1) / (n - 1)))) - Vector(path(k))
        voxelize(m, f"{name}_{i}", [cap((0, 0, 0), tuple(nxt * 1.05), r_, r_ * 0.95)], v, colfn)
    return [f"{name}_{i}" for i in range(n)]


def serpent_head(m, part, s, col, eye, jaw_col="#3a0e1a", horn_col=None, horn_tip=None):
    skull = ell((0, 0.1 * s, 0.2 * s), (0.6 * s, 0.45 * s, 0.7 * s))
    voxelize(m, part, [skull, cap((0, 0, 0.5 * s), (0, -0.05 * s, 1.3 * s), 0.38 * s, 0.25 * s), ell((0, 0.35 * s, 0.4 * s), (0.5 * s, 0.15 * s, 0.35 * s))],
             0.09, col)
    put_eyes(m, part, skull, s, eye, glow=3.0, x=0.38, y=0.2, size=1.0, slit=True)
    m.part(part + "_jaw", part, (0, -0.3 * s, 0.4 * s))
    voxelize(m, part + "_jaw", [cap((0, 0, 0), (0, -0.05 * s, 0.85 * s), 0.3 * s, 0.2 * s)], 0.085, lambda p, n: jaw_col if n.y > 0.5 else col(p, n))
    for sx in (1, -1):
        m.box(part, (sx * 0.18 * s, -0.32 * s, 1.15 * s), (0.06 * s, 0.25 * s, 0.06 * s), "#f6f0e2")
        if horn_col:
            horn(m, part, (sx * 0.35 * s, 0.4 * s, 0.0), (sx * 0.4, 0.6, -0.8), 1.5 * s, 0.2 * s, -12, horn_col, horn_tip, tip_emit=2, tag="glow")


def build_cosmic_worm():
    """Puesto 10: ciempiés cósmico. Cabeza alzada con mandíbulas, ojos y antenas;
    segmentos con placas dorsales brillantes y un par de patas por segmento."""
    m = new("cosmic_worm", 96)
    m.part("worm", "root", (0, 0.9, 0))
    n = 15

    def path(k):  # pose de reposo recta (fácil de animar)
        return Vector((0, 0.15, 4.2 - k * 8.5))

    body_col = lambda p, nn: cosmic_col(p, pal=("#1a0f4a", "#24125f", "#2e1670", "#140a3a"), neb=("#e05ae8", "#3ad0f0"))

    def plate(p, nn):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if abs(p.x) > 0.62 and nn.y > 0.2:
            return ("#ffb8f0", 1.8, "glow")
        if h > 0.96:
            return ("#ffffff", 2.5, "twinkle")
        return ["#120a30", "#1a1040", "#0e0826"][int(h * 97) % 3]

    for i in range(n):
        k = i / (n - 1)
        p0, p1 = path(k), path(min(1.0, k + 1 / (n - 1)))
        d = (p1 - p0) if i < n - 1 else (p0 - path(k - 1 / (n - 1)))
        q = Vector((0, 0, -1)).rotation_difference(d.normalized())
        w = 1.0 - 0.45 * k if i > 0 else 1.1
        sname = f"seg{i}"
        m.part(sname, "worm", tuple(p0), q)
        if i == 0:
            continue
        voxelize(m, sname, [ell((0, 0, 0), (0.7 * w, 0.42 * w, 0.42))], 0.1, body_col)
        voxelize(m, sname, [ell((0, 0.22 * w, 0), (0.78 * w, 0.2 * w, 0.4))], 0.1, plate)
        for side, sx in (("L", 1), ("R", -1)):
            up = f"leg{i}_{side}"
            m.part(up, sname, (sx * 0.62 * w, -0.1 * w, 0.0), (0, 0, 0))
            segment(m, up, (0, 0, 0), (sx * 0.3 * w, 0.02, 0), (0.2 * w + 0.05, 0.16 * w + 0.05), "#2a1a5a")  # coxa
            m.box(up, (sx * 0.3 * w, 0.02, 0), (0.2 * w + 0.04,) * 3, "#e05ae8", r=(45, 0, 45), emit=1.6, tag="glow")  # articulación
            segment(m, up, (sx * 0.3 * w, 0.02, 0), (sx * 0.8 * w, 0.4, 0.05), (0.16 * w + 0.04, 0.14 * w + 0.04), "#3a2a7a")  # fémur
            segment(m, up, (sx * 0.34 * w, 0.12, 0), (sx * 0.76 * w, 0.48, 0.05), (0.08 * w + 0.03, 0.05), "#120a30")  # placa
            m.box(up, (sx * 0.55 * w, 0.32, 0.05), (0.06, 0.06, 0.12 * w + 0.06), "#ffb8f0", emit=1.5, tag="glow")
            lo_ = f"foot{i}_{side}"
            m.part(lo_, up, (sx * 0.8 * w, 0.4, 0.05))
            m.box(lo_, (0, 0, 0), (0.16 * w + 0.04,) * 3, "#7fe8ff", r=(45, 0, 45), emit=1.6, tag="glow")
            knee = Vector((sx * 0.25 * w, -0.65 * w - 0.15, 0.12))
            segment(m, lo_, (0, 0, 0), knee, (0.12 * w + 0.03, 0.1 * w + 0.03), "#2a1a5a")  # tibia
            for j in (0.35, 0.65):  # púas
                pp = knee * j
                m.box(lo_, pp + Vector((sx * 0.06, 0, 0)), (0.05, 0.12, 0.05), "#c8a8ff", r=(0, 0, sx * -40))
            tip = knee + Vector((sx * 0.05, -0.32 * w - 0.08, 0.12))
            segment(m, lo_, knee, tip, (0.08 * w + 0.02, 0.06), "#e6d6ff", emit=0.6, tag="glow")  # garra
            m.box(lo_, tip, (0.08, 0.1, 0.08), "#7fe8ff", emit=2.2, tag="glow")
    # cabeza
    h = "seg0"
    skull = ell((0, 0.05, -0.15), (0.75, 0.55, 0.7))
    voxelize(m, h, [skull, ell((0, 0.35, -0.3), (0.65, 0.25, 0.5))], 0.09, plate)
    voxelize(m, h, [ell((0, -0.1, -0.1), (0.6, 0.4, 0.55))], 0.09, body_col)
    # racimo de ojos brillantes (frente = -z del segmento)
    for sx in (1, -1):
        for j, (ex, ey) in enumerate(((0.32, 0.3), (0.5, 0.15), (0.2, 0.45))):
            m.box(h, (sx * ex, ey, -0.78 + 0.05 * j), (0.16 - 0.03 * j, 0.16 - 0.03 * j, 0.08), "#fff3a0", emit=4, tag="eyes")
    # mandíbulas curvas
    for side, sx in (("L", 1), ("R", -1)):
        mp = f"mandible_{side}"
        m.part(mp, h, (sx * 0.35, -0.2, -0.65))
        pts = [Vector((sx * (0.05 + 0.25 * math.sin(u * math.pi * 0.8)), -0.05 * u, -1.1 * u)) for u in (j / 6 for j in range(7))]
        for j in range(6):
            col = "#e6d6ff" if j < 4 else "#ffb8f0"
            segment(m, mp, pts[j], pts[j + 1], (0.2 - 0.025 * j, 0.16 - 0.02 * j), col, emit=0.5 if j < 4 else 2.0, tag="glow")
        # antenas segmentadas
        an = f"antenna_{side}"
        m.part(an, h, (sx * 0.28, 0.5, -0.55))
        pts = [Vector((sx * 0.5 * u, 1.3 * math.sin(u * math.pi * 0.6), -0.8 * u + 0.9 * u * u)) for u in (j / 8 for j in range(9))]
        for j in range(8):
            segment(m, an, pts[j], pts[j + 1], 0.07, "#c8a8ff" if j % 2 else "#7fe8ff", emit=1.2, tag="glow")
        m.box(an, pts[-1], (0.14, 0.14, 0.14), "#ffffff", emit=3, tag="twinkle")
    # púas de la cola
    last = f"seg{n - 1}"
    for sx in (1, -1):
        segment(m, last, (sx * 0.15, 0, 0.2), (sx * 0.5, 0.2, 1.2), 0.08, "#ffb8f0", emit=1.5, tag="glow")
    ring(m, h, 0.8, 20, (0.06, 0.06), "#ffe08a", center=(0, 0.05, -0.2), rot=(90, 0, 0), emit=1.5, tag="neon")

    def animate(t):
        a = t * TAU
        pose = {"worm": {"p": (0, 0.05 * math.sin(a * 2), 0)}}
        for i in range(n):
            pose[f"seg{i}"] = {"p": (0.35 * math.sin(a * 2 - i * 0.55), 0, 0), "r": quat((0, 12 * math.cos(a * 2 - i * 0.55), 0))}
            if i > 0:
                for side, sx in (("L", 1), ("R", -1)):
                    ph = a * 4 - i * 0.9 + (0 if sx > 0 else math.pi)
                    pose[f"leg{i}_{side}"] = {"r": quat((0, 25 * math.sin(ph), sx * 12 * max(0.0, math.cos(ph))))}
        pose["seg0"] = {"p": (0.35 * math.sin(a * 2), 0, 0), "r": quat((-10 - 8 * math.sin(a * 2), 14 * math.sin(a), 0))}
        snap = max(0.0, math.sin(a * 2)) ** 6
        pose["mandible_L"] = {"r": quat((0, -28 * snap + 6, 0))}
        pose["mandible_R"] = {"r": quat((0, 28 * snap - 6, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"antenna_{side}"] = {"r": quat((10 * math.sin(a * 3 + sx), sx * 8 * math.sin(a * 2), 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0,
                        "glow": 0.75 + 0.25 * math.sin(t * TAU * 4), "neon": 0.9}
    return finish(m, 10, "#e05ae8", "#0a0626", [P_("float", 320, "#ffffff", 0.12, (6, 26), (-2, 20), 0.6, "square", 2.0, True),
                                               P_("rise", 160, "#c8a8ff", 0.2, (0.3, 4), (0.3, 6), 0.4, "sparkle", 2.4)], extra={"dist": 1.3})


# ======================================================================================
# 11-20
# ======================================================================================
def build_celestial_wolf():
    m = new("celestial_wolf", 96)
    d = wolf_beast(m, white=True)
    for ti in range(6):
        ang = -55 + ti * 22
        parent, piv = "body", (0, 0.6, -1.6)
        for i in range(7):
            k = i / 6
            n = f"t{ti}_{i}"
            m.part(n, parent, piv, (-40 if i == 0 else 8, ang if i == 0 else 0, 0))
            r_ = 0.2 + 0.25 * math.sin(k * math.pi * 0.9 + 0.15)
            col = "#ffffff" if k < 0.45 else ("#bfe8ff" if k < 0.75 else "#5fb8ff")
            voxelize(m, n, [ell((0, 0, -0.22), (r_, r_, 0.32), 0.15, 4)], 0.09, lambda p, nn, col=col, k=k: (col, 0.4 + 2.4 * k, "glow"))
            parent, piv = n, (0, 0, -0.42)
    m.part("moon", "head", (0, 1.4, -0.3))
    for k in range(14):
        a = -0.9 + k / 13 * 3.4
        w = 0.28 * math.sin((k + 0.5) / 14 * math.pi) + 0.06
        m.box("moon", (math.cos(a + 1.2) * 0.6, math.sin(a + 1.2) * 0.6, 0), (w, w, 0.14), "#dff0ff", emit=2, tag="glow")
    m.box("head", (0, 0.5, 0.85), (0.08, 0.4, 0.04), "#5fb8ff", emit=3, tag="glow")
    for sx in (1, -1):  # brazaletes lunares
        for leg in ("FL", "BL") if sx > 0 else ("FR", "BR"):
            ring(m, f"low_{leg}", 0.24, 12, (0.08, 0.1), "#cfe6ff", center=(0, -0.3, 0), metal=1)

    def animate(t):
        a = t * TAU
        howl = max(0.0, math.sin(a)) ** 2
        pose = {"body": {"r": quat((-8 * howl, 0, 0)), "p": (0, 0.06 * math.sin(a * 2), 0)},
                "head": {"r": quat((-50 * howl, 0, 0))}, "jaw": {"r": quat((32 * howl, 0, 0))},
                "moon": {"r": quat((0, 0, math.degrees(a) * 0.5)), "s": (1 + 0.15 * howl,) * 3}}
        for ti in range(6):
            for i in range(1, 7):
                pose[f"t{ti}_{i}"] = {"r": quat((8 + 6 * math.sin(a * 2 - i * 0.6 + ti), 10 * math.sin(a - i * 0.5 + ti * 0.7), 0))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.75 + 0.25 * math.sin(t * TAU * 2), "eyes": 0.8 + 0.6 * max(0.0, math.sin(t * TAU)) ** 2, "neon": 0.9}
    return finish(m, 11, "#5fb8ff", "#0a1430", [P_("orbit", 160, "#bfe8ff", 0.24, (3, 7), (0.5, 8), 0.25, "sparkle", 2.6),
                                               P_("float", 220, "#ffffff", 0.12, (8, 24), (0.5, 18), 0.6, "square", 1.8, True)],
                  extra={"beam": {"color": "#5fb8ff", "top": 2.6, "bottom": 1.8, "height": 4.5, "y": 0.8, "intensity": 0.3}})


def build_griffin_emperor():
    m = new("griffin_emperor", 72)
    f = fur(["#c89a52", "#bf904a", "#d4a660"], belly="#f6e2b8", dorsal="#a87a3a")
    feathers = fur(["#ffffff", "#f4f4f4", "#ececec"], belly="#ffffff")
    d = beast(m, dict(S=1.4, L=3.0, W=1.4, H=1.35, legF=1.2, hs=1.15, snout=0.0, v=0.09, fur=f, head_fur=feathers, ear="pointy", tail="tuft", tail_n=7,
                      tail_seg=0.34, tail_w=0.1, tail_lift=-15, eye="#ffb020", eye_glow=2.0, ear_inner="#e8e8e8", claws="#f2c14e", tuft_col="#8a5a20",
                      brow="#c8c8c8", body_extra=[ell((0, 0.2, 1.3), (0.95, 0.95, 0.7), 0.15, 4)],
                      leg_fur=fur(["#c89a52"], extra=lambda p, n, h: "#f2c14e" if p.y < -0.9 else None)))
    hs = d["hs"]
    voxelize(m, "head", [cap((0, -0.05 * hs, 0.5 * hs), (0, -0.35 * hs, 1.25 * hs), 0.24 * hs, 0.04 * hs)], 0.06, lambda p, n: "#f2c14e")
    for b in m.parts["head"].boxes:
        if b["col"] == "#f2c14e":
            b["metal"] = 1
    m.part("crown_g", "head", (0, 0.62 * hs, 0.1))
    ring(m, "crown_g", 0.46, 16, (0.14, 0.2), "#f2c14e", metal=1)
    for k in range(8):
        a = k / 8 * TAU
        m.box("crown_g", (math.cos(a) * 0.46, 0.26, math.sin(a) * 0.46), (0.12, 0.4, 0.12), "#f2c14e", metal=1)
        m.box("crown_g", (math.cos(a) * 0.46, 0.5, math.sin(a) * 0.46), (0.15, 0.15, 0.15), "#ff4d6d" if k % 2 else "#4d9bff", r=(45, 0, 45), emit=1.5, tag="glow")
    # armadura imperial
    for i in range(3):
        m.box("body", (0, 0.95 - i * 0.05, 0.9 - i * 0.6), (1.5 - i * 0.1, 0.12, 0.5), "#f2c14e", metal=1)
    gold = ["#fff6d8", "#ffe7a8", "#f2c14e"]
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.7, 0.75, 0.8), (0, sx * -10, sx * 10))
        _wing(m, w, sx, [(15, 2.6, 5.0, 0.8, -0.16, gold), (13, 1.6, 3.0, 0.75, 0.0, ["#ffffff", "#fff6d8", "#ffe7a8"]),
                         (9, 0.8, 1.6, 0.7, 0.14, ["#ffffff", "#ffffff", "#fff6d8"])],
              [(0, 0), (1.3, 1.0), (2.6, 2.4), (3.7, 3.8)], "#f2c14e", "#f2c14e")

    def animate(t):
        a = t * TAU
        glide = math.sin(a)
        pose = {"body": {"p": (0, 1.8 + 0.35 * math.sin(a * 2), 0), "r": quat((-6, 0, 8 * glide))}}
        for k in ("FL", "FR"):
            pose[f"leg_{k}"] = {"r": quat((-50, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((40, 0, 0))}
        for k in ("BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((45, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((-20, 0, 0))}
        flap = math.sin(a * 2) * 0.6
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 8 * flap, sx * (22 * flap - 5)))}
        pose["head"] = {"r": quat((6, -8 * glide, 0))}
        tail_sway(pose, t, 7, amp=8)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.85, "eyes": 1.0, "neon": 0.8 + 0.2 * math.sin(t * TAU * 2)}
    return finish(m, 12, "#ffd23a", "#1a2a4a", [P_("snow", 90, "#fff6d8", 0.3, (1, 8), (0, 11), 0.35, "sparkle", 2.4),
                                               P_("orbit", 140, "#ffffff", 0.14, (5, 9), (1, 9), 0.5, "square", 1.6)])


def build_abyss_hydra():
    m = new("abyss_hydra", 96)
    sc = scales(["#1e1636", "#2a1e48", "#16102a"], ["#3a2a5a", "#30224e"], glow_col="#b06bff")
    d = beast(m, dict(S=1.6, L=3.0, W=2.0, H=1.4, legF=0.95, hs=0.01, snout=0.0, v=0.11, fur=sc, ear="none", tail="long", tail_n=9, tail_seg=0.42,
                      tail_w=0.26, tail_lift=-5, claws="#b06bff", neckUp=0.0, neckFwd=0.0))
    for nm in ("head", "jaw"):
        m.parts[nm].boxes.clear()
    S = 1.6
    for i in range(7):
        ang = (i - 3) * 20
        lift = 40 + abs(i - 3) * 5
        parent, piv = "body", ((i - 3) * 0.35, 0.6 * S, 1.3 * S)
        for j in range(6):
            n = f"n{i}_{j}"
            m.part(n, parent, piv, (-lift if j == 0 else 8, ang if j == 0 else 0, 0))
            r_ = 0.32 - 0.02 * j
            voxelize(m, n, [cap((0, 0, 0), (0, 0, 0.48), r_, r_ - 0.02)], 0.09, sc)
            parent, piv = n, (0, 0, 0.46)
        h = f"h{i}"
        m.part(h, parent, piv, (lift - 5, 0, 0))
        serpent_head(m, h, 0.62 if i != 3 else 0.8, sc, "#d8a8ff", horn_col="#2a1e48", horn_tip="#b06bff")
    for k in range(12):
        crystal(m, "body", ((k % 3 - 1) * 0.7, 1.15, 1.6 - k * 0.38), 0.34, 0.8, "#8a4ae8", emit=1.2, tag="glow")

    def animate(t):
        a = t * TAU
        pose = {"body": {"p": (0, 0.06 * math.sin(a * 2), 0)}}
        for i in range(7):
            for j in range(1, 6):
                pose[f"n{i}_{j}"] = {"r": quat((6 * math.sin(a * 2 - j * 0.5 + i), 9 * math.sin(a - j * 0.5 + i * 0.9), 0))}
            snap = max(0.0, math.sin(a * 2 + i * 0.9)) ** 8
            pose[f"h{i}_jaw"] = {"r": quat((35 * snap, 0, 0))}
        tail_sway(pose, t, 9, amp=8)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.6 + 0.4 * math.sin(t * TAU * 2) ** 2, "eyes": 1.0, "neon": 0.9}
    return finish(m, 13, "#b06bff", "#0c0618", [P_("rise", 240, "#b06bff", 0.2, (0.5, 7), (0, 11), 0.5, "square", 2.4),
                                               P_("float", 160, "#6a4aa8", 0.16, (7, 22), (0.5, 13), 0.4, "square", 1.4)])


def build_world_titan():
    """Puesto 14: bestia colosal de piedra (rinoceronte de roca) con montañas en el lomo."""
    m = new("world_titan", 72)
    rk = rock(["#6a6e78", "#5e626c", "#767a84", "#585c66"], crystal_col="#5ff4ff")
    d = beast(m, dict(S=1.7, L=3.2, W=1.8, H=1.6, legF=1.05, hs=1.3, snout=0.85, v=0.12, fur=rk, ear="round", tail="long", tail_n=4, tail_seg=0.3,
                      tail_w=0.16, tail_lift=-30, eye="#5ff4ff", eye_glow=3.0, nose="#3a3e46", ear_inner="#3a3e46", claws="#2a2c32",
                      brow="#4a4e58", muzzleW=1.25, fur_noise=0.14, waist=1.0, skullW=1.1,
                      body_extra=[ell((0, 0.9, 0.0), (1.1, 0.5, 1.9), 0.25, 1.5, 3.0)]))
    S = 1.7
    hs = d["hs"]
    # cuernos de cristal en el hocico
    crystal(m, "head", (0, 0.15 * hs, 0.95 * hs + d["sn"] * 0.8), 0.5, 1.8, "#5ff4ff", rot=(-35, 0, 0), emit=1.8, tag="glow")
    crystal(m, "head", (0, 0.25 * hs, 0.6 * hs + d["sn"] * 0.4), 0.35, 0.9, "#c88aff", rot=(-25, 0, 0), emit=1.6, tag="glow")
    # cordillera en el lomo: picos de roca con nieve y cristales
    body_boxes = m.parts["body"].boxes

    def back_top(x, z):
        ys = [b["c"].y for b in body_boxes if abs(b["c"].x - x) < 0.35 and abs(b["c"].z - z) < 0.35]
        return max(ys) if ys else 1.5

    for i, (z, h, w) in enumerate(((1.4, 1.6, 1.3), (0.4, 2.2, 1.5), (-0.6, 1.9, 1.4), (-1.5, 1.4, 1.1))):
        x0 = 0.2 * ((-1) ** i)
        base = Vector((x0, back_top(x0, z) - 0.35, z))
        steps = 7
        for j in range(steps):
            k = j / steps
            ww = w * (1 - k) + 0.12
            col = "#f4f8ff" if k > 0.62 else ("#6a6e78" if j % 2 else "#5e626c")
            m.box("body", base + Vector((0, (j + 0.5) * h / steps, 0)), (ww, h / steps + 0.02, ww), col, r=(0, 20 * j + 15 * i, 0))
        crystal(m, "body", base + Vector((0.5, 0.4, 0.2)), 0.3, 0.8, "#5ff4ff", rot=(0, 0, -30), emit=1.5, tag="glow")
    for i in range(6):  # pinos diminutos entre las montañas
        px, pz = (i % 2 - 0.5) * 1.3, 1.9 - i * 0.7
        p = Vector((px, back_top(px, pz) - 0.1, pz))
        for j, w in enumerate((0.36, 0.26, 0.16)):
            m.box("body", p + Vector((0, 0.2 + j * 0.18, 0)), (w, 0.2, w), "#2f6a3a" if j % 2 else "#3a7a42")
    for sx in (1, -1):  # placas de roca en hombros y brazaletes de cristal
        m.box("body", (sx * 1.4, 0.7, 1.4), (0.3, 0.9, 1.1), "#4a4e58", r=(0, 0, sx * 15))
    for leg in ("FL", "FR", "BL", "BR"):
        crystal(m, f"low_{leg}", (0, -0.3, 0.3), 0.3, 0.5, "#5ff4ff", rot=(70, 0, 0), emit=1.5, tag="glow")
    m.part("quake", "root", (0, 0.86, 0))
    ring(m, "quake", 2.6, 48, (0.14, 0.05), "#ffcf7a", emit=2, tag="quake")
    ring(m, "quake", 2.2, 44, (0.08, 0.05), "#5ff4ff", emit=2, tag="quake")

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=16, speed=1, bob=0.08, knee=22)
        stomp = max(0.0, math.sin(a * 2)) ** 6
        pose["body"]["p"] = (0, 0.08 * abs(math.sin(a)) - 0.06 * stomp, 0)
        pose["head"] = {"r": quat((-14 * stomp + 4 * math.sin(a * 2), 8 * math.sin(a), 0))}
        pose["jaw"] = {"r": quat((18 * stomp, 0, 0))}
        ph = (t * 2) % 1
        pose["quake"] = {"s": (0.6 + 3 * ph, 1, 0.6 + 3 * ph)}
        tail_sway(pose, t, 4, amp=10)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "quake": 1 - (t * 2) % 1, "neon": 0.9}
    return finish(m, 14, "#5ff4ff", "#1a1c24", [P_("rise", 200, "#b8a890", 0.24, (1, 8), (0, 3.5), 0.8, "square", 1.2),
                                               P_("float", 140, "#5ff4ff", 0.16, (4, 13), (0.5, 13), 0.4, "sparkle", 2.0)], extra={"dist": 1.25})


def build_prismatic_unicorn():
    m = new("prismatic_unicorn", 48)
    rainbow = ["#ff9ab8", "#ffd27a", "#fff3a0", "#a8f0b8", "#9ad8ff", "#c8a8ff"]
    pearl = fur(["#fbf8ff", "#f6f2ff", "#fffaff"], belly="#ffffff", extra=lambda p, n, h: "#f0e6ff" if h > 0.93 else None)
    d = beast(m, dict(S=1.35, L=3.0, W=1.1, H=1.2, legF=1.8, hs=1.0, snout=0.75, v=0.085, fur=pearl, ear="pointy", tail="long", tail_n=9, tail_seg=0.34,
                      tail_w=0.12, tail_lift=-30, neckUp=1.1, neckFwd=0.55, eye="#c88aff", eye_glow=1.5, nose="#e6d6f0", ear_inner="#ffd6f0",
                      paw="#f2c14e", waist=0.85, muzzleW=0.85,
                      tail_fur=lambda p, n: (rainbow[int((p.y * 3 + p.x * 3 + 30)) % 6], 1.0, "glow")))
    S = 1.35
    neck_end = d["neck_end"]
    for i in range(12):  # crin iridiscente esculpida
        k = i / 11
        p = Vector((0, 0.3 * d["H"], 0.38 * d["L"])).lerp(neck_end, k)
        n = f"mane{i}"
        m.part(n, "body", tuple(p + Vector((0, 0.42 * S, -0.15))))
        voxelize(m, n, [ell((0, 0, 0), (0.18, 0.35, 0.28), 0.25, 5, i)], 0.08, lambda pp, nn, i=i: (rainbow[(i + int(pp.y * 6 + 10)) % 6], 1.2, "glow"))
    crystal(m, "head", (0, 0.85, 0.6), 0.3, 1.6, "#e8f6ff", rot=(-30, 0, 0), emit=2.0, tag="glow")
    crystal(m, "head", (0, 0.85, 0.6), 0.14, 1.4, "#ffffff", rot=(-30, 0, 0), emit=3.0, tag="glow")
    for k in range(6):
        m.box("head", ((k - 2.5) * 0.12, 0.45, 0.35 - 0.04 * k), (0.14, 0.32, 0.3), rainbow[k], emit=1.0, tag="glow")

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=20, speed=2, gallop=False, bob=0.12, knee=35)
        tail_sway(pose, t, 9, amp=10, speed=2, axis="x")
        pose["head"] = {"r": quat((-6 * math.sin(a * 4), 0, 0))}
        for i in range(12):
            pose[f"mane{i}"] = {"r": quat((-12 * math.sin(a * 4 - i * 0.5), 0, 6 * math.sin(a * 2 - i * 0.4)))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 4), "eyes": 1.0, "neon": 0.9}
    return finish(m, 15, "#ff9ad8", "#1a1030", [P_("rise", 220, "#ffd6f0", 0.2, (0.4, 4.5), (0.3, 7), 1.2, "sparkle", 2.6),
                                               P_("orbit", 180, "#9ad8ff", 0.18, (3, 7), (0.5, 8), 0.4, "square", 2.0),
                                               P_("orbit", 140, "#fff3a0", 0.18, (3.5, 8), (0.5, 8), -0.3, "square", 2.0)],
                  extra={"beam": {"color": "#ffd6f0", "top": 2.6, "bottom": 2.0, "height": 5, "y": 0.8, "intensity": 0.3}})


def build_shadow_sovereign():
    m = new("shadow_sovereign", 72)
    dragon_sculpt(m, dict(S=1.65, fur=scales(["#16121e", "#1e1828", "#100c16"], ["#2a2238", "#221c2e"], glow_col="#b06bff"), eye="#c88aff", claw="#b06bff",
                          spike="#8a4ae8", spine_emit=1.8, horn="#1a1424", horn_tip="#c88aff", horn_emit=2.5, horn_len=2.8, wing_scale=1.2, wing_pairs=3,
                          wing_bone="#1a1424", membrane=("#3a1a5a", "#2a1240")))
    for i in range(9):
        n = f"vflame{i}"
        m.part(n, "body", (0, 1.25, 2.0 - i * 0.55))
        flame(m, n, (0, 0, 0), 1.0 - 0.05 * i, 0.4, seed=i, tag="vfire")
        for b in m.parts[n].boxes:
            b["col"] = ["#5a1aa8", "#7a2ac8", "#9a4ae8", "#b86aff", "#d8a8ff", "#f2e6ff"][min(5, int((b["c"].y / 1.0) * 6))]
    m.part("crown_s", "head", (0, 1.0, -0.2))
    for k in range(7):  # corona de pinchos oscuros
        a = (k - 3) * 0.32
        m.box("crown_s", (math.sin(a) * 0.6, 0.3 + 0.2 * (1 - abs(k - 3) / 3), math.cos(a) * 0.1), (0.12, 0.6 + 0.3 * (1 - abs(k - 3) / 3), 0.12), "#1a1424")
        m.box("crown_s", (math.sin(a) * 0.6, 0.75 + 0.3 * (1 - abs(k - 3) / 3), math.cos(a) * 0.1), (0.1, 0.1, 0.1), "#c88aff", emit=3, tag="glow")

    def animate(t):
        a = t * TAU
        roar = max(0.0, math.sin(a)) ** 3
        pose = {"body": {"p": (0, 1.4 + 0.3 * math.sin(a * 2 - 1), 0), "r": quat((-4, 0, 0))}}
        for k in ("FL", "FR", "BL", "BR"):
            pose[f"leg_{k}"] = {"r": quat((25 if k[0] == "B" else -15, 0, 0))}
            pose[f"low_{k}"] = {"r": quat((20 if k[0] == "F" else -15, 0, 0))}
        for pi in range(3):
            for side, sx in (("L", 1), ("R", -1)):
                pose[f"wing{pi}_{side}"] = {"r": quat((0, sx * 10 * math.sin(a * 2), sx * 30 * math.sin(a * 2 - pi * 0.5)))}
        pose["head"] = {"r": quat((-12 * roar, 0, 0))}
        pose["jaw"] = {"r": quat((42 * roar, 0, 0))}
        for i in range(9):
            f = 1 + 0.15 * math.sin(a * 8 + i * 1.7)
            pose[f"vflame{i}"] = {"s": (1 / f ** 0.5, f, 1 / f ** 0.5)}
        tail_sway(pose, t, 12, amp=8)
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 1.0, "vfire": 0.85 + 0.15 * math.sin(t * TAU * 12), "fire": 1.0, "neon": 0.9}
    return finish(m, 16, "#b06bff", "#08050e", [P_("rise", 280, "#3a2a4a", 0.42, (0.5, 7), (0, 10), 0.5, "dot", 0.9),
                                               P_("rise", 200, "#b06bff", 0.18, (0.5, 6), (0.5, 11), 0.8, "square", 2.4)], extra={"dist": 1.25})


def build_cosmic_leviathan():
    m = new("cosmic_leviathan", 96)
    n = 12
    neb = lambda p, nn: cosmic_col(p, pal=("#0a1a4a", "#102462", "#0e1e56", "#183080"), neb=("#5ff4ff", "#d14ee8"))
    path = lambda k: (0, 0, 4.4 - k * 9.0)  # pose de reposo recta
    segs = serpent_chain(m, "worm", "root", n, path, 1.6, 0.5, 0.17, neb, (0, 3.2, 0))
    h = segs[0]
    m.part("lhead", h, (0, 0.1, 0.6))
    skull = ell((0, 0.25, 0.5), (1.35, 1.0, 1.4))
    voxelize(m, "lhead", [skull, cap((0, 0.15, 1.2), (0, 0.0, 2.6), 1.0, 0.65), ell((0, 0.85, 0.9), (0.9, 0.35, 1.1))], 0.13, neb)
    put_eyes(m, "lhead", ell((0, 0.35, 1.3), (1.15, 0.8, 1.0)), 2.2, "#fff3a0", glow=4.0, x=0.42, y=0.12, size=1.0, brow="#5ff4ff", slit=True)
    m.part("ljaw", "lhead", (0, -0.55, 0.9))
    voxelize(m, "ljaw", [cap((0, 0, 0), (0, -0.15, 1.7), 0.85, 0.55)], 0.13, lambda p, nn: "#3a0e2a" if nn.y > 0.5 else neb(p, nn))
    for k in range(7):  # dientes de cristal arriba y abajo
        for sx in (1, -1):
            z = 1.2 + k * 0.22
            m.box("lhead", (sx * (0.55 - k * 0.04), -0.55, z), (0.1, 0.28, 0.1), "#e6f6ff", emit=0.6, tag="glow")
            m.box("ljaw", (sx * (0.5 - k * 0.04), 0.25, 0.3 + k * 0.2), (0.09, 0.24, 0.09), "#e6f6ff", emit=0.6, tag="glow")
    for side, sx in (("L", 1), ("R", -1)):  # barbas luminosas
        bb = f"barbel_{side}"
        m.part(bb, "lhead", (sx * 0.6, -0.2, 2.3))
        pts = [Vector((sx * (0.2 + 0.5 * u), -0.4 * u - 0.6 * u * u, -0.6 * u)) for u in (j / 6 for j in range(7))]
        for j in range(6):
            segment(m, bb, pts[j], pts[j + 1], 0.09 - 0.008 * j, "#5ff4ff", emit=1.5, tag="glow")
        m.box(bb, pts[-1], (0.18, 0.18, 0.18), "#ffffff", emit=3, tag="twinkle")
        fn_ = f"fin_{side}"
        m.part(fn_, h, (sx * 1.4, -0.4, -0.2))
        voxelize(m, fn_, [ell((sx * 1.3, -0.2, -0.4), (1.5, 0.12, 0.8))], 0.12,
                 lambda p, nn: ("#ffffff", 1.6, "glow") if abs(p.z + 0.4) > 0.55 else ("#5ff4ff", 1.0, "glow"))
    for k in range(5):  # cresta de cristales en la cabeza
        crystal(m, "lhead", (0, 1.15 - 0.05 * k, 1.5 - k * 0.45), 0.35, 1.0 - 0.1 * k, "#5ff4ff", rot=(-40, 0, 0), emit=1.6, tag="glow")
    for sx in (1, -1):  # cuernos
        horn(m, "lhead", (sx * 0.8, 0.9, 0.3), (sx * 0.5, 0.5, -0.8), 1.6, 0.25, -12, "#1a2a5a", "#d14ee8", tip_emit=2.0, tag="glow")
    for i in range(2, n, 2):
        crystal(m, segs[i], (0, 1.6 - i * 0.09, 0), 0.5, 1.3, "#5ff4ff", rot=(-30, 0, 0), emit=1.5, tag="glow")
    for sx in (1, -1):
        m.box(segs[-1], (sx * 1.0, 0, -0.6), (1.9, 0.14, 1.0), "#5ff4ff", r=(0, sx * 25, 0), emit=1.5, tag="glow")
    for k in range(3):
        pn = f"planet{k}"
        a = k / 3 * TAU
        m.part(pn, "root", (math.cos(a) * 7, 3.5 + k, math.sin(a) * 7))
        voxelize(m, pn, [ell((0, 0, 0), (0.6 + 0.15 * k,) * 3)], 0.13,
                 lambda p, nn, k=k: ["#ff8a4a", "#7fe0ff", "#9cff8a"][k] if math.sin(p.y * 8) > 0 else "#2a2a4a")

    def animate(t):
        a = t * TAU
        pose = {"worm": {"p": (0, 0.4 * math.sin(a * 2), 0), "r": quat((0, 8 * math.sin(a), 0))}}
        for i in range(n):
            pose[f"worm_{i}"] = {"r": quat((7 * math.sin(a * 2 - i * 0.6), 4 * math.sin(a - i * 0.4), 0))}
        pose["ljaw"] = {"r": quat((22 * max(0.0, math.sin(a * 2)) ** 3 + 4, 0, 0))}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"barbel_{side}"] = {"r": quat((12 * math.sin(a * 2 + sx), sx * 10 * math.sin(a * 3), 0))}
            pose[f"fin_{side}"] = {"r": quat((0, 0, sx * 18 * math.sin(a * 2)))}
        for k in range(3):
            ang = k / 3 * TAU + a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 7 - piv.x, 0.3 * math.sin(a * 2 + k), math.sin(ang) * 7 - piv.z), "r": quat((0, math.degrees(a * 2), 20))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "eyes": 1.0, "glow": 0.9, "neon": 0.9}
    return finish(m, 17, "#5ff4ff", "#040a24", [P_("float", 420, "#ffffff", 0.14, (9, 32), (-4, 24), 0.6, "square", 2.0, True),
                                               P_("orbit", 180, "#d14ee8", 0.24, (4, 9), (1, 9), 0.2, "sparkle", 2.4)],
                  extra={"ground": None, "dist": 1.15})


def build_phoenix_deity():
    m = new("phoenix_deity", 72)
    sun = ["#fff6d8", "#ffe14a", "#ffb020"]

    def plumage(p, n):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if n.y < -0.4:
            return ("#fff6d8", 1.5, "glow")
        k = (p.y * 2 + math.sin(p.x * 6) * 0.3) % 1
        if k < 0.15:
            return ("#ffffff", 1.5, "glow")
        return ["#ffb020", "#ffc030", "#ffa010"][int(h * 97) % 3]

    bird_sculpt(m, 1.5, dict(fur=plumage, beak="#f2c14e", leg="#f2c14e", accent="#ffffff", brow="#ff8a1a"),
                [(15, 2.1, 4.0, 0.7, -0.14, sun), (13, 1.3, 2.4, 0.66, 0.0, ["#ffffff", "#fff6d8", "#ffe14a"]),
                 (9, 0.6, 1.2, 0.62, 0.12, ["#ffffff", "#ffffff", "#fff6d8"])], ["#ff8a1a", "#ffd23a", "#fff6d8"], eye="#ffffff", eye_glow=3.0,
                tail_feathers=11)
    m.part("halo", "head", (0, 0.25, -0.8))
    for k in range(18):
        a = k / 18 * TAU
        n = f"hf{k}"
        m.part(n, "halo", (math.cos(a) * 1.5, math.sin(a) * 1.5, 0), (0, 0, math.degrees(a) - 90))
        flame(m, n, (0, 0, 0), 0.7, 0.24, seed=k)
    ring(m, "halo", 1.5, 44, (0.16, 0.16), "#f2c14e", rot=(90, 0, 0), metal=1)
    m.part("sun", "bird", (0, 2.0, -2.0))
    for k in range(28):
        a = k / 28 * TAU
        segment(m, "sun", (math.cos(a) * 1.4, math.sin(a) * 1.4, 0), (math.cos(a) * (2.9 + 0.4 * (k % 2)), math.sin(a) * (2.9 + 0.4 * (k % 2)), 0),
                (0.14, 0.06), "#ffe14a", emit=1.5, tag="glow")
    voxelize(m, "sun", [ell((0, 0, 0), (1.25, 1.25, 0.2))], 0.12, lambda p, n: ("#fff6d8", 1.5, "glow") if p.length > 1.0 else ("#ffd23a", 1.0, "glow"))

    def animate(t):
        a = t * TAU
        flap = math.sin(a * 2)
        pose = {"bird": {"p": (0, 0.45 * math.sin(a * 2 - 1), 0), "r": quat((-5 * flap, 0, 0))}}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 12 * flap, sx * 32 * flap))}
        pose["tailfan"] = {"r": quat((8 * math.sin(a * 2 + 1), 6 * math.sin(a), 0))}
        pose["halo"] = {"r": quat((0, 0, math.degrees(a)))}
        pose["sun"] = {"r": quat((0, 0, -math.degrees(a) * 0.5)), "s": (1 + 0.05 * math.sin(a * 4),) * 3}
        pose["crest"] = {"s": (1, 1 + 0.15 * math.sin(a * 8), 1)}
        return pose

    m.animate = animate
    m.glow = lambda t: {"glow": 0.8 + 0.2 * math.sin(t * TAU * 4), "fire": 0.85 + 0.15 * math.sin(t * TAU * 12), "eyes": 1.0, "neon": 0.9}
    return finish(m, 18, "#ffb020", "#2a1404", [P_("rise", 320, "#ffb020", 0.2, (0.5, 6), (0.5, 13), 0.8, "square", 2.6),
                                               P_("orbit", 220, "#fff6d8", 0.24, (4, 9), (1, 11), 0.3, "sparkle", 2.6)],
                  extra={"beam": {"color": "#ffd23a", "top": 2.6, "bottom": 1.6, "height": 3.6, "y": 0.8, "intensity": 0.4}, "dist": 1.25})


def build_world_serpent():
    m = new("world_serpent", 96)
    n = 28

    def sc(p, nn):
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        if h > 0.97:
            return ("#9ffcff", 2.5, "twinkle")
        if abs(fbm(p, 1.3, 2.0) - 0.5) < 0.03:
            return ("#3affd0", 2.0, "glow")
        row = int((p.y + 20) / 0.2)
        return ["#0e2a2a", "#123434", "#0a2222", "#1a3e3a"][(row + int((p.x + 20) / 0.2)) % 4]

    path = lambda k: (0, 0.0, 6.5 - k * 13.0)  # pose de reposo recta
    segs = serpent_chain(m, "worm", "root", n, path, 0.85, 0.3, 0.12, sc, (0, 2.2, 0))
    d0 = (Vector(path(0)) - Vector(path(0.03))).normalized()
    m.part("shead", segs[0], (0, 0.5, 0), Vector((0, 0, 1)).rotation_difference(d0) @ quat((-15, 0, 0)))
    serpent_head(m, "shead", 2.2, sc, "#ff3a6a", horn_col="#1a3e3a", horn_tip="#3affd0")
    for k in range(5):  # capucha/cresta dimensional
        crystal(m, "shead", (0, 1.0 - 0.05 * k, 0.4 - k * 0.45), 0.4, 1.1 - 0.12 * k, "#3affd0", rot=(-45, 0, 0), emit=1.8, tag="glow")
    for sx in (1, -1):
        m.box("shead", (sx * 0.95, 0.1, 0.3), (0.12, 0.9, 1.2), "#123434", r=(0, sx * 25, 0))
        m.box("shead", (sx * 1.0, 0.1, 0.3), (0.06, 0.7, 1.0), "#3affd0", r=(0, sx * 25, 0), emit=1.5, tag="glow")
    for k, kk in enumerate((0.2, 0.5, 0.8)):
        p = Vector(path(kk)) + Vector((0, 2.2, 0))
        pn = f"portal{k}"
        m.part(pn, "root", tuple(p))
        ring(m, pn, 1.5, 36, (0.2, 0.2), "#b06bff" if k % 2 else "#3affd0", rot=(90, 0, 0), emit=3, tag="portal")
        ring(m, pn, 1.25, 36, (0.07, 0.07), "#ffffff", rot=(90, 0, 0), emit=2, tag="portal")
    for k in range(4):
        pn = f"planet{k}"
        a = k / 4 * TAU
        m.part(pn, "root", (math.cos(a) * 7.5, 3.5 + k * 0.8, math.sin(a) * 7.5))
        cols = [("#ff8a4a", "#c9522a"), ("#7fe0ff", "#3a8ac9"), ("#9cff8a", "#3f9a5a"), ("#e6d6ff", "#8a6ac8")][k]
        voxelize(m, pn, [ell((0, 0, 0), (0.6 + 0.15 * (k % 2),) * 3)], 0.13, lambda p, nn, cols=cols: cols[0] if math.sin(p.y * 8) > 0 else cols[1])
        if k == 1:
            ring(m, pn, 1.2, 28, (0.22, 0.04), "#e6d6ff", rot=(20, 0, 10))

    def animate(t):
        a = t * TAU
        pose = {"worm": {"p": (0, 0.6 + 0.2 * math.sin(a * 2), 0)}}
        for i in range(n):
            pose[f"worm_{i}"] = {"r": quat((2 * math.sin(a * 2 - i * 0.4), 9 * math.sin(a * 2 - i * 0.45), 0))}
        pose["shead_jaw"] = {"r": quat((25 * max(0.0, math.sin(a * 2)) ** 4, 0, 0))}
        for k in range(3):
            pose[f"portal{k}"] = {"s": (1 + 0.08 * math.sin(a * 4 + k),) * 3}
        for k in range(4):
            ang = k / 4 * TAU - a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 7.5 - piv.x, 0.3 * math.sin(a * 2 + k), math.sin(ang) * 7.5 - piv.z), "r": quat((0, math.degrees(a * 2), 15))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "glow": 0.7 + 0.3 * math.sin(t * TAU * 2), "eyes": 1.0,
                        "portal": 0.8 + 0.2 * math.sin(t * TAU * 6), "neon": 0.9}
    return finish(m, 19, "#3affd0", "#020a0c", [P_("float", 420, "#ffffff", 0.14, (9, 32), (-4, 24), 0.6, "square", 2.0, True),
                                               P_("orbit", 240, "#b06bff", 0.22, (4, 9), (1, 10), 0.3, "sparkle", 2.4)], extra={"dist": 1.1})


def build_genesis_beast():
    m = new("genesis_beast", 96)
    cosmos = lambda p, n: cosmic_col(p, pal=("#0e0a2e", "#160f44", "#1d1456", "#0a0822"), neb=("#ffb8f0", "#7fe8ff"))
    d = beast(m, dict(S=1.6, L=3.0, W=1.4, H=1.35, legF=1.25, hs=1.2, snout=0.55, v=0.1, fur=cosmos, ear="pointy", tail="long", tail_n=11, tail_seg=0.38,
                      tail_w=0.12, tail_lift=-20, eye="#fff6d8", eye_glow=3.5, nose="#0a0822", ear_inner="#7fe8ff", teeth=True, claws="#f2c14e",
                      paw="#f2c14e", brow="#ffe08a", muzzleW=1.1,
                      tail_fur=lambda p, n: ("#ffb8f0", 1.5, "glow") if _hash(round(p.x, 3), round(p.z, 3)) > 0.5 else ("#7fe8ff", 1.5, "glow")))
    hs = d["hs"]
    m.part("mane", "head", (0, -0.05 * hs, -0.05 * hs))
    mp = [ell((0, 0.05 * hs, -0.12 * hs), (1.15 * hs, 1.15 * hs, 0.65 * hs), 0.3, 2.6, 4.0), ell((0, 0.2 * hs, -0.8 * hs), (1.0 * hs, 1.0 * hs, 0.5 * hs), 0.25, 2.5, 7)]
    carve = [ell((0, 0.02 * hs, 0.4 * hs), (0.62 * hs, 0.6 * hs, 0.5 * hs))]
    mp = mp[:1]
    voxelize(m, "mane", mp, 0.11, lambda p, n: ("#ffe9a8", 2.5, "twinkle") if _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3)) > 0.95 else
             ["#2a1f6a", "#3a2a8a", "#5a3ab8", "#4a2aa0"][int(_hash(round(p.x, 3), round(p.y, 3), round(p.z, 3)) * 97) % 4], carve=carve)
    for sx in (1, -1):
        horn(m, "head", (sx * hs * 0.3, hs * 0.42, hs * 0.0), (sx * 0.35, 0.7, -0.6), 2.8, hs * 0.2, -12, "#f2c14e", "#fff6d8", tip_emit=2, tag="glow")
    for b in m.parts["head"].boxes:
        if b["col"] in ("#f2c14e", "#fff6d8"):
            b["metal"] = 1
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "body", (sx * 0.9, 0.9, 0.6), (0, sx * -15, sx * 5))
        tips = []
        for i in range(9):
            k = i / 8
            th = math.radians(-15 + k * 100)
            Lw = 2.0 + 1.8 * math.sin(k * math.pi * 0.85 + 0.25)
            dd = Vector((sx * math.cos(th), math.sin(th), 0))
            rot = (0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th))
            crystal(m, w, dd * (0.3 + Lw / 2), 0.7, Lw, ["#6a4cff", "#ffb8f0", "#7fe8ff"][i % 3], rot=rot, emit=0.8, tag="nebula")
            tip = dd * (0.4 + Lw)
            tips.append(tip)
            if i % 2 == 0:
                star(m, w, tip + Vector((0, 0, 0.1)), 0.4, "#ffffff", emit=3, tag="twinkle")
    m.part("halo", "head", (0, 2.6, -0.4), (15, 0, 0))
    ring(m, "halo", 1.0, 36, (0.2, 0.16), "#f2c14e", metal=1)
    ring(m, "halo", 1.0, 36, (0.07, 0.2), "#fff6d8", emit=1.5, tag="glow")
    m.part("galaxy", "root", (0, 10.0, 0), (75, 0, 0))
    for arm in range(3):
        for i in range(24):
            u = i / 23
            a = arm * TAU / 3 + u * TAU * 0.9
            r_ = 0.2 + u * 2.4
            col = "#ffffff" if u < 0.25 else ["#ffb8f0", "#7fe8ff", "#c8a8ff"][arm]
            m.box("galaxy", (math.cos(a) * r_, (_hash(i, arm) - 0.5) * 0.2, math.sin(a) * r_), (0.2 - 0.09 * u,) * 3, col, emit=3 - 2 * u, tag="twinkle")
    for k in range(4):
        pn = f"planet{k}"
        a = k / 4 * TAU
        m.part(pn, "root", (math.cos(a) * 8.5, 4.5 + k * 0.7, math.sin(a) * 8.5))
        cols = [("#ff8a4a", "#c9522a"), ("#7fe0ff", "#3a8ac9"), ("#9cff8a", "#3f9a5a"), ("#ffe08a", "#c8a040")][k]
        voxelize(m, pn, [ell((0, 0, 0), (0.6,) * 3)], 0.13, lambda p, nn, cols=cols: cols[0] if math.sin(p.y * 8 + p.x * 3) > 0 else cols[1])

    def animate(t):
        a = t * TAU
        pose = walk({}, t, amp=14, speed=1, bob=0.06, knee=22)
        pose["head"] = {"r": quat((-4 * math.sin(a * 2), 8 * math.sin(a), 0))}
        pose["mane"] = {"r": quat((0, 0, math.degrees(a) * 0.25)), "s": (1 + 0.05 * math.sin(a * 4),) * 3}
        for side, sx in (("L", 1), ("R", -1)):
            pose[f"wing_{side}"] = {"r": quat((0, sx * 10 * math.sin(a * 2), sx * 20 * math.sin(a * 2)))}
        pose["halo"] = {"r": quat((0, math.degrees(a), 0))}
        pose["galaxy"] = {"r": quat((0, math.degrees(a), 0))}
        tail_sway(pose, t, 11, amp=10)
        for k in range(4):
            ang = k / 4 * TAU + a
            piv = m.parts[f"planet{k}"].pivot
            pose[f"planet{k}"] = {"p": (math.cos(ang) * 8.5 - piv.x, 0.4 * math.sin(a * 2 + k), math.sin(ang) * 8.5 - piv.z), "r": quat((0, math.degrees(a * 2), 20))}
        return pose

    m.animate = animate
    m.glow = lambda t: {"twinkle": 0.5 + 0.5 * math.sin(t * TAU * 5) ** 2, "nebula": 0.8 + 0.2 * math.sin(t * TAU * 2), "glow": 0.85 + 0.15 * math.sin(t * TAU * 4),
                        "eyes": 1.0, "neon": 0.9}
    return finish(m, 20, "#ffb8f0", "#06041a", [P_("float", 260, "#ffffff", 0.12, (12, 34), (-4, 26), 0.6, "square", 1.8, True),
                                               P_("orbit", 90, "#ffb8f0", 0.22, (5, 10), (1, 11), 0.25, "sparkle", 2.2)],
                  extra={"beam": {"color": "#ffb8f0", "top": 3.4, "bottom": 2.4, "height": 5.5, "y": 0.8, "intensity": 0.25}, "dist": 0.95, "targetY": 4.2})


import animals as _first  # noqa: E402  (primera versión de bloques, la preferida para 1-4)


def _scaled(fn, scale):
    def run():
        sculpt.VOXEL_SCALE = scale
        return fn()
    return run


BUILDERS = {
    "animal_rabbit": _first.build_rabbit, "animal_cat": _first.build_cat, "animal_dog": _first.build_dog, "animal_cheetah": _first.build_cheetah,
    "animal_wolf": build_wolf, "animal_lion": build_lion, "animal_frost_tiger": build_frost_tiger, "animal_phoenix": build_phoenix,
    "animal_ancient_dragon": build_ancient_dragon, "animal_cosmic_worm": build_cosmic_worm, "animal_celestial_wolf": build_celestial_wolf,
    "animal_griffin_emperor": build_griffin_emperor, "animal_abyss_hydra": build_abyss_hydra, "animal_world_titan": build_world_titan,
    "animal_prismatic_unicorn": build_prismatic_unicorn, "animal_shadow_sovereign": build_shadow_sovereign,
    "animal_cosmic_leviathan": build_cosmic_leviathan, "animal_phoenix_deity": build_phoenix_deity, "animal_world_serpent": build_world_serpent,
    "animal_genesis_beast": build_genesis_beast,
}
BUILDERS = {k: (v if k in ("animal_rabbit", "animal_cat", "animal_dog", "animal_cheetah") else _scaled(v, 1.45)) for k, v in BUILDERS.items()}
