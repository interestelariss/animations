# Sistema de hechizos para Roblox (sangre, fuego, hielo)

Tres hechizos como ítems de inventario, seleccionables con las teclas **1**, **2** y **3**.
Al hacer clic con uno equipado, el personaje reproduce una animación de lanzamiento
(levanta el brazo, carga sobre la cabeza y lanza). En el instante del lanzamiento
sale la bola, con sus VFX, su sonido y su efecto al impactar.

| Tecla | Hechizo        | Efecto al impactar                               |
|-------|----------------|--------------------------------------------------|
| 1     | Bola de sangre | Daño + robo de vida (cura al lanzador el 50 %)   |
| 2     | Bola de fuego  | Daño + quemadura (4 ticks, fuego sobre el objetivo) |
| 3     | Bola de hielo  | Daño + ralentización (45 % de velocidad, 2,5 s)   |

## Estructura

```
src/
├─ ReplicatedStorage/SpellSystem/          (Folder)
│  ├─ Config.luau          ModuleScript  – ajustes globales (ID de animación, etc.)
│  ├─ SpellRegistry.luau   ModuleScript  – carga y ordena los hechizos
│  ├─ VFX.luau             ModuleScript  – helpers de partículas, trails, luces, sonido
│  ├─ CastAnimation.luau   ModuleScript  – animación de lanzamiento + Animator
│  └─ Spells/              (Folder)
│     ├─ BloodBall.luau    ModuleScript  – hechizo 1
│     ├─ FireBall.luau     ModuleScript  – hechizo 2
│     └─ IceBall.luau      ModuleScript  – hechizo 3
├─ ServerScriptService/SpellServer.server.luau               Script
└─ StarterPlayer/StarterPlayerScripts/SpellClient.client.luau LocalScript
tools/CreateCastAnimationForEditor.luau   – script para la barra de comandos de Studio
```

Cada hechizo es un módulo independiente con sus datos (daño, velocidad, cooldown,
colores, texturas, sonidos) y sus funciones:

| Función                        | Dónde corre | Qué hace                                   |
|--------------------------------|-------------|--------------------------------------------|
| `BuildCharge(attachment)`      | cliente     | VFX en la mano durante la carga            |
| `BuildProjectile()`            | cliente     | Visual de la bola (Part con emisores/trail/luz) |
| `BuildImpact(cframe, parent)`  | cliente     | VFX de impacto                             |
| `OnHit(ctx)`                   | servidor    | Efecto extra (robo de vida, quemadura, lentitud) |

Para añadir un cuarto hechizo: duplica un módulo de `Spells`, cambia `Id`, `DisplayName`
y `Order = 4`. Aparecerá solo en la tecla 4.

### Cómo funciona

1. **Servidor** crea un `Tool` por hechizo en `StarterPack`, en orden de `Order`. La barra de
   inventario de Roblox asigna las teclas 1, 2, 3 según ese orden.
2. **Cliente**, al hacer clic (`Tool.Activated`): reproduce la animación en el `Animator`,
   muestra la carga en la mano y avisa al servidor (los demás jugadores ven la carga).
3. Al llegar el marcador **`Release`** de la animación, el cliente envía el punto apuntado
   con el ratón. El servidor valida (Tool equipado, cooldown, personaje vivo) y simula el
   proyectil con `Workspace:Spherecast` cada `Heartbeat`: movimiento, gravedad, colisión
   y tiempo de vida. El daño solo lo aplica el servidor.
4. Todos los clientes dibujan el proyectil a partir de origen + velocidad y, al recibir
   `Impact`/`Expire`, lo detienen y reproducen el impacto.
5. **Limpieza**: todo efecto local vive en `Workspace/SpellFX_Local` y se destruye con
   `Debris` cuando termina la vida de sus partículas y trails. Al desequipar o morir
   durante la carga, se cancela la animación y la carga (sin gastar el cooldown).
   Quemaduras y ralentizaciones se retiran solas, y si llega otro impacto se renuevan
   en vez de acumularse.

## Instalación

**Con Rojo** (recomendado): `rojo serve` en esta carpeta y conecta el plugin de Rojo en Studio.

**A mano**: crea en Studio las instancias de la tabla anterior con los mismos nombres y
pega el contenido de cada archivo (`.server.luau` = `Script`, `.client.luau` = `LocalScript`,
el resto = `ModuleScript`). `SpellSystem` y `Spells` son `Folder`.

Pulsa **Play**: ya funciona en Studio con VFX generados por código y la animación
generada (solo para rigs R15). Para el juego publicado necesitas los pasos siguientes.

## Lo que tienes que configurar a mano

### 1. Animación de lanzamiento (obligatorio para publicar)

En Studio, la animación se crea por código y se registra con un ID temporal
(`KeyframeSequenceProvider:RegisterKeyframeSequence`), **que solo funciona en Studio**.
Para el juego publicado:

1. Inserta un rig R15 (*Avatar → Rig Builder → R15*) y selecciónalo.
2. Abre *View → Command Bar*, pega el contenido de `tools/CreateCastAnimationForEditor.luau`
   y pulsa Enter. Se crea `SpellCast` dentro de `<Rig>/AnimSaves`.
3. Abre el **Animation Editor** con el rig seleccionado, carga `SpellCast`, retócala si
   quieres y publícala (*… → Publish to Roblox*). La animación debe publicarla la misma
   cuenta o grupo dueño de la experiencia, o no se reproducirá.
4. Pega el ID en `Config.DefaultCastAnimationId = "rbxassetid://TU_ID"`.
   Si quieres una animación distinta por hechizo, usa `AnimationId` en su módulo.

