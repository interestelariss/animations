"""Piezas comunes del kit de mascotas: contexto, colores de piel y patrones naturales.

Cada mascota se diseña a mano en pet_roster.py (especie, proporciones, rasgos y
colores propios); estos módulos (pk_*.py) solo saben construir los planos de
cuerpo y los rasgos que se piden.
"""

import math

from mathutils import Vector

from eggs import _hash
from eggs_themes import vnoise
from tiers import _mix
from voxel import quat, segment

TAU = math.tau
mix = _mix


class Ctx:
    """Calidad y tema del huevo para una mascota.

    S: escala; v: tamaño de vóxel; L: nivel de rareza (0..6);
    en/acc/metal: colores del huevo; tint: cuánto se tiñe la especie hacia el huevo;
    glow: patrón de marcas brillantes según el huevo (runas, grietas, circuitos...).
    """

    def __init__(self, S, v, L, sp, tint=0.0, glow=None, giant=False):
        self.S, self.v, self.L = S, v, L
        self.sp = sp
        self.en, self.acc, self.metal = sp["energy"], sp["accent"], sp["metal"]
        self.shell = sp["shell"]
        self.tint = tint
        self.glow = glow
        self.giant = giant

    def c(self, h):
        """Color natural de la especie, teñido hacia el huevo."""
        if not self.tint or h is None:
            return h
        return mix(h, self.shell[0], self.tint)

    @property
    def eye_glow(self):
        return 0.0 if self.L < 3 else 0.5 + 0.25 * (self.L - 2)


def shades(c, k=0.08):
    return [c, mix(c, "#000000", k), mix(c, "#ffffff", k * 0.8)]


def vor(p, f, seed=0.0):
    """Celdas de Voronoi: (distancia al centro más cercano, al segundo, id de celda)."""
    x, y, z = p.x * f + seed, p.y * f, p.z * f
    ix, iy, iz = math.floor(x), math.floor(y), math.floor(z)
    d1 = d2 = 9.0
    cid = 0.0
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                cx, cy, cz = ix + dx, iy + dy, iz + dz
                jx, jy, jz = _hash(cx, cy, cz), _hash(cy, cz, cx + 7), _hash(cz + 3, cx, cy)
                d = (cx + jx - x) ** 2 + (cy + jy - y) ** 2 + (cz + jz - z) ** 2
                if d < d1:
                    d2, d1, cid = d1, d, _hash(cx + 11, cy + 5, cz + 2)
                elif d < d2:
                    d2 = d
    return math.sqrt(d1), math.sqrt(d2), cid


