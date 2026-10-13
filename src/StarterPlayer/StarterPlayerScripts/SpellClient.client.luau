-- Cliente del sistema de hechizos.
--
-- * Engancha los Tools de hechizo (atributo SpellId). Las teclas 1, 2 y 3 las
--   gestiona la barra de inventario de Roblox; al hacer clic se dispara Activated.
-- * Reproduce la animación de lanzamiento en el Animator, muestra la carga en la
--   mano y, en el marcador "Release", pide al servidor que lance el proyectil.
-- * Dibuja los VFX de todos los jugadores (carga, proyectil, impacto) y los limpia.

local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local Workspace = game:GetService("Workspace")

local SpellSystem = ReplicatedStorage:WaitForChild("SpellSystem")
local Config = require(SpellSystem:WaitForChild("Config"))
local Registry = require(SpellSystem:WaitForChild("SpellRegistry"))
local VFX = require(SpellSystem:WaitForChild("VFX"))
local CastAnimation = require(SpellSystem:WaitForChild("CastAnimation"))

local remotes = ReplicatedStorage:WaitForChild(Config.RemotesFolderName)
local castRemote = remotes:WaitForChild("CastSpell") :: RemoteEvent
local fxRemote = remotes:WaitForChild("SpellFX") :: RemoteEvent

local player = Players.LocalPlayer

-- Todos los efectos locales cuelgan de esta carpeta (fácil de limpiar/excluir).
local fxFolder = Instance.new("Folder")
fxFolder.Name = Config.ClientFXFolderName
fxFolder.Parent = Workspace

--------------------------------------------------------------------------------
-- Carga en la mano
--------------------------------------------------------------------------------

local function getHand(character: Model): BasePart?
	local hand = character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm")
	return if hand and hand:IsA("BasePart") then hand else nil
end

local function createCharge(character: Model?, spell): Attachment?
	local hand = character and getHand(character)
	if not hand then
		return nil
	end

	local template = VFX.GetTemplate(spell.Id, "Charge")
	local attachment: Attachment
	if template and template:IsA("Attachment") then
		-- Plantilla de VFX Studio: respetamos su posición dentro de la mano.
		attachment = template:Clone()
	else
		attachment = Instance.new("Attachment")
		attachment.Position = if hand.Name == "RightHand" then Vector3.new(0, -0.3, 0) else Vector3.new(0, -1.1, 0)
		if template then
			for _, child in template:GetChildren() do
				child:Clone().Parent = attachment
			end
		elseif spell.BuildCharge then
			spell.BuildCharge(attachment)
		end
	end
	attachment.Name = "SpellCharge"
	attachment.Parent = hand
	VFX.PlaySoundIn(spell.Sounds and spell.Sounds.Charge, attachment)
	return attachment
end

local function fadeOutCharge(attachment: Attachment?)
	if attachment and attachment.Parent then
		VFX.StopEmitting(attachment)
		Debris:AddItem(attachment, VFX.MaxLifetime(attachment) + 0.1)
	end
end

--------------------------------------------------------------------------------
-- Lanzamiento local
--------------------------------------------------------------------------------

type CastState = {
	Tool: Tool,
	SpellId: string,
	Track: AnimationTrack?,
	Charge: Attachment?,
}

local castState: CastState? = nil
local cooldowns: { [string]: number } = {}

local function getAimPosition(character: Model): Vector3
	local camera = Workspace.CurrentCamera
	local mouse = UserInputService:GetMouseLocation()
	local ray = camera:ViewportPointToRay(mouse.X, mouse.Y)

	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { character, fxFolder }

	local result = Workspace:Raycast(ray.Origin, ray.Direction * Config.MaxAimDistance, params)
	return if result then result.Position else ray.Origin + ray.Direction * Config.MaxAimDistance
end

local function cancelCast(notifyServer: boolean)
	local state = castState
	if not state then
		return
	end
	castState = nil
	cooldowns[state.SpellId] = nil -- no se gastó el hechizo
	if state.Track then
		state.Track:Stop(0.15)
	end
	fadeOutCharge(state.Charge)
	if notifyServer then
		castRemote:FireServer("Cancel")
	end
