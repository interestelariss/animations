"""Constructor de modelos hechos de cubos.

Un modelo es una jerarquía de "partes" (pivotes con posición + rotación) y cada
parte tiene una lista de cajas. Todo se define en coordenadas Y-arriba,
frente = +Z (igual que three.js / Roblox). La escena de Blender pone todo bajo
un empty "Root" girado 90° en X, así que en Blender queda Z-arriba y de frente.

De la misma definición salen:
  * un JSON (partes, cajas y animación muestreada) para el visor web, y
  * la escena de Blender (empties + mallas + keyframes) -> .blend / .glb / render.
"""

import json
import math

from mathutils import Euler, Matrix, Quaternion, Vector


def quat(deg=(0, 0, 0)):
    """Euler en grados (orden XYZ de Blender) -> Quaternion."""
    return Euler([math.radians(a) for a in deg], "XYZ").to_quaternion()


def mirror_rot(deg):
    return (deg[0], -deg[1], -deg[2])


class Part:
    def __init__(self, name, parent, pivot, rot):
        self.name = name
        self.parent = parent
        self.pivot = Vector(pivot)
        self.quat = rot if isinstance(rot, Quaternion) else quat(rot)
        self.boxes = []


class Model:
    def __init__(self, name, fps=24, frames=72):
        self.name = name
        self.fps = fps
        self.frames = frames
        self.parts = {}
        self.animate = None  # f(t in [0,1)) -> {part: dict(p=Vector, r=Quaternion, s=Vector)}
        self.glow = None  # f(t) -> {tag: float}
        self.stage = None  # ajustes del visor web (fondo, luces, partículas...)
        self.meta = None  # título y rareza para la colección

    # -- construcción -------------------------------------------------------
    def part(self, name, parent=None, pivot=(0, 0, 0), rot=(0, 0, 0)):
        p = Part(name, parent, pivot, rot)
        self.parts[name] = p
        return p

    def box(self, part, c, s, col, r=(0, 0, 0), emit=0.0, tag=None, metal=0):
        part = self.parts[part] if isinstance(part, str) else part
        q = r if isinstance(r, Quaternion) else quat(r)
        part.boxes.append(dict(c=Vector(c), s=Vector(s), q=q, col=col, emit=emit, tag=tag, metal=metal))

    def sym(self, part, c, s, col, r=(0, 0, 0), **kw):
        """Caja + su espejo en X."""
        self.box(part, c, s, col, r, **kw)
        self.box(part, (-c[0], c[1], c[2]), s, col, mirror_rot(r), **kw)

    # -- matemáticas ----------------------------------------------------------
    def local_matrix(self, part, pose=None):
        p, q, s = part.pivot, part.quat, Vector((1, 1, 1))
        if pose and part.name in pose:
            d = pose[part.name]
            if "p" in d:
                p = p + Vector(d["p"])
            if "r" in d:
                q = q @ d["r"]
            if "s" in d:
                s = Vector(d["s"])
        return Matrix.LocRotScale(p, q, s)

    def world_matrix(self, name, pose=None):
        part = self.parts[name]
        m = self.local_matrix(part, pose)
        if part.parent:
            m = self.world_matrix(part.parent, pose) @ m
        return m

    def world_point(self, name, local):
        return self.world_matrix(name) @ Vector(local)

    def to_local(self, name, world):
        return self.world_matrix(name).inverted() @ Vector(world)

    def world_quat(self, name):
        return self.world_matrix(name).to_quaternion()

    def box_corners(self, name, b):
        m = self.world_matrix(name) @ Matrix.LocRotScale(b["c"], b["q"], Vector((1, 1, 1)))
        h = b["s"] / 2
        return [m @ Vector((sx * h.x, sy * h.y, sz * h.z)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]

    def bounds(self):
        lo = Vector((1e9, 1e9, 1e9))
        hi = -lo
        for name, part in self.parts.items():
            for b in part.boxes:
                for v in self.box_corners(name, b):
                    lo = Vector(map(min, lo, v))
                    hi = Vector(map(max, hi, v))
        return lo, hi

    def ground(self, part_name):
        """Sube/baja la parte indicada para que el punto más bajo quede en y=0."""
        lo, _ = self.bounds()
        self.parts[part_name].pivot.y -= lo.y

    def box_count(self):
        return sum(len(p.boxes) for p in self.parts.values())

    # -- animación ------------------------------------------------------------
    def sample(self):
        """Pose local completa por frame: {parte: [[px,py,pz,qx,qy,qz,qw,sx,sy,sz], ...]}."""
        tracks, glow = {}, {}
        if not self.animate:
            return tracks, glow
        poses = [self.animate(f / self.frames) for f in range(self.frames)]
        names = sorted({n for pose in poses for n in pose})
        for n in names:
            part = self.parts[n]
            rows = []
            for pose in poses:
                d = pose.get(n, {})
                p = part.pivot + Vector(d.get("p", (0, 0, 0)))
                q = part.quat @ d.get("r", Quaternion())
                s = Vector(d.get("s", (1, 1, 1)))
                rows.append([p.x, p.y, p.z, q.x, q.y, q.z, q.w, s.x, s.y, s.z])
            tracks[n] = rows
        if self.glow:
            for f in range(self.frames):
                for tag, v in self.glow(f / self.frames).items():
                    glow.setdefault(tag, []).append(v)
        return tracks, glow

    # -- exportación JSON -------------------------------------------------------
    def to_json(self):
        r = lambda v: [round(x, 4) for x in v]
        qv = lambda q: r((q.x, q.y, q.z, q.w))
        tracks, glow = self.sample()
        lo, hi = self.bounds()
        return {
            "name": self.name,
            "fps": self.fps,
            "frames": self.frames,
            "bounds": [r(lo), r(hi)],
            "parts": [
                {
                    "name": p.name,
                    "parent": p.parent,
                    "p": r(p.pivot),
                    "q": qv(p.quat),
                    "boxes": [
                        dict(
                            c=r(b["c"]), s=r(b["s"]), q=qv(b["q"]), col=b["col"],
                            **({"emit": b["emit"]} if b["emit"] else {}),
                            **({"tag": b["tag"]} if b["tag"] else {}),
                            **({"metal": b["metal"]} if b["metal"] else {}),
                        )
                        for b in p.boxes
                    ],
                }
                for p in self.parts.values()
            ],
            "tracks": {k: [r(row) for row in v] for k, v in tracks.items()},
            "glow": {k: r(v) for k, v in glow.items()},
            **({"stage": self.stage} if self.stage else {}),
            **({"meta": self.meta} if self.meta else {}),
        }

    def save_json(self, path):
        with open(path, "w") as f:
            json.dump(self.to_json(), f, separators=(",", ":"))


# -- helpers de forma -----------------------------------------------------------

def stepped_fin(m, part, base, length, height, steps, sweep, width, col, axis_up=1, taper=0.75):
    """Aleta triangular hecha de escalones de cajas (para no usar curvas)."""
    for j in range(steps):
        k = j / steps
        L = max(length * (1 - k * taper) - k * 0.1, 0.15)
        y = base[1] + axis_up * (j + 0.5) * height / steps
        z = base[2] - k * sweep
        w = width * (1 - 0.4 * k)
        m.box(part, (base[0], y, z), (w, abs(height) / steps + 0.02, L), col)


def teeth_row(m, part, points, size, col, up=False):
    """Dientes en diamante (cubo girado 45°) -> forma pinchuda solo con cajas."""
    for (x, y, z) in points:
        m.box(part, (x, y, z), (size, size, size * 0.6), col, r=(0, 0, 45))


def segment(m, part, a, b, thick, col, **kw):
    """Barra (caja) que va del punto a al punto b."""
    a, b = Vector(a), Vector(b)
    d = b - a
    if d.length < 1e-6:
        return
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    tw = thick if isinstance(thick, (tuple, list)) else (thick, thick)
    m.box(part, (a + b) / 2, (tw[0], tw[1], d.length + tw[0] * 0.6), col, r=q, **kw)


def polyline(m, part, pts, thick, col, closed=False, **kw):
    pts = list(pts)
    n = len(pts) if closed else len(pts) - 1
    for i in range(n):
        segment(m, part, pts[i], pts[(i + 1) % len(pts)], thick, col, **kw)


def ring(m, part, radius, count, thick, col, center=(0, 0, 0), rot=(0, 0, 0), **kw):
    """Anillo hecho de segmentos de caja (en el plano XZ, luego girado)."""
    rq = quat(rot)
    c = Vector(center)
    pts = [c + rq @ Vector((math.cos(i / count * math.tau) * radius, 0, math.sin(i / count * math.tau) * radius))
           for i in range(count)]
    polyline(m, part, pts, thick, col, closed=True, **kw)


def star(m, part, c, size, col, **kw):
    """Destello de 4 puntas: dos cajas finas cruzadas + núcleo."""
    m.box(part, c, (size * 0.14, size, size * 0.14), col, **kw)
    m.box(part, c, (size, size * 0.14, size * 0.14), col, **kw)
    m.box(part, c, (size * 0.3, size * 0.3, size * 0.3), col, r=(0, 0, 45), **kw)


def crystal(m, part, c, width, height, col, rot=(0, 0, 0), **kw):
    """Cristal octaédrico hecho de capas de cajas (punta arriba y abajo)."""
    rq = quat(rot)
    c = Vector(c)
    steps = 7
    for j in range(steps):
        k = (j + 0.5) / steps * 2 - 1  # -1..1
        w = width * (1 - abs(k)) ** 0.9 + 0.04
        y = k * height / 2
        m.box(part, c + rq @ Vector((0, y, 0)), (w, height / steps + 0.01, w), col, r=rq @ quat((0, 45, 0)), **kw)


def egg_radius(y, R, h_bottom, h_top):
    h = h_top if y > 0 else h_bottom
    t = y / h
    if abs(t) >= 1:
        return 0.0
    return R * math.sqrt(1 - t * t) * (1 + 0.06 * (-t))  # algo más ancho abajo


def egg_voxels(R, h_bottom, h_top, v):
    """Voxels de la cáscara de un huevo: devuelve [(pos, normal)]."""
    inside = lambda x, y, z: x * x + z * z <= egg_radius(y, R, h_bottom, h_top) ** 2
    n = int(math.ceil(max(R * 1.1, h_top, h_bottom) / v)) + 1
    out = []
    for iy in range(-n, n + 1):
        for ix in range(-n, n + 1):
            for iz in range(-n, n + 1):
                x, y, z = ix * v, iy * v, iz * v
                if not inside(x, y, z):
                    continue
                if all(inside(x + dx * v, y + dy * v, z + dz * v) for dx, dy, dz in
                       ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
                    continue
                nrm = Vector((x, y * (R / (h_top if y > 0 else h_bottom)) ** 2, z))
                out.append((Vector((x, y, z)), nrm.normalized() if nrm.length else Vector((0, 1, 0))))
    return out


def egg_surface(R, h_bottom, h_top, y, ang, off=0.0):
    r = egg_radius(y, R, h_bottom, h_top) + off
    return Vector((math.sin(ang) * r, y, math.cos(ang) * r))
