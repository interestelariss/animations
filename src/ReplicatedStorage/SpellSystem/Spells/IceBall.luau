-- Hechizo: Bola de hielo (tecla 3)
-- Escarcha, cristales y partículas azul claro. Al impactar ralentiza al objetivo.
--
-- Misma estructura que FireBall.luau (ver comentarios allí).

local VFX = require(script.Parent.Parent.VFX)

local IceBall = {
	Id = "IceBall",
	DisplayName = "Bola de hielo",
	Description = "Lanza una bola de hielo que ralentiza al objetivo.",
	Order = 3, -- tecla 3
	Icon = "",

	AnimationId = "",
	AnimationSpeed = 1,

	Cooldown = 1.4,
	Speed = 100,
	Gravity = 0,
	Radius = 1.1,
	Lifetime = 2.5,
	Damage = 14,

	Slow = { Factor = 0.45, Duration = 2.5 }, -- WalkSpeed * 0.45 durante 2.5 s

	Colors = {
		Core = Color3.fromRGB(170, 225, 255),
		Bright = Color3.fromRGB(230, 250, 255),
		Deep = Color3.fromRGB(70, 150, 230),
		Light = Color3.fromRGB(140, 210, 255),
	},

	Textures = {
		Frost = VFX.Textures.Smoke,
		Crystal = VFX.Textures.Sparkle,
	},

	Sounds = {
		Charge = "",
		Cast = "",
		Travel = "",
		Impact = "",
	},
}

local C = IceBall.Colors
local T = IceBall.Textures

