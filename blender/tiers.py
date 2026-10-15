"""Colección de 45 huevos para el juego, generados por rareza.

Rarezas (de menos a más): Común · Poco común · Raro · Épico · Mítico ·
Legendario · Secreto, más una serie especial Hacker (estilo Robux).

Cuanto más raro, más piezas (estructura, emblema, alas, corona, órbitas,
halo, flotantes), más animación y más VFX en el visor.
"""

import math

from mathutils import Vector

from eggs import _hash, _wing
from eggs_themes import (bolt, cloud, egg_scene, fbm, flame, flower, horn, leaf, membrane_wing,
                         mushroom, vnoise)
from voxel import crystal, egg_radius, egg_surface, polyline, quat, ring, segment, star

TAU = math.tau

RARITIES = {
    # id: (nombre, nivel, color de la etiqueta)
    "comun": ("Común", 0, "#9aa3ad"),
    "poco_comun": ("Poco común", 1, "#4cc26a"),
    "raro": ("Raro", 2, "#3d8bff"),
    "epico": ("Épico", 3, "#a35cff"),
    "mitico": ("Mítico", 4, "#ff4d6d"),
    "legendario": ("Legendario", 5, "#ffb627"),
    "secreto": ("Secreto", 6, "#f2f2f2"),
    "hacker": ("Hacker", 5, "#39ff88"),
}


def S(id, name, rarity, shell, accent, pattern, **kw):
    d = dict(id=id, name=name, rarity=rarity, shell=shell, accent=accent, pattern=pattern,
             dark=kw.pop("dark", None), energy=kw.pop("energy", accent), metal=kw.pop("metal", "#f2c14e"),
             base=kw.pop("base", "stone"), structure=kw.pop("structure", "band"), crown=kw.pop("crown", "gem"),
             wings=kw.pop("wings", "feather"), wing_cols=kw.pop("wing_cols", None), floater=kw.pop("floater", "star"),
             particles=kw.pop("particles", "sparkle"), bg=kw.pop("bg", None))
    d.update(kw)
    return d


