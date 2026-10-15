# Cómo crear huevos mágicos 3D hechos de bloques (guía para una IA)

> **Para la IA que lee esto:** este documento explica exactamente cómo se han
> creado 7 huevos mágicos 3D (estilo "pet egg" de Roblox) y cómo crear más con
> otras temáticas. Junto a este texto te paso unas imágenes. Las de
> **referencia** (`docs/referencias/`) marcan el estilo que hay que conseguir.
> Las de **resultado** (`docs/resultados/`) son los huevos que salieron con este
> método. Léelo entero antes de empezar. Al final tienes una plantilla y una
> lista de comprobación.

---

## 0. Imágenes que acompañan a este texto

**Referencias (el objetivo de estilo):**

| Archivo | Qué muestra | Qué hay que copiar de ella |
|---|---|---|
| `ref1_huevo_celestial.png`, `ref5_…`, `ref6_…` | Huevo azul pixelado con jaula dorada, halo, alas blancas y anillos de neón | Cáscara hecha de **cubitos** azules con destellos blancos, **jaula dorada de rombos**, emblema de cristal en el frente, gema arriba, **halo dorado**, **alas de plumas** grandes, **anillos de neón** cruzados (turquesa y rosa) y un anillo brillante en el suelo |
| `ref3_huevo_cristal.png`, `ref7_…`, `ref8_…` | Huevo azul oscuro con corona de cristales, alas de hielo, espirales y estanque | **Corona de cristales**, alas de **esquirlas**, **espirales de energía** alrededor, partículas y cristales flotando, **base de agua** con ondas |
| `ref2_tiburon_dino.png`, `ref4_buzon.png` | Otros modelos del mismo encargo | Lenguaje "todo de bloques" con buenos materiales y luz |

**Resultados (lo que salió con este método):** `docs/resultados/web_egg_*.jpg`
(visor web) y `exports/egg_*.png` (render de Blender con Cycles).

---

## 1. El estilo, en una frase

**"Huevo de mascota de Roblox, construido con bloques como un set de LEGO o un
modelo de MagicaVoxel, presentado como pieza de colección en una vitrina
mágica."**

Rasgos que lo definen:

1. **Todo son cubos.** Cada pieza es una caja (cubo estirado o girado). No hay
   esferas ni cilindros de verdad: lo "redondo" (la cáscara, los anillos, el
   halo) se hace con **vóxeles** o con **segmentos de caja** puestos en círculo.
   Las curvas se notan escalonadas, y eso es buscado: es el encanto del estilo.
2. **Silueta de trofeo:** pedestal → huevo flotando → alas a los lados →
   corona/gema arriba → halo o elemento flotante encima. Siempre se lee como un
   rombo vertical, simétrico.
3. **Capas de detalle:** cáscara con patrón + estructura encima (jaula, bandas,
   lianas, ramas) + emblema frontal. Nunca dejes la cáscara lisa.
4. **Un color dominante, un metal y un color de energía.** Ejemplo del
   Celestial: azul (cáscara) + oro (jaula/halo) + turquesa/rosa (neón).
5. **Energía contenida:** hay brillo y VFX, pero **poco**. El dueño del
   proyecto pidió expresamente que los huevos sean **muy poco brillosos**: los
   colores y la forma tienen que leerse, el resplandor solo acompaña (sección 6).
6. **Siempre en movimiento:** el huevo flota, las alas aletean, los anillos
   giran, la gema rota, las estrellas titilan. Bucle perfecto de 4 s.

---

## 2. Anatomía de un huevo (las 9 capas)

Construye siempre estas capas, en este orden. Las medidas son en "studs"
(1 unidad ≈ 1 stud de Roblox), con Y hacia arriba y el frente hacia +Z.

