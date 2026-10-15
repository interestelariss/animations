"""Atajos para escribir el catálogo de mascotas a mano (pet_roster*.py)."""


def Q(name, **kw):
    return (name, "quad", kw)


def LZ(name, **kw):
    return (name, "lizard", kw)


def TH(name, **kw):
    return (name, "theropod", kw)


def B(name, **kw):
    return (name, "bird", kw)


def F(name, **kw):
    return (name, "fish", kw)


def BG(name, **kw):
    return (name, "bug", kw)


def CR(name, **kw):
    return (name, "crust", kw)


def CE(name, **kw):
    return (name, "ceph", kw)


def CH(name, **kw):
    return (name, "chain", kw)


def SH(name, **kw):
    return (name, "shell", kw)


def FR(name, **kw):
    return (name, "frog", kw)


def BP(name, **kw):
    return (name, "biped", kw)


def BL(name, **kw):
    return (name, "blob", kw)


def BT(name, **kw):
    return (name, "bat", kw)


def sk(base, belly=None, pat=None, pc=None, pc2=None, ps=1.0, back=None, seed=0.0, region=None):
    d = dict(base=base, pat=pat, pc=pc, pc2=pc2, ps=ps, seed=seed)
    if belly:
        d["belly"] = belly
    if back:
        d["back"] = back
    if region:
        d["region"] = region
    return d


# --- zonas de la cabeza (p, n, hs, sn) -> color | None
def muzzle(col, k=0.42):
    return lambda p, n, hs, sn: col if (p.z > k * hs and p.y < 0.02 * hs) else None


def mask(col):  # mapache: antifaz
    return lambda p, n, hs, sn: col if (abs(p.y - 0.12 * hs) < 0.11 * hs and n.z > 0.2 and p.z > 0.15 * hs and abs(p.x) > 0.05 * hs) else None


def eyepatch(col):  # panda
    return lambda p, n, hs, sn: col if (abs(abs(p.x) - 0.25 * hs) < 0.13 * hs and abs(p.y - 0.13 * hs) < 0.13 * hs and n.z > 0.1) else None


def blaze(col):  # caballo: lista blanca
    return lambda p, n, hs, sn: col if (abs(p.x) < 0.09 * hs and n.z > 0.1 and n.y > -0.3) else None


def face(col, k=0.25):
    return lambda p, n, hs, sn: col if (n.z > 0.35 and p.z > k * hs) else None


def combo(*fns):
    def f(p, n, hs, sn):
        for g in fns:
            r = g(p, n, hs, sn)
            if r is not None:
                return r
        return None
    return f


def lower(col, y):  # para pieles de cuerpo: todo lo que esté por debajo de y (local)
    return lambda p, n: col if p.y < y else None
