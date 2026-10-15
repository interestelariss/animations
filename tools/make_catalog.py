"""Catálogo, miniaturas, hojas de revisión y paquetes para el visor.

    python3 tools/make_catalog.py [carpeta_paquetes]

* exports/catalog.json            lista de modelos (título, rareza, grupo, huevo…)
* exports/thumbs/<modelo>.jpg     miniatura 320 px (del render de Blender)
* docs/resultados/*.jpg           hojas numeradas para revisar (huevos, animales, mascotas)
* docs/fichas/*.jpg               ficha individual de cada huevo y animal
* <carpeta_paquetes>/             bundle_<grupo>.json + sprite_<grupo>.jpg (miniaturas en rejilla)
"""

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "exports")
DOCS = os.path.join(ROOT, "docs")
EGG_ORDER = ["comun", "poco_comun", "raro", "epico", "mitico", "legendario", "secreto", "hacker", "renacimiento", "destacados"]
COL = {"comun": "#9aa3ad", "poco_comun": "#4cc26a", "raro": "#3d8bff", "epico": "#a35cff", "mitico": "#ff4d6d", "legendario": "#ffb627",
       "secreto": "#f2f2f2", "hacker": "#39ff88", "renacimiento": "#ff8a3a", "animal": "#ff8a3a", "otros": "#7f8ea3"}
GROUP_NAMES = {"destacados": "Huevos destacados (hechos a mano)", "comun": "Huevos comunes", "poco_comun": "Huevos poco comunes",
               "raro": "Huevos raros", "epico": "Huevos épicos", "mitico": "Huevos míticos", "legendario": "Huevos legendarios",
               "secreto": "Huevos secretos", "hacker": "Huevos hacker (estilo Robux)", "renacimiento": "Huevos de renacimiento",
               "animales": "Animales de renacimiento", "otros": "Otros modelos"}
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def crop_for(meta, name):
    lvl = meta.get("level", -1)
    if name.startswith("pet_") or name in ("animal_rabbit", "animal_cat", "animal_dog", "animal_cheetah"):
        return (0.94, 0.5, 0.5)  # renderizados con la cámara ajustada al tamaño
    if name.startswith("animal_") or name in ("shark_dino", "mailbox"):
        return (0.9, 0.5, 0.47)
    return {0: (0.56, 0.52, 0.54), 1: (0.6, 0.52, 0.54), 2: (0.7, 0.52, 0.5)}.get(lvl, (0.84, 0.5, 0.44))


def load_items():
    os.makedirs(os.path.join(EXP, "thumbs"), exist_ok=True)
    items = []
    for fn in sorted(os.listdir(EXP)):
        if not fn.endswith(".json") or fn == "catalog.json":
            continue
        name = fn[:-5]
        with open(os.path.join(EXP, fn)) as f:
            d = json.load(f)
        meta = d.get("meta") or {"title": {"shark_dino": "Tiburón-Dino", "mailbox": "Buzón-Monstruo"}.get(name, name),
                                 "rarity": "otros", "rarityName": "Otros", "level": -1}
        if name.startswith("pet_"):
            group = "mascotas"
        elif name.startswith("animal_"):
            group = "animales"
        else:
            group = meta.get("group") or ("destacados" if meta.get("featured") else meta["rarity"])
        png = os.path.join(EXP, name + ".png")
        if os.path.exists(png):
            im = Image.open(png).convert("RGB")
            w, h = im.size
            size, cx, cy = crop_for(meta, name)
            box = (int(w * (cx - size / 2)), int(h * (cy - size / 2)), int(w * (cx + size / 2)), int(h * (cy + size / 2)))
            im.crop(box).resize((320, 320), Image.LANCZOS).save(os.path.join(EXP, "thumbs", name + ".jpg"), quality=86)
        cubes = sum(len(p.get("bx", p.get("boxes", []))) for p in d["parts"])
        it = dict(id=name, title=meta["title"], rarity=meta["rarity"], rarityName=meta["rarityName"], level=meta.get("level", -1),
                  group=group, cubes=cubes)
        for k in ("egg", "eggName", "rebirth", "subtitle", "requirement", "bonus"):
            if k in meta:
                it[k] = meta[k]
        items.append(it)
    return items


def sort_items(items):
    eggs = [i for i in items if i["group"] in EGG_ORDER]
    eggs.sort(key=lambda i: (EGG_ORDER.index(i["group"]), i.get("rebirth", 0), i["title"]))
    egg_rank = {e["id"]: k for k, e in enumerate(eggs)}
    egg_group = {e["id"]: e["group"] for e in eggs}
    animals = sorted([i for i in items if i["group"] == "animales"], key=lambda i: i.get("rebirth", 0))
    pets = sorted([i for i in items if i["group"] == "mascotas"], key=lambda i: (egg_rank.get(i.get("egg"), 999), i["id"]))
    others = [i for i in items if i["group"] == "otros"]
    for p in pets:
        p["eggGroup"] = egg_group.get(p.get("egg"), "otros")
    out = eggs + animals + pets + others
    for n, it in enumerate(out, 1):
        it["n"] = n
    return out


def thumb(it, size=320):
    p = os.path.join(EXP, "thumbs", it["id"] + ".jpg")
    im = Image.open(p) if os.path.exists(p) else Image.new("RGB", (320, 320), "#141a24")
    return im.resize((size, size)) if size != 320 else im