| # | Capa | Medidas típicas | Notas |
|---|---|---|---|
| 1 | **Base / pedestal** | 4,4–7 de ancho, 0,4–1,8 de alto | Octógono hecho de dos cuadrados girados 45°, estanque de vóxeles, asteroide, roca… Le da contexto a la temática |
| 2 | **Anillos de suelo** | radio 1,6–3,7 | Anillos finos de segmentos emisivos que giran despacio |
| 3 | **Cáscara de vóxeles** | R=2,0, alto abajo 2,2, alto arriba 2,85, vóxel 0,2 | 1.500–3.000 cubos. Solo la capa exterior. El color sale de una función (sección 3.2) |
| 4 | **Estructura sobre la cáscara** | se separa 0,1–0,15 de la superficie | Jaula de rombos (hélices cruzadas), bandas ecuatoriales, lianas, ramas, banda de pinchos |
| 5 | **Emblema frontal** | ~1,2 × 1,8, a la altura y≈0,3 | Rombo con marco de metal y cristal en capas por dentro; o espiral galáctica, ojo, rayo, flor… |
| 6 | **Corona / remate** | encima del todo | Gema octaédrica, corona de cristales, llamas, setas, luna, nube… |
| 7 | **Alas** | 3–4 de envergadura por lado | Plumas, esquirlas, membrana de murciélago, hojas, pétalos. Salen de atrás (z≈−0,8), abiertas hacia atrás unos 22° |
| 8 | **Órbitas** | radio 2,9–3,9, inclinadas 60–75° | Uno o dos anillos de neón con una "cabeza de cometa" (3–4 cubos decrecientes), espirales, anillos planetarios |
| 9 | **Elementos flotantes** | alrededor, radio 3–5 | Estrellas de 4 puntas, esquirlas, lunas, runas, que rotan, titilan u orbitan |

El huevo **flota** sobre la base (el centro está en y≈4,5; el pedestal termina
en y≈1). El hueco se rellena con un **haz de luz** o un anillo brillante.

---

## 3. Método de construcción (procedural, en Python + Blender)

Nada se modela a mano: cada huevo es una **función de Python** que coloca cajas.
De esa misma definición salen la escena de Blender (`.blend`, `.glb`, render) y
un JSON para el visor web. El código real está en el repo:

- `blender/voxel.py`: el constructor (partes, cajas, animación, helpers de forma)
- `blender/eggs.py`: Celestial y Hielo
- `blender/eggs_themes.py`: Infierno, Pantano, Galaxia, Tormenta y Sakura
- `blender/build.py`: construye en Blender y exporta `.blend`, `.glb`, `.json` y `.png`
- `viewer/voxelstage.js`: visor three.js con los VFX

### 3.1 Modelo de datos

```text
Modelo
 └─ Parte (pivote: posición + rotación; padre opcional)   ← se anima
     └─ Caja (centro, tamaño, rotación, color, emisión, etiqueta, metal)
```

- Las **partes** son lo que se mueve: `egg` (todo el huevo flota), `shell`
  (la cáscara, que es lo que explota al romperse), `wing_L`/`wing_R`, `halo`,
  `topgem`, `orbit1`, `star0…`, `flame0…`, `planet0…`
- Cada **caja** lleva una **etiqueta de brillo** (`tag`) como `core`, `neon`,
  `twinkle`, `lava`, `vein`… La animación cambia la intensidad de cada etiqueta
  por separado, así que todo lo que tiene la misma etiqueta late a la vez.
- `metal=1` hace que la caja sea metálica (oro, hierro, acero), con reflejos
  del entorno.

### 3.2 La cáscara de vóxeles (la clave del estilo)

Perfil de huevo: elipsoide con media altura distinta arriba (más puntiaguda) y
abajo, y un poco más ancho en la base:

```python
def egg_radius(y, R, h_bottom, h_top):
    h = h_top if y > 0 else h_bottom
    t = y / h
    if abs(t) >= 1:
        return 0.0
    return R * math.sqrt(1 - t * t) * (1 + 0.06 * (-t))

def egg_voxels(R, h_bottom, h_top, v):
    """Solo los vóxeles de la superficie: dentro del huevo y con algún vecino fuera."""
    inside = lambda x, y, z: x*x + z*z <= egg_radius(y, R, h_bottom, h_top) ** 2
    n = int(math.ceil(max(R * 1.1, h_top, h_bottom) / v)) + 1
    out = []
    for iy in range(-n, n + 1):
        for ix in range(-n, n + 1):
            for iz in range(-n, n + 1):
                x, y, z = ix * v, iy * v, iz * v
                if not inside(x, y, z):
                    continue
                if all(inside(x + dx*v, y + dy*v, z + dz*v) for dx, dy, dz in
                       ((1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1))):
                    continue   # está tapado por todos lados: no se ve
                out.append(Vector((x, y, z)))
    return out
```

Valores buenos: `R=2.0, h_bottom=2.2, h_top=2.85, v=0.2` (unos 2.000 cubos).