end

-- Espera al marcador "Release" de la animación (o a un tiempo fijo si no hay
-- animación). Devuelve false si el lanzamiento se canceló mientras tanto.
local function waitForRelease(state: CastState, spell): boolean
	local track = state.Track
	if not track then
		task.wait((spell.ReleaseTime or Config.FallbackReleaseTime) / (spell.AnimationSpeed or 1))
		return castState == state
	end

	local released = false
	local markerConnection = track:GetMarkerReachedSignal(Config.ReleaseMarkerName):Connect(function()
		released = true
	end)
	local start = os.clock()
	while not released and castState == state and os.clock() - start < Config.ReleaseMarkerTimeout do
		task.wait()
	end
	markerConnection:Disconnect()
	return castState == state
end

local function castSpell(tool: Tool, spell)
	if castState then
		return
	end
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	if not character or not humanoid or humanoid.Health <= 0 then
		return
	end
	local now = os.clock()
	local lastCast = cooldowns[spell.Id]
	if lastCast and now - lastCast < spell.Cooldown then
		return
	end
	cooldowns[spell.Id] = now

	local state: CastState = { Tool = tool, SpellId = spell.Id }
	castState = state
	castRemote:FireServer("Charge", spell.Id)
	state.Charge = createCharge(character, spell)
	state.Track = CastAnimation.Play(humanoid, spell)

	if not waitForRelease(state, spell) then
		return
	end
	castState = nil

	castRemote:FireServer("Release", spell.Id, getAimPosition(character))
	fadeOutCharge(state.Charge)
end

local hookedTools = setmetatable({}, { __mode = "k" })

local function hookTool(tool: Instance)
	if not tool:IsA("Tool") or hookedTools[tool] then
		return
	end
	local spellId = tool:GetAttribute("SpellId")
	local spell = spellId and Registry.Get(spellId)
	if not spell then
		return
	end
	hookedTools[tool] = true

	tool.Activated:Connect(function()
		castSpell(tool, spell)
	end)
	tool.Unequipped:Connect(function()
		if castState and castState.Tool == tool then
			cancelCast(true)
		end
	end)
end

local function onCharacterAdded(character: Model)
	cancelCast(false)

	local backpack = player:WaitForChild("Backpack")
	for _, child in backpack:GetChildren() do
		hookTool(child)
	end
	backpack.ChildAdded:Connect(hookTool)
	character.ChildAdded:Connect(hookTool)

	local humanoid = character:WaitForChild("Humanoid") :: Humanoid
	humanoid.Died:Connect(function()
		cancelCast(false)
	end)
end

player.CharacterAdded:Connect(onCharacterAdded)
if player.Character then
	task.spawn(onCharacterAdded, player.Character)
end

--------------------------------------------------------------------------------
-- VFX replicados (todos los jugadores)
--------------------------------------------------------------------------------

type ProjectileVisual = {
	Spell: any,
	Visual: PVInstance,
	Position: Vector3,
	Velocity: Vector3,
	Gravity: number,
	Age: number,
	Lifetime: number,
	Frozen: boolean,
	Params: RaycastParams,
}

local projectiles: { [number]: ProjectileVisual } = {}
local remoteCharges: { [number]: Attachment } = {}

local function endRemoteCharge(userId: number)
	fadeOutCharge(remoteCharges[userId])
	remoteCharges[userId] = nil
end

local function createProjectileVisual(spell, cframe: CFrame): PVInstance
	local template = VFX.GetTemplate(spell.Id, "Projectile")
	if template then
		return VFX.Instantiate(template, cframe, fxFolder)
	end
	local visual = spell.BuildProjectile()
	visual:PivotTo(cframe)
	visual.Parent = fxFolder
	return visual
end

local function finishProjectile(id: number, position: Vector3?)
	local record = projectiles[id]
	if not record then
		return
	end
	projectiles[id] = nil
	if position then
		record.Visual:PivotTo(CFrame.new(position))
	end
	-- Los trails y partículas ya emitidos se desvanecen solos antes de destruir.
	VFX.StopEmitting(record.Visual)
	Debris:AddItem(record.Visual, VFX.MaxLifetime(record.Visual) + 0.2)
