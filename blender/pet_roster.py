"""Catálogo de mascotas: 4 por huevo, cada una diseñada a mano (ver pet_roster_*.py)."""

import importlib

EGG_TINT = {}
ROSTER = {}
for _mod in ("pet_roster_a", "pet_roster_b", "pet_roster_c", "pet_roster_d", "pet_roster_e"):
    try:
        _m = importlib.import_module(_mod)
    except ModuleNotFoundError as e:
        if e.name != _mod:
            raise
        continue
    ROSTER.update(_m.R)
    EGG_TINT.update(_m.TINT)
