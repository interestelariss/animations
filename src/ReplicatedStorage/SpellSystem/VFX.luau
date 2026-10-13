-- Utilidades de efectos visuales compartidas por todos los hechizos.
--
-- Dos formas de obtener los VFX de un hechizo:
--   1. Plantillas creadas con VFX Studio en ReplicatedStorage/SpellVFX/<Id>/...
--      (tienen prioridad; ver README.md, sección "VFX Studio").
--   2. Efectos de respaldo generados por código en cada módulo de Spells,
--      usando los helpers de este archivo y texturas que vienen con Roblox.

local Debris = game:GetService("Debris")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Workspace = game:GetService("Workspace")

local Config = require(script.Parent.Config)

local VFX = {}

-- Texturas incluidas en el cliente de Roblox (no requieren subir nada).
-- Sustitúyelas en cada hechizo por tus propias texturas (rbxassetid://...).
VFX.Textures = {
	Sparkle = "rbxasset://textures/particles/sparkles_main.dds",
	Fire = "rbxasset://textures/particles/fire_main.dds",
	FireSparks = "rbxasset://textures/particles/fire_sparks_main.dds",
	Smoke = "rbxasset://textures/particles/smoke_main.dds",
}

local random = Random.new()

--------------------------------------------------------------------------------
-- Conversión de valores
--------------------------------------------------------------------------------

-- Número o lista {{tiempo, valor[, envolvente]}, ...} -> NumberSequence
function VFX.NS(value): NumberSequence
	if typeof(value) == "NumberSequence" then
		return value
	elseif typeof(value) == "number" then
		return NumberSequence.new(value)
	end
	local keypoints = {}
	for _, point in value do
		table.insert(keypoints, NumberSequenceKeypoint.new(point[1], point[2], point[3] or 0))
	end
	return NumberSequence.new(keypoints)
end

-- Color3 o lista {{tiempo, Color3}, ...} -> ColorSequence
function VFX.CS(value): ColorSequence
	if typeof(value) == "ColorSequence" then
		return value
	elseif typeof(value) == "Color3" then
		return ColorSequence.new(value)
	end
	local keypoints = {}
	for _, point in value do
		table.insert(keypoints, ColorSequenceKeypoint.new(point[1], point[2]))
	end
	return ColorSequence.new(keypoints)
end

local function toRange(value)
	if typeof(value) == "number" then
		return NumberRange.new(value)
	elseif type(value) == "table" then
		return NumberRange.new(value[1], value[2])
	end
	return value
end

local SEQUENCE_KEYS = { Size = true, Transparency = true, Squash = true, WidthScale = true }
local RANGE_KEYS = { Lifetime = true, Speed = true, Rotation = true, RotSpeed = true }
local ATTRIBUTE_KEYS = { EmitCount = true, EmitDelay = true }

-- Aplica una tabla de propiedades convirtiendo números/tablas al tipo correcto
-- según la clase (ParticleEmitter, Trail, Beam...).
local function apply(instance: Instance, props)
	local isSequenced = instance:IsA("ParticleEmitter") or instance:IsA("Trail") or instance:IsA("Beam")
	for key, value in props do
		if ATTRIBUTE_KEYS[key] then
			instance:SetAttribute(key, value)
		elseif isSequenced and key == "Color" then
			(instance :: any)[key] = VFX.CS(value)
		elseif isSequenced and SEQUENCE_KEYS[key] then
			(instance :: any)[key] = VFX.NS(value)
		elseif instance:IsA("ParticleEmitter") and RANGE_KEYS[key] then
			(instance :: any)[key] = toRange(value)
		elseif key == "SpreadAngle" and typeof(value) == "number" then
			(instance :: any)[key] = Vector2.new(value, value)
		else
			(instance :: any)[key] = value
		end
	end
end

--------------------------------------------------------------------------------
-- Constructores
--------------------------------------------------------------------------------

-- Parte visual sin físicas ni colisiones (por defecto, una esfera).
function VFX.Part(props): BasePart
	local part = Instance.new("Part")
	part.Shape = Enum.PartType.Ball
	part.Size = Vector3.one
	part.Anchored = true
	part.CanCollide = false
	part.CanQuery = false
	part.CanTouch = false
	part.CastShadow = false
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	apply(part, props or {})
	return part
end

-- Parte invisible que sirve de ancla para emisores de impacto.
function VFX.Anchor(cframe: CFrame, parent: Instance?): BasePart
	local anchor = VFX.Part({
		Name = "VFXAnchor",
		Shape = Enum.PartType.Block,
		Size = Vector3.one * 0.2,
		Transparency = 1,
		CFrame = cframe,
	})
	anchor.Parent = parent
	return anchor
end

function VFX.Emitter(parent: Instance, props): ParticleEmitter
	local emitter = Instance.new("ParticleEmitter")
	emitter.LightInfluence = 0
	apply(emitter, props)
	emitter.Parent = parent
	return emitter
end

-- Trail orientado a cámara. props.Width = ancho en studs.
function VFX.Trail(part: BasePart, props): Trail
	local width = props.Width or 1
	local a0 = Instance.new("Attachment")
	a0.Name = "TrailTop"
	a0.Position = Vector3.new(0, width / 2, 0)
	a0.Parent = part
	local a1 = Instance.new("Attachment")
	a1.Name = "TrailBottom"
	a1.Position = Vector3.new(0, -width / 2, 0)
	a1.Parent = part

	local trail = Instance.new("Trail")
	trail.Attachment0 = a0
	trail.Attachment1 = a1
	trail.FaceCamera = true
	local rest = table.clone(props)
	rest.Width = nil
	apply(trail, rest)
	trail.Parent = part
	return trail
end

function VFX.Light(parent: Instance, props): PointLight
	local light = Instance.new("PointLight")
	light.Shadows = false
	apply(light, props)
	light.Parent = parent
	return light
end

-- Destello de luz que se apaga en `duration` segundos.
function VFX.Flash(parent: Instance, props)
	local duration = props.Duration or 0.4
	local rest = table.clone(props)
	rest.Duration = nil
	local light = VFX.Light(parent, rest)
	TweenService:Create(light, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Brightness = 0,
	}):Play()
	Debris:AddItem(light, duration + 0.1)
	return light
