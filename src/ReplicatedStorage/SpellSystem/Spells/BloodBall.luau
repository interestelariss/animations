-- Hechizo: Bola de sangre (tecla 1)
-- Esfera roja oscura que gotea, deja salpicaduras y manchas al impactar.
-- Al golpear roba vida: cura al lanzador un porcentaje del daño hecho.
--
-- Misma estructura que FireBall.luau (ver comentarios allí).

local VFX = require(script.Parent.Parent.VFX)

local BloodBall = {
	Id = "BloodBall",
	DisplayName = "Bola de sangre",
	Description = "Lanza una bola de sangre que roba vida al objetivo.",
	Order = 1, -- tecla 1
	Icon = "",

	AnimationId = "",
	AnimationSpeed = 1,

	Cooldown = 1.0,
	Speed = 95,
	Gravity = 12, -- cae un poco: se siente más "líquida"
	Radius = 1,
	Lifetime = 2.5,
	Damage = 15,

	Lifesteal = 0.5, -- 50 % del daño hecho cura al lanzador

	Colors = {
		Core = Color3.fromRGB(120, 0, 8),
		Bright = Color3.fromRGB(200, 10, 20),
		Dark = Color3.fromRGB(45, 0, 3),
		Light = Color3.fromRGB(255, 30, 30),
	},

	Textures = {
		Drop = VFX.Textures.Smoke, -- mancha suave; sustitúyela por una gota propia
		Mist = VFX.Textures.Smoke,
		Glint = VFX.Textures.Sparkle,
	},

	Sounds = {
		Charge = "",
		Cast = "",
		Travel = "",
		Impact = "",
	},
}

local C = BloodBall.Colors
local T = BloodBall.Textures

function BloodBall.BuildCharge(attachment: Attachment)
	-- Velocidad negativa: las gotas convergen hacia la mano.
	VFX.Emitter(attachment, {
		Name = "ChargeDrops",
		Texture = T.Drop,
		Color = { { 0, C.Bright }, { 1, C.Dark } },
		Size = { { 0, 0.15 }, { 0.5, 0.35 }, { 1, 0 } },
		Lifetime = { 0.3, 0.5 },
		Rate = 35,
		Speed = { -4, -2 },
		SpreadAngle = 180,
		LightInfluence = 1,
	})
	VFX.Emitter(attachment, {
		Name = "ChargeMist",
		Texture = T.Mist,
		Color = C.Core,
		Size = { { 0, 0.6 }, { 1, 1.2 } },
		Transparency = { { 0, 0.5 }, { 1, 1 } },
		Lifetime = { 0.4, 0.7 },
		Rate = 10,
		Speed = { 0.2, 0.6 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		LightInfluence = 1,
	})
	VFX.Light(attachment, { Color = C.Light, Brightness = 1, Range = 6 })
end

function BloodBall.BuildProjectile(): BasePart
	local core = VFX.Part({
		Name = "BloodBall",
		Size = Vector3.one * 1.3,
		Color = C.Core,
		Material = Enum.Material.Glass,
		Reflectance = 0.15,
		Transparency = 0.05,
	})
	local attachment = Instance.new("Attachment")
	attachment.Parent = core

	VFX.Emitter(attachment, {
		Name = "Drips",
		Texture = T.Drop,
		Color = { { 0, C.Bright }, { 1, C.Dark } },
		Size = { { 0, 0.3 }, { 1, 0.1 } },
		Transparency = { { 0, 0 }, { 0.8, 0.2 }, { 1, 1 } },
		Lifetime = { 0.5, 0.9 },
		Rate = 45,
		Speed = { 0.5, 2 },
		SpreadAngle = 180,
		Acceleration = Vector3.new(0, -50, 0),
		LightInfluence = 1,
	})
	VFX.Emitter(attachment, {
		Name = "Mist",
		Texture = T.Mist,
		Color = C.Core,
		Size = { { 0, 1 }, { 1, 2.2 } },
		Transparency = { { 0, 0.55 }, { 1, 1 } },
		Lifetime = { 0.4, 0.7 },
		Rate = 25,
		Speed = { 0, 0.5 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		LightInfluence = 1,
	})
	VFX.Emitter(attachment, {
		Name = "Glints",
		Texture = T.Glint,
		Color = C.Bright,
		Size = { { 0, 0.4 }, { 1, 0 } },
		Lifetime = { 0.15, 0.3 },
		Rate = 15,
		Speed = { 0, 0 },
		LightEmission = 0.6,
	})
	VFX.Trail(core, {
		Width = 1,
		Color = { { 0, C.Bright }, { 1, C.Dark } },
		Transparency = { { 0, 0.1 }, { 1, 1 } },
		WidthScale = { { 0, 1 }, { 1, 0.2 } },
		Lifetime = 0.3,
		LightInfluence = 1,
	})
	VFX.Light(core, { Color = C.Light, Brightness = 1.2, Range = 9 })
	return core
end

function BloodBall.BuildImpact(cframe: CFrame, parent: Instance): Instance
	local root = VFX.Anchor(cframe, parent)
	local attachment = Instance.new("Attachment")
	attachment.Parent = root

	VFX.Emitter(attachment, {
		Name = "Splash",
		Enabled = false,
		EmitCount = 45,
		Texture = T.Drop,
		Color = { { 0, C.Bright }, { 1, C.Dark } },
		Size = { { 0, 0.45 }, { 1, 0.15 } },
		Lifetime = { 0.5, 0.9 },
		Speed = { 12, 28 },
		SpreadAngle = 70, -- abanico alrededor de la normal de la superficie
		Acceleration = Vector3.new(0, -60, 0),
		Drag = 1.5,
		EmissionDirection = Enum.NormalId.Front,
		LightInfluence = 1,
	})
	VFX.Emitter(attachment, {
		Name = "BurstMist",
		Enabled = false,
		EmitCount = 10,
		Texture = T.Mist,
		Color = C.Core,
		Size = { { 0, 2 }, { 1, 4.5 } },
		Transparency = { { 0, 0.4 }, { 1, 1 } },
		Lifetime = { 0.6, 1 },
		Speed = { 3, 6 },
		SpreadAngle = 180,
		Drag = 4,
		Rotation = { 0, 360 },
		LightInfluence = 1,
	})
	VFX.Shockwave(parent, cframe, {
		Color = C.Core,
		Material = Enum.Material.Glass,
		StartSize = 1,
		EndSize = 6,
		Duration = 0.25,
		Transparency = 0.2,
	})
	VFX.Splats(parent, cframe.Position, {
		Count = 6,
		Radius = 3,
		Color = C.Dark,
		Material = Enum.Material.Glass,
		Reflectance = 0.1,
		Lifetime = 5,
	})
	VFX.Flash(root, { Color = C.Light, Brightness = 2, Range = 12, Duration = 0.3 })
	return root
end

-- [Servidor] Robo de vida.
function BloodBall.OnHit(ctx)
	local casterCharacter = ctx.CasterCharacter
	local casterHumanoid = casterCharacter and casterCharacter:FindFirstChildOfClass("Humanoid")
	if casterHumanoid and casterHumanoid.Health > 0 and ctx.Damage > 0 then
		casterHumanoid.Health = math.min(casterHumanoid.MaxHealth, casterHumanoid.Health + ctx.Damage * BloodBall.Lifesteal)
	end
end

return BloodBall
