"""Buzón-monstruo (basado en la captura del buzón naranja), hecho solo de cubos.

Caja roja-naranja con ojos enfadados, puerta-mandíbula con dientes, lengua y
una carta en la boca, techo escalonado color crema, banderita lateral, ventana
con casita y un poste de piedra con ladrillos sobre una base rocosa.
"""

import math

from voxel import Model, quat

RED = "#e2552b"
RED_DARK = "#b93e1d"
ORANGE = "#f28a33"
ORANGE_LIGHT = "#ffb35a"
CREAM = "#f3ecd9"
CREAM_DARK = "#d9cfb6"
WHITE = "#ffffff"
BLACK = "#121212"
BROWN = "#3a2216"
MOUTH = "#2b0a08"
TOOTH = "#fbf6ea"
TONGUE = "#e0475a"
TONGUE_DARK = "#b32f43"
GOLD = "#f2c14e"
STONE = "#9aa0a7"
STONE_LIGHT = "#b9bec4"
STONE_DARK = "#6c7178"
PILLAR = "#c9cdd2"
GROOVE = "#8f949a"
WOOD = "#8a5a32"
WOOD_DARK = "#6a4224"
FLAG = "#ff6a1a"
ENVELOPE = "#fffaf0"
STAMP = "#2f7fd8"
GRASS = "#4fa23a"


