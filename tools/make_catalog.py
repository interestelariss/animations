"""Genera exports/catalog.json, las miniaturas y los paquetes de datos por rareza.

    python3 tools/make_catalog.py [carpeta_paquetes]

* exports/catalog.json: lista de modelos con título, rareza y miniatura.
* exports/thumbs/<modelo>.jpg: miniatura de 320 px a partir del render de Blender.
* <carpeta_paquetes>/bundle_<grupo>.json (opcional): todos los JSON de un grupo
  en un solo archivo, para subirlos de una vez al visor de Claude Design.
"""

import json
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP = os.path.join(ROOT, "exports")
ORDER = ["comun", "poco_comun", "raro", "epico", "mitico", "legendario", "secreto", "hacker"]


def main():
    out_bundles = sys.argv[1] if len(sys.argv) > 1 else None
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
        group = "destacados" if meta.get("featured") else meta["rarity"]
        png = os.path.join(EXP, name + ".png")
        if os.path.exists(png):
            im = Image.open(png).convert("RGB")
            w, h = im.size
            lvl = meta.get("level", -1)
            # recorte según el tamaño del modelo en el render (los comunes son pequeños)
            size, cx, cy = {0: (0.56, 0.52, 0.54), 1: (0.6, 0.52, 0.54), 2: (0.7, 0.52, 0.5)}.get(lvl, (0.84, 0.5, 0.44))
            if name in ("shark_dino", "mailbox"):
                size, cx, cy = 0.9, 0.5, 0.48
            box = (int(w * (cx - size / 2)), int(h * (cy - size / 2)), int(w * (cx + size / 2)), int(h * (cy + size / 2)))
            im = im.crop(box).resize((320, 320), Image.LANCZOS)
            im.save(os.path.join(EXP, "thumbs", name + ".jpg"), quality=86)
        cubes = sum(len(p["boxes"]) for p in d["parts"])
        items.append(dict(id=name, title=meta["title"], rarity=meta["rarity"], rarityName=meta["rarityName"],
                          level=meta.get("level", -1), group=group, cubes=cubes))

    def key(it):
        g = it["group"]
        gi = ORDER.index(g) if g in ORDER else (len(ORDER) if g == "destacados" else len(ORDER) + 1)
        return (gi, it["title"])

    items.sort(key=key)
    with open(os.path.join(EXP, "catalog.json"), "w") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    print(f"{len(items)} modelos en el catálogo")

    make_sheets(items)

    if out_bundles:
        os.makedirs(out_bundles, exist_ok=True)
        groups = {}
        for it in items:
            groups.setdefault(it["group"], []).append(it["id"])
        for g, ids in groups.items():
            bundle = {}
            for i in ids:
                with open(os.path.join(EXP, i + ".json")) as f:
                    bundle[i] = json.load(f)
            path = os.path.join(out_bundles, f"bundle_{g}.json")
            with open(path, "w") as f:
                json.dump(bundle, f, separators=(",", ":"))
            print(g, len(ids), f"{os.path.getsize(path) / 1e6:.1f} MB")


COL = {"comun": "#9aa3ad", "poco_comun": "#4cc26a", "raro": "#3d8bff", "epico": "#a35cff", "mitico": "#ff4d6d",
       "legendario": "#ffb627", "secreto": "#f2f2f2", "hacker": "#39ff88", "otros": "#7f8ea3"}
GROUP_NAMES = {"destacados": "Destacados (hechos a mano)", "comun": "Comunes", "poco_comun": "Poco comunes", "raro": "Raros",
               "epico": "Épicos", "mitico": "Míticos", "legendario": "Legendarios", "secreto": "Secretos",
               "hacker": "Hacker (estilo Robux)", "otros": "Otros modelos"}


def make_sheets(items):
    """Fichas numeradas (docs/fichas) y una hoja por grupo (docs/resultados/coleccion_*.jpg)."""
    from PIL import ImageDraw, ImageFont
    fb = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    fr = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f1, f2, ft = ImageFont.truetype(fb, 22), ImageFont.truetype(fr, 16), ImageFont.truetype(fb, 34)
    docs = os.path.join(ROOT, "docs")
    os.makedirs(os.path.join(docs, "fichas"), exist_ok=True)
    os.makedirs(os.path.join(docs, "resultados"), exist_ok=True)
    groups = []
    for i, it in enumerate(items, 1):
        it["n"] = i
        if not groups or groups[-1][0] != it["group"]:
            groups.append((it["group"], []))
        groups[-1][1].append(it)
    CW, IH, TH = 320, 320, 78

    def label(d, x, y, it, col):
        d.rectangle([x, y + IH, x + CW, y + IH + TH], fill="#121821")
        d.rectangle([x, y + IH, x + 6, y + IH + TH], fill=col)
        d.rounded_rectangle([x + 10, y + 10, x + 66, y + 44], 6, fill="#000000", outline=col, width=2)
        d.text((x + 38, y + 27), f"#{it['n']}", font=f1, fill="#ffffff", anchor="mm")
        d.text((x + 16, y + IH + 12), it["title"], font=f1, fill="#ffffff")
        d.text((x + 16, y + IH + 44), f"{it['rarityName']} · {it['cubes']} cubos", font=f2, fill=col)

    for gi, (g, group) in enumerate(groups):
        cols = 5
        rows = (len(group) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * CW + (cols + 1) * 16, 80 + rows * (IH + TH + 16) + 16), "#0a0d13")
        d = ImageDraw.Draw(sheet)
        d.text((16, 22), f"{GROUP_NAMES.get(g, g)}  ·  {len(group)} modelos", font=ft, fill="#e8edf5")
        for k, it in enumerate(group):
            x, y = 16 + (k % cols) * (CW + 16), 80 + (k // cols) * (IH + TH + 16)
            th = Image.open(os.path.join(EXP, "thumbs", it["id"] + ".jpg"))
            col = COL.get(it["rarity"], "#7f8ea3")
            sheet.paste(th, (x, y))
            label(d, x, y, it, col)
            card = Image.new("RGB", (CW, IH + TH), "#121821")
            card.paste(th, (0, 0))
            label(ImageDraw.Draw(card), 0, 0, it, col)
            card.save(os.path.join(docs, "fichas", f"{it['n']:02d}_{it['id']}.jpg"), quality=88)
        sheet.save(os.path.join(docs, "resultados", f"coleccion_{gi + 1:02d}_{g}.jpg"), quality=88)


if __name__ == "__main__":
    main()