end

-- Esfera que se expande y se desvanece (onda de choque).
function VFX.Shockwave(parent: Instance, cframe: CFrame, props)
	local duration = props.Duration or 0.35
	local sphere = VFX.Part({
		Name = "Shockwave",
		Size = Vector3.one * (props.StartSize or 1),
		Color = props.Color or Color3.new(1, 1, 1),
		Material = props.Material or Enum.Material.Neon,
		Transparency = props.Transparency or 0.3,
		CFrame = cframe,
	})
	sphere.Parent = parent
	TweenService:Create(sphere, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Size = Vector3.one * (props.EndSize or 8),
		Transparency = 1,
	}):Play()
	Debris:AddItem(sphere, duration + 0.1)
end

-- Fragmentos que salen despedidos desde el punto de impacto (cristales, trozos...).
-- El LookVector de `cframe` es la dirección principal (la normal de la superficie).
function VFX.Fragments(parent: Instance, cframe: CFrame, props)
	local count = props.Count or 8
	local duration = props.Duration or 0.6
	local baseSize: Vector3 = props.Size or Vector3.new(0.4, 0.4, 0.4)
	for _ = 1, count do
		local size = baseSize * random:NextNumber(0.6, 1.4)
		local fragment = VFX.Part({
			Name = "Fragment",
			Shape = Enum.PartType.Block,
			Size = size,
			Color = props.Color or Color3.new(1, 1, 1),
			Material = props.Material or Enum.Material.SmoothPlastic,
			Transparency = props.Transparency or 0,
			Reflectance = props.Reflectance or 0,
			CFrame = cframe * CFrame.Angles(random:NextNumber(0, 6.28), random:NextNumber(0, 6.28), 0),
		})
		fragment.Parent = parent

		local direction = (cframe.LookVector + random:NextUnitVector() * (props.Spread or 0.9)).Unit
		local distance = random:NextNumber((props.Distance or 5) * 0.5, props.Distance or 5)
		local target = cframe.Position + direction * distance - Vector3.new(0, props.Drop or 1.5, 0)
		local spin = CFrame.Angles(random:NextNumber(-6, 6), random:NextNumber(-6, 6), random:NextNumber(-6, 6))
		TweenService:Create(fragment, TweenInfo.new(duration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			CFrame = CFrame.new(target) * spin,
			Size = size * 0.3,
			Transparency = 1,
		}):Play()
		Debris:AddItem(fragment, duration + 0.1)
	end
