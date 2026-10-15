# Animations: huevos y modelos de bloques (Blender + visor web)

Modelos 3D hechos **solo de cubos**, generados con Python dentro de Blender, con
animación en bucle y un visor web con VFX (bloom, partículas, haz de luz y
animación de "romper el huevo").

- **627 modelos:** 121 huevos (7 destacados, 94 de colección por rareza, 20 de
  renacimiento), 484 mascotas diseñadas una a una (4 por huevo, todas de especies
  distintas, con la temática y la calidad de su huevo; las de huevos secretos y
  hacker son gigantes), 20 animales de renacimiento esculpidos con vóxeles, el Tiburón-Dino y
  el Buzón-Monstruo.
- **Huesos:** cada modelo de Blender tiene esqueleto (un hueso por parte), malla
  pesada a los huesos y la animación en keyframes de los huesos.
- **Guía para otra IA:** [`docs/GUIA_HUEVOS_PARA_IA.md`](docs/GUIA_HUEVOS_PARA_IA.md)
  (método, estilo, recetas y escala por rareza; con las capturas de referencia
  en `docs/referencias/`).

## Estructura

```
blender/
  voxel.py         constructor: partes, cajas, animación muestreada, helpers (segment, ring, crystal, star, egg_voxels…)
  eggs.py          huevos Celestial y de Hielo
  eggs_themes.py   huevos Infierno, Pantano, Galaxia, Tormenta y Sakura (+ piezas: cuernos, llamas, hojas, setas, nubes, rayos…)
  tiers.py         huevos de colección y de renacimiento generados por rareza (catálogo SPECS)
  sculpt.py        escultura con vóxeles (elipsoides y cápsulas -> cubitos de superficie)
  rebirth.py       los 20 animales de renacimiento (animals.py: primera versión, usada en 1-4)
  pets.py          mascotas: calidad por rareza, animación, peana y escenario
  pet_roster_*.py  catálogo a mano de las 484 mascotas (especie, proporciones, rasgos, colores)
  pk_*.py          planos de cuerpo: cuadrúpedos, lagartos, dinosaurios, aves, peces, insectos, robots…
  shark_dino.py    tiburón-dinosaurio
  mailbox_monster.py  buzón-monstruo
  build.py         construye en Blender y exporta .blend / .glb / .json / .png
tools/make_catalog.py   catálogo, miniaturas y paquetes por rareza
viewer/            visor web (three.js r149 incluido en vendor/) + voxelstage.js
exports/           resultados: .json (todos), .blend con esqueleto (huevos y animales), .glb (animales),
                   .png (huevos y animales), thumbs/ (todos) y catalog.json
docs/              guía, referencias y capturas de resultados
```

## Uso

```bash
# Blender 4.2+ (o el módulo de Python: pip install bpy==5.2.2 con Python 3.13)
python blender/build.py                     # todos los modelos (o: blender -b -P blender/build.py --)
python blender/build.py egg_celestial --samples 64 --res 1200
python blender/build.py --json-only         # solo los JSON para el visor (segundos)
python3 tools/make_catalog.py               # catálogo y miniaturas

# Visor web
python3 -m http.server 8000                 # desde la raíz del repo
# abre http://localhost:8000/viewer/
```

En Blender cada modelo es un empty raíz con un empty por parte (los pivotes
animados) y una malla por parte con un modificador de bisel. La animación está
en keyframes (bucle de 4 s en los huevos) y se exporta también en el `.glb`.
