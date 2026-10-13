-- Hechizo: Bola de fuego (tecla 2)
-- Llamas, brillo naranja y chispas. Al impactar quema al objetivo durante unos segundos.
--
-- Funciones del módulo:
--   BuildCharge(attachment)      [cliente] VFX en la mano mientras se carga
--   BuildProjectile() -> Part    [cliente] visual del proyectil
--   BuildImpact(cframe, parent)  [cliente] VFX de impacto (devuelve la raíz)
--   OnHit(ctx)                   [servidor] efecto extra al golpear a un Humanoid
-- Si existe ReplicatedStorage/SpellVFX/FireBall/{Charge,Projectile,Impact},
-- esas plantillas (VFX Studio) sustituyen a las funciones Build*.

local VFX = require(script.Parent.Parent.VFX)

local FireBall = {
	Id = "FireBall",
	DisplayName = "Bola de fuego",
	Description = "Lanza una bola de fuego que quema al objetivo.",
	Order = 2, -- tecla 2
	Icon = "", -- rbxassetid://... de la imagen del ítem (vacío = muestra el nombre)

	AnimationId = "", -- vacío = Config.DefaultCastAnimationId
	AnimationSpeed = 1,

	-- Proyectil
	Cooldown = 1.2,
	Speed = 110, -- studs/s
	Gravity = 0, -- studs/s² hacia abajo
	Radius = 1.1, -- radio de colisión
	Lifetime = 2.5, -- segundos antes de desaparecer
	Damage = 18,

	-- Quemadura tras el impacto
	Burn = { Ticks = 4, Interval = 0.5, Damage = 3 },

	Colors = {
		Core = Color3.fromRGB(255, 190, 70),
		Outer = Color3.fromRGB(255, 100, 10),
		Dark = Color3.fromRGB(140, 25, 0),
		Smoke = Color3.fromRGB(60, 40, 35),
		Light = Color3.fromRGB(255, 140, 40),
	},

	Textures = {
		Flame = VFX.Textures.Fire,
		Sparks = VFX.Textures.FireSparks,
		Smoke = VFX.Textures.Smoke,
	},

	-- IDs de audio (rbxassetid://...). Vacío = sin sonido. Ver README.md.
	Sounds = {
		Charge = "",
		Cast = "",
		Travel = "",
		Impact = "",
	},
}

local C = FireBall.Colors
local T = FireBall.Textures

function FireBall.BuildCharge(attachment: Attachment)
	VFX.Emitter(attachment, {
		Name = "ChargeFlames",
		Texture = T.Flame,
		Color = { { 0, C.Core }, { 1, C.Outer } },
		Size = { { 0, 0.7 }, { 1, 0 } },
		Transparency = { { 0, 0.2 }, { 1, 1 } },
		Lifetime = { 0.2, 0.4 },
		Rate = 40,
		Speed = { 0.5, 1.5 },
		SpreadAngle = 180,
		RotSpeed = { -180, 180 },
		Rotation = { 0, 360 },
		LightEmission = 1,
	})
	VFX.Emitter(attachment, {
		Name = "ChargeSparks",
		Texture = T.Sparks,
		Color = C.Core,
		Size = { { 0, 0.2 }, { 1, 0 } },
		Lifetime = { 0.3, 0.6 },
		Rate = 15,
		Speed = { 2, 4 },
		SpreadAngle = 180,
		Drag = 3,
		LightEmission = 1,
	})
	VFX.Light(attachment, { Color = C.Light, Brightness = 2, Range = 8 })
end

function FireBall.BuildProjectile(): BasePart
	local core = VFX.Part({
		Name = "FireBall",
		Size = Vector3.one * 1.4,
		Color = C.Core,
		Material = Enum.Material.Neon,
		Transparency = 0.15,
	})
	local attachment = Instance.new("Attachment")
	attachment.Parent = core

	-- Las partículas salen con velocidad 0 en espacio de mundo: al moverse la
	-- bola dejan una estela de llamas detrás.
	VFX.Emitter(attachment, {
		Name = "Flames",
		Texture = T.Flame,
		Color = { { 0, C.Core }, { 0.5, C.Outer }, { 1, C.Dark } },
		Size = { { 0, 2.4 }, { 1, 0.4 } },
		Transparency = { { 0, 0.1 }, { 0.7, 0.5 }, { 1, 1 } },
		Lifetime = { 0.25, 0.45 },
		Rate = 90,
		Speed = { 0, 0.5 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		RotSpeed = { -200, 200 },
		LightEmission = 1,
	})
	VFX.Emitter(attachment, {
		Name = "Smoke",
		Texture = T.Smoke,
		Color = C.Smoke,
		Size = { { 0, 1.2 }, { 1, 3 } },
		Transparency = { { 0, 0.6 }, { 1, 1 } },
		Lifetime = { 0.6, 1 },
		Rate = 20,
		Speed = { 0.5, 1 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		LightInfluence = 1,
	})
	VFX.Emitter(attachment, {
		Name = "Sparks",
		Texture = T.Sparks,
		Color = C.Core,
		Size = { { 0, 0.25 }, { 1, 0 } },
		Lifetime = { 0.4, 0.8 },
		Rate = 40,
		Speed = { 4, 8 },
		SpreadAngle = 180,
		Acceleration = Vector3.new(0, -10, 0),
		Drag = 2,
		LightEmission = 1,
	})
	VFX.Trail(core, {
		Width = 1.2,
		Color = { { 0, C.Core }, { 1, C.Dark } },
		Transparency = { { 0, 0.2 }, { 1, 1 } },
		WidthScale = { { 0, 1 }, { 1, 0 } },
		Lifetime = 0.25,
		LightEmission = 1,
	})
	VFX.Light(core, { Color = C.Light, Brightness = 3, Range = 14 })
	return core
end

function FireBall.BuildImpact(cframe: CFrame, parent: Instance): Instance
	local root = VFX.Anchor(cframe, parent)
	local attachment = Instance.new("Attachment")
	attachment.Parent = root

	VFX.Emitter(attachment, {
		Name = "Explosion",
		Enabled = false,
		EmitCount = 35,
		Texture = T.Flame,
		Color = { { 0, C.Core }, { 0.4, C.Outer }, { 1, C.Dark } },
		Size = { { 0, 2 }, { 1, 5 } },
		Transparency = { { 0, 0 }, { 0.6, 0.4 }, { 1, 1 } },
		Lifetime = { 0.4, 0.7 },
		Speed = { 10, 25 },
		SpreadAngle = 180,
		Drag = 6,
		Rotation = { 0, 360 },
		RotSpeed = { -120, 120 },
		LightEmission = 1,
	})
	VFX.Emitter(attachment, {
		Name = "BurstSparks",
		Enabled = false,
		EmitCount = 50,
		Texture = T.Sparks,
		Color = C.Core,
		Size = { { 0, 0.35 }, { 1, 0 } },
		Lifetime = { 0.5, 1 },
		Speed = { 20, 45 },
		SpreadAngle = 180,
		Acceleration = Vector3.new(0, -40, 0),
		Drag = 2,
		LightEmission = 1,
	})
	VFX.Emitter(attachment, {
		Name = "BurstSmoke",
		Enabled = false,
		EmitCount = 12,
		EmitDelay = 0.1,
		Texture = T.Smoke,
		Color = C.Smoke,
		Size = { { 0, 3 }, { 1, 7 } },
		Transparency = { { 0, 0.5 }, { 1, 1 } },
		Lifetime = { 1, 1.6 },
		Speed = { 3, 8 },
		SpreadAngle = 180,
		Drag = 3,
		Rotation = { 0, 360 },
		LightInfluence = 1,
	})
	VFX.Shockwave(parent, cframe, { Color = C.Outer, StartSize = 1, EndSize = 10, Duration = 0.35 })
	VFX.Flash(root, { Color = C.Light, Brightness = 6, Range = 22, Duration = 0.5 })
	return root
end

-- [Servidor] Quemadura: daño por ticks y fuego visible sobre el objetivo.
function FireBall.OnHit(ctx)
	local humanoid: Humanoid = ctx.TargetHumanoid
	local rootPart = ctx.TargetCharacter:FindFirstChild("HumanoidRootPart")
	if not rootPart then
		return
	end

	-- Un token por golpe: si llega otra bola de fuego, la quemadura se renueva.
	local token = (humanoid:GetAttribute("SpellBurnToken") or 0) + 1
	humanoid:SetAttribute("SpellBurnToken", token)

	local fire = rootPart:FindFirstChild("SpellBurn")
	if not fire then
		fire = Instance.new("Fire")
		fire.Name = "SpellBurn"
		fire.Color = C.Outer
		fire.SecondaryColor = C.Dark
		fire.Size = 5
		fire.Heat = 6
		fire.Parent = rootPart
	end

	for _ = 1, FireBall.Burn.Ticks do
		task.wait(FireBall.Burn.Interval)
		if humanoid:GetAttribute("SpellBurnToken") ~= token or humanoid.Health <= 0 or not humanoid.Parent then
			break
		end
		humanoid:TakeDamage(FireBall.Burn.Damage)
	end

	if humanoid:GetAttribute("SpellBurnToken") == token then
		fire:Destroy()
	end
end

return FireBall