**El color de cada vóxel decide la temática.** Se calcula con una función que
recibe la posición `p`, la altura normalizada `t` (0 abajo, 1 arriba) y el
ángulo `ang` alrededor del eje (0 = frente). Herramientas:

- `_hash(x,y,z)`: número pseudoaleatorio estable entre 0 y 1 por vóxel. Sirve
  para mezclar 3–5 tonos parecidos (efecto "pixel art") y para salpicar
  destellos (`h > 0.975` → vóxel blanco emisivo con etiqueta `twinkle`).
- `fbm(p)`: ruido suave (value noise de 2 octavas). Sirve para manchas (musgo,
  nebulosas, nubes) con `fbm > 0.6`, y para **grietas/vetas** con
  `abs(fbm - 0.5) < 0.03`, que dibuja líneas finas y ramificadas (lava,
  rayos, kintsugi dorado).
- `t`: degradados verticales (base violeta, punta más clara, barro abajo).
- `ang` y `p.y`: patrones geométricos (escamas por filas desplazadas, un rombo
  frontal como `abs(ang)/0.62 + abs(p.y-0.3)/1.45 ≈ 1`).

Ejemplo (Infierno):

```python
def shell(p, n, t, ang):
    f = fbm(p, 1.15, 3.0)
    if abs(f - 0.5) < 0.028:                      # grieta de lava (línea fina)
        return ("#ff6a14", 3.0, "lava")
    if abs(f - 0.5) < 0.055:                      # borde de la grieta, más oscuro
        return ("#c2300c", 1.2, "lava")
    if t < 0.18 and _hash(p.x, p.y, p.z) > 0.55:  # la base del huevo arde
        return ("#ff4a10", 1.5, "lava")
    obsidiana = ["#1b0e10", "#25110f", "#2f1612", "#140a0b", "#3a1a14"]
    return obsidiana[int(_hash(p.x, p.y, p.z) * 97) % 5]
```

### 3.3 Helpers de forma (todo con cajas)

| Helper | Qué hace | Para |
|---|---|---|
| `segment(a, b, grosor)` | Una caja estirada del punto a al b | Barras, huesos, lianas, rayos |
| `polyline(puntos)` | Varios `segment` seguidos | Jaulas, espirales, marcos de emblema |
| `ring(radio, n, grosor, centro, rot)` | n segmentos en círculo | Halos, órbitas, anillos de suelo, bandas |
| `egg_surface(y, ang, separación)` | Punto sobre la cáscara | Colocar jaulas, lianas y ramas pegadas al huevo |
| `crystal(c, ancho, alto)` | 7 capas de cubos girados 45°, anchas en el centro y finas en las puntas | Gemas, esquirlas, alas de hielo, corona |
| `star(c, tamaño)` | Dos cajas finas cruzadas + núcleo girado 45° | Destellos de 4 puntas |
| `_wing(filas, hueso)` | Plumas en abanico: cada pluma son 3 cajas que se estrechan + una punta. 3 filas: primarias largas, secundarias y coberteras | Alas de ángel, de trueno o de pétalos |
| `membrane_wing` | Dedos de hueso + membrana rellena con barras y borde festoneado | Alas de murciélago (Infierno) |
| `leaf`, `flower`, `mushroom`, `cloud`, `bolt`, `horn`, `flame`, `voxel_ball` | Piezas temáticas | Pantano, Sakura, Tormenta, Infierno, Galaxia |

**Jaula de rombos** (la del Celestial): 8 hélices que suben girando +90° y otras
8 que giran −90°. Al cruzarse forman rombos. Se añaden una banda ecuatorial
gruesa, collares arriba y abajo y tachuelas en los cruces.

```python
for sgn in (1, -1):
    for k in range(8):
        pts = [egg_surface(R, HB, HT, y0 + (y1 - y0) * u, k/8*TAU + sgn*u*TAU/4, 0.13)
               for u in (i / 28 for i in range(29))]
        polyline(m, "cage", pts, 0.13, GOLD, metal=1)
```

**Alas de plumas:** el ángulo de cada pluma va de −45° (base, hacia fuera y
abajo) a +83° (punta, hacia arriba). El largo sigue una curva
`sin(k·π·0,85 + 0,25)`: cortas en la base, largas en el centro y medianas en la
punta. Las plumas son **anchas (0,7) y se solapan**. Si quedan estrechas
parecen palitos sueltos, y ese fallo ya ocurrió en la primera versión.