# ----------------------------------------------------------------------------- catálogo
SPECS = [
    # ---------------- COMUNES (10): cáscara con patrón sencillo, peana simple, solo flotan
    S("comun_basico", "Huevo Básico", "comun", ["#f4efe6", "#ece4d6", "#e3d9c8"], "#9a6a44", "spots"),
    S("comun_hierba", "Huevo de Hierba", "comun", ["#7cc45a", "#6fb84f", "#86cf63"], "#4f8f34", "stripes", base="grass"),
    S("comun_arena", "Huevo de Arena", "comun", ["#ecd39a", "#e3c785", "#f2dcaa"], "#c9a25c", "spots", base="sand"),
    S("comun_piedra", "Huevo de Piedra", "comun", ["#9aa0a7", "#8a9097", "#a9afb5"], "#6c7178", "plain"),
    S("comun_barro", "Huevo de Barro", "comun", ["#8a5f3c", "#7d5534", "#966a45"], "#5e3d22", "spots", base="grass"),
    S("comun_cielo", "Huevo Cielo", "comun", ["#bfe3ff", "#aed9ff", "#d0ebff"], "#ffffff", "spots"),
    S("comun_melocoton", "Huevo Melocotón", "comun", ["#ffc9a8", "#ffbb94", "#ffd6bb"], "#ff9a6a", "stripes"),
    S("comun_lima", "Huevo Lima", "comun", ["#d6f26a", "#c8ea55", "#e1f784"], "#9cc43a", "zigzag"),
    S("comun_cacao", "Huevo de Cacao", "comun", ["#6b4429", "#5e3a22", "#7a4f31"], "#f0e2c8", "stripes"),
    S("comun_nube", "Huevo Nube", "comun", ["#ffffff", "#f2f6fb", "#e6edf6"], "#bcd3ea", "spots"),

    # ---------------- POCO COMUNES (8): + banda, peana de dos pisos, gira despacio
    S("pc_bosque", "Huevo del Bosque", "poco_comun", ["#3f7a3a", "#4a8a42", "#356a31"], "#a6d36a", "diag", base="grass", metal="#8a5a32"),
    S("pc_oceano", "Huevo Océano", "poco_comun", ["#2b7fd8", "#3a8ee6", "#2370c4"], "#bfe8ff", "zigzag", base="water", metal="#f2c14e"),
    S("pc_calabaza", "Huevo Calabaza", "poco_comun", ["#ff8a24", "#f57d17", "#ff9a3c"], "#c95e0c", "ribs", base="grass", metal="#3f7a2a", crown="leaf"),
    S("pc_brasa", "Huevo Brasa", "poco_comun", ["#3a2420", "#4a2c24", "#30201b"], "#ff6a1a", "crack", base="rock", metal="#55585f"),
    S("pc_escarcha", "Huevo Escarcha", "poco_comun", ["#d9f3ff", "#c8ecff", "#e8f8ff"], "#7fd6ff", "diag", base="ice", metal="#bfe8ff"),
    S("pc_miel", "Huevo de Miel", "poco_comun", ["#ffc23a", "#f5b320", "#ffcf5a"], "#c98a0a", "hex", base="grass", metal="#8a5a32"),
    S("pc_arcilla", "Huevo de Arcilla", "poco_comun", ["#c8714a", "#b9643f", "#d47f56"], "#f2e2c8", "zigzag", base="sand", metal="#7a4a2a"),
    S("pc_pradera", "Huevo Pradera", "poco_comun", ["#f6f1d8", "#efe8c6", "#fbf7e6"], "#ff9ac0", "flowers", base="grass", metal="#6fb84f"),

    # ---------------- RAROS (7): + emblema, corona, flota sobre base octogonal, destellos
    S("raro_coral", "Huevo de Coral", "raro", ["#ff7a8a", "#ff6a7c", "#ff8c9a"], "#ffd0d6", "spots", base="water", crown="crystals", energy="#6fe0ff", metal="#ffe0b0", floater="bubble"),
    S("raro_amatista", "Huevo Amatista", "raro", ["#8a5cd8", "#7a4cc8", "#9a6ce6"], "#e0c8ff", "facets", base="rock", crown="crystals", energy="#c89bff", metal="#d8d8e8"),
    S("raro_tigre", "Huevo Tigre", "raro", ["#ff9a2a", "#f58c1a", "#ffa83f"], "#1a1210", "tiger", base="grass", crown="ears", energy="#ffd27a", metal="#f2f2f2"),
    S("raro_panal", "Huevo Panal Real", "raro", ["#ffcf3a", "#ffc020", "#ffda5a"], "#a86a0a", "hex", base="grass", crown="crown", energy="#fff0a0", metal="#f2c14e"),
    S("raro_caramelo", "Huevo Caramelo", "raro", ["#ffffff", "#fff2f6", "#ffe6ee"], "#ff4d7a", "candy", base="candy", crown="gem", energy="#ff9ac0", metal="#7fe0c8"),
    S("raro_hongo", "Huevo Hongo", "raro", ["#e8423a", "#d93a33", "#f0524a"], "#ffffff", "spots", base="grass", crown="shroom", energy="#ffd27a", metal="#f2e8d0", spot_scale=1.3),
    S("raro_rubi", "Huevo Rubí", "raro", ["#c8143a", "#b00f32", "#dc2048"], "#ff8aa0", "facets", base="rock", crown="gem", energy="#ff5a7a", metal="#f2c14e"),

    # ---------------- ÉPICOS (6): + estructura, alas, órbita, anillos de suelo, partículas
    S("epico_dragon_fuego", "Dragón de Fuego", "epico", ["#b8261a", "#a01f15", "#c8301f"], "#ffb020", "scales", base="lava", structure="band",
      crown="horns", wings="bat", wing_cols=["#5c0f14", "#7a1a14", "#2b1612"], energy="#ff7a1a", metal="#3a3c42", particles="ember", floater="ember"),
    S("epico_rey_mar", "Rey del Mar", "epico", ["#1f6fb8", "#2a7fc8", "#1a60a8"], "#7fe8ff", "scales", base="water", structure="band",
      crown="crown", wings="fin", wing_cols=["#2fa8d8", "#5fc8f0", "#1a7fb8"], energy="#6fe0ff", metal="#f2c14e", particles="bubble", floater="bubble"),
    S("epico_bosque_encantado", "Bosque Encantado", "epico", ["#2f6a3a", "#3a7a42", "#285a31"], "#c6ff7a", "swirl", base="grass", structure="vines",
      crown="shroom", wings="leaf", wing_cols=["#4f9a35", "#6fb84a", "#2f6b22"], energy="#b6ff5a", metal="#6a4424", particles="firefly", floater="leafy"),
    S("epico_esmeralda", "Huevo Esmeralda", "epico", ["#14a35a", "#0f8f4e", "#1ab866"], "#b8ffd8", "facets", base="rock", structure="cage",
      crown="crystals", wings="crystal", wing_cols=["#5fe8a0", "#b8ffd8", "#2fc87a"], energy="#5fffb0", metal="#f2c14e", floater="crystal"),
    S("epico_mecanico", "Huevo Mecánico", "epico", ["#8a8f98", "#7a7f88", "#9aa0a8"], "#ffb020", "plates", base="tech", structure="rings",
      crown="antenna", wings="mech", wing_cols=["#5a5f68", "#c0c8d8", "#ffb020"], energy="#ffb020", metal="#c08a3a", particles="spark", floater="gear"),
    S("epico_unicornio", "Huevo Unicornio", "epico", ["#fff4fb", "#ffe8f6", "#f6e6ff"], "#ff9ad8", "rainbow", base="cloud", structure="band",
      crown="unihorn", wings="feather", wing_cols=["#ffd6f0", "#e6d6ff", "#c8f0ff"], energy="#ff9ad8", metal="#f2c14e", particles="sparkle", floater="star"),

    # ---------------- MÍTICOS (4): + halo/aura, haz de luz, flotantes, alas grandes
    S("mitico_fenix", "Fénix", "mitico", ["#ff5a1a", "#ff7a1a", "#e8401a"], "#ffe14a", "flamefeather", base="lava", structure="cage",
      crown="flames", wings="feather", wing_cols=["#ff8a1a", "#ffb020", "#ffe14a"], energy="#ffb020", metal="#f2c14e", particles="ember", floater="ember"),
    S("mitico_kraken", "Kraken", "mitico", ["#3a1f5a", "#46266a", "#2f184a"], "#ff6ad8", "suckers", base="water", structure="tentacles",
      crown="crystals", wings="fin", wing_cols=["#6a3a9a", "#8a5ac8", "#3a1f5a"], energy="#5ff4ff", metal="#c0c8d8", particles="bubble", floater="bubble"),
    S("mitico_dragon_glacial", "Dragón Glacial", "mitico", ["#8fd8ff", "#7fc8f0", "#a8e4ff"], "#ffffff", "scales", base="ice", structure="band",
      crown="horns", wings="crystal", wing_cols=["#bff3ff", "#8fe0ff", "#ffffff"], energy="#7fe8ff", metal="#e6f4ff", particles="snow", floater="crystal",
      horn_cols=("#dff6ff", "#7fe8ff")),
    S("mitico_golem_jade", "Gólem de Jade", "mitico", ["#3aa878", "#2f9868", "#46b888"], "#f2c14e", "runes", base="rock", structure="rings",
      crown="crown", wings="crystal", wing_cols=["#5fc89a", "#2f8a60", "#b8f0d0"], energy="#7fffc8", metal="#f2c14e", floater="crystal"),

    # ---------------- LEGENDARIOS (3): todo, como los huevos destacados
    S("leg_sol", "Sol Dorado", "legendario", ["#ffcf3a", "#ffc020", "#ffdc5a"], "#ff8a1a", "sunrays", base="pedestal", structure="cage",
      crown="sunburst", wings="feather", wing_cols=["#fff6d8", "#ffe7a8", "#ffd27a"], energy="#ffb020", metal="#f2c14e", particles="sparkle", floater="star"),
    S("leg_luna", "Luna de Plata", "legendario", ["#c8d0e0", "#b8c2d6", "#d8e0ee"], "#5a6a9a", "craters", base="pedestal", structure="cage",
      crown="moon", wings="feather", wing_cols=["#f0f4ff", "#d8e2f6", "#b8c8e6"], energy="#a8c8ff", metal="#e6ecf6", particles="sparkle", floater="star", bg="#0a1230"),
    S("leg_arcoiris", "Dragón Arcoíris", "legendario", ["#ff5a7a", "#ffb020", "#5ad8ff"], "#ffffff", "rainbow_scales", base="cloud", structure="cage",
      crown="horns", wings="feather", wing_cols=["#ff8ab0", "#ffd27a", "#8ae8ff"], energy="#ff9ad8", metal="#f2c14e", particles="sparkle", floater="star",
      horn_cols=("#fff6d8", "#ff9ad8")),

    # ---------------- SECRETOS (2): raros de verdad
    S("secreto_vacio", "Huevo del Vacío", "secreto", ["#0a0810", "#120e1c", "#06050a"], "#b06bff", "void", base="portal", structure="shards",
      crown="eye", wings="bat", wing_cols=["#1a1028", "#2a1640", "#0a0810"], energy="#b06bff", metal="#2a2a34", particles="void", floater="shard", bg="#000000"),
    S("secreto_prisma", "Huevo Prisma", "secreto", ["#f2f2ff", "#e6f0ff", "#fff0f8"], "#ffffff", "prism", base="portal", structure="cage",
      crown="crystals", wings="crystal", wing_cols=["#ff9ad8", "#9ae8ff", "#fff0a0"], energy="#ffffff", metal="#e6ecf6", particles="rainbow", floater="crystal", bg="#0a0a14"),

    # ---------------- HACKER (5): estilo hacker de Robux
    S("hacker_matrix", "Matrix", "hacker", ["#020604", "#04100a", "#010302"], "#39ff88", "code", base="tech", structure="circuit",
      crown="antenna", wings="mech", wing_cols=["#0a1a10", "#39ff88", "#062010"], energy="#39ff88", metal="#1a2a20", particles="binary", floater="binary", bg="#000a04"),
    S("hacker_robux", "Robux Hacker", "hacker", ["#0e3a22", "#124a2c", "#0a2c1a"], "#ffd23a", "hexgrid", base="tech", structure="circuit",
      crown="coin", wings="mech", wing_cols=["#0a2014", "#ffd23a", "#39ff88"], energy="#39ff88", metal="#f2c14e", particles="coin", floater="coin", bg="#021008"),
    S("hacker_glitch", "Error 404", "hacker", ["#14141c", "#1c1c28", "#0a0a10"], "#ff2bd6", "glitch", base="tech", structure="shards",
      crown="antenna", wings="mech", wing_cols=["#14141c", "#ff2bd6", "#2bf0ff"], energy="#2bf0ff", metal="#3a3a48", particles="glitch", floater="pixel", bg="#05030a"),
    S("hacker_terminal", "Terminal", "hacker", ["#1a1d22", "#22262c", "#15181c"], "#39ff88", "scanlines", base="keyboard", structure="cables",
      crown="antenna", wings="mech", wing_cols=["#22262c", "#39ff88", "#0a0c0e"], energy="#39ff88", metal="#3a3f48", particles="binary", floater="screen", bg="#020403"),
    S("hacker_firewall", "Firewall", "hacker", ["#1a0606", "#240909", "#120404"], "#ff3a2a", "circuit_red", base="tech", structure="circuit",
      crown="lock", wings="mech", wing_cols=["#1a0606", "#ff3a2a", "#ffb020"], energy="#ff3a2a", metal="#3a2a2a", particles="ember", floater="shield", bg="#0a0202"),
]


