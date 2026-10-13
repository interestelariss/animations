-- Configuración global del sistema de hechizos.
-- Los valores propios de cada hechizo (daño, velocidad, colores, sonidos...)
-- están en su módulo dentro de SpellSystem/Spells.

local Config = {
	-- Animación de lanzamiento compartida por los tres hechizos.
	-- Pega aquí el ID publicado ("rbxassetid://123456789"). Cada hechizo puede
	-- sobrescribirlo con su propio campo AnimationId.
	DefaultCastAnimationId = "",

	-- Si no hay ID publicado y estás en Roblox Studio, se genera la animación
	-- por código (KeyframeSequence) y se registra temporalmente para probar.
	-- Esto NO funciona en un servidor publicado: ahí necesitas un ID real.
	UseStudioGeneratedAnimation = true,

	-- Nombre del marcador (KeyframeMarker) en la animación que indica el
	-- instante exacto en que sale la bola.
	ReleaseMarkerName = "Release",
	-- Si la animación no tiene el marcador, se lanza tras este tiempo máximo.
	ReleaseMarkerTimeout = 1.0,
	-- Tiempo de carga cuando no hay animación disponible.
	FallbackReleaseTime = 0.6,

	-- Distancia máxima del rayo de apuntado (desde la cámara).
	MaxAimDistance = 600,
	-- Distancia hacia delante desde la mano a la que aparece el proyectil.
	SpawnForwardOffset = 1.5,
	-- Tolerancia de cooldown en el servidor para absorber la latencia.
	CooldownLeniency = 0.15,
	-- Tiempo máximo que los demás jugadores ven la carga si no llega el lanzamiento.
	MaxChargeTime = 2,

	-- Daño entre compañeros de equipo (solo si los jugadores tienen Team).
	FriendlyFire = false,

	-- Carpeta opcional en ReplicatedStorage con los VFX hechos en VFX Studio:
	-- ReplicatedStorage/SpellVFX/<IdDelHechizo>/{Charge, Projectile, Impact}
	VFXTemplatesFolderName = "SpellVFX",
	-- Partículas que se emiten por defecto en un emisor de impacto sin atributo EmitCount.
	DefaultEmitCount = 20,

	RemotesFolderName = "SpellSystemRemotes",
	ClientFXFolderName = "SpellFX_Local",
}

return Config