### 3.4 Animación (bucle de 96 fotogramas a 24 fps = 4 s)

Una función `animate(t)` con `t` en [0,1) devuelve, para cada parte, un
desplazamiento, una rotación y una escala. Se **muestrea** en todos los
fotogramas y se guarda tal cual en el JSON y como keyframes en Blender. Usa
siempre `sin(t·2π·n)` con `n` entero para que el bucle cierre perfecto.

| Elemento | Movimiento |
|---|---|
| Huevo | Flota ±0,18 en Y (2 ciclos), se balancea 2–5° |
| Alas | Aletean ±10–14° en Z y ±8–10° en Y (2–4 ciclos) |
| Gema superior | Gira 720° y sube y baja |
| Halo | Gira 360° con un pequeño cabeceo |
| Órbitas | Giran en sentidos opuestos (720°) |
| Estrellas | Titilan con la escala (0,55–1) y giran |
| Llamas | Escala Y alta frecuencia (parpadeo) con volumen conservado (`x = z = 1/√y`) |
| Ojos | Parpadeo de 0,08 s una vez por bucle (escala Y → 0,1) |
| Ondas de agua | Escala de 0,6 a 3,4 en bucle, con el brillo bajando a la vez |

Una función `glow(t)` devuelve un multiplicador por etiqueta (por ejemplo,
`core` = 0,75–1, `neon` parpadea rápido, `twinkle` = 0,5–1). Los rayos de la
Tormenta usan destellos bruscos: 2 golpes por bucle con parpadeo.

---

## 4. Las 7 recetas (lo que lleva cada huevo)

### 4.1 Celestial (`egg_celestial`): referencia principal
- **Cáscara:** 5 azules (`#2f63f5 #3b74ff #4985ff #2a56e6 #5a97ff`), base
  violeta `#5a4ef0`, punta más clara `#79b8ff`, 2,5 % de destellos blancos emisivos
- **Estructura:** jaula dorada de rombos (`#f6c64a`, metal) + banda ecuatorial
  + 16 tachuelas + corona escalonada
- **Emblema:** rombo dorado doble con cristal menta `#9dfbe6` en 9 capas y una cruz de luz
- **Remate:** gema octaédrica menta con núcleo blanco y **halo dorado** encima
- **Alas:** 3 filas de plumas blancas a celestes con hueso y cuchillas doradas
- **Órbitas:** turquesa `#33ffd0` y rosa `#ff7ce0` con cabeza de cometa
- **Base:** pedestal octogonal azul noche con remates de oro, anillos turquesa y haz de luz
- **Extras:** 7 estrellas que titilan

### 4.2 Hielo (`egg_ice`)
- Escamas azul marino en filas desplazadas, con borde oscuro (`#1b3170 #223e88 #2a4ea3`, borde `#121f4d`)
- Vetas cian `#5ff4ff` que dibujan un rombo frontal y un anillo ecuatorial
- Cristal frontal facetado en 3 profundidades. Corona de 7 púas de hielo
- Alas de esquirlas en 2 capas. Dos espirales (cian y lavanda) y un halo lavanda
- Estanque de vóxeles con borde de piedra, 3 ondas que se expanden y 8 esquirlas orbitando

### 4.3 Infierno (`egg_inferno`)
- Obsidiana con **grietas de lava** de ruido (`abs(fbm-0.5)`) y base incandescente
- Ojo demoníaco amarillo con pupila de rendija que parpadea, y banda de hierro con pinchos
- **Cuernos** curvos con anillos y punta de lava. **Corona de 5 llamas** que parpadean
- **Alas de murciélago** de membrana granate. Anillo de brasas con 6 runas-estrella
- Base de obsidiana escalonada, río de lava y rocas puntiagudas con la punta encendida

### 4.4 Pantano (`egg_swamp`)
- Verdes musgosos con manchas de musgo claro y barro, y esporas lima brillantes
- 3 **lianas** en espiral con hojitas. Cristal tóxico con marco de raíces
- **Setas bioluminiscentes** (turquesa y violeta) en la cima y en los costados
- **Alas de hojas** con nervio central
- Estanque turbio, tocón, **nenúfares** con flor rosa y **espadañas**. Luciérnagas