# ----------------------------------------------------------------------------- cáscara
def make_shell_fn(sp, L):
    c1, c2, c3 = sp["shell"]
    acc, en = sp["accent"], sp["energy"]
    dark = sp["dark"] or "#000000"
    pat = sp["pattern"]
    tw = 0.0 if L < 2 else 0.006 * L

    def mix(p):
        return (c1, c2, c3)[int(_hash(p.x, p.y, p.z) * 97) % 3]

    def fn(p, n, t, ang):
        h = _hash(p.x, p.y, p.z)
        u = ang / TAU + 0.5  # 0..1 alrededor
        if tw and h > 1 - tw and pat not in ("code", "void"):
            return ("#ffffff", 2.0, "twinkle")
        if pat == "plain":
            return mix(p) if h > 0.12 else acc
        if pat == "spots":
            sc = 1.6 * sp.get("spot_scale", 1.0)
            return acc if vnoise(p.x * sc + 3, p.y * sc, p.z * sc - 2) > 0.64 else mix(p)
        if pat == "stripes":
            return acc if math.floor((p.y + 3) / 0.75) % 2 == 0 else mix(p)
        if pat == "zigzag":
            tri = abs((u * 10) % 2 - 1) * 0.45
            yy = (p.y - tri) % 1.3
            return acc if yy < 0.35 else mix(p)
        if pat == "diag":
            return acc if math.floor(u * 8 + p.y * 0.8) % 2 == 0 else mix(p)
        if pat == "ribs":
            return acc if (u * 10) % 1 < 0.14 else mix(p)
        if pat == "hex":
            cx, cy = u * 14, (p.y + 3) / 0.55
            cy2 = cy + (0.5 if math.floor(cx) % 2 else 0)
            fx, fy = cx % 1, cy2 % 1
            return acc if fx < 0.16 or fy < 0.16 else mix(p)
        if pat == "flowers":
            if vnoise(p.x * 2.2, p.y * 2.2, p.z * 2.2) > 0.7:
                return acc if h > 0.25 else "#ffe14a"
            return mix(p)
        if pat == "crack":
            if abs(fbm(p, 1.2, 2.0) - 0.5) < 0.03:
                return (acc, 2.5, "vein") if L >= 1 else acc
            return mix(p)
        if pat == "facets":
            k = math.floor(u * 9) + math.floor((p.y + 3) / 0.9) * 3
            return (c1, c2, c3, acc)[k % 4] if h > 0.08 else "#ffffff"
        if pat == "tiger":
            v = math.sin(u * TAU * 7 + vnoise(p.x * 1.5, p.y * 1.5, p.z * 1.5) * 4 + p.y * 0.8)
            return acc if v > 0.55 else ("#fff2e0" if t < 0.18 else mix(p))
        if pat == "candy":
            return acc if math.floor(u * 10 + p.y * 1.2) % 2 == 0 else mix(p)
        if pat == "scales":
            row = math.floor((p.y + 3) / 0.45)
            col = math.floor(u * 18 + (row % 2) * 0.5)
            fy = ((p.y + 3) / 0.45) % 1
            if fy < 0.22:
                return dark if sp["dark"] else "#2a1010" if L < 4 else (c3,)[0]
            return (c1, c2, c3)[(row + col) % 3] if not (t < 0.3 and p.z > 0) else acc
        if pat == "swirl":
            v = fbm(Vector((math.sin(ang + p.y * 0.6) * 2, p.y, math.cos(ang + p.y * 0.6) * 2)), 0.9, 4.0)
            if v > 0.62:
                return (acc, 1.5, "vein") if h > 0.6 else acc
            return mix(p)
        if pat == "plates":
            fx, fy = (u * 12) % 1, ((p.y + 3) / 0.8) % 1
            if fx < 0.1 or fy < 0.12:
                return "#5a5f68"
            if fx > 0.85 and fy > 0.8:
                return acc  # remache
            return mix(p)
        if pat == "rainbow":
            bands = ["#ff9ab8", "#ffd27a", "#fff3a0", "#a8f0b8", "#9ad8ff", "#c8a8ff"]
            if vnoise(p.x * 1.4, p.y * 1.4, p.z * 1.4) > 0.6:
                return bands[int((p.y + 3) / 0.8) % 6]
            return mix(p)
        if pat == "flamefeather":
            v = (p.y + 3) / 0.5 + math.sin(u * TAU * 8) * 0.5
            k = v % 1
            if k < 0.18:
                return ("#ffe14a", 2.0, "vein")
            return (c1, c2, c3)[int(v) % 3]
        if pat == "suckers":
            if p.z > 0.3 and vnoise(p.x * 2.5, p.y * 2.5, p.z * 2.5) > 0.68:
                return "#e8a8d8"
            if t < 0.25:
                return acc if h > 0.6 else c3
            return mix(p)
        if pat == "runes":
            fx, fy = (u * 8) % 1, ((p.y + 3) / 1.0) % 1
            if (abs(fx - 0.5) < 0.06 and 0.2 < fy < 0.8) or (abs(fy - 0.5) < 0.06 and 0.3 < fx < 0.7):
                return (sp["energy"], 2.0, "vein")
            return mix(p)
        if pat == "sunrays":
            if (u * 16) % 1 < 0.22 and t > 0.15:
                return acc
            return mix(p) if t > 0.15 else "#ff9a2a"
        if pat == "craters":
            v = vnoise(p.x * 1.8 + 7, p.y * 1.8, p.z * 1.8)
            if v > 0.66:
                return "#8a96b0"
            if v > 0.6:
                return "#e6ecf6"
            return mix(p)
        if pat == "rainbow_scales":
            bands = ["#ff5a7a", "#ff9a3a", "#ffd23a", "#5ae07a", "#5ad8ff", "#8a6aff"]
            row = math.floor((p.y + 3) / 0.45)
            fy = ((p.y + 3) / 0.45) % 1
            col = math.floor(u * 18 + (row % 2) * 0.5)
            if fy < 0.2:
                return "#ffffff"
            return bands[(row + col // 3) % 6]
        if pat == "void":
            if abs(fbm(p, 1.1, 9.0) - 0.5) < 0.025:
                return (en, 3.0, "vein")
            if h > 0.992:
                return ("#ffffff", 3.0, "twinkle")
            return mix(p)
        if pat == "prism":
            bands = ["#ffb8d8", "#ffe0a8", "#fff8c0", "#c8ffd8", "#b8ecff", "#d8c8ff"]
            k = int(u * 6 + (p.y + 3) * 0.6) % 6
            return (bands[k], 0.6, "nebula") if h > 0.3 else "#ffffff"
        if pat == "code":
            col = math.floor(u * 22)
            phase = _hash(col, 1.0)
            k = ((p.y + 3) / 0.2 + phase * 30) % 9
            if k < 3.2 and _hash(col, math.floor((p.y + 3) / 0.2)) > 0.25:
                return ("#39ff88" if k < 1 else "#1fae5a", 2.5 if k < 1 else 1.2, f"code{col % 4}")
            return mix(p)
        if pat == "hexgrid":
            cx, cy = u * 12, (p.y + 3) / 0.6
            cy2 = cy + (0.5 if math.floor(cx) % 2 else 0)
            fx, fy = cx % 1, cy2 % 1
            if fx < 0.14 or fy < 0.14:
                return ("#39ff88", 1.5, "vein")
            return acc if _hash(math.floor(cx), math.floor(cy2)) > 0.88 else mix(p)
        if pat == "glitch":
            band = math.floor((p.y + 3) / 0.4)
            r = _hash(band, math.floor(u * 6))
            if r > 0.86:
                return ("#ff2bd6", 1.5, "vein")
            if r > 0.72:
                return ("#2bf0ff", 1.5, "vein")
            return mix(p) if h > 0.1 else "#ffffff"
        if pat == "scanlines":
            if math.floor((p.y + 3) / 0.2) % 3 == 0:
                return ("#1fae5a", 0.6, "vein")
            return mix(p)
        if pat == "circuit_red":
            fx, fy = (u * 14) % 1, ((p.y + 3) / 0.6) % 1
            line = (fx < 0.1 and _hash(math.floor(u * 14), 2) > 0.4) or (fy < 0.12 and _hash(math.floor((p.y + 3) / 0.6), 3) > 0.5)
            if line:
                return (acc, 2.0, "vein")
            return mix(p)
        return mix(p)

    return fn


# ----------------------------------------------------------------------------- base
def build_base(m, sp, L):
    """Devuelve la altura de la parte superior de la base."""
    b = sp["base"]
    stone, stone2 = "#8a9097", "#a9afb5"
    if L <= 1:
        cols = {"grass": ("#5fae3a", "#4f9a35"), "sand": ("#e3c785", "#d4b46c"), "water": ("#9aa0a7", "#b9bec4"),
                "rock": ("#5a5f68", "#6c7178"), "ice": ("#cfeaf7", "#e6f7ff")}.get(b, (stone, stone2))
        m.box("root", (0, 0.2, 0), (2.8, 0.4, 2.8), cols[1])
        m.box("root", (0, 0.5, 0), (2.2, 0.2, 2.2), cols[0])
        top = 0.6
        if L == 1:
            m.box("root", (0, 0.2, 0), (2.8, 0.4, 2.8), cols[1], r=(0, 45, 0))
            ring(m, "root", 1.25, 20, (0.1, 0.08), sp["metal"], center=(0, 0.62, 0))
        for k in range(8):  # cuna que sujeta el huevo
            a = k / 8 * TAU
            m.box("root", (math.cos(a) * 0.85, top + 0.15, math.sin(a) * 0.85), (0.32, 0.3, 0.32), cols[0], r=(0, -math.degrees(a), 0))
        if b == "grass":
            for k in range(6):
                a = k / 6 * TAU + 0.3
                m.box("root", (math.cos(a) * 1.25, 0.55, math.sin(a) * 1.25), (0.08, 0.3, 0.08), "#4fa83a", r=(0, 0, 12 * math.sin(k)))
        return top
    # L >= 2: octógono y base temática
    pal = {
        "stone": ("#3a3f4a", "#4a505c"), "grass": ("#3f6a2f", "#4f7f3a"), "sand": ("#b8955a", "#cfae70"),
        "water": ("#1f4f7a", "#2a6090"), "rock": ("#2f2a34", "#3d3744"), "ice": ("#8fbcd8", "#a9cfe6"),
        "candy": ("#ff9ac0", "#ffd0e0"), "lava": ("#1c0c0b", "#261210"), "tech": ("#14181e", "#1e242c"),
        "cloud": ("#e6edf6", "#ffffff"), "pedestal": ("#1a2244", "#232e5c"), "portal": ("#0a0810", "#141020"),
        "keyboard": ("#1a1d22", "#22262c"),
    }
    c0, c1 = pal.get(b, pal["stone"])
    size = 3.2 + 0.35 * L
    m.box("root", (0, 0.2, 0), (size, 0.4, size), c0)
    m.box("root", (0, 0.2, 0), (size, 0.4, size), c0, r=(0, 45, 0))
    m.box("root", (0, 0.55, 0), (size * 0.72, 0.3, size * 0.72), c1, r=(0, 22.5, 0))
    top = 0.7
    en = sp["energy"]
    ring(m, "root", size * 0.42, 28, (0.08, 0.06), en, center=(0, 0.72, 0), emit=1.5 + 0.3 * L, tag="neon")
    for k in range(8):
        a = k / 8 * TAU + TAU / 16
        m.box("root", (math.cos(a) * size * 0.53, 0.42, math.sin(a) * size * 0.53), (0.28, 0.12, 0.28), sp["metal"],
              r=(0, -math.degrees(a), 0), metal=1)
    R2 = size * 0.62
    if b == "water" or b == "ice":
        col = "#2fb8f0" if b == "water" else "#bff3ff"
        for k in range(28):
            a = k / 28 * TAU
            m.box("root", (math.cos(a) * R2, 0.06, math.sin(a) * R2), (0.7, 0.1, 0.6), col, r=(0, -math.degrees(a), 0), emit=0.4, tag="water")
    elif b == "lava":
        for k in range(28):
            a = k / 28 * TAU
            m.box("root", (math.cos(a) * R2, 0.06, math.sin(a) * R2), (0.7, 0.1, 0.6), "#ff5a10" if k % 3 else "#ffa12a",
                  r=(0, -math.degrees(a), 0), emit=2, tag="vein")
    elif b == "grass":
        for k in range(14):
            a = k / 14 * TAU + 0.2
            r_ = R2 + 0.2 * _hash(k, 1)
            h = 0.4 + 0.5 * _hash(k, 2)
            m.box("root", (math.cos(a) * r_, h / 2, math.sin(a) * r_), (0.1, h, 0.1), "#5fae3a", r=(0, 0, 15 * math.sin(k)))
            if k % 3 == 0:
                flower(m, "root", (math.cos(a) * r_, h + 0.05, math.sin(a) * r_), 0.3, "#ff9ac0", "#ffe14a", rot=(-90, 0, 0))
    elif b == "rock" or b == "stone":
        for k in range(7):
            a = k / 7 * TAU + 0.4
            h = 0.6 + 0.9 * _hash(k, 7)
            m.box("root", (math.cos(a) * R2, h / 2, math.sin(a) * R2), (0.5, h, 0.5), c1, r=(10 * math.sin(k), math.degrees(a), 10 * math.cos(k)))
            if L >= 3:
                crystal(m, "root", (math.cos(a) * R2, h + 0.25, math.sin(a) * R2), 0.3, 0.6, en, emit=1.0, tag="neon")
    elif b == "candy":
        for k in range(8):
            a = k / 8 * TAU
            for j in range(4):
                m.box("root", (math.cos(a) * R2, 0.2 + j * 0.25, math.sin(a) * R2), (0.22, 0.25, 0.22), "#ff4d7a" if j % 2 else "#ffffff")
    elif b == "tech" or b == "keyboard":
        for k in range(16):
            a = k / 16 * TAU
            m.box("root", (math.cos(a) * R2, 0.08, math.sin(a) * R2), (0.5, 0.12, 0.35), c1 if k % 2 else "#2a3038",
                  r=(0, -math.degrees(a), 0))
            if k % 2 == 0:
                m.box("root", (math.cos(a) * R2, 0.15, math.sin(a) * R2), (0.3, 0.04, 0.12), en, r=(0, -math.degrees(a), 0), emit=2, tag="neon")
        if b == "keyboard":
            for ix in range(-3, 4):
                for iz in range(-1, 2):
                    m.box("root", (ix * 0.55, 0.95 + 0.0, iz * 0.55 + 0.0), (0.45, 0.18, 0.45), "#2a2f36")
            top = 1.05
    elif b == "cloud":
        for k in range(6):
            a = k / 6 * TAU
            cloud(m, "root", (math.cos(a) * R2, 0.35, math.sin(a) * R2), 0.55, "#ffffff", "#e6edf6")
    elif b == "portal":
        for i in range(3):
            ring(m, "root", R2 - i * 0.45, 40, (0.12, 0.06), en, center=(0, 0.06 + i * 0.02, 0), emit=2.5, tag="neon")
    elif b == "pedestal":
        for k in range(8):
            a = k / 8 * TAU + TAU / 16
            m.box("root", (math.cos(a) * R2, 0.5, math.sin(a) * R2), (0.35, 1.0, 0.35), sp["metal"], metal=1)
            m.box("root", (math.cos(a) * R2, 1.05, math.sin(a) * R2), (0.25, 0.25, 0.25), en, r=(0, 45, 45), emit=2, tag="neon")
    elif b == "sand":
        for k in range(10):
            a = k / 10 * TAU
            m.box("root", (math.cos(a) * R2, 0.1, math.sin(a) * R2), (0.8, 0.2, 0.6), "#e3c785", r=(0, -math.degrees(a), 0))
    if L >= 3:
        m.part("floor_rings", "root", (0, 0.04, 0))
        ring(m, "floor_rings", size * 0.85, 56, (0.08, 0.04), en, emit=1.5 + 0.3 * L, tag="neon")
        if L >= 4:
            ring(m, "floor_rings", size * 0.95, 64, (0.05, 0.04), en, emit=1.5, tag="neon")
    return top


# ----------------------------------------------------------------------------- piezas
def build_structure(m, sp, L, R, HB, HT):
    st = sp["structure"]
    metal, en = sp["metal"], sp["energy"]
    if L >= 1 and st in ("band", "cage", "rings", "vines", "tentacles", "circuit", "cables", "shards") or (L >= 1):
        y = 0.1
        ring(m, "egg", egg_radius(y, R, HB, HT) + 0.12, 36 + 4 * L, (0.2, 0.14), metal, center=(0, y, 0), metal=1)
        if L >= 2:
            for k in range(8):
                a = k / 8 * TAU
                p = egg_surface(R, HB, HT, y, a, 0.26)
                m.box("egg", p, (0.16, 0.16, 0.16), en if L >= 3 else metal, r=(0, math.degrees(a) + 45, 45),
                      emit=1.5 if L >= 3 else 0, tag="core" if L >= 3 else None, metal=0 if L >= 3 else 1)
    if L < 3:
        return
    if st == "cage":
        n = 6 if L < 5 else 8
        y0, y1 = -HB + 0.4, HT - 0.5
        for sgn in (1, -1):
            for k in range(n):
                pts = [egg_surface(R, HB, HT, y0 + (y1 - y0) * u, k / n * TAU + sgn * u * TAU / 4, 0.13) for u in (i / 22 for i in range(23))]
                polyline(m, "egg", pts, 0.12, metal, metal=1)
        for y in (y0, y1):
            ring(m, "egg", egg_radius(y, R, HB, HT) + 0.15, 32, (0.18, 0.12), metal, center=(0, y, 0), metal=1)
    elif st == "rings":
        for y in (-1.2, 1.2, 2.1):
            ring(m, "egg", egg_radius(y, R, HB, HT) + 0.12, 32, (0.16, 0.12), metal, center=(0, y, 0), metal=1)
            for k in range(6):
                a = k / 6 * TAU + y
                m.box("egg", egg_surface(R, HB, HT, y, a, 0.24), (0.14, 0.14, 0.14), en, emit=1.5, tag="core")
    elif st == "vines":
        for k in range(3):
            pts = [egg_surface(R, HB, HT, -HB + 0.4 + u * (HB + HT - 0.9), k / 3 * TAU + u * TAU * 1.1, 0.1) for u in (i / 30 for i in range(31))]
            polyline(m, "egg", pts, 0.14, "#2f5f24")
            for i in range(2, 29, 4):
                p = pts[i]
                m.box("egg", p * 1.05, (0.34, 0.14, 0.22), "#5fae3a", r=(0, math.degrees(math.atan2(p.x, p.z)), 30))
    elif st == "tentacles":
        for k in range(6):
            a = k / 6 * TAU + 0.3
            base = egg_surface(R, HB, HT, -1.3, a, -0.1)
            out = Vector((math.sin(a), -0.6, math.cos(a)))
            horn(m, "egg", base, out, 3.2, 0.5, 18, sp["shell"][0], sp["accent"], steps=11, tip_emit=1.5, tag="core")
    elif st in ("circuit", "cables"):
        for k in range(10 if L >= 5 else 6):
            a = k / 10 * TAU
            pts = []
            y = -HB + 0.5
            ang = a
            for i in range(10):
                pts.append(egg_surface(R, HB, HT, y, ang, 0.1))
                if i % 2 == 0:
                    y += 0.5
                else:
                    ang += 0.25 * (1 if _hash(k, i) > 0.5 else -1)
            polyline(m, "egg", pts, 0.09 if st == "circuit" else 0.16, en if st == "circuit" else "#0a0c0e",
                     emit=2.0 if st == "circuit" else 0, tag="vein" if st == "circuit" else None)
            m.box("egg", pts[-1] * 1.04, (0.2, 0.2, 0.2), en, emit=3, tag="core")
    elif st == "shards":
        m.part("shardring", "egg", (0, 0.2, 0), (12, 0, 8))
        for k in range(10):
            a = k / 10 * TAU
            crystal(m, "shardring", (math.cos(a) * 2.9, 0.3 * math.sin(k * 2), math.sin(a) * 2.9), 0.35, 0.9, sp["accent"] if k % 2 else en,
                    rot=(30 * k, 0, 20), emit=1.2, tag="core")


def build_emblem(m, sp, L, R, HB, HT):
    if L < 2:
        return
    en, metal = sp["energy"], sp["metal"]
    y = 0.35
    zf = egg_radius(y, R, HB, HT) + 0.12
    m.part("emblem", "egg", (0, y, zf))
    W, H = 0.9 + 0.08 * L, 1.3 + 0.1 * L
    pat = sp["pattern"]
    if pat in ("hexgrid",):  # moneda hexagonal
        hexa = [(math.sin(k / 6 * TAU) * 0.8, math.cos(k / 6 * TAU) * 0.8, 0) for k in range(6)]
        polyline(m, "emblem", hexa, (0.2, 0.2), metal, closed=True, metal=1)
        for j in range(7):
            k = (j + 0.5) / 7 * 2 - 1
            m.box("emblem", (0, k * 0.6, 0.02), (1.25 * (1 - abs(k) * 0.5), 0.18, 0.1), "#ffd23a", emit=1.5, tag="core")
        polyline(m, "emblem", [(-0.25, -0.4, 0.1), (-0.25, 0.4, 0.1), (0.2, 0.4, 0.1), (0.25, 0.1, 0.1), (-0.2, 0.0, 0.1), (0.25, -0.4, 0.1)],
                 0.1, "#0a2c1a")
        return
    if pat == "scanlines":  # pantalla de terminal
        m.box("emblem", (0, 0, 0), (1.6, 1.2, 0.12), "#050806")
        polyline(m, "emblem", [(-0.85, 0.65, 0.05), (0.85, 0.65, 0.05), (0.85, -0.65, 0.05), (-0.85, -0.65, 0.05)], 0.1, sp["metal"], closed=True)
        for i in range(5):
            w = 0.4 + 0.9 * _hash(i, 4)
            m.box("emblem", (-0.65 + w / 2, 0.42 - i * 0.2, 0.08), (w, 0.08, 0.04), "#39ff88", emit=2, tag="core")
        m.box("emblem", (-0.55, -0.48, 0.08), (0.14, 0.12, 0.04), "#39ff88", emit=3, tag="cursor")
        return
    if sp["crown"] == "lock" or pat == "circuit_red":  # señal de peligro
        tri = [(0, 0.75, 0), (0.7, -0.5, 0), (-0.7, -0.5, 0)]
        polyline(m, "emblem", tri, (0.18, 0.18), "#ffb020", closed=True, emit=1.5, tag="core")
        m.box("emblem", (0, 0.05, 0.05), (0.14, 0.5, 0.08), "#ffb020", emit=2, tag="core")
        m.box("emblem", (0, -0.3, 0.05), (0.14, 0.14, 0.08), "#ffb020", emit=2, tag="core")
        return
    polyline(m, "emblem", [(0, H / 2, 0), (W / 2, 0, 0), (0, -H / 2, 0), (-W / 2, 0, 0)], (0.16, 0.16), metal, closed=True, metal=1)
    n = 7
    for j in range(n):
        k = (j + 0.5) / n * 2 - 1
        m.box("emblem", (0, k * (H - 0.25) / 2, 0.02), ((W - 0.25) * (1 - abs(k)) + 0.04, (H - 0.25) / n + 0.01, 0.1), en,
              emit=0.8 + 0.25 * L, tag="core")
    if L >= 4:
        polyline(m, "emblem", [(0, H / 2 + 0.22, -0.04), (W / 2 + 0.18, 0, -0.04), (0, -H / 2 - 0.22, -0.04), (-W / 2 - 0.18, 0, -0.04)],
                 (0.07, 0.07), metal, closed=True, metal=1)


def build_crown(m, sp, L, R, HB, HT):
    if L < 2:
        if sp["crown"] == "leaf":
            leaf(m, "egg", (0, HT - 0.1, 0), 70, 0.9, 0.45, "#5fae3a", "#3f7d2a", sx=1)
            leaf(m, "egg", (0, HT - 0.1, 0), 70, 0.8, 0.4, "#5fae3a", "#3f7d2a", sx=-1)
            segment(m, "egg", (0, HT - 0.2, 0), (0, HT + 0.25, 0), 0.18, "#4f7a2a")
        return
    ct = sp["crown"]
    en, metal = sp["energy"], sp["metal"]
    m.part("crown", "egg", (0, HT - 0.15, 0))
    if ct == "gem" or (ct not in ("crystals", "horns", "ears", "flames", "shroom", "crown", "antenna", "unihorn", "sunburst", "moon", "eye", "coin", "lock", "leaf")):
        for k in range(8):
            a = k / 8 * TAU
            m.box("crown", (math.sin(a) * 0.45, 0.05, math.cos(a) * 0.45), (0.22, 0.22, 0.22), metal, r=(0, math.degrees(a), 0), metal=1)
        crystal(m, "crown", (0, 0.75, 0), 0.6, 1.1, en, emit=1.2, tag="core")
    elif ct == "crystals":
        crystal(m, "crown", (0, 0.8, 0), 0.55, 1.5, en, emit=1.2, tag="core")
        for k in range(5):
            a = k / 5 * TAU
            crystal(m, "crown", (math.sin(a) * 0.5, 0.45, math.cos(a) * 0.5), 0.35, 0.9, sp["accent"] if k % 2 else en,
                    rot=(math.cos(a) * 25, 0, -math.sin(a) * 25), emit=0.9, tag="core")
    elif ct == "horns":
        hc = sp.get("horn_cols", ("#3b2620", en))
        for sx in (1, -1):
            horn(m, "crown", (sx * 0.7, -0.4, 0.2), (sx, 0.5, 0.15), 2.2 + 0.2 * (L - 3), 0.45, 15, hc[0], hc[1], tip_emit=1.5, tag="core")
    elif ct == "ears":
        for sx in (1, -1):
            for j in range(4):
                w = 0.6 - j * 0.14
                m.box("crown", (sx * 0.65, -0.1 + j * 0.2, 0.1), (w, 0.22, 0.3), sp["shell"][0] if j < 3 else "#1a1210")
            m.box("crown", (sx * 0.65, 0.1, 0.27), (0.28, 0.35, 0.06), "#ffb8c8")
    elif ct == "flames":
        for i in range(5):
            a = i / 5 * TAU
            n = f"flame{i}"
            m.part(n, "crown", (0 if i == 0 else math.sin(a) * 0.5, 0, 0 if i == 0 else math.cos(a) * 0.5))
            flame(m, n, (0, 0, 0), 1.5 if i == 0 else 1.0, 0.6 if i == 0 else 0.4, seed=i)
    elif ct == "shroom":
        mushroom(m, "crown", (0, -0.1, 0), 0.6, 0.5, sp["shell"][0] if sp["pattern"] == "spots" else "#4ff0c0", "#ffffff", emit=0.8 if L >= 3 else 0,
                 tag="core" if L >= 3 else None)
        mushroom(m, "crown", (0.5, -0.2, 0.2), 0.35, 0.3, "#b06bff", "#ffffff", emit=0.8 if L >= 3 else 0, tag="core" if L >= 3 else None)
    elif ct == "crown":
        ring(m, "crown", 0.62, 16, (0.2, 0.3), metal, center=(0, 0.1, 0), metal=1)
        for k in range(6):
            a = k / 6 * TAU
            m.box("crown", (math.sin(a) * 0.62, 0.45, math.cos(a) * 0.62), (0.18, 0.5, 0.18), metal, metal=1)
            m.box("crown", (math.sin(a) * 0.62, 0.75, math.cos(a) * 0.62), (0.2, 0.2, 0.2), en, r=(45, 0, 45), emit=1.5, tag="core")
    elif ct == "antenna":
        segment(m, "crown", (0, -0.1, 0), (0, 1.2, 0), 0.12, sp["metal"])
        segment(m, "crown", (0, 0.6, 0), (0.4, 0.95, 0), 0.08, sp["metal"])
        m.box("crown", (0, 1.3, 0), (0.28, 0.28, 0.28), en, emit=3, tag="cursor")
        m.box("crown", (0.42, 1.0, 0), (0.16, 0.16, 0.16), en, emit=3, tag="cursor")
    elif ct == "unihorn":
        for j in range(8):
            w = 0.42 * (1 - j / 8) + 0.06
            m.box("crown", (0, 0.1 + j * 0.24, 0.1 + j * 0.04), (w, 0.26, w), "#f2c14e" if j % 2 else "#ffe9a8", r=(0, 30 * j, 0), metal=1)
    elif ct == "sunburst":
        crystal(m, "crown", (0, 0.8, 0), 0.7, 1.3, "#fff0a0", emit=1.5, tag="core")
        for k in range(12):
            a = k / 12 * TAU
            segment(m, "crown", (math.sin(a) * 0.5, 0.8 + math.cos(a) * 0.5, 0), (math.sin(a) * 1.3, 0.8 + math.cos(a) * 1.3, 0), 0.14, metal, metal=1)
    elif ct == "moon":
        for k in range(14):
            a = -0.9 + k / 13 * 1.8 * math.pi * 0.62
            r_ = 0.7
            w = 0.32 * math.sin((k + 0.5) / 14 * math.pi) + 0.06
            m.box("crown", (math.cos(a + 1.1) * r_, 1.0 + math.sin(a + 1.1) * r_, 0), (w, w, 0.22), "#e6ecf6", emit=0.8, tag="core")
    elif ct == "eye":
        m.box("crown", (0, 0.6, 0), (1.0, 0.6, 0.3), "#1a1028")
        m.box("crown", (0, 0.6, 0.12), (0.7, 0.4, 0.12), en, emit=2.5, tag="core")
        m.box("crown", (0, 0.6, 0.2), (0.12, 0.38, 0.06), "#000000")
    elif ct == "coin":
        m.part("coin", "crown", (0, 1.0, 0))
        hexa = [(math.sin(k / 6 * TAU) * 0.55, math.cos(k / 6 * TAU) * 0.55, 0) for k in range(6)]
        polyline(m, "coin", hexa, (0.18, 0.22), metal, closed=True, metal=1)
        m.box("coin", (0, 0, 0), (0.6, 0.6, 0.16), "#ffd23a", r=(0, 0, 30), emit=1.2, tag="core")
    elif ct == "lock":
        m.box("crown", (0, 0.45, 0), (0.8, 0.65, 0.4), "#3a2a2a", metal=1)
        polyline(m, "crown", [(-0.25, 0.75, 0), (-0.25, 1.1, 0), (0.25, 1.1, 0), (0.25, 0.75, 0)], 0.12, "#c0c8d8", metal=1)
        m.box("crown", (0, 0.45, 0.21), (0.16, 0.25, 0.04), "#ff3a2a", emit=3, tag="core")


def build_wings(m, sp, L):
    if L < 3:
        return
    wt = sp["wings"]
    cols = sp["wing_cols"] or ["#f4fbff", "#e4f5ff", "#c4ecff"]
    big = L - 3  # 0..3
    for side, sx in (("L", 1), ("R", -1)):
        w = f"wing_{side}"
        m.part(w, "egg", (sx * 1.55, 0.6, -0.8), (0, sx * -22, sx * 6))
        if wt == "feather":
            rows = [(8 + 2 * big, 1.4 + 0.25 * big, 2.4 + 0.4 * big, 0.66, -0.14, cols)]
            if big >= 1:
                rows.append((7 + big, 0.9, 1.6 + 0.2 * big, 0.62, 0.0, [cols[1], cols[1], cols[2]]))
            if big >= 2:
                rows.append((6, 0.5, 1.0, 0.6, 0.12, ["#ffffff", cols[0], cols[1]]))
            bone = [(0, 0), (0.7, 0.55), (1.4, 1.3), (1.9 + 0.2 * big, 2.0 + 0.25 * big)]
            _wing(m, w, sx, rows, bone, sp["metal"], sp["metal"])
        elif wt == "bat":
            sc = 0.75 + 0.1 * big
            tips = [(1.2 * sc, 2.4 * sc), (2.6 * sc, 2.3 * sc), (3.4 * sc, 1.1 * sc), (3.2 * sc, -0.3 * sc), (2.2 * sc, -1.0 * sc)]
            membrane_wing(m, w, sx, (1.2 * sc, 1.4 * sc), tips, cols[2], cols[0], cols[1])
        elif wt == "leaf":
            for i in range(5 + big):
                k = i / (4 + big)
                leaf(m, w, (0, 0, 0), -20 + k * 100, 1.5 + 1.0 * math.sin(k * math.pi * 0.85 + 0.25), 0.75, cols[i % 2], cols[2], sx=sx, z=-0.1 * (i % 2))
        elif wt == "crystal":
            for i in range(6 + 2 * big):
                k = i / (5 + 2 * big)
                th = math.radians(-30 + k * 120)
                Lw = 1.3 + (1.1 + 0.3 * big) * math.sin(k * math.pi * 0.85 + 0.25)
                d = Vector((sx * math.cos(th), math.sin(th), 0))
                rot = (0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th))
                crystal(m, w, d * (0.3 + Lw / 2), 0.55, Lw, cols[i % 3], rot=rot, emit=0.6, tag="core")
        elif wt == "fin":
            for i in range(3 + big):
                k = i / (2 + big)
                ang = -20 + k * 90
                Lf = 1.6 + 0.8 * math.sin(k * math.pi)
                leaf(m, w, (0, 0, 0), ang, Lf, 0.9, cols[i % 2], cols[2], sx=sx, steps=7)
            for i in range(4):
                segment(m, w, (0, 0, 0.08), (sx * (1.2 + 0.4 * i) * math.cos(math.radians(-10 + i * 25)), (1.2 + 0.4 * i) * math.sin(math.radians(-10 + i * 25)), 0.08), 0.06, cols[2])
        elif wt == "mech":
            for i in range(4 + big):
                k = i / (3 + big)
                th = math.radians(-20 + k * 100)
                Lm = 1.5 + 1.0 * math.sin(k * math.pi * 0.85 + 0.25)
                d = Vector((sx * math.cos(th), math.sin(th), 0))
                rot = (0, 0, math.degrees(th) - 90 if sx > 0 else 90 - math.degrees(th))
                m.box(w, d * (0.3 + Lm / 2), (0.42, Lm, 0.1), cols[0], r=rot)
                m.box(w, d * (0.3 + Lm / 2) + Vector((0, 0, 0.06)), (0.08, Lm * 0.9, 0.04), cols[1], r=rot, emit=2, tag="vein")
                m.box(w, d * (0.4 + Lm), (0.2, 0.2, 0.14), cols[2], r=rot, emit=2.5, tag="core")
        m.box(w, (0, 0, 0), (0.45, 0.45, 0.45), sp["metal"], r=(0, 0, 45), metal=1)


def build_orbits(m, sp, L):
    if L < 3:
        return
    en = sp["energy"]
    m.part("orbit1", "egg", (0, 0.2, 0), (72, 0, 18))
    ring(m, "orbit1", 3.0 + 0.1 * L, 64, (0.07, 0.07), en, emit=2.0 + 0.4 * L, tag="neon")
    for i in range(3):
        m.box("orbit1", (3.0 + 0.1 * L, 0, -0.18 * i), (0.26 - i * 0.06, 0.26 - i * 0.06, 0.22), "#ffffff", emit=3 - i, tag="neon")
    if L >= 5:
        m.part("orbit2", "egg", (0, 0.4, 0), (-62, 0, -28))
        ring(m, "orbit2", 2.8, 60, (0.06, 0.06), sp["accent"] if sp["accent"] != "#ffffff" else en, emit=3, tag="neon")
    if L >= 5:
        m.part("halo", "egg", (0, 2.85 + 2.0, 0), (8, 0, 0))
        ring(m, "halo", 1.0, 30, (0.22, 0.18), sp["metal"], metal=1)
        ring(m, "halo", 1.0, 30, (0.08, 0.22), en, emit=1.2, tag="core")


def build_floaters(m, sp, L, CY):
    if L < 4:
        return
    ft = sp["floater"]
    n = 3 + L
    for i in range(n):
        a = i / n * TAU
        r_ = 3.8 + 0.4 * (i % 2)
        name = f"float{i}"
        m.part(name, "root", (math.cos(a) * r_, CY - 1.5 + 3.2 * _hash(i, 3), math.sin(a) * r_), (15 * i, 25 * i, 10))
        en = sp["energy"]
        if ft == "star":
            star(m, name, (0, 0, 0), 0.45, "#ffffff", emit=3, tag="twinkle")
        elif ft in ("crystal", "shard"):
            crystal(m, name, (0, 0, 0), 0.32, 0.75, en if i % 2 else sp["accent"], emit=1.2, tag="core")
        elif ft == "bubble":
            m.box(name, (0, 0, 0), (0.3, 0.3, 0.3), "#bfefff", emit=0.8, tag="core")
            m.box(name, (0.06, 0.06, 0.12), (0.1, 0.1, 0.1), "#ffffff", emit=2, tag="core")
        elif ft == "ember":
            flame(m, name, (0, -0.3, 0), 0.6, 0.25, seed=i)
        elif ft == "leafy":
            leaf(m, name, (0, 0, 0), 60, 0.6, 0.35, "#7fc24a", "#3f7d2a")
        elif ft == "gear":
            ring(m, name, 0.3, 8, (0.12, 0.1), sp["metal"], metal=1)
            for k in range(8):
                aa = k / 8 * TAU
                m.box(name, (math.cos(aa) * 0.42, 0, math.sin(aa) * 0.42), (0.12, 0.1, 0.12), sp["metal"], r=(0, -math.degrees(aa), 0), metal=1)
        elif ft in ("binary", "pixel"):
            for k in range(3):
                m.box(name, (0, k * 0.28, 0), (0.22, 0.22, 0.22), en if (i + k) % 2 else "#0a2014", emit=0.8 if (i + k) % 2 else 0, tag="core")
        elif ft == "coin":
            hexa = [(math.sin(k / 6 * TAU) * 0.3, math.cos(k / 6 * TAU) * 0.3, 0) for k in range(6)]
            polyline(m, name, hexa, (0.1, 0.14), sp["metal"], closed=True, metal=1)
            m.box(name, (0, 0, 0), (0.32, 0.32, 0.1), "#ffd23a", r=(0, 0, 30), emit=1, tag="core")
        elif ft == "screen":
            m.box(name, (0, 0, 0), (0.9, 0.6, 0.06), "#050806")
            for k in range(3):
                m.box(name, (-0.1, 0.15 - k * 0.15, 0.04), (0.5 + 0.2 * _hash(i, k), 0.06, 0.02), "#39ff88", emit=2, tag="core")
        elif ft == "shield":
            hexa = [(math.sin(k / 6 * TAU) * 0.35, math.cos(k / 6 * TAU) * 0.35, 0) for k in range(6)]
            polyline(m, name, hexa, (0.08, 0.1), en, closed=True, emit=2, tag="core")


# ----------------------------------------------------------------------------- escena del visor
def _mix(hexa, hexb, t):
    a = [int(hexa[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(hexb[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{int(a[i] + (b[i] - a[i]) * t):02x}" for i in range(3))


PARTICLES = {
    "sparkle": ("orbit", "sparkle"), "ember": ("rise", "square"), "bubble": ("rise", "dot"), "firefly": ("float", "dot"),
    "spark": ("rise", "sparkle"), "snow": ("snow", "square"), "void": ("rise", "square"), "rainbow": ("orbit", "sparkle"),
    "binary": ("snow", "square"), "coin": ("orbit", "sparkle"), "glitch": ("float", "square"),
}


def make_stage(sp, L, CY):
    rname, _, rcol = RARITIES[sp["rarity"]]
    en = sp["energy"]
    bg = sp["bg"] or (_mix(rcol, "#000000", 0.78) if L >= 2 else "#2c3442")
    stage = {
        "bgTop": bg, "bgBottom": _mix(bg, "#000000", 0.85), "fog": [30, 80, _mix(bg, "#000000", 0.7)],
        "ground": _mix(bg, "#000000", 0.55), "dist": 2.05 if L >= 3 else 2.3, "targetY": CY + (0.3 if L >= 3 else -0.6),
        "envTint": [_mix(en, "#ffffff", 0.5), _mix(bg, "#000000", 0.5)],
        "lights": {"sky": _mix(en, "#ffffff", 0.6), "groundCol": _mix(bg, "#000000", 0.4), "hemi": 1.0, "key": 2.4, "points": []},
        "bloom": {"strength": [0.0, 0.1, 0.25, 0.4, 0.5, 0.55, 0.6][L], "threshold": 1.3, "radius": 1.0, "exposure": 0.95},
        "emitScale": 0.45,
        "particles": [],
        "burstPart": "shell", "shakePart": "egg", "burstColor": en, "burstColor2": sp["accent"],
        "views": {"front": [0, 0.12], "side": [1.5708, 0.12], "tq": [0.55, 0.22]},
    }
    if L >= 2:
        stage["lights"]["points"].append({"color": en, "intensity": 1.5 + 0.4 * L, "pos": [0, 2.5, 3.5], "distance": 12})
        stage["groundGlow"] = _rgba(en, 0.12 + 0.03 * L)
        stage["groundGlowSize"] = 7 + L
    if L >= 4:
        stage["beam"] = {"color": en, "top": 1.2, "bottom": 0.6, "height": CY - 2.6, "y": 0.8, "intensity": 0.5}
    kind, sprite = PARTICLES.get(sp["particles"], ("orbit", "sparkle"))
    counts = [0, 25, 50, 90, 140, 200, 260]
    if L >= 1:
        stage["particles"].append({"kind": kind, "count": counts[L], "color": en if L >= 2 else "#ffffff", "size": 0.18 + 0.02 * L,
                                   "radius": [2.5, 6], "height": [0.5, 10], "speed": 0.4 if kind != "snow" else 1.0,
                                   "sprite": sprite, "intensity": 1.5 + 0.3 * L})
    if L >= 3:
        stage["particles"].append({"kind": "float", "count": 60 + 30 * L, "color": _mix(en, "#ffffff", 0.5), "size": 0.12,
                                   "radius": [7, 22], "height": [0.5, 16], "speed": 0.7, "sprite": "square", "intensity": 1.6})
    if L >= 5:
        stage["particles"].append({"kind": "rise", "count": 120, "color": en, "size": 0.2, "radius": [0.4, 3.0], "height": [0.8, 11],
                                   "speed": 0.6, "intensity": 2.5})
    return stage


def _rgba(hexc, a):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{a:.2f})"


# ----------------------------------------------------------------------------- constructor
def build(sp):
    _, L, _ = RARITIES[sp["rarity"]]
    R, HB, HT = 2.0, 2.2, 2.85
    V = 0.25 if L <= 1 else (0.22 if L <= 3 else 0.2)
    top = None

    # la base se construye primero en un modelo temporal para saber su altura
    from voxel import Model
    tmp = Model("tmp")
    tmp.part("root")
    top = build_base(tmp, sp, L)
    CY = top + HB * 0.9 if L <= 1 else top + HB + 0.5 + 0.12 * L

    m = egg_scene("egg_" + sp["id"], R, HB, HT, V, CY, make_shell_fn(sp, L))
    build_base(m, sp, L)
    build_structure(m, sp, L, R, HB, HT)
    build_emblem(m, sp, L, R, HB, HT)
    build_crown(m, sp, L, R, HB, HT)
    build_wings(m, sp, L)
    build_orbits(m, sp, L)
    build_floaters(m, sp, L, CY)

    has = set(m.parts)
    code_cols = 4

    def animate(t):
        a = t * TAU
        pose = {}
        amp = [0.06, 0.1, 0.14, 0.16, 0.18, 0.2, 0.22][L]
        yaw = [0, 8, 10, 6, 6, 6, 8][L]
        pose["egg"] = {"p": (0, amp * math.sin(a * 2) if L >= 2 else amp * max(0, math.sin(a * 2)) ** 2, 0),
                       "r": quat((2 * math.sin(a * 2 + 0.6) if L >= 2 else 0, yaw * math.sin(a), (1.5 + 0.3 * L) * math.sin(a)))}
        if "crown" in has:
            pose["crown"] = {"r": quat((0, math.degrees(a) if L >= 2 else 0, 0)), "p": (0, 0.06 * math.sin(a * 4), 0)}
        if "emblem" in has:
            pose["emblem"] = {"s": (1 + 0.03 * math.sin(a * 4),) * 3}
        flap = math.sin(a * (2 if L < 5 else 4))
        for side, sx in (("L", 1), ("R", -1)):
            if f"wing_{side}" in has:
                amp_w = 6 + 2 * L
                pose[f"wing_{side}"] = {"r": quat((0, sx * amp_w * 0.7 * flap, sx * amp_w * flap))}
        for n in ("orbit1", "floor_rings", "shardring"):
            if n in has:
                pose[n] = {"r": quat((0, -math.degrees(a * 2) if n == "orbit1" else math.degrees(a), 0))}
        if "orbit2" in has:
            pose["orbit2"] = {"r": quat((0, math.degrees(a * 2), 0))}
        if "halo" in has:
            pose["halo"] = {"p": (0, 0.12 * math.sin(a * 2 + 1), 0), "r": quat((5 * math.sin(a * 2), math.degrees(a), 0))}
        if "coin" in has:
            pose["coin"] = {"r": quat((0, math.degrees(a * 2), 0))}
        for i in range(5):
            if f"flame{i}" in has:
                f = 1 + 0.12 * math.sin(a * 8 + i * 2.1)
                pose[f"flame{i}"] = {"s": (1 / f ** 0.5, f, 1 / f ** 0.5)}
        i = 0
        while f"float{i}" in has:
            pose[f"float{i}"] = {"p": (0, 0.3 * math.sin(a * 2 + i), 0), "r": quat((0, math.degrees(a * 2), 0))}
            i += 1
        return pose

    def glow(t):
        a = t * TAU
        g = {"core": 0.8 + 0.2 * math.sin(a * 4), "neon": 0.8 + 0.2 * math.sin(a * 6), "twinkle": 0.5 + 0.5 * math.sin(a * 6) ** 2,
             "vein": 0.65 + 0.35 * math.sin(a * 2) ** 2, "water": 0.85 + 0.15 * math.sin(a * 4), "nebula": 0.8 + 0.2 * math.sin(a * 3),
             "cursor": 1.0 if (t * 4) % 1 < 0.5 else 0.1}
        for c in range(code_cols):  # lluvia de código: cada columna se enciende en su momento
            g[f"code{c}"] = 0.3 + 0.7 * max(0.0, math.sin(a * 2 - c * 1.57)) ** 2
        return g

    m.animate, m.glow = animate, glow
    m.stage = make_stage(sp, L, CY)
    m.meta = {"title": sp["name"], "rarity": sp["rarity"], "rarityName": RARITIES[sp["rarity"]][0], "level": L}
    return m


BUILDERS = {"egg_" + sp["id"]: (lambda sp=sp: build(sp)) for sp in SPECS}