end

-- Manchas planas sobre las superficies cercanas (ej. charcos de sangre).
function VFX.Splats(parent: Instance, position: Vector3, props)
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { parent }

	for _ = 1, props.Count or 5 do
		local offset = Vector3.new(random:NextNumber(-1, 1), 0, random:NextNumber(-1, 1)) * (props.Radius or 3)
		local result = Workspace:Raycast(position + Vector3.new(0, 1, 0) + offset, Vector3.new(0, -10, 0), params)
		local model = result and result.Instance:FindFirstAncestorOfClass("Model")
		local onCharacter = model ~= nil and model:FindFirstChildOfClass("Humanoid") ~= nil
		if result and not onCharacter then
			local normal = result.Normal
			local perpendicular = normal:Cross(math.abs(normal.Y) < 0.99 and Vector3.yAxis or Vector3.xAxis).Unit
			local diameter = random:NextNumber(props.MinSize or 0.6, props.MaxSize or 2)
			local splat = VFX.Part({
				Name = "Splat",
				Shape = Enum.PartType.Cylinder,
				Size = Vector3.new(0.05, 0.1, 0.1),
				Color = props.Color or Color3.new(0.3, 0, 0),
				Material = props.Material or Enum.Material.SmoothPlastic,
				Reflectance = props.Reflectance or 0,
				-- El eje del cilindro es X: lo alineamos con la normal de la superficie.
				CFrame = CFrame.fromMatrix(result.Position + normal * 0.03, normal, perpendicular),
			})
			splat.Parent = parent
			TweenService:Create(splat, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
				Size = Vector3.new(0.05, diameter, diameter),
			}):Play()
			local lifetime = props.Lifetime or 4
			task.delay(lifetime - 1, function()
				if splat.Parent then
					TweenService:Create(splat, TweenInfo.new(1), { Transparency = 1 }):Play()
				end
			end)
			Debris:AddItem(splat, lifetime + 0.1)
		end
	end
end

--------------------------------------------------------------------------------
-- Plantillas de VFX Studio
--------------------------------------------------------------------------------

-- Devuelve ReplicatedStorage/SpellVFX/<spellId>/<kind> si existe.
-- kind: "Charge" | "Projectile" | "Impact"
function VFX.GetTemplate(spellId: string, kind: string): Instance?
	local folder = ReplicatedStorage:FindFirstChild(Config.VFXTemplatesFolderName)
	local spellFolder = folder and folder:FindFirstChild(spellId)
	return spellFolder and spellFolder:FindFirstChild(kind)
end

-- Deja una plantilla lista para moverla por CFrame sin físicas ni colisiones.
function VFX.PrepareVisual(root: Instance)
	local parts = root:GetDescendants()
	table.insert(parts, root)
	for _, item in parts do
		if item:IsA("BasePart") then
			item.Anchored = true
			item.CanCollide = false
			item.CanQuery = false
			item.CanTouch = false
			item.CastShadow = false
		end
	end
end

-- Clona una plantilla y la coloca en `cframe`.
-- Acepta BasePart o Model (se mueve con PivotTo), o un Attachment/Folder con
-- emisores (se mete en una parte invisible).
function VFX.Instantiate(template: Instance, cframe: CFrame, parent: Instance): PVInstance
	local root: PVInstance
	if template:IsA("BasePart") or template:IsA("Model") then
		root = template:Clone() :: PVInstance
	else
		root = VFX.Anchor(cframe, nil)
		if template:IsA("Attachment") then
			template:Clone().Parent = root
		else
			for _, child in template:GetChildren() do
				child:Clone().Parent = root
			end
		end
	end
	VFX.PrepareVisual(root)
	root:PivotTo(cframe)
	root.Parent = parent
	return root