### 4.5 Galaxia (`egg_galaxy`)
- Espacio índigo con **nebulosas** magenta y cian (2 ruidos) y estrellas de 2 tamaños
- **Galaxia espiral** de 2 brazos en el frente, que gira
- **Anillos planetarios** de 4 bandas. **Luna creciente** de vóxeles (esfera menos esfera desplazada)
- **Alas de constelación:** esquirlas violetas con una estrella en cada punta, unidas por una línea
- 3 **planetas** de vóxeles a rayas orbitando y un **asteroide** como base

### 4.6 Tormenta (`egg_storm`)
- Gris tormenta con nubes claras de ruido y **grietas-rayo** amarillas
- Emblema de rayo dorado en un hexágono de acero
- **Nubarrón** encima con rayos colgando, y 4 **rayos** que caen al suelo con destellos bruscos
- Alas de plumas gris acero con puntas amarillas y un rayo recorriendo el ala
- Anillo de nubes girando y plataforma de roca con charcos. Lluvia

### 4.7 Sakura (`egg_sakura`)
- Porcelana rosa pálido con manchas rosas y **vetas de kintsugi** doradas metálicas
- 2 **ramas de cerezo** envolviendo el huevo, con flores de 5 pétalos orientadas hacia fuera
- Gran flor frontal con pentágono de oro. Corona de flores con **kanzashi** (aguja de oro con colgantes)
- **Alas de pétalos** rosas con hueso dorado. Anillo de pétalos orbitando
- Estanque **koi** con peces, tarima de madera y **farolillo de piedra** encendido. Pétalos cayendo

---

## 5. Visor web y VFX (three.js r149, sin addons)

Archivo: `viewer/voxelstage.js`. Puntos clave:

1. **InstancedMesh por parte y material:** 2.000–3.000 cubos van fluidos. Una
   sola `BoxGeometry(1,1,1)` y cada instancia con su matriz
   (posición, rotación y escala de la caja).
2. **Bloom HDR propio:** la escena se renderiza a un render target `HalfFloat`
   con MSAA. Luego un pase de brillo (umbral), 5 niveles de blur gaussiano
   separable a mitad de resolución cada uno, y una composición con tone
   mapping ACES, conversión a sRGB y una viñeta suave.
3. **Entorno PMREM** generado con una esfera degradada y unos paneles
   blancos. Sin él, el oro metálico se ve negro.
4. `ColorManagement.legacyMode = false` para que los colores hex sean
   correctos. **Ojo:** en r149, sin `physicallyCorrectLights`, las luces se
   multiplican por π, así que hay que dividir las intensidades entre π. Si no,
   todo sale quemado (otro fallo que ya pasó).
5. **Partículas** (`THREE.Points` aditivos con sprite de punto suave, destello
   de 4 puntas o cuadrado), en 4 tipos: `rise` (suben, para brasas y
   chispas), `snow` (caen, para nieve, lluvia y pétalos), `orbit` (giran) y
   `float` (flotan, para luciérnagas y polvo de estrellas).
6. **Brillo en el suelo** (degradado radial aditivo), **haz de luz** (cilindro
   abierto con degradado) y **anillos** del modelo.
7. **Romper el huevo** (botón): de 0 a 1,1 s el huevo tiembla cada vez más y
   el brillo sube. A 1,1 s hay un destello de pantalla, una onda expansiva en
   el suelo y 2 estallidos de partículas (en los colores del tema). De 1,1 a
   2,0 s cada vóxel de la cáscara sale disparado según su normal, girando.
   De 2,0 a 3,0 s todos vuelven a su sitio.
8. Cámara orbital (arrastrar y rueda), giro automático y vistas
   Frente / Lado / 3/4.

Cada huevo exporta en su JSON un bloque `stage` con su fondo (degradado),
niebla, luces de color, partículas, color del estallido y vistas. Así el visor
no necesita código por huevo.

---

## 6. Regla de brillo (muy importante)

El dueño del proyecto pidió **huevos muy poco brillosos**. Valores que funcionan:

- Emisión efectiva de las cajas brillantes: `emit × 0,2` aproximadamente
  (en el código, `emitScale ≈ 0,4` multiplicado por un factor global de 0,45)
- Bloom: intensidad ≈ 0,2, umbral ≈ 1,5 (solo brilla de verdad el neón)
- Haz de luz y brillo de suelo al 45 % de su opacidad original
- Partículas al 60 % de intensidad
- Plumas y piedras claras: nunca blanco puro bajo luz fuerte. Mejor
  `#f4fbff`, `#e4f5ff`…