def pattern_hit(pat, p, n, ps, seed=0.0):
    """0 = color base, 1 = color de patrón, 2 = segundo color de patrón."""
    if pat is None:
        return 0
    x, y, z = p.x / ps, p.y / ps, p.z / ps
    if pat == "stripes":  # tigre: bandas verticales irregulares en los flancos
        v = math.sin(z * 6.5 + vnoise(x * 2 + seed, y * 2, z * 2) * 3.2 + abs(x) * 1.2)
        return 1 if v > 0.68 and n.y > -0.55 else 0
    if pat == "zebra":
        v = math.sin(z * 9 + abs(y) * 2.5 + vnoise(x * 1.5, y * 1.5 + seed, z * 1.5) * 2)
        return 1 if v > 0.1 else 0
    if pat == "tabby":
        v = math.sin(z * 8 + y * 3 + vnoise(x * 3, y * 3, z * 3 + seed) * 2.5)
        return 1 if v > 0.75 else 0
    if pat == "bands":  # anillos transversales a lo largo de z
        return 1 if int(math.floor(z * 3.2 + 50)) % 2 else 0
    if pat == "bands_y":
        return 1 if int(math.floor(y * 3.2 + 50)) % 2 else 0
    if pat == "spots":  # manchas sueltas (dálmata, guepardo)
        d1, d2, cid = vor(Vector((x, y, z)), 3.2, seed)
        return 1 if d1 < 0.28 and cid < 0.75 else 0
    if pat == "bigspots":
        d1, d2, cid = vor(Vector((x, y, z)), 1.8, seed)
        return 1 if d1 < 0.33 and cid < 0.7 else 0
    if pat == "rosettes":  # leopardo/jaguar: anillo oscuro con centro más oscuro que la base
        d1, d2, cid = vor(Vector((x, y, z)), 2.6, seed)
        if 0.2 < d1 < 0.36:
            return 1
        return 2 if d1 <= 0.2 and cid < 0.5 else 0
    if pat == "giraffe":  # manchas grandes separadas por líneas claras
        d1, d2, cid = vor(Vector((x, y, z)), 2.2, seed)
        return 1 if d2 - d1 > 0.14 else 0
    if pat == "cow":
        d1, d2, cid = vor(Vector((x, y, z)), 1.3, seed)
        return 1 if cid < 0.42 else 0
    if pat == "patches":  # manchas grandes de ruido (calicó, pinto)
        return 1 if vnoise(x * 1.4 + seed, y * 1.4, z * 1.4) > 0.6 else (2 if vnoise(x * 1.4, y * 1.4 + 9, z * 1.4 + seed) > 0.68 else 0)
    if pat == "speckle":
        return 1 if _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3)) > 0.86 else 0
    if pat == "dorsal":  # franja en el lomo (mofeta, ardilla listada)
        return 1 if n.y > 0.35 and abs(x) < 0.12 else (2 if n.y > 0.2 and 0.2 < abs(x) < 0.28 else 0)
    if pat == "countershade":
        return 1 if n.y > 0.25 else 0
    if pat == "saddle":  # tapir, panda: banda ancha en el medio
        return 1 if abs(z) < 0.35 else 0
    if pat == "scales":
        row = math.floor(y * 6 + 50)
        col = (z * 6 + (row % 2) * 0.5) % 1
        return 1 if col < 0.16 else 0
    if pat == "hex":
        d1, d2, cid = vor(Vector((x, y, z)), 4.0, seed)
        return 1 if d2 - d1 < 0.08 else 0
    if pat == "dots":  # puntitos claros (pez globo, gallina de guinea)
        d1, d2, cid = vor(Vector((x, y, z)), 5.0, seed)
        return 1 if d1 < 0.2 else 0
    if pat == "warts":
        d1, d2, cid = vor(Vector((x, y, z)), 4.0, seed)
        return 1 if d1 < 0.22 and cid < 0.6 else 0
    if pat == "lines_h":  # rayas horizontales (pez, tilacino al revés)
        return 1 if math.sin(y * 14 + vnoise(x, y, z) * 1.5) > 0.55 else 0
    if pat == "back_stripes":  # rayas solo en la mitad trasera (tilacino, okapi)
        v = math.sin(z * 10)
        return 1 if z < -0.05 and v > 0.3 and n.y > -0.4 else 0
    return 0


def skin(base, belly=None, pat=None, pc=None, pc2=None, ps=1.0, back=None, seed=0.0, ctx=None, emit_pat=0.0,
         belly_k=-0.35, region=None, glow=True):
    """Función de color de una parte.

    base: color o lista de tonos; belly: vientre (normal hacia abajo); back: lomo;
    pat/pc/pc2: patrón natural; region(p, n) -> color|None para zonas propias (máscara, calcetines...).
    Si el contexto lo pide, añade marcas brillantes del huevo (runas, grietas, circuitos...).
    """
    tc = (lambda h: ctx.c(h)) if ctx else (lambda h: h)
    cols = [tc(c) for c in (base if isinstance(base, (list, tuple)) else shades(base))]
    belly, back, pc, pc2 = tc(belly), tc(back), tc(pc), tc(pc2)
    gpat = ctx.glow if (ctx and glow and ctx.glow and ctx.L >= 3) else None
    gcol = ctx.en if ctx else None
    gemit = 0.8 + 0.25 * (ctx.L if ctx else 0)

    def fn(p, n):
        if gpat:
            g = glow_hit(gpat, p, n, ctx.S, ctx.L)
            if g:
                return (gcol, gemit, "glow")
        if region:
            r = region(p, n)
            if r is not None:
                return r
        h = _hash(round(p.x, 3), round(p.y, 3), round(p.z, 3))
        hit = pattern_hit(pat, p, n, ps, seed)
        if hit == 1 and pc:
            return (pc, emit_pat, "glow") if emit_pat else pc
        if hit == 2 and pc2:
            return pc2
        if belly and n.y < belly_k:
            return belly
        if back and n.y > 0.55:
            return back
        return cols[int(h * 97) % len(cols)]
    return fn