end

-- Parte principal de un visual (para colgarle sonidos).
function VFX.GetRootPart(root: Instance): BasePart?
	if root:IsA("BasePart") then
		return root
	elseif root:IsA("Model") then
		return root.PrimaryPart or root:FindFirstChildWhichIsA("BasePart", true)
	end
	return nil
end

--------------------------------------------------------------------------------
-- Reproducción y limpieza
--------------------------------------------------------------------------------

local function descendantsAndSelf(root: Instance)
	local list = root:GetDescendants()
	table.insert(list, root)
	return list
end

-- Dispara todos los emisores de un efecto de impacto.
-- Convención compatible con muchos plugins de VFX: atributos EmitCount y EmitDelay.
function VFX.EmitAll(root: Instance)
	for _, item in descendantsAndSelf(root) do
		if item:IsA("ParticleEmitter") then
			local emitter = item
			local count = emitter:GetAttribute("EmitCount")
			local delay = emitter:GetAttribute("EmitDelay") or 0
			if count == nil and emitter.Enabled then
				-- Emisor continuo sin EmitCount: lo dejamos encendido un instante.
				task.delay(delay + 0.15, function()
					emitter.Enabled = false
				end)
			else
				emitter.Enabled = false
				task.delay(delay, function()
					if emitter.Parent then
						emitter:Emit(count or Config.DefaultEmitCount)
					end
				end)
			end
		end
	end
end

-- Detiene un efecto sin cortarlo de golpe: apaga emisores, luces y sonidos y
-- oculta las partes; las partículas y trails ya emitidos se desvanecen solos.
function VFX.StopEmitting(root: Instance)
	for _, item in descendantsAndSelf(root) do
		if item:IsA("ParticleEmitter") or item:IsA("Beam") then
			item.Enabled = false
		elseif item:IsA("Light") then
			TweenService:Create(item, TweenInfo.new(0.2), { Brightness = 0 }):Play()
		elseif item:IsA("Sound") then
			item:Stop()
		elseif item:IsA("BasePart") then
			item.Transparency = 1
		end
	end
end

-- Tiempo que tardan en desaparecer las partículas/trails de un efecto.
function VFX.MaxLifetime(root: Instance): number
	local longest = 0
	for _, item in descendantsAndSelf(root) do
		if item:IsA("ParticleEmitter") then
			longest = math.max(longest, item.Lifetime.Max + (item:GetAttribute("EmitDelay") or 0))
		elseif item:IsA("Trail") then
			longest = math.max(longest, item.Lifetime)
		end
	end
	return longest
end

--------------------------------------------------------------------------------
-- Sonido
--------------------------------------------------------------------------------

local function newSound(soundId: string, props)
	local sound = Instance.new("Sound")
	sound.SoundId = soundId
	sound.Volume = 0.6
	sound.RollOffMaxDistance = 120
	sound.PlaybackSpeed = random:NextNumber(0.95, 1.05)
	if props then
		apply(sound, props)
	end
	return sound
end

-- Sonido posicional dentro de una parte o attachment. Ignora IDs vacíos.
function VFX.PlaySoundIn(soundId: string?, parent: Instance?, props): Sound?
	if not soundId or soundId == "" or not parent then
		return nil
	end
	local sound = newSound(soundId, props)
	sound.Parent = parent
	sound:Play()
	if not sound.Looped then
		sound.Ended:Once(function()
			sound:Destroy()
		end)
	end
	return sound
end

-- Sonido de un solo uso en una posición del mundo.
function VFX.PlaySoundAt(soundId: string?, position: Vector3, props): Sound?
	if not soundId or soundId == "" then
		return nil
	end
	local attachment = Instance.new("Attachment")
	attachment.Name = "SpellSound"
	attachment.Parent = Workspace.Terrain
	attachment.WorldPosition = position
	local sound = VFX.PlaySoundIn(soundId, attachment, props)
	Debris:AddItem(attachment, 10)
	return sound
end

return VFX
