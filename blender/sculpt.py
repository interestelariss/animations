"""Escultura con vóxeles: volúmenes orgánicos (elipsoides y cápsulas, con ruido
opcional) convertidos en miles de cubitos de superficie, coloreados por una
función. Es el mismo lenguaje visual que las cáscaras de los huevos, aplicado a
criaturas: cada parte animable (cuerpo, cabeza, mandíbula, patas, cola…) se
voxeliza por separado.
"""

import math

from mathutils import Vector

from eggs_themes import vnoise


VOXEL_SCALE = 1.0  # multiplica el tamaño de vóxel (más grande = menos cubos)
MODE = "voxel"  # "voxel": cubitos de superficie · "smooth": piezas suaves esculpidas (estilo Roblox con studs)


def ell(c, r, noise=0.0, freq=2.0, seed=0.0):
    """Elipsoide. noise > 0 deforma la superficie (pelaje, roca, melena)."""
    return ("e", Vector(c), Vector(r), noise, freq, seed)


def cap(a, b, r0, r1=None, noise=0.0, freq=2.0, seed=0.0):
    """Cápsula de a a b con radio que va de r0 a r1."""
    return ("c", Vector(a), Vector(b), r0, r0 if r1 is None else r1, noise, freq, seed)


def box(c, s):
    return ("b", Vector(c), Vector(s))


def _inside(prims, p):
    for pr in prims:
        k = pr[0]
        if k == "e":
            _, c, r, nz, fq, sd = pr
            d = Vector(((p.x - c.x) / r.x, (p.y - c.y) / r.y, (p.z - c.z) / r.z)).length
            lim = 1.0 + (nz * (vnoise(p.x * fq + sd, p.y * fq, p.z * fq - sd) - 0.5) * 2 if nz else 0)
            if d <= lim:
                return True
        elif k == "c":
            _, a, b, r0, r1, nz, fq, sd = pr
            ab = b - a
            L2 = ab.length_squared
            t = 0.0 if L2 == 0 else max(0.0, min(1.0, (p - a).dot(ab) / L2))
            q = a + ab * t
            r = r0 + (r1 - r0) * t
            if nz:
                r *= 1.0 + nz * (vnoise(p.x * fq + sd, p.y * fq, p.z * fq - sd) - 0.5) * 2
            if (p - q).length <= r:
                return True
        else:
            _, c, s = pr
            if abs(p.x - c.x) <= s.x / 2 and abs(p.y - c.y) <= s.y / 2 and abs(p.z - c.z) <= s.z / 2:
                return True
    return False


def _bounds(prims):
    lo = Vector((1e9, 1e9, 1e9))
    hi = -lo
    for pr in prims:
        if pr[0] == "e":
            c, r = pr[1], pr[2] * (1 + pr[3] + 0.05)
            a, b = c - r, c + r
        elif pr[0] == "c":
            rr = max(pr[3], pr[4]) * (1 + pr[5] + 0.05)
            a = Vector(map(min, pr[1], pr[2])) - Vector((rr, rr, rr))
            b = Vector(map(max, pr[1], pr[2])) + Vector((rr, rr, rr))
        else:
            a, b = pr[1] - pr[2] / 2, pr[1] + pr[2] / 2
        lo = Vector(map(min, lo, a))
        hi = Vector(map(max, hi, b))
    return lo, hi


def voxelize(m, part, prims, v, colfn, carve=None):
    """Añade a la parte los vóxeles de superficie del volumen.

    colfn(p, n) -> color | (color, emit, tag): p = posición local, n = normal aproximada.
    carve: primitivas que se restan (bocas, cuencas…).
    """
    if MODE == "smooth":
        return _smooth(m, part, prims, colfn)
    v *= VOXEL_SCALE
    lo, hi = _bounds(prims)
    nx, ny, nz = (int(math.ceil((hi[i] - lo[i]) / v)) + 2 for i in range(3))
    grid = {}
    for ix in range(nx):
        x = lo.x + (ix - 0.5) * v
        for iy in range(ny):
            y = lo.y + (iy - 0.5) * v
            for iz in range(nz):
                p = Vector((x, y, lo.z + (iz - 0.5) * v))
                if _inside(prims, p) and not (carve and _inside(carve, p)):
                    grid[(ix, iy, iz)] = p
    count = 0
    for (ix, iy, iz), p in grid.items():
        n = Vector((0, 0, 0))
        exposed = False
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            if (ix + d[0], iy + d[1], iz + d[2]) not in grid:
                exposed = True
                n += Vector(d)
        if not exposed:
            continue
        n = n.normalized() if n.length else Vector((0, 1, 0))
        res = colfn(p, n)
        if res is None:
            continue
        col, emit, tag = (tuple(res) + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
        m.box(part, p, (v, v, v), col, emit=emit, tag=tag)
        count += 1
    return count


def surface_point(e, x, y, front=1):
    """Punto de la superficie frontal (+z) de un elipsoide para colocar ojos, placas…"""
    _, c, r = e[0], e[1], e[2]
    u = 1 - ((x - c.x) / r.x) ** 2 - ((y - c.y) / r.y) ** 2
    z = c.z + front * r.z * math.sqrt(max(0.0, u))
    return Vector((x, y, z))


def _smooth(m, part, prims, colfn):
    """Cada primitiva se convierte en una pieza suave (elipsoide o cápsula) de un solo color."""
    from mathutils import Quaternion
    count = 0
    for pr in prims:
        if pr[0] == "e":
            c, r = pr[1], pr[2]
            shape = ("ell", c, r, Quaternion())
            probe = c
        elif pr[0] == "c":
            shape = ("cap", pr[1], pr[2], pr[3], pr[4])
            probe = (pr[1] + pr[2]) / 2
        else:
            res = colfn(pr[1], Vector((0, 0.2, 1)).normalized())
            col, emit, tag = (tuple(res) + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
            m.box(part, pr[1], pr[2], col, emit=emit, tag=tag)
            count += 1
            continue
        res = colfn(probe, Vector((0.3, 0.2, 1)).normalized())
        if res is None:
            continue
        col, emit, tag = (tuple(res) + (0, None))[:3] if isinstance(res, tuple) else (res, 0, None)
        m.prim(part, shape, col, emit=emit, tag=tag)
        count += 1
    return count