- En Blender: emisión del material × 0,35

Prueba rápida: si en una captura no distingues las plumas de las alas una a una
o la jaula dorada se convierte en una mancha de luz, **está demasiado brillante**.

---

## 7. Plantilla para un huevo nuevo

```python
def build_<tema>():
    R, HB, HT, V, CY = 2.0, 2.2, 2.85, 0.2, 4.5

    def shell(p, n, t, ang):
        # 1) destellos raros   2) grietas/vetas (abs(fbm-0.5) < 0.03)
        # 3) manchas (fbm > 0.6)   4) degradado por t   5) mezcla de 3-5 tonos con _hash
        ...

    m = egg_scene("egg_<tema>", R, HB, HT, V, CY, shell)
    # 4. estructura sobre la cáscara (polyline sobre egg_surface, ring)
    # 5. emblema frontal (parte "emblem" en z = egg_radius(y) + 0.1)
    # 6. corona/remate (parte propia, animada)
    # 7. alas (parte wing_L / wing_R, pivote (±1.55, 0.6, -0.8), rot (0, ∓22, ±8))
    # 8. órbitas (ring inclinado 60-75°, en parte propia que gira)
    # 9. flotantes (partes con estrellas/cristales)
    # 1-2. base y anillos de suelo en "root"

    def animate(t): ...   # flotar, aletear, girar, titilar (múltiplos enteros de 2π)
    def glow(t): ...      # multiplicador por etiqueta
    m.animate, m.glow = animate, glow
    m.stage = {...}       # fondo, luces, partículas, colores del estallido
    return m
```

**Cómo elegir la paleta de un tema nuevo:**
1. Material de la cáscara: 3–5 tonos muy cercanos del color dominante, más un
   tono oscuro para bordes y grietas.
2. Un metal o material de estructura (oro, hierro, madera, raíz, acero).
3. Un color de energía saturado y emisivo para vetas, emblema, órbitas y
   partículas. Opcionalmente un segundo color de energía complementario
   (turquesa con rosa, cian con lavanda, lima con turquesa).
4. Fondo del visor: degradado del mismo tono que la temática pero casi negro,
   para que el huevo destaque.

---

## 8. Escala por rareza (colección del juego: 45 huevos más)

En el juego los huevos tienen rareza. **Cuanto más raro, más piezas, más
animación y más VFX.** Un común tiene que verse claramente "básico" al lado de
un legendario. Generador: `blender/tiers.py` (catálogo `SPECS` con 45 huevos).

| Nivel | Rareza | Cáscara | Piezas | Animación | VFX en el visor |
|---|---|---|---|---|---|
| 0 | **Común** (10) | Vóxel grande (0,25), patrón simple de 2–3 tonos (manchas, rayas, zigzag) | Peana cuadrada de 2 pisos con una cuna de 8 cubos. El huevo apoyado, sin flotar | Solo un saltito suave | Ninguno: sin partículas ni bloom |
| 1 | **Poco común** (8) | Igual, con un patrón más marcado (diagonales, gajos, panal, flores, grietas) | + Banda metálica en el ecuador y peana octogonal con aro | + Giro lento | 25 partículas blancas |
| 2 | **Raro** (7) | Vóxel 0,22 y destellos sueltos | + Emblema frontal, corona temática (cristales, orejas, seta, corona…). Flota sobre una base temática | + Balanceo y corona girando | Bloom bajo, brillo de suelo, 50 partículas |
| 3 | **Épico** (6) | Escamas, facetas, remolinos… | + Estructura (jaula, lianas, anillos), **alas** (plumas, murciélago, hojas, cristal, aletas, mecánicas), 1 órbita y anillos de suelo | + Aleteo y órbita | 2 sistemas de partículas |
| 4 | **Mítico** (4) | Vóxel 0,2, patrones con vetas emisivas | + Alas más grandes, **flotantes** a su alrededor (esquirlas, burbujas, brasas…) y tentáculos o cuernos | + Flotantes animados | + Haz de luz |
| 5 | **Legendario** (3) | Muy trabajada | + 3 filas de plumas, 2 órbitas y **halo** | Todo | 3 sistemas de partículas |
| 6 | **Secreto** (2) | "Imposible": vacío con grietas violetas, prisma arcoíris | Todo, con remates únicos (ojo, anillo de esquirlas, portal) | Todo | Lo máximo (siempre con brillo contenido) |
| — | **Hacker** (5) | Estética "hacker de Robux": lluvia de código verde, rejilla hexagonal con moneda, glitch magenta/cian, terminal con pantalla, cortafuegos rojo | Alas mecánicas con líneas de neón, antena que parpadea, circuitos sobre la cáscara, cubos binarios y monedas flotando, base tecnológica o de teclado | Como legendario + cursor que parpadea + columnas de código que se encienden por turnos | Partículas binarias, monedas o glitch |