end

local function playImpact(spell, position: Vector3, normal: Vector3)
	local cframe = CFrame.lookAt(position, position + normal)
	local template = VFX.GetTemplate(spell.Id, "Impact")
	local root: Instance? = nil
	if template then
		root = VFX.Instantiate(template, cframe, fxFolder)
	elseif spell.BuildImpact then
		root = spell.BuildImpact(cframe, fxFolder)
	end
	if root then
		VFX.EmitAll(root)
		Debris:AddItem(root, VFX.MaxLifetime(root) + 0.5)
	end
	VFX.PlaySoundAt(spell.Sounds and spell.Sounds.Impact, position)
end

local handlers = {}

function handlers.Charge(data)
	local spell = Registry.Get(data.SpellId)
	local caster = Players:GetPlayerByUserId(data.CasterUserId)
	if not spell or not caster or caster == player then
		return
	end
	endRemoteCharge(data.CasterUserId)
	local attachment = createCharge(caster.Character, spell)
	if attachment then
		remoteCharges[data.CasterUserId] = attachment
		-- Seguridad: si nunca llega el lanzamiento, la carga se apaga sola.
		task.delay(Config.MaxChargeTime, function()
			if remoteCharges[data.CasterUserId] == attachment then
				endRemoteCharge(data.CasterUserId)
			end
		end)
	end
end

function handlers.ChargeEnd(data)
	endRemoteCharge(data.CasterUserId)
end

function handlers.Projectile(data)
	local spell = Registry.Get(data.SpellId)
	if not spell then
		return
	end
	endRemoteCharge(data.CasterUserId)

	local origin: Vector3 = data.Origin
	local velocity: Vector3 = data.Velocity
	local visual = createProjectileVisual(spell, CFrame.lookAt(origin, origin + velocity))

	-- El visual se detiene antes de atravesar paredes mientras llega el impacto
	-- del servidor (que es quien decide de verdad dónde golpea).
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	local caster = Players:GetPlayerByUserId(data.CasterUserId)
	params.FilterDescendantsInstances = { fxFolder, caster and caster.Character or nil }

	projectiles[data.Id] = {
		Spell = spell,
		Visual = visual,
		Position = origin,
		Velocity = velocity,
		Gravity = data.Gravity,
		Age = 0,
		Lifetime = data.Lifetime,
		Frozen = false,
		Params = params,
	}

	VFX.PlaySoundAt(spell.Sounds and spell.Sounds.Cast, origin)
	VFX.PlaySoundIn(spell.Sounds and spell.Sounds.Travel, VFX.GetRootPart(visual), { Looped = true })
end

function handlers.Impact(data)
	local spell = Registry.Get(data.SpellId)
	finishProjectile(data.Id, data.Position)
	if spell then
		playImpact(spell, data.Position, data.Normal)
	end
end

function handlers.Expire(data)
	finishProjectile(data.Id, data.Position)
end

fxRemote.OnClientEvent:Connect(function(kind: string, data)
	local handler = handlers[kind]
	if handler then
		handler(data)
	end
end)

Players.PlayerRemoving:Connect(function(leaving)
	endRemoteCharge(leaving.UserId)
end)

RunService.RenderStepped:Connect(function(dt)
	for id, record in projectiles do
		record.Age += dt
		-- Seguridad por si se pierde el mensaje de impacto/expiración.
		if record.Age > record.Lifetime + 0.5 then
			finishProjectile(id)
			continue
		end
		if record.Frozen then
			continue
		end

		local velocity = record.Velocity - Vector3.new(0, record.Gravity * dt, 0)
		local displacement = velocity * dt
		local hit = Workspace:Raycast(record.Position, displacement, record.Params)
		if hit then
			record.Position = hit.Position
			record.Frozen = true
		else
			record.Position += displacement
			record.Velocity = velocity
		end
		record.Visual:PivotTo(CFrame.lookAt(record.Position, record.Position + record.Velocity))
	end
end)