function IceBall.BuildCharge(attachment: Attachment)
	VFX.Emitter(attachment, {
		Name = "ChargeCrystals",
		Texture = T.Crystal,
		Color = { { 0, C.Bright }, { 1, C.Core } },
		Size = { { 0, 0.5 }, { 1, 0 } },
		Lifetime = { 0.3, 0.5 },
		Rate = 30,
		Speed = { -3, -1.5 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		LightEmission = 0.8,
	})
	VFX.Emitter(attachment, {
		Name = "ChargeFrost",
		Texture = T.Frost,
		Color = C.Core,
		Size = { { 0, 0.6 }, { 1, 1.4 } },
		Transparency = { { 0, 0.6 }, { 1, 1 } },
		Lifetime = { 0.5, 0.8 },
		Rate = 12,
		Speed = { 0.2, 0.6 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		LightEmission = 0.3,
	})
	VFX.Light(attachment, { Color = C.Light, Brightness = 1.5, Range = 7 })
end

function IceBall.BuildProjectile(): BasePart
	local core = VFX.Part({
		Name = "IceBall",
		Size = Vector3.one * 1.4,
		Color = C.Core,
		Material = Enum.Material.Ice,
		Reflectance = 0.2,
		Transparency = 0.15,
	})
	local attachment = Instance.new("Attachment")
	attachment.Parent = core

	VFX.Emitter(attachment, {
		Name = "Frost",
		Texture = T.Frost,
		Color = { { 0, C.Bright }, { 1, C.Core } },
		Size = { { 0, 1.4 }, { 1, 3 } },
		Transparency = { { 0, 0.55 }, { 1, 1 } },
		Lifetime = { 0.5, 0.8 },
		Rate = 30,
		Speed = { 0, 0.5 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		RotSpeed = { -40, 40 },
		LightEmission = 0.3,
	})
	VFX.Emitter(attachment, {
		Name = "Crystals",
		Texture = T.Crystal,
		Color = { { 0, C.Bright }, { 1, C.Deep } },
		Size = { { 0, 0.5 }, { 1, 0 } },
		Lifetime = { 0.4, 0.7 },
		Rate = 35,
		Speed = { 1, 3 },
		SpreadAngle = 180,
		Rotation = { 0, 360 },
		RotSpeed = { -90, 90 },
		LightEmission = 0.8,
	})
	VFX.Emitter(attachment, {
		Name = "Snow",
		Texture = T.Crystal,
		Color = C.Bright,
		Size = { { 0, 0.15 }, { 1, 0.05 } },
		Lifetime = { 0.6, 1 },
		Rate = 25,
		Speed = { 1, 2 },
		SpreadAngle = 180,
		Acceleration = Vector3.new(0, -6, 0),
		LightEmission = 1,
	})
	VFX.Trail(core, {
		Width = 1.2,
		Color = { { 0, C.Bright }, { 1, C.Deep } },
		Transparency = { { 0, 0.2 }, { 1, 1 } },
		WidthScale = { { 0, 1 }, { 1, 0 } },
		Lifetime = 0.3,
		LightEmission = 0.6,
	})
	VFX.Light(core, { Color = C.Light, Brightness = 2, Range = 12 })
	return core
end

function IceBall.BuildImpact(cframe: CFrame, parent: Instance): Instance
	local root = VFX.Anchor(cframe, parent)
	local attachment = Instance.new("Attachment")
	attachment.Parent = root

	VFX.Emitter(attachment, {
		Name = "FrostBurst",
		Enabled = false,
		EmitCount = 18,
		Texture = T.Frost,
		Color = { { 0, C.Bright }, { 1, C.Core } },
		Size = { { 0, 2 }, { 1, 5 } },
		Transparency = { { 0, 0.3 }, { 1, 1 } },
		Lifetime = { 0.6, 1.1 },
		Speed = { 6, 14 },
		SpreadAngle = 180,
		Drag = 5,
		Rotation = { 0, 360 },
		LightEmission = 0.3,
	})
	VFX.Emitter(attachment, {
		Name = "CrystalBurst",
		Enabled = false,
		EmitCount = 40,
		Texture = T.Crystal,
		Color = { { 0, C.Bright }, { 1, C.Deep } },
		Size = { { 0, 0.6 }, { 1, 0 } },
		Lifetime = { 0.5, 0.9 },
		Speed = { 15, 30 },
		SpreadAngle = 180,
		Drag = 3,
		Acceleration = Vector3.new(0, -20, 0),
		Rotation = { 0, 360 },
		RotSpeed = { -180, 180 },
		LightEmission = 1,
	})
	VFX.Fragments(parent, cframe, {
		Count = 10,
		Size = Vector3.new(0.35, 0.9, 0.35),
		Color = C.Core,
		Material = Enum.Material.Ice,
		Transparency = 0.2,
		Reflectance = 0.2,
		Distance = 6,
		Duration = 0.7,
	})
	VFX.Shockwave(parent, cframe, {
		Color = C.Bright,
		Material = Enum.Material.Ice,
		StartSize = 1,
		EndSize = 8,
		Duration = 0.4,
		Transparency = 0.3,
	})
	VFX.Flash(root, { Color = C.Light, Brightness = 4, Range = 16, Duration = 0.4 })
	return root
end

-- [Servidor] Ralentización + resaltado azul en el objetivo.
function IceBall.OnHit(ctx)
	local humanoid: Humanoid = ctx.TargetHumanoid
	local character: Model = ctx.TargetCharacter

	-- Guardamos la velocidad original una sola vez para que varios impactos
	-- seguidos no "acumulen" la ralentización.
	local baseSpeed = humanoid:GetAttribute("SpellBaseWalkSpeed")
	if baseSpeed == nil then
		baseSpeed = humanoid.WalkSpeed
		humanoid:SetAttribute("SpellBaseWalkSpeed", baseSpeed)
	end

	local token = (humanoid:GetAttribute("SpellSlowToken") or 0) + 1
	humanoid:SetAttribute("SpellSlowToken", token)
	humanoid.WalkSpeed = baseSpeed * IceBall.Slow.Factor

	local highlight = character:FindFirstChild("SpellFrost")
	if not highlight then
		highlight = Instance.new("Highlight")
		highlight.Name = "SpellFrost"
		highlight.FillColor = C.Core
		highlight.FillTransparency = 0.6
		highlight.OutlineColor = C.Bright
		highlight.OutlineTransparency = 0.2
		highlight.Parent = character
	end

	task.wait(IceBall.Slow.Duration)
	if humanoid.Parent and humanoid:GetAttribute("SpellSlowToken") == token then
		humanoid.WalkSpeed = baseSpeed
		humanoid:SetAttribute("SpellBaseWalkSpeed", nil)
		highlight:Destroy()
	end
end

return IceBall