Los 7 huevos hechos a mano (sección 4) son los **destacados**: Celestial,
Galaxia y Sakura (legendarios), Hielo, Infierno y Tormenta (míticos) y Pantano
(épico).

**Catálogo:**
- **Comunes:** Básico, Hierba, Arena, Piedra, Barro, Cielo, Melocotón, Lima, Cacao, Nube
- **Poco comunes:** Bosque, Océano, Calabaza, Brasa, Escarcha, Miel, Arcilla, Pradera
- **Raros:** Coral, Amatista, Tigre, Panal Real, Caramelo, Hongo, Rubí
- **Épicos:** Dragón de Fuego, Rey del Mar, Bosque Encantado, Esmeralda, Mecánico, Unicornio
- **Míticos:** Fénix, Kraken, Dragón Glacial, Gólem de Jade
- **Legendarios:** Sol Dorado, Luna de Plata, Dragón Arcoíris
- **Secretos:** Huevo del Vacío, Huevo Prisma
- **Hacker:** Matrix, Robux Hacker, Error 404, Terminal, Firewall

Cada huevo es una línea de datos: colores de la cáscara, color de acento y de
energía, patrón, base, estructura, corona, alas, flotantes y partículas. El
generador decide qué piezas añadir según el nivel. Para crear un huevo nuevo
basta con añadir una línea a `SPECS`:

```python
S("raro_menta", "Huevo Menta", "raro", ["#9ff0d0", "#8ae6c2", "#b4f6dc"], "#ffffff", "candy",
  base="candy", crown="gem", energy="#5fffc8", metal="#f2c14e")
```

---

## 9. Ideas para más huevos

| Tema | Cáscara | Estructura / emblema | Alas | Base | VFX |
|---|---|---|---|---|---|
| Océano abisal | Azul profundo con escamas y bioluminiscencia | Conchas y perlas, emblema de tridente | Aletas de manta | Arrecife de coral de vóxeles | Burbujas que suben, rayos de luz |
| Desierto / faraón | Arena dorada con jeroglíficos en relieve | Bandas de lapislázuli, ojo de Horus | Alas de halcón doradas | Pirámide escalonada | Arena flotando, brillo de sol |
| Caramelo | Rosa y menta a rayas en espiral | Glaseado goteando, bastones de caramelo | Alas de gominola translúcidas | Pastel de pisos | Confeti cuadrado |
| Mecánico steampunk | Cobre y latón con remaches | Engranajes que giran y tubos | Alas de pistones y plumas de metal | Caldera | Vapor y chispas |
| Bosque otoñal | Madera y hojas naranjas | Ramas con bellotas | Alas de hojas secas | Tocón con setas | Hojas cayendo |
| Arcoíris / unicornio | Blanco nacarado con franjas arcoíris | Cuerno espiral dorado | Plumas pastel | Nube | Estela arcoíris |
| Volcán de cristal | Amatista facetada | Geoda abierta en el frente | Esquirlas violetas | Roca con cristales | Polvo brillante |
| Fantasma / Halloween | Calabaza o lápida con caras talladas | Velas y telarañas | Alas de tela rasgada | Cementerio de bloques | Fuegos fatuos verdes |
| Navidad | Rojo y blanco con cintas | Lazo dorado y acebo | Alas de copos | Montaña de regalos | Nieve |
| Cyberpunk | Negro con circuitos neón | Pantallas y antenas | Alas de hologramas | Plataforma con rejilla | Glitch y líneas de datos |

---

## 10. Lista de comprobación antes de dar un huevo por terminado