Si haces tu propia animación (o tu juego usa R6), añade un **evento de animación llamado
`Release`** en el fotograma en que sale la bola. Sin él, la bola sale tras
`Config.ReleaseMarkerTimeout` (1 s).

Si en tu versión de Studio el Animation Editor no muestra `SpellCast` en *Load*, guarda
cualquier animación una vez con el editor (eso crea `AnimSaves`) y vuelve a ejecutar el
script, o usa clic derecho sobre la `KeyframeSequence` → *Save to Roblox*.

### 2. VFX Studio

No conozco con certeza el formato exacto que exporta tu versión del plugin VFX Studio,
así que el sistema **no depende de él**: trae VFX de respaldo hechos con
`ParticleEmitter`, `Trail`, `PointLight` y partes, y usa los tuyos cuando existen.

Para usar los efectos que diseñes con VFX Studio, crea esta estructura:

```
ReplicatedStorage
└─ SpellVFX                (Folder)
   ├─ BloodBall            (Folder, nombre = Id del hechizo)
   │  ├─ Charge            Attachment con emisores (se mete en la mano derecha)
   │  ├─ Projectile        BasePart o Model (la bola) con emisores/trails/luces dentro
   │  └─ Impact            BasePart, Model o Attachment con los emisores del impacto
   ├─ FireBall
   └─ IceBall
```

Puedes rellenar solo las piezas que quieras: las que falten siguen usando el VFX por código.
Comprueba en cada efecto exportado:

- Que esté hecho con instancias estándar (`ParticleEmitter`, `Trail`, `Beam`, `PointLight`,
  `Attachment`, partes). El sistema las clona y las mueve; **si el plugin necesita un
  script o módulo propio en tiempo de ejecución** (p. ej. para animar mallas o cambiar
  tamaños por tween), ese comportamiento no se reproducirá: tendrás que llamar a su API
  desde `BuildImpact`/`BuildProjectile` o copiar su lógica.
- **Impact**: cada `ParticleEmitter` que deba salir en ráfaga necesita el atributo
  numérico `EmitCount` (cuántas partículas) y opcionalmente `EmitDelay` (segundos).
  Muchos plugins ya usan esos nombres; si el tuyo usa otros, renómbralos o añádelos a
  mano (*Properties → Attributes → +*). Los emisores sin `EmitCount` y con `Enabled = true`
  se dejan encendidos 0,15 s.
- **Projectile**: si es un `Model`, ponle `PrimaryPart`. Todas sus partes se anclan y se
  quitan colisiones automáticamente. La colisión real la decide el servidor con `Radius`.
- **Trail**: necesita sus dos `Attachment` dentro de la parte que se mueve.
- La orientación del impacto: el eje *LookVector* (−Z, "Front") apunta hacia fuera
  de la superficie golpeada.

### 3. Texturas

Por defecto se usan texturas incluidas en el cliente de Roblox
(`rbxasset://textures/particles/...`: fuego, chispas, humo, destellos), teñidas con los
colores de cada hechizo. Para usar las tuyas (o las que genere VFX Studio):

1. Sube la imagen (*Asset Manager → Import* o Creator Dashboard). Para partículas usa PNG
   con fondo transparente; para flipbooks, la rejilla que indique tu plugin.
2. Copia su ID y cámbialo en la tabla `Textures` del hechizo, p. ej. en `BloodBall.luau`:
   `Drop = "rbxassetid://TU_ID_DE_GOTA"`.
3. Para el icono del ítem en la barra, pon el ID en `Icon`.

Sugerencias: sangre → gota/salpicadura oscura y una mancha para el suelo; fuego → llama
en flipbook y chispa alargada; hielo → copo/cristal hexagonal y niebla suave.

### 4. Sonidos

No incluyo IDs de audio porque no puedo garantizar que existan ni que tu experiencia
tenga permiso para usarlos. Cada hechizo tiene:

```lua
Sounds = { Charge = "", Cast = "", Travel = "", Impact = "" },
```

Busca en *Toolbox → Audio* o en la Creator Store (p. ej. "fireball", "fire whoosh",
"ice shatter", "freeze", "blood splash", "magic charge"), comprueba que el audio sea
público/utilizable en tu experiencia y pega su ID (`"rbxassetid://123..."`).
Los vacíos se ignoran. `Travel` se reproduce en bucle mientras vuela la bola.

### 5. Teclas 1, 2, 3

Usan la barra de inventario estándar de Roblox (`CoreGui Backpack`). Si la desactivas para
usar una barra propia, equipa los Tools con `Humanoid:EquipTool()` desde tu UI; la lógica
de lanzamiento no cambia porque escucha `Tool.Activated`.

## Ajustes rápidos

- Daño, velocidad, gravedad, radio, vida, cooldown: en cada módulo de `Spells`.
- Fuego amigo y tolerancias: `Config.luau`.
- Ajustar la pose de la animación generada: `CastAnimation.Keyframes`.

## Lista de pruebas en Studio

1. *Play*: aparecen 3 ítems en la barra (1 sangre, 2 fuego, 3 hielo).
2. Pulsa 1 y haz clic: el brazo sube, gotas convergen en la mano, la bola sale al bajar el brazo.
3. Dispara a un *Dummy* (*Avatar → Rig Builder*): baja la vida; con fuego arde, con hielo
   se vuelve azul y más lento, con sangre te curas.
4. Cambia de ítem durante la carga: se cancela sin lanzar.
5. *Test → Clients and Servers* con 2 jugadores: cada uno ve la carga y las bolas del otro.
6. Tras unos segundos, `Workspace/SpellFX_Local` debe quedar vacío.
