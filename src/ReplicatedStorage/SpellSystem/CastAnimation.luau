-- Animación de lanzamiento de hechizo vinculada al Animator del personaje.
--
-- Prioridad para obtener la animación:
--   1. spell.AnimationId (ID publicado propio del hechizo)
--   2. Config.DefaultCastAnimationId (ID publicado común)
--   3. Solo en Studio: la KeyframeSequence generada por CastAnimation.Build(),
--      registrada con KeyframeSequenceProvider (ID temporal "rbxtemp://").
--
-- La animación generada es para rigs R15: levanta el brazo derecho, carga sobre
-- la cabeza y lanza hacia delante. El marcador "Release" marca la salida de la bola.
-- Usa tools/CreateCastAnimationForEditor.luau para llevarla al Animation Editor
-- y publicarla (ver README.md).

local KeyframeSequenceProvider = game:GetService("KeyframeSequenceProvider")
local RunService = game:GetService("RunService")

local Config = require(script.Parent.Config)

local CastAnimation = {}

local function ang(x: number, y: number, z: number): CFrame
	return CFrame.Angles(math.rad(x), math.rad(y), math.rad(z))
end

-- Jerarquía de Poses R15: cada Pose cuelga de la Pose de su parte padre.
local HIERARCHY = {
	HumanoidRootPart = {
		LowerTorso = {
			UpperTorso = {
				Head = {},
				RightUpperArm = { RightLowerArm = { RightHand = {} } },
				LeftUpperArm = { LeftLowerArm = { LeftHand = {} } },
			},
		},
	},
}

-- Fotogramas clave. Las partes que no aparecen quedan en posición neutra.
-- El easing de cada fotograma se aplica al tramo que va hacia el siguiente.
-- Ejes (R15): X+ en el hombro levanta el brazo hacia delante, Z+ en el brazo
-- derecho lo abre hacia fuera, Y- en el torso gira el hombro derecho hacia atrás.
CastAnimation.Keyframes = {
	{
		Name = "Start",
		Time = 0,
		Easing = Enum.PoseEasingStyle.Cubic,
		Direction = Enum.PoseEasingDirection.Out,
		Poses = {},
	},
	{
		-- Levanta la mano: brazo derecho sobre la cabeza, torso girado hacia atrás.
		Name = "Raise",
		Time = 0.22,
		Easing = Enum.PoseEasingStyle.Linear,
		Direction = Enum.PoseEasingDirection.In,
		Poses = {
			UpperTorso = ang(5, -25, 0),
			Head = ang(-5, 20, 0),
			RightUpperArm = ang(150, 0, 15),
			RightLowerArm = ang(35, 0, 0),
			LeftUpperArm = ang(35, 0, -15),
			LeftLowerArm = ang(20, 0, 0),
		},
	},
	{
		-- Carga: mantiene el brazo arriba y lo lleva un poco más atrás.
		Name = "Charge",
		Time = 0.48,
		Easing = Enum.PoseEasingStyle.Cubic,
		Direction = Enum.PoseEasingDirection.In,
		Poses = {
			UpperTorso = ang(8, -30, 0),
			Head = ang(-5, 25, 0),
			RightUpperArm = ang(165, 0, 20),
			RightLowerArm = ang(45, 0, 0),
			RightHand = ang(-15, 0, 0),
			LeftUpperArm = ang(45, 0, -20),
			LeftLowerArm = ang(25, 0, 0),
		},
	},
	{
		-- Lanzamiento: brazo extendido hacia delante. Aquí sale la bola.
		Name = "Release",
		Time = 0.6,
		Marker = "Release",
		Easing = Enum.PoseEasingStyle.Cubic,
		Direction = Enum.PoseEasingDirection.InOut,
		Poses = {
			UpperTorso = ang(-12, 25, 0),
			Head = ang(5, -20, 0),
			RightUpperArm = ang(90, 0, 0),
			RightLowerArm = ang(5, 0, 0),
			RightHand = ang(-20, 0, 0),
			LeftUpperArm = ang(-20, 0, -10),
		},
	},
	{
		Name = "Recover",
		Time = 0.95,
		Easing = Enum.PoseEasingStyle.Linear,
		Direction = Enum.PoseEasingDirection.In,
		Poses = {},
	},
}

local function buildPose(name: string, children, keyframeData): Pose
	local pose = Instance.new("Pose")
	pose.Name = name
	pose.CFrame = keyframeData.Poses[name] or CFrame.identity
	pose.EasingStyle = keyframeData.Easing
	pose.EasingDirection = keyframeData.Direction
	for childName, grandChildren in children do
		buildPose(childName, grandChildren, keyframeData).Parent = pose
	end
	return pose
end

-- Construye la KeyframeSequence de la animación de lanzamiento.
function CastAnimation.Build(): KeyframeSequence
	local sequence = Instance.new("KeyframeSequence")
	sequence.Name = "SpellCast"
	sequence.Loop = false
	sequence.Priority = Enum.AnimationPriority.Action

	for _, keyframeData in CastAnimation.Keyframes do
		local keyframe = Instance.new("Keyframe")
		keyframe.Name = keyframeData.Name
		keyframe.Time = keyframeData.Time
		for rootName, children in HIERARCHY do
			buildPose(rootName, children, keyframeData).Parent = keyframe
		end
		if keyframeData.Marker then
			local marker = Instance.new("KeyframeMarker")
			marker.Name = keyframeData.Marker
			keyframe:AddMarker(marker)
		end
		keyframe.Parent = sequence
	end

	return sequence
end

local studioTempId: string? = nil
local studioTempFailed = false
local warnedR6 = false

local function resolveAnimationId(spell, humanoid: Humanoid): string?
	if spell.AnimationId and spell.AnimationId ~= "" then
		return spell.AnimationId
	end
	if Config.DefaultCastAnimationId ~= "" then
		return Config.DefaultCastAnimationId
	end
	if not (Config.UseStudioGeneratedAnimation and RunService:IsStudio()) then
		return nil
	end
	if humanoid.RigType ~= Enum.HumanoidRigType.R15 then
		if not warnedR6 then
			warnedR6 = true
			warn("[SpellSystem] La animación generada es solo para R15. Publica una animación R6 y pon su ID en Config.")
		end
		return nil
	end
	if not studioTempId and not studioTempFailed then
		local ok, result = pcall(function()
			return KeyframeSequenceProvider:RegisterKeyframeSequence(CastAnimation.Build())
		end)
		if ok then
			studioTempId = result
		else
			studioTempFailed = true
			warn("[SpellSystem] No se pudo registrar la animación temporal:", result)
		end
	end
	return studioTempId
end

-- Cache de pistas por Animator (claves débiles para no retener personajes muertos).
local trackCache = setmetatable({}, { __mode = "k" })

-- Reproduce la animación de lanzamiento. Devuelve la pista o nil si no hay animación.
function CastAnimation.Play(humanoid: Humanoid, spell): AnimationTrack?
	local animator = humanoid:FindFirstChildOfClass("Animator")
	if not animator then
		return nil
	end
	local animationId = resolveAnimationId(spell, humanoid)
	if not animationId then
		return nil
	end

	local tracks = trackCache[animator]
	if not tracks then
		tracks = {}
		trackCache[animator] = tracks
	end
	local track = tracks[animationId]
	if not track then
		local animation = Instance.new("Animation")
		animation.AnimationId = animationId
		track = animator:LoadAnimation(animation)
		track.Priority = Enum.AnimationPriority.Action
		track.Looped = false
		tracks[animationId] = track
	end

	track:Play(0.1, 1, spell.AnimationSpeed or 1)
	return track
end

return CastAnimation