- [ ] Todo está hecho de cajas (vóxeles, segmentos o cubos girados)
- [ ] Silueta de trofeo simétrica: base, huevo flotando, alas, corona y elemento superior
- [ ] La cáscara tiene patrón (mezcla de tonos y vetas o manchas) y destellos sueltos
- [ ] Hay estructura sobre la cáscara y un emblema frontal
- [ ] Las alas son llenas, con piezas anchas y solapadas (no "palitos")
- [ ] Ninguna pieza flota suelta sin motivo y las bases de aletas y cuernos están hundidas en el cuerpo
- [ ] Bucle de animación perfecto: flota, aletea, gira y titila
- [ ] Brillo bajo: se distinguen plumas y piezas, y el bloom es solo un halo suave
- [ ] La paleta tiene 1 dominante, 1 metal o estructura y 1–2 de energía
- [ ] La base cuenta la temática (estanque, lava, asteroide, koi…)
- [ ] Tiene partículas del tema y su color de estallido para "romper"
- [ ] El nivel de detalle, animación y VFX corresponde a su rareza (sección 8)

---

## 11. Animales de renacimiento (lo principal del juego)

Archivo: `blender/rebirth.py` (+ `blender/sculpt.py`). Son 20 formas, del
Conejo (renacimiento 1) a la Genesis Beast (20). **Todos llevan el máximo
detalle**, no dependen de rarezas. Del 1 al 4 se usa la primera versión de
bloques (`blender/animals.py`), que gustó más. Del 5 al 20 son **esculturas de
vóxeles**:

- **Escultura de vóxeles:** cada parte se define con elipsoides y cápsulas
  (con ruido para el pelo, la roca o la melena) y se convierte en cubitos de
  superficie (`voxelize`). Cuerpo = pecho + costillas + cintura + cadera +
  omóplatos + cuello. Cabeza = cráneo + cejas + mofletes + hocico + nariz.
  Mandíbula aparte, patas de 2 segmentos con zarpas, cola articulada.
- **Color de pelaje:** 3 tonos mezclados, lomo más oscuro, vientre claro y un
  patrón (rayas, manchas, runas brillantes, cósmico, escamas, roca con musgo).
- **Detalles que los hacen épicos:** ojos con iris y brillo, cejas, colmillos,
  garras, coronas y armaduras de oro, cristales, llamas, alas de plumas o de
  membrana, halos, planetas orbitando y bases con anillos de energía.
- **Tamaño de vóxel:** se buscan unos 2.000–8.000 cubos por animal. Más no
  aporta; lo que importa es que se vea bien.
- **Pose de reposo neutra:** de pie, recta y simétrica (las serpientes y el
  ciempiés estirados en línea recta). La animación se hace después con los
  huesos.

## 12. Mascotas (4 por huevo, ~480)

Archivo: `blender/pets.py` + `blender/pet_names.py`. Cada huevo tiene 4
mascotas con su temática (Panal Real → Abeja Reina, Obrera, Zángano,
Guardiana; Rubí → golem, escarabajo, serpiente y zorro de rubí…). Hay 16 tipos
de cuerpo: cuadrúpedos (gato, perro, zorro, conejo, oso, panda, ciervo,
caballo, unicornio, tigre, león, lobo, cerdo, ratón), aves, peces y tiburones,
insectos, serpientes, dragones, slimes, fantasmas, medusas, setas, golems,
robots, pulpos, ranas, tortugas, cangrejos y murciélagos. Los colores salen de
la paleta del huevo.

**La rareza del huevo decide la calidad de sus mascotas:**

| Nivel | Vóxel | Accesorios | Animación | VFX |
|---|---|---|---|---|
| Común | grande | ninguno | saltito / balanceo | ninguno |
| Poco común | | + collar | + caminar, cola | pocas chispas |
| Raro | | + gema en la frente, ojos brillantes | + orejas | brillo de suelo |
| Épico | | + alas del tipo del huevo, aura | + mandíbula, aleteo | 2 sistemas de partículas |
| Mítico | | + orbes orbitando, corona | | + bloom |
| Legendario | | + halo, aura doble | | 3 sistemas |
| Secreto | fino | + llamas de aura | todo | máximo (con brillo contenido) |

## 13. Huesos (esqueleto) en Blender

Cada modelo se construye con un **Armature**: un hueso por parte animable
(cuerpo, cabeza, mandíbula, orejas, patas, colas, alas, segmentos…) con la
misma jerarquía. La malla es única, con un grupo de vértices por hueso
(peso 1, piel rígida) y modificadores Bevel y Armature. La animación de
reposo se guarda como keyframes de los huesos (`matrix_basis = reposo⁻¹ ·
pose`) y se exporta en el `.glb` (esqueleto + animación) de los animales.
