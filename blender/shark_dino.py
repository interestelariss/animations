"""Tiburón-dinosaurio (basado en la referencia de VOS Studios), hecho solo de cubos.

Bípedo terópodo con cabeza de tiburón martillo, branquias rojas brillantes,
aleta dorsal escalonada, cola de tiburón con aleta caudal y un arpón rayado
con cuentas rojas colgando.
"""

import math

from mathutils import Quaternion, Vector

from voxel import Model, quat, stepped_fin

# Paleta
BODY = "#44515f"
DARK = "#283039"
MID = "#5a6979"
BELLY = "#9aa6b2"
BELLY2 = "#7e8a97"
GLOW = "#ff2b22"
EYE = "#ff3b2f"
BLACK = "#0d0f12"
TOOTH = "#f3eedf"
GUM = "#8a2433"
MOUTH = "#3a0c12"
TONGUE = "#a83a4a"
CLAW = "#d8d0bd"
SHAFT = "#1a1d22"
BAND = "#e9e9e9"
STEEL = "#c3ccd6"
RIPPLE = "#cfe3ff"


def build():
    m = Model("shark_dino", fps=24, frames=72)

    m.part("root")
    m.part("hips", "root", (0, 5.0, 0))

    # ---------------- cadera ----------------
    m.box("hips", (0, 0, -0.2), (2.6, 1.9, 2.8), BODY)
    m.box("hips", (0, -0.75, 0.3), (2.2, 0.5, 2.0), BELLY2)
    m.box("hips", (0, 0.95, -0.3), (1.6, 0.3, 2.4), DARK)
    # pequeñas aletas pélvicas
    for sx in (1, -1):
        stepped_fin(m, "hips", (sx * 1.35, -0.7, -0.6), 1.1, -0.9, 3, 0.4, 0.2, DARK)

    # ---------------- torso (inclinado hacia delante) ----------------
    m.part("torso", "hips", (0, 0.5, 0.5), (40, 0, 0))
    m.box("torso", (0, 1.6, 0), (2.9, 3.5, 2.7), BODY)
    m.box("torso", (0, 1.7, -1.38), (2.1, 3.3, 0.3), DARK)  # lomo
    for sx in (1, -1):
        m.box("torso", (sx * 1.48, 2.3, -0.2), (0.25, 2.0, 1.9), MID)  # músculos laterales
    # placas ventrales (pliegues de tiburón)
    for i in range(7):
        col = BELLY if i % 2 == 0 else BELLY2
        m.box("torso", (0, 0.15 + i * 0.46, 1.36), (2.1 - abs(i - 3) * 0.08, 0.42, 0.3), col)
    # costillas rojas brillantes en el pecho
    for i in range(3):
        m.box("torso", (0, 1.1 + i * 0.55, 1.53), (1.3 - i * 0.2, 0.07, 0.05), GLOW, emit=4, tag="glow")
    # branquias: 5 rajas por lado
    for i in range(5):
        for sx in (1, -1):
            m.box("torso", (sx * 1.47, 2.0 + i * 0.3, 0.45), (0.16, 0.1, 1.3), GLOW, emit=5, tag="glow")
            m.box("torso", (sx * 1.46, 2.0 + i * 0.3 + 0.08, 0.45), (0.14, 0.06, 1.4), DARK)
    # pinchos en la columna
    for i in range(5):
        m.box("torso", (0, 0.4 + i * 0.65, -1.6), (0.22, 0.35, 0.35), DARK, r=(45, 0, 0))

    # aleta dorsal: perfil de tiburón (borde de ataque curvo, borde de salida cóncavo),
    # con la base hundida en el lomo para que no quede flotando
    m.part("dorsal", "torso", (0, 1.9, -1.35), (-70, 0, 0))
    FH = 2.5
    n = 16
    for j in range(n):
        y = -0.5 + (j + 0.5) * (FH + 0.5) / n
        u = max(0.0, y / FH)
        front = 1.25 - 2.15 * u ** 1.35
        back = -1.55 + 0.65 * u ** 0.6
        if front - back < 0.12:
            front = back + 0.12
        w = 0.5 - 0.32 * u
        m.box("dorsal", (0, y, (front + back) / 2), (w, (FH + 0.5) / n + 0.02, front - back), DARK if j > 3 else BODY)
        if j > 3:
            m.box("dorsal", (0, y, front - 0.05), (w + 0.04, (FH + 0.5) / n + 0.02, 0.12), MID)  # borde de ataque
    # ---------------- cuello y cabeza ----------------
    m.part("neck", "torso", (0, 3.25, 0.1), (-25, 0, 0))
    m.box("neck", (0, 0.5, 0.1), (2.3, 1.3, 2.3), BODY)
    m.box("neck", (0, 0.4, 1.2), (1.8, 1.0, 0.3), BELLY)
    m.box("neck", (0, 0.6, -1.2), (1.6, 1.1, 0.25), DARK)

    m.part("head", "neck", (0, 1.0, 0.3), (-15, 0, 0))
    # cráneo y hocico que se estrecha (escalones)
    m.box("head", (0, 0.62, 0.6), (2.5, 1.45, 2.2), BODY)
    m.box("head", (0, 0.72, 2.2), (2.25, 1.15, 1.4), BODY)
    m.box("head", (0, 0.76, 3.35), (1.85, 0.95, 1.2), BODY)
    m.box("head", (0, 0.74, 4.3), (1.35, 0.75, 0.9), BODY)
    m.box("head", (0, 0.7, 4.95), (0.85, 0.55, 0.5), BODY)
    m.box("head", (0, 1.38, 1.6), (1.5, 0.2, 3.2), DARK)  # cresta superior
    m.box("head", (0, 1.25, 3.4), (1.1, 0.15, 1.4), DARK)
    m.box("head", (0, 1.45, 0.2), (0.5, 0.35, 0.9), DARK)
    # martillo lateral con los ojos al final
    for sx in (1, -1):
        m.box("head", (sx * 1.38, 0.78, 1.9), (0.7, 0.55, 1.1), BODY)
        m.box("head", (sx * 1.38, 1.07, 1.9), (0.72, 0.1, 1.1), DARK)
        m.box("head", (sx * 1.74, 0.8, 1.9), (0.1, 0.42, 0.42), EYE, emit=6, tag="eye")
        m.box("head", (sx * 1.79, 0.8, 1.9), (0.04, 0.34, 0.1), BLACK)
        m.box("head", (sx * 1.66, 1.12, 1.95), (0.32, 0.14, 0.7), DARK, r=(0, 0, sx * -12))  # ceja
        m.box("head", (sx * 0.5, 0.52, 4.75), (0.2, 0.1, 0.28), BLACK)  # orificios nasales
        # marcas rojas en la mejilla
        for i in range(3):
            m.box("head", (sx * 1.27, 0.35, 0.3 + i * 0.3), (0.06, 0.45 - i * 0.08, 0.08), GLOW, emit=3, tag="glow")
    # paladar, encías y dientes superiores
    m.box("head", (0, 0.08, 2.6), (1.85, 0.12, 3.6), MOUTH)
    for sx in (1, -1):
        m.box("head", (sx * 0.98, 0.05, 2.5), (0.14, 0.2, 3.3), GUM)
    m.box("head", (0, 0.05, 4.3), (1.4, 0.2, 0.14), GUM)
    for i in range(8):
        z = 1.1 + i * 0.4
        for sx in (1, -1):
            m.box("head", (sx * 0.92, -0.1, z), (0.2, 0.2, 0.12), TOOTH, r=(0, 0, 45))
            m.box("head", (sx * 0.62, -0.02, z + 0.2), (0.13, 0.13, 0.09), TOOTH, r=(0, 0, 45))
    for i in range(5):
        m.box("head", (-0.6 + i * 0.3, -0.1, 4.25), (0.2, 0.2, 0.12), TOOTH, r=(0, 0, 45))

    # mandíbula (abierta)
    m.part("jaw", "head", (0, 0.1, 0.8), (28, 0, 0))
    m.box("jaw", (0, -0.4, 1.6), (2.05, 0.55, 3.1), BODY)
    m.box("jaw", (0, -0.73, 1.5), (1.8, 0.15, 2.8), BELLY)
    m.box("jaw", (0, -0.35, 3.45), (1.45, 0.5, 0.8), BODY)
    m.box("jaw", (0, -0.65, 3.4), (1.2, 0.12, 0.7), BELLY)
    m.box("jaw", (0, -0.1, 1.7), (1.65, 0.1, 2.9), MOUTH)
    m.box("jaw", (0, -0.03, 1.6), (1.15, 0.12, 2.2), TONGUE)
    for sx in (1, -1):
        m.box("jaw", (sx * 0.93, -0.05, 1.9), (0.14, 0.18, 2.8), GUM)
    m.box("jaw", (0, -0.05, 3.7), (1.2, 0.18, 0.14), GUM)
    for i in range(7):
        z = 0.75 + i * 0.4
        for sx in (1, -1):
            m.box("jaw", (sx * 0.88, 0.1, z), (0.2, 0.2, 0.12), TOOTH, r=(0, 0, 45))
    for i in range(4):
        m.box("jaw", (-0.45 + i * 0.3, 0.1, 3.68), (0.2, 0.2, 0.12), TOOTH, r=(0, 0, 45))

    # ---------------- cola (4 segmentos + aleta caudal) ----------------
    segs = [(2.1, 2.0, 1.7, 8), (1.9, 1.55, 1.3, 4), (1.7, 1.1, 0.95, 2), (1.5, 0.7, 0.65, -6)]
    parent, pivot = "hips", (0, 0.25, -1.5)
    for k, (L, w, h, tilt) in enumerate(segs):
        name = f"tail{k + 1}"
        m.part(name, parent, pivot, (tilt, 0, 0))
        m.box(name, (0, 0, -L / 2), (w, h, L + 0.05), BODY)
        m.box(name, (0, -h / 2 + 0.06, -L / 2), (w * 0.8, 0.14, L), BELLY2)
        m.box(name, (0, h / 2, -L / 2), (w * 0.55, 0.12, L), DARK)
        for sx in (1, -1):
            m.box(name, (sx * w / 2, 0.05, -L / 2), (0.06, h * 0.25, L * 0.9), MID)
        # pinchos de sierra en la parte superior
        n = 3 if k < 2 else 2
        for i in range(n):
            sz = 0.34 - k * 0.05
            m.box(name, (0, h / 2 + 0.1, -0.3 - i * L / n), (0.2, sz, sz), DARK, r=(45, 0, 0))
        parent, pivot = name, (0, 0, -L)
    # segunda dorsal pequeña
    stepped_fin(m, "tail2", (0, 0.65, -0.5), 1.2, 0.9, 4, 0.5, 0.25, DARK)

    m.part("tailfin", "tail4", (0, 0, -1.45), (0, 0, 0))
    # aleta caudal maciza en media luna (lóbulo superior largo, inferior corto)
    for j in range(16):
        y = (j + 0.5) * 0.2
        u = y / 3.2
        front = 0.35 - 2.3 * u ** 1.2
        back = -0.55 - 1.35 * u ** 0.7
        if front - back < 0.15:
            front = back + 0.15
        m.box("tailfin", (0, y, (front + back) / 2), (0.36 - 0.18 * u, 0.22, front - back), DARK)
    for j in range(9):
        y = -(j + 0.5) * 0.2
        u = -y / 1.8
        front = 0.35 - 1.25 * u ** 1.2
        back = -0.55 - 0.9 * u ** 0.6
        if front - back < 0.15:
            front = back + 0.15
        m.box("tailfin", (0, y, (front + back) / 2), (0.36 - 0.18 * u, 0.22, front - back), DARK)
    m.box("tailfin", (0, 0, -0.1), (0.5, 0.7, 0.9), BODY)
    m.box("tailfin", (0, 1.2, -0.6), (0.4, 1.4, 0.08), MID, r=(-30, 0, 0))

    # ---------------- piernas ----------------
    for side, sx in (("L", 1), ("R", -1)):
        th, sh, mt, ft = f"thigh_{side}", f"shin_{side}", f"meta_{side}", f"foot_{side}"
        m.part(th, "hips", (sx * 1.35, -0.25, 0.1), (-25, 0, sx * 4))
        m.box(th, (0, -1.0, 0), (1.35, 2.3, 1.7), BODY)
        m.box(th, (sx * 0.7, -0.9, 0), (0.12, 1.7, 1.3), MID)
        m.box(th, (0, -1.0, 0.86), (0.9, 1.8, 0.1), BELLY2)
        m.part(sh, th, (0, -2.0, 0), (55, 0, 0))
        m.box(sh, (0, -1.0, 0), (0.95, 2.15, 1.05), BODY)
        m.box(sh, (0, -0.2, -0.55), (0.6, 0.6, 0.3), DARK)  # espolón de rodilla
        m.box(sh, (0, -1.0, 0.54), (0.6, 1.8, 0.08), BELLY2)
        m.part(mt, sh, (0, -2.0, 0), (-50, 0, 0))
        m.box(mt, (0, -0.65, 0), (0.75, 1.4, 0.75), BODY)
        m.box(mt, (0, -0.65, -0.4), (0.4, 1.0, 0.1), DARK)
        m.part(ft, mt, (0, -1.3, 0), (20, 0, -sx * 4))
        m.box(ft, (0, -0.15, 0.3), (1.25, 0.32, 1.25), BODY)
        m.box(ft, (0, 0.05, 0.1), (0.85, 0.2, 0.85), MID)
        for tx in (-0.42, 0, 0.42):
            m.box(ft, (tx, -0.17, 1.15), (0.34, 0.3, 0.75), BODY)
            m.box(ft, (tx, -0.2, 1.62), (0.2, 0.22, 0.3), CLAW)
            m.box(ft, (tx, -0.12, 1.82), (0.12, 0.12, 0.18), CLAW)
        m.box(ft, (0, -0.15, -0.45), (0.3, 0.26, 0.5), BODY)
        m.box(ft, (0, -0.18, -0.75), (0.16, 0.18, 0.2), CLAW)

    # ---------------- brazos ----------------
    arm_pose = {
        # (rot brazo rel. hombro, rot antebrazo); el derecho sujeta el arpón, el izquierdo amenaza
        "L": ((-75, 0, 20), (-45, 0, -15)),
        "R": ((-15, 0, -20), (-65, 0, 10)),
    }
    for side, sx in (("L", 1), ("R", -1)):
        sh, ua, fa, hd = f"shoulder_{side}", f"upperarm_{side}", f"forearm_{side}", f"hand_{side}"
        m.part(sh, "torso", (sx * 1.5, 2.85, 0.5))
        m.box(sh, (sx * 0.2, 0, 0), (0.9, 0.9, 1.0), MID)
        m.box(sh, (sx * 0.45, 0.05, 0), (0.12, 0.6, 0.7), GLOW, emit=3, tag="glow")
        ur, fr = arm_pose[side]
        m.part(ua, sh, (sx * 0.3, -0.1, 0), ur)
        m.box(ua, (0, -0.75, 0), (0.75, 1.6, 0.8), BODY)
        m.box(ua, (0, -0.75, 0.42), (0.5, 1.2, 0.06), BELLY2)
        m.part(fa, ua, (0, -1.5, 0), fr)
        m.box(fa, (0, -0.65, 0), (0.62, 1.4, 0.66), BODY)
        m.box(fa, (sx * 0.33, -0.6, 0), (0.06, 0.9, 0.3), GLOW, emit=3, tag="glow")
        m.part(hd, fa, (0, -1.4, 0))
        m.box(hd, (0, -0.2, 0), (0.6, 0.55, 0.62), BODY)
        for i in range(3):
            m.box(hd, (-0.2 + i * 0.2, -0.5, 0.25), (0.12, 0.2, 0.12), CLAW)

    # ---------------- arpón (en la mano derecha, inclinado hacia atrás y arriba) ----------------
    grip = m.to_local("torso", m.world_point("hand_R", (0, -0.25, 0)))
    up_back = Vector((-0.55, 0.62, -0.55)).normalized()  # dirección en el mundo hacia el extremo de las cuentas
    q = m.world_quat("torso").inverted() @ Vector((0, 1, 0)).rotation_difference(up_back)
    m.part("spear", "torso", tuple(grip), q)
    top, bottom = 5.2, -2.4
    L = top - bottom
    m.box("spear", (0, (top + bottom) / 2, 0), (0.18, L, 0.18), SHAFT)
    y = bottom + 0.4
    while y < top - 0.2:
        m.box("spear", (0, y, 0), (0.23, 0.12, 0.23), BAND)
        y += 0.55
    # punta de lanza escalonada con núcleo rojo
    m.box("spear", (0, bottom - 0.15, 0), (0.42, 0.3, 0.14), STEEL)
    m.box("spear", (0, bottom - 0.5, 0), (0.5, 0.45, 0.12), STEEL)
    m.box("spear", (0, bottom - 0.9, 0), (0.36, 0.4, 0.12), STEEL)
    m.box("spear", (0, bottom - 1.2, 0), (0.22, 0.3, 0.12), STEEL)
    m.box("spear", (0, bottom - 1.42, 0), (0.1, 0.2, 0.12), STEEL)
    m.box("spear", (0, bottom - 0.75, 0), (0.08, 1.0, 0.16), GLOW, emit=5, tag="glow")
    m.box("spear", (0, top, 0), (0.3, 0.3, 0.3), DARK)

    # cuentas rojas colgando del extremo superior
    sq = m.world_quat("spear")
    m.part("bead0", "spear", (0, top + 0.15, 0), sq.inverted() @ quat((-25, 0, 10)))
    m.box("bead0", (0, 0, 0), (0.2, 0.2, 0.2), GLOW, emit=4, tag="glow")
    for i in range(1, 12):
        m.part(f"bead{i}", f"bead{i - 1}", (0, -0.21, 0), (9, 0, 0))
        s = 0.2 - i * 0.008
        m.box(f"bead{i}", (0, 0, 0), (s, s, s), GLOW, emit=4, tag="glow")

    m.ground("hips")

    # ondas cuadradas brillantes en el suelo (como el anillo del vídeo)
    for k in range(2):
        r = f"ripple{k + 1}"
        m.part(r, "root", (0, 0.03, 0.4), (0, 45, 0))
        for i, half in enumerate((2.2, 3.2)):
            for (cx, cz, sx_, sz_) in [(0, half, 2 * half, 0.07), (0, -half, 2 * half, 0.07),
                                        (half, 0, 0.07, 2 * half), (-half, 0, 0.07, 2 * half)]:
                m.box(r, (cx, 0, cz), (sx_, 0.04, sz_), RIPPLE, emit=3, tag="ripple")

    # ---------------- animación: idle amenazante (3 s en bucle) ----------------
    tau = math.tau

    def animate(t):
        a = t * tau
        pose = {}
        breathe = math.sin(a * 2)
        pose["torso"] = {"r": quat((2.5 * breathe, 4 * math.sin(a), 1.5 * math.sin(a)))}
        pose["neck"] = {"r": quat((-2 * breathe, 0, 0))}
        pose["head"] = {"r": quat((3 * math.sin(a * 2 + 1), 10 * math.sin(a), 0))}
        # mordisco: dos chasquidos por bucle
        snap = max(0.0, math.sin(a * 2 - 0.6)) ** 6
        pose["jaw"] = {"r": quat((-24 * snap + 6 * breathe, 0, 0))}
        for k in range(4):
            pose[f"tail{k + 1}"] = {"r": quat((2 * math.sin(a * 2 - k), 7 * math.sin(a - k * 0.7), 0))}
        pose["tailfin"] = {"r": quat((0, 12 * math.sin(a - 3.2), 0))}
        pose["dorsal"] = {"r": quat((0, 0, 2 * math.sin(a - 1)))}
        for i in range(12):
            pose[f"bead{i}"] = {"r": quat((6 * math.sin(a * 2 - i * 0.5), 0, 10 * math.sin(a - i * 0.45)))}
        for k in range(2):
            ph = (t * 2 + k * 0.5) % 1.0
            sc = 0.6 + 0.8 * ph
            pose[f"ripple{k + 1}"] = {"s": (sc, 1, sc), "r": quat((0, 30 * ph, 0))}
        return pose

    def glow(t):
        a = t * tau
        return {"glow": 0.65 + 0.35 * math.sin(a * 2) ** 2, "eye": 0.8 + 0.2 * math.sin(a * 6),
                "ripple": 0.5 + 0.5 * math.cos(a * 2)}

    m.animate = animate
    m.glow = glow
    return m