def build():
    m = Model("mailbox", fps=24, frames=48)
    m.part("root")

    # ---------------- base de roca ----------------
    m.box("root", (0, 0.4, 0), (3.4, 0.8, 3.4), STONE)
    m.box("root", (0, 0.95, 0), (2.7, 0.35, 2.7), STONE_LIGHT)
    rocks = [
        ((1.85, 0.3, 1.2), (0.8, 0.6, 0.9), STONE_LIGHT, 12),
        ((-1.9, 0.25, 0.7), (0.7, 0.5, 1.0), STONE_DARK, -8),
        ((-1.2, 0.3, -1.9), (1.1, 0.6, 0.7), STONE_LIGHT, 20),
        ((1.4, 0.2, -1.85), (0.9, 0.4, 0.7), STONE, -15),
        ((0.3, 0.2, 2.0), (0.8, 0.4, 0.6), STONE_DARK, 30),
        ((2.3, 0.12, -0.6), (0.4, 0.24, 0.4), STONE_LIGHT, 40),
        ((-2.4, 0.1, -0.9), (0.35, 0.2, 0.35), STONE, 10),
    ]
    for c, s, col, ry in rocks:
        m.box("root", c, s, col, r=(0, ry, 0))
    # grietas
    for c, s in [((1.71, 0.45, 0.3), (0.02, 0.5, 0.06)), ((-0.6, 0.5, 1.71), (0.06, 0.45, 0.02)),
                 ((0.9, 0.3, 1.71), (0.5, 0.05, 0.02)), ((-1.71, 0.55, -0.4), (0.02, 0.05, 0.7))]:
        m.box("root", c, s, STONE_DARK)
    # matas de hierba alrededor
    for (x, z, h) in [(1.6, 1.9, 0.5), (-2.0, 1.6, 0.4), (2.1, -1.4, 0.45), (-1.7, -1.7, 0.35), (0, -2.2, 0.3)]:
        for i, dx in enumerate((-0.12, 0.0, 0.12)):
            m.box("root", (x + dx, h / 2 * (0.8 + 0.2 * i), z), (0.08, h * (0.8 + 0.2 * i), 0.08), GRASS, r=(0, 0, dx * 120))

    # ---------------- poste de piedra con ladrillos ----------------
    m.box("root", (0, 2.75, 0), (1.3, 3.3, 1.3), PILLAR)
    for i in range(7):
        y = 1.35 + i * 0.46
        m.box("root", (0, y, 0), (1.33, 0.05, 1.33), GROOVE)  # junta horizontal
        off = 0.33 if i % 2 else -0.33
        for (cx, cz, sx, sz) in [(off, 0.66, 0.04, 0.02), (0.66, off, 0.02, 0.04),
                                 (-off, -0.66, 0.04, 0.02), (-0.66, -off, 0.02, 0.04)]:
            m.box("root", (cx, y + 0.23, cz), (sx + (0.02 if sx < 0.03 else 0), 0.42, sz + (0.02 if sz < 0.03 else 0)), GROOVE)
    m.box("root", (0, 4.5, 0), (1.75, 0.3, 1.75), STONE_LIGHT)  # capitel
    m.box("root", (0, 4.3, 0), (1.5, 0.12, 1.5), STONE)
    # soporte de madera
    m.box("root", (0, 4.75, 0), (2.9, 0.22, 1.1), WOOD)
    m.box("root", (0, 4.75, 0.56), (2.9, 0.1, 0.04), WOOD_DARK)
    for sx in (1, -1):
        m.box("root", (sx * 1.25, 4.75, 0.58), (0.12, 0.12, 0.06), STONE_DARK)  # tornillos

    # ---------------- la caja (cabeza) ----------------
    m.part("body", "root", (0, 4.86, 0))
    W, H, D = 3.6, 3.2, 3.4
    MH = 1.65  # altura de la boca (hueco real en la parte baja del frente)
    m.box("body", (0, (H + MH) / 2, 0), (W, H - MH, D), RED)
    m.box("body", (0, MH / 2, -0.35), (W, MH, D - 0.7), RED)
    # marco: esquinas y bordes
    for sx in (1, -1):
        for sz in (1, -1):
            m.box("body", (sx * W / 2, H / 2, sz * D / 2), (0.32, H + 0.05, 0.32), ORANGE)
    for y in (0.08, H - 0.05):
        for sz in (1, -1):
            m.box("body", (0, y, sz * D / 2), (W + 0.1, 0.28, 0.3), ORANGE)
        for sx in (1, -1):
            m.box("body", (sx * W / 2, y, 0), (0.3, 0.28, D + 0.1), ORANGE)
    # paneles laterales hundidos (más oscuros) con ribete
    for sx in (1, -1):
        m.box("body", (sx * (W / 2 + 0.01), H / 2, 0), (0.04, H - 0.7, D - 0.7), RED_DARK)
        m.box("body", (sx * (W / 2 + 0.02), H / 2, 0), (0.04, 0.08, D - 0.7), ORANGE)
    # remaches
    for sx in (1, -1):
        for y in (0.45, H - 0.45):
            for z in (D / 2 - 0.55, -D / 2 + 0.55):
                m.box("body", (sx * (W / 2 + 0.05), y, z), (0.08, 0.12, 0.12), ORANGE_LIGHT)

    # ventana con casita (lateral derecho del personaje = -X)
    sx = -1
    m.box("body", (sx * (W / 2 + 0.06), 2.25, 0.55), (0.08, 1.3, 1.3), ORANGE_LIGHT)
    m.box("body", (sx * (W / 2 + 0.09), 2.25, 0.55), (0.06, 1.05, 1.05), CREAM)
    m.box("body", (sx * (W / 2 + 0.12), 2.08, 0.55), (0.04, 0.45, 0.5), RED)  # casa
    m.box("body", (sx * (W / 2 + 0.12), 1.98, 0.55), (0.05, 0.25, 0.14), BROWN)  # puerta
    for i, w in enumerate((0.7, 0.5, 0.3, 0.12)):
        m.box("body", (sx * (W / 2 + 0.12), 2.36 + i * 0.1, 0.55), (0.045, 0.1, w), RED_DARK)  # tejado escalonado

    # techo escalonado color crema (curva hecha de escalones)
    m.box("body", (0, H + 0.2, 0), (W + 0.4, 0.4, D + 0.4), CREAM)
    m.box("body", (0, H + 0.08, 0), (W + 0.45, 0.12, D + 0.45), CREAM_DARK)
    m.box("body", (0, H + 0.55, 0), (W - 0.1, 0.3, D + 0.2), CREAM)
    m.box("body", (0, H + 0.8, 0), (W - 0.9, 0.24, D + 0.1), CREAM)
    m.box("body", (0, H + 0.98, 0), (W - 1.8, 0.14, D), CREAM_DARK)
    for i in range(4):  # nervios del techo
        z = -D / 2 + 0.4 + i * (D - 0.8) / 3
        m.box("body", (0, H + 0.42, z), (W + 0.42, 0.06, 0.08), CREAM_DARK)
    m.box("body", (0, H + 1.12, -0.6), (0.5, 0.18, 0.5), ORANGE)  # tapón de la chimenea
    m.box("body", (0, H + 1.05, -0.6), (0.35, 0.2, 0.35), CREAM_DARK)

    # cara: placa frontal
    FZ = D / 2
    m.box("body", (0, 2.3, FZ + 0.02), (W - 0.6, 1.5, 0.04), RED_DARK)
    # ojos (parte propia para parpadear)
    for side, ex in (("L", 0.78), ("R", -0.78)):
        m.box("body", (ex, 2.35, FZ + 0.05), (1.18, 1.18, 0.06), BROWN)  # marco del ojo
        e = f"eye_{side}"
        m.part(e, "body", (ex, 2.35, FZ + 0.1))
        m.box(e, (0, 0, 0), (1.0, 1.0, 0.1), WHITE)
        px = -0.17 if ex > 0 else 0.17  # mirada hacia el centro (enfadado)
        m.box(e, (px, -0.12, 0.07), (0.42, 0.56, 0.06), BLACK)
        m.box(e, (px + 0.1, 0.04, 0.11), (0.13, 0.13, 0.03), WHITE)
        m.box(e, (px - 0.1, -0.28, 0.11), (0.06, 0.06, 0.03), WHITE)
        b = f"brow_{side}"
        m.part(b, "body", (ex, 3.03, FZ + 0.2), (0, 0, 16 if ex > 0 else -16))
        m.box(b, (0, 0, 0), (1.3, 0.32, 0.32), BROWN)
        m.box(b, (0, 0.12, 0.12), (1.2, 0.08, 0.1), "#5a3624")

    # boca: hueco real con paredes, techo, suelo y garganta
    MZ = FZ - 0.35
    m.box("body", (0, MH / 2 + 0.05, FZ - 0.69), (W - 0.4, MH - 0.1, 0.06), MOUTH)  # garganta
    m.box("body", (0, 0.13, MZ), (W - 0.4, 0.26, 0.7), "#4a1210")  # suelo
    m.box("body", (0, MH - 0.05, MZ), (W - 0.4, 0.1, 0.7), MOUTH)  # paladar
    for sxm in (1, -1):
        m.box("body", (sxm * (W / 2 - 0.12), MH / 2, MZ), (0.24, MH, 0.7), RED)  # mejillas
    m.box("body", (0, MH + 0.05, FZ + 0.1), (W - 0.3, 0.18, 0.22), ORANGE)  # labio superior
    # dientes superiores colgando hacia abajo dentro del hueco
    for i in range(6):
        x = -1.25 + i * 0.5
        m.box("body", (x, MH - 0.22, FZ - 0.12), (0.36, 0.32, 0.22), TOOTH)
        m.box("body", (x, MH - 0.45, FZ - 0.12), (0.18, 0.16, 0.2), TOOTH)  # punta hacia abajo

    # mandíbula inferior = puerta del buzón, con bisagra abajo; se abre hacia delante
    m.part("door", "body", (0, 0.12, FZ + 0.02), (72, 0, 0))
    m.box("door", (0, 0.72, 0.12), (W - 0.2, 1.44, 0.24), RED)
    m.box("door", (0, 0.72, -0.01), (W - 0.6, 1.2, 0.04), "#5a1410")  # cara interior
    m.box("door", (0, 1.42, 0.12), (W - 0.15, 0.14, 0.3), ORANGE)
    m.box("door", (0, 0.05, 0.12), (W - 0.15, 0.14, 0.3), ORANGE)
    for sxd in (1, -1):
        m.box("door", (sxd * (W / 2 - 0.12), 0.72, 0.12), (0.16, 1.45, 0.3), ORANGE)
    m.box("door", (0, 0.72, 0.27), (0.6, 0.22, 0.1), GOLD)  # pestillo
    m.box("door", (0, 0.72, 0.32), (0.22, 0.1, 0.06), "#b8862a")
    for i in range(5):  # dientes inferiores en el borde, mirando hacia dentro de la boca
        x = -1.0 + i * 0.5
        m.box("door", (x, 1.36, -0.12), (0.34, 0.26, 0.24), TOOTH)
        m.box("door", (x, 1.36, -0.32), (0.16, 0.14, 0.16), TOOTH)
    for sxd in (1, -1):  # bisagras
        m.box("door", (sxd * 1.2, 0.0, 0.05), (0.4, 0.18, 0.2), STONE_DARK)

    # lengua apoyada sobre la cara interior de la mandíbula (se mueve con ella)
    m.part("tongue", "door", (0, 0.3, -0.12), (0, 0, 0))
    m.box("tongue", (0, 0.42, -0.02), (1.5, 0.95, 0.14), TONGUE)
    m.box("tongue", (0, 0.95, -0.02), (1.15, 0.25, 0.13), TONGUE)
    m.box("tongue", (0, 0.5, -0.1), (0.08, 0.8, 0.04), TONGUE_DARK)

    # carta encima de la lengua
    m.part("letter", "tongue", (0.1, 0.45, -0.12), (0, 0, 14))
    m.box("letter", (0, 0, 0), (1.3, 0.85, 0.05), ENVELOPE)
    m.box("letter", (0.35, 0.18, -0.03), (0.3, 0.32, 0.03), STAMP)
    m.box("letter", (0.35, 0.18, -0.045), (0.18, 0.2, 0.02), WHITE)
    for sxf in (1, -1):  # solapa en V
        m.box("letter", (sxf * 0.3, -0.12, -0.03), (0.72, 0.05, 0.02), CREAM_DARK, r=(0, 0, sxf * 28))
    m.box("letter", (0, -0.28, -0.04), (0.14, 0.14, 0.03), "#d4372c")  # sello de lacre

    # banderita lateral (izquierda del personaje = +X)
    m.part("flag", "body", (W / 2 + 0.12, 1.4, -0.9), (0, 0, 0))
    m.box("flag", (0.1, 0.08, 0), (0.24, 0.24, 0.24), STONE_DARK)  # eje
    m.box("flag", (0.12, 1.0, 0), (0.14, 2.0, 0.16), ORANGE)  # mástil
    m.box("flag", (0.12, 1.65, -0.6), (0.12, 0.8, 1.1), FLAG)
    m.box("flag", (0.13, 1.65, -0.6), (0.12, 0.6, 0.9), ORANGE_LIGHT)
    m.box("flag", (0.14, 1.65, -0.6), (0.12, 0.42, 0.72), FLAG)
    m.box("flag", (0.12, 2.05, 0), (0.22, 0.12, 0.22), ORANGE_LIGHT)

    # ---------------- animación: mordiscos y rebote (2 s en bucle) ----------------
    tau = math.tau

    def animate(t):
        a = t * tau
        pose = {}
        chomp = max(0.0, math.sin(a * 2)) ** 8  # 0 = abierta (casi siempre), 1 = mordisco
        squash = math.sin(a * 2)
        pose["body"] = {
            "p": (0, 0.12 * max(0, -squash), 0),
            "s": (1 + 0.035 * squash, 1 - 0.05 * squash, 1 + 0.035 * squash),
            "r": quat((0, 6 * math.sin(a), 2 * math.sin(a * 2))),
        }
        pose["door"] = {"r": quat((-50 * chomp, 0, 0))}
        pose["tongue"] = {"r": quat((-4 * math.sin(a * 4), 3 * math.sin(a * 2), 0))}
        pose["letter"] = {"r": quat((0, 0, 4 * math.sin(a * 4 + 1)))}
        # parpadeo rápido hacia el final del bucle
        blink = max(0.0, 1 - abs(t - 0.78) / 0.05)
        for side in ("L", "R"):
            pose[f"eye_{side}"] = {"s": (1, 1 - 0.9 * blink, 1)}
            sgn = 1 if side == "L" else -1
            pose[f"brow_{side}"] = {"p": (0, 0.06 * chomp, 0), "r": quat((0, 0, sgn * 6 * chomp))}
        pose["flag"] = {"r": quat((-20 - 25 * math.sin(a * 2), 0, 0))}
        return pose

    m.animate = animate
    return m