def glow_hit(kind, p, n, S, L):
    """Marcas brillantes del huevo sobre la piel (solo rareza alta)."""
    x, y, z = p.x / S, p.y / S, p.z / S
    k = 1.0 + 0.15 * (L - 3)
    if kind == "runes":
        fx, fy = (z * 2.6) % 1, (y * 2.6 + 0.3) % 1
        return abs(n.x) > 0.5 and ((abs(fx - 0.5) < 0.06 and 0.2 < fy < 0.8) or (abs(fy - 0.5) < 0.06 and 0.3 < fx < 0.7))
    if kind == "cracks":
        d1, d2, cid = vor(Vector((x, y, z)), 2.5)
        return d2 - d1 < 0.025 * k
    if kind == "circuit":
        gx, gz = (z * 5) % 1, (y * 5) % 1
        line = (gx < 0.08 and _hash(math.floor(z * 5), math.floor(y * 5)) > 0.45) or (gz < 0.08 and _hash(math.floor(y * 5), math.floor(z * 5), 3) > 0.55)
        return abs(n.x) > 0.4 and line
    if kind == "stars":
        return _hash(round(p.x, 2), round(p.y, 2), round(p.z, 2)) > 0.965 - 0.01 * (L - 3)
    if kind == "veins":
        return abs(vnoise(x * 2.2, y * 2.2, z * 2.2) - 0.5) < 0.016 * k
    if kind == "spots":
        d1, d2, cid = vor(Vector((x, y, z)), 3.0)
        return d1 < 0.09 * k and cid < 0.45
    if kind == "stripes":
        return math.sin(z * 9 + y * 2) > 0.96 - 0.01 * (L - 3) and n.y > -0.3
    if kind == "code":
        return abs(n.x) > 0.3 and (z * 7) % 1 < 0.35 and _hash(math.floor(z * 7), math.floor(y * 9)) > 0.62
    return False


def solid(c, emit=0.0, tag=None):
    if emit:
        return lambda p, n: (c, emit, tag or "glow")
    return lambda p, n: c


def eyes(m, part, center, sep, size, iris, glow=0.0, pupil="#050505", slit=False, yaw=18, white="#fbfbf6", lid=None, shine=True,
         style="round"):
    """Ojos de caja: blanco, iris, pupila y brillo. center = punto medio entre los ojos (superficie)."""
    c = Vector(center)
    for sx in (1, -1):
        p = c + Vector((sx * sep, 0, 0))
        r = (0, sx * yaw, 0)
        s = size
        if style == "bead":  # ojillo negro brillante (pájaros pequeños, roedores)
            m.box(part, p, (s * 0.7, s * 0.7, s * 0.5), pupil if not glow else iris, r=r, emit=glow, tag="eyes" if glow else None)
            if shine:
                m.box(part, p + Vector((sx * s * 0.12, s * 0.15, s * 0.22)), (s * 0.22, s * 0.22, 0.02), "#ffffff", r=r)
            continue
        if style == "compound":  # ojo compuesto de insecto
            m.box(part, p, (s, s, s * 0.8), iris, r=r, emit=glow, tag="eyes" if glow else None)
            m.box(part, p + Vector((0, 0, s * 0.1)), (s * 0.7, s * 0.7, s * 0.75), mix(iris, "#ffffff", 0.2), r=r, emit=glow * 0.8,
                  tag="eyes" if glow else None)
            continue
        m.box(part, p, (s, s * 0.8, s * 0.3), white, r=r)
        m.box(part, p + Vector((0, -s * 0.03, s * 0.1)), (s * 0.66, s * 0.66, s * 0.22), iris, r=r, emit=glow, tag="eyes" if glow else None)
        m.box(part, p + Vector((0, -s * 0.05, s * 0.2)), (s * (0.16 if slit else 0.32), s * 0.55, s * 0.12), pupil, r=r)
        if shine:
            m.box(part, p + Vector((sx * s * 0.15, s * 0.2, s * 0.26)), (s * 0.18, s * 0.18, 0.02), "#ffffff", r=r)
        if lid:
            m.box(part, p + Vector((0, s * 0.42, s * 0.02)), (s * 1.15, s * 0.22, s * 0.4), lid, r=(0, sx * yaw, sx * -8))


def spikes_on(m, part, pts, normal_fn, length, width, col, tip=None, emit=0.0, tag=None):
    """Púas que salen a lo largo de la normal (erizo, puercoespín, dragones)."""
    for p in pts:
        nrm = normal_fn(p)
        a = Vector(p)
        b = a + nrm * length
        segment(m, part, a, a.lerp(b, 0.6), (width, width), col)
        segment(m, part, a.lerp(b, 0.55), b, (width * 0.55, width * 0.55), tip or col, emit=emit, tag=tag)


def leaf_quad(m, part, a, d, length, width, col, col2=None, steps=5):
    """Hoja/pluma plana hecha de cajas escalonadas."""
    a, d = Vector(a), Vector(d).normalized()
    for j in range(steps):
        k = (j + 0.5) / steps
        w = width * math.sin(math.pi * min(0.98, k * 0.9 + 0.08))
        q = Vector((0, 0, 1)).rotation_difference(d)
        m.box(part, a + d * length * k, (w, 0.04, length / steps + 0.02), col if (j % 2 == 0 or not col2) else col2, r=q)