def card(it, f1, f2, sub=None, CW=320, TH=78):
    col = COL.get(it["rarity"], "#7f8ea3")
    c = Image.new("RGB", (CW, CW + TH), "#121821")
    c.paste(thumb(it, CW), (0, 0))
    d = ImageDraw.Draw(c)
    d.rectangle([0, CW, 6, CW + TH], fill=col)
    d.rounded_rectangle([10, 10, 82, 44], 6, fill="#000000", outline=col, width=2)
    d.text((46, 27), f"#{it['n']}", font=f1, fill="#ffffff", anchor="mm")
    title = it["title"] if len(it["title"]) <= 24 else it["title"][:23] + "…"
    d.text((16, CW + 12), title, font=f1, fill="#ffffff")
    d.text((16, CW + 44), sub or f"{it['rarityName']} · {it['cubes']} cubos", font=f2, fill=col)
    return c


def make_sheets(items):
    f1, f2, ft, f3 = ImageFont.truetype(FB, 22), ImageFont.truetype(FR, 16), ImageFont.truetype(FB, 34), ImageFont.truetype(FR, 14)
    os.makedirs(os.path.join(DOCS, "fichas"), exist_ok=True)
    os.makedirs(os.path.join(DOCS, "resultados"), exist_ok=True)
    for folder in ("fichas", "resultados"):
        for fn in os.listdir(os.path.join(DOCS, folder)):
            if fn.startswith(("coleccion_", "mascotas_", "animales_")) or folder == "fichas":
                os.remove(os.path.join(DOCS, folder, fn))
    groups = []
    for it in items:
        if it["group"] == "mascotas":
            continue
        if not groups or groups[-1][0] != it["group"]:
            groups.append((it["group"], []))
        groups[-1][1].append(it)
    for gi, (g, group) in enumerate(groups, 1):
        cols = 5
        for page in range(0, len(group), 20):
            chunk = group[page:page + 20]
            rows = (len(chunk) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * 320 + (cols + 1) * 16, 80 + rows * (398 + 16) + 16), "#0a0d13")
            d = ImageDraw.Draw(sheet)
            pg = f" ({page // 20 + 1}/{(len(group) + 19) // 20})" if len(group) > 20 else ""
            d.text((16, 22), f"{GROUP_NAMES.get(g, g)}{pg}  ·  {len(group)} modelos", font=ft, fill="#e8edf5")
            for k, it in enumerate(chunk):
                sub = it.get("requirement") if g == "animales" else None
                c = card(it, f1, f2, sub)
                sheet.paste(c, (16 + (k % cols) * 336, 80 + (k // cols) * 414))
                c.save(os.path.join(DOCS, "fichas", f"{it['n']:03d}_{it['id']}.jpg"), quality=84)
            tag = "animales" if g == "animales" else "coleccion"
            sheet.save(os.path.join(DOCS, "resultados", f"{tag}_{gi:02d}_{g}_{page // 20 + 1}.jpg"), quality=84)
    eggs = {i["id"]: i for i in items if i["group"] in EGG_ORDER}
    pets_by_egg = {}
    for it in items:
        if it["group"] == "mascotas":
            pets_by_egg.setdefault(it["egg"], []).append(it)
    order = [e for e in eggs if e in pets_by_egg]
    T, per = 200, 8
    for page in range(0, len(order), per):
        chunk = order[page:page + per]
        sheet = Image.new("RGB", (16 + 5 * (T + 12) + 4, 70 + len(chunk) * (T + 70) + 10), "#0a0d13")
        d = ImageDraw.Draw(sheet)
        d.text((16, 18), f"Mascotas por huevo ({page // per + 1}/{(len(order) + per - 1) // per})", font=ft, fill="#e8edf5")
        for r, eid in enumerate(chunk):
            y = 70 + r * (T + 70)
            for k, it in enumerate([eggs[eid]] + pets_by_egg[eid]):
                x = 16 + k * (T + 12)
                col = COL.get(it["rarity"], "#7f8ea3")
                sheet.paste(thumb(it, T), (x, y))
                d.rectangle([x, y + T, x + T, y + T + 52], fill="#121821" if k else "#1b2230")
                d.rectangle([x, y + T, x + 4, y + T + 52], fill=col)
                t = it["title"] if len(it["title"]) <= 19 else it["title"][:18] + "…"
                d.text((x + 10, y + T + 6), f"#{it['n']} {t}", font=f3, fill="#ffffff")
                d.text((x + 10, y + T + 28), ("HUEVO · " if k == 0 else "") + it["rarityName"], font=f3, fill=col)
        sheet.save(os.path.join(DOCS, "resultados", f"mascotas_{page // per + 1:02d}.jpg"), quality=82)


def make_bundles(items, out):
    os.makedirs(out, exist_ok=True)
    groups = {}
    for it in items:
        g = it["group"] if it["group"] != "mascotas" else "m_" + it["eggGroup"]
        groups.setdefault(g, []).append(it)
    for g, group in groups.items():
        bundle = {}
        for it in group:
            with open(os.path.join(EXP, it["id"] + ".json")) as f:
                bundle[it["id"]] = json.load(f)
        with open(os.path.join(out, f"bundle_{g}.json"), "w") as f:
            json.dump(bundle, f, separators=(",", ":"))
        S, cols = 160, 10
        rows = (len(group) + cols - 1) // cols
        sp = Image.new("RGB", (cols * S, rows * S), "#141a24")
        for k, it in enumerate(group):
            sp.paste(thumb(it, S), ((k % cols) * S, (k // cols) * S))
            it["bundle"], it["cell"] = g, k
        sp.save(os.path.join(out, f"sprite_{g}.jpg"), quality=82)
        print(g, len(group), f"{os.path.getsize(os.path.join(out, f'bundle_{g}.json')) / 1e6:.1f} MB")


def main():
    items = sort_items(load_items())
    make_sheets(items)
    if len(sys.argv) > 1:
        make_bundles(items, sys.argv[1])
    with open(os.path.join(EXP, "catalog.json"), "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=0)
    print(f"{len(items)} modelos en el catálogo")


if __name__ == "__main__":
    main()
