-- Servidor del sistema de hechizos.
--
-- * Crea los RemoteEvents y los Tools del inventario (uno por hechizo, en orden
--   de spell.Order -> teclas 1, 2, 3 del inventario de Roblox).
-- * Valida cada lanzamiento (herramienta equipada, cooldown, personaje vivo).
-- * Simula los proyectiles con Spherecast (autoritativo: el daño solo se aplica aquí).
-- * Avisa a los clientes para que dibujen la carga, el proyectil y el impacto.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local StarterPack = game:GetService("StarterPack")
local Workspace = game:GetService("Workspace")

local SpellSystem = ReplicatedStorage:WaitForChild("SpellSystem")
local Config = require(SpellSystem:WaitForChild("Config"))
local Registry = require(SpellSystem:WaitForChild("SpellRegistry"))

--------------------------------------------------------------------------------
-- Remotes
--------------------------------------------------------------------------------

local remotes = Instance.new("Folder")
remotes.Name = Config.RemotesFolderName

-- Cliente -> servidor: ("Charge", spellId) | ("Release", spellId, aimPosition) | ("Cancel")
local castRemote = Instance.new("RemoteEvent")
castRemote.Name = "CastSpell"
castRemote.Parent = remotes

-- Servidor -> clientes: ("Charge" | "ChargeEnd" | "Projectile" | "Impact" | "Expire", data)
local fxRemote = Instance.new("RemoteEvent")
fxRemote.Name = "SpellFX"
fxRemote.Parent = remotes

remotes.Parent = ReplicatedStorage

--------------------------------------------------------------------------------
-- Inventario: un Tool por hechizo
--------------------------------------------------------------------------------

local function createTool(spell): Tool
	local tool = Instance.new("Tool")
	tool.Name = spell.DisplayName
	tool.ToolTip = spell.Description or spell.DisplayName
	tool.TextureId = spell.Icon or ""
	tool.RequiresHandle = false
	tool.CanBeDropped = false
	tool:SetAttribute("SpellId", spell.Id)
	return tool
end

local function findSpellTool(container: Instance, spellId: string): Tool?
	for _, child in container:GetChildren() do
		if child:IsA("Tool") and child:GetAttribute("SpellId") == spellId then
			return child
		end
	end
	return nil
end

-- StarterPack se copia al Backpack en cada aparición y conserva el orden de
-- inserción, que es el que usa la barra de Roblox para las teclas 1-9.
-- Si ya pusiste a mano un Tool con el atributo SpellId (p. ej. con un Handle
-- propio), se respeta y no se crea otro.
for _, spell in Registry.GetAll() do
	if not findSpellTool(StarterPack, spell.Id) then
		createTool(spell).Parent = StarterPack
	end
end

-- Jugadores que ya habían aparecido antes de que corriera este script.
for _, player in Players:GetPlayers() do
	local backpack = player:FindFirstChildOfClass("Backpack")
	if backpack then
		for _, spell in Registry.GetAll() do
			local hasTool = findSpellTool(backpack, spell.Id)
				or (player.Character and findSpellTool(player.Character, spell.Id))
			if not hasTool then
				findSpellTool(StarterPack, spell.Id):Clone().Parent = backpack
			end
		end
	end
end

--------------------------------------------------------------------------------
-- Estado
--------------------------------------------------------------------------------

type PlayerState = { LastCast: { [string]: number }, LastCharge: number, Charging: boolean }

local playerStates: { [Player]: PlayerState } = {}

local function getState(player: Player): PlayerState
	local state = playerStates[player]
	if not state then
		state = { LastCast = {}, LastCharge = 0, Charging = false }
		playerStates[player] = state
	end
	return state
end

Players.PlayerRemoving:Connect(function(player)
	playerStates[player] = nil
end)

local function fireAllExcept(except: Player, kind: string, data)
	for _, player in Players:GetPlayers() do
		if player ~= except then
			fxRemote:FireClient(player, kind, data)
		end
	end
end

-- Devuelve personaje, humanoid y raíz si el jugador está vivo y tiene equipado
-- el Tool del hechizo indicado.
local function getCasterParts(player: Player, spellId: string)
	local character = player.Character
	local humanoid = character and character:FindFirstChildOfClass("Humanoid")
	local rootPart = character and character:FindFirstChild("HumanoidRootPart")
	if not humanoid or humanoid.Health <= 0 or not rootPart then
		return nil
	end
	if not findSpellTool(character, spellId) then
		return nil
	end
	return character, humanoid, rootPart
end

--------------------------------------------------------------------------------
-- Proyectiles
--------------------------------------------------------------------------------

type Projectile = {
	Id: number,
	Spell: any,
	Caster: Player,
	CasterCharacter: Model,
	Position: Vector3,
	Velocity: Vector3,
	Age: number,
	Params: RaycastParams,
}

local projectiles: { [number]: Projectile } = {}
local nextProjectileId = 0

local function findHumanoid(instance: Instance): (Model?, Humanoid?)
	local model = instance:FindFirstAncestorOfClass("Model")
	while model do
		local humanoid = model:FindFirstChildOfClass("Humanoid")
		if humanoid then
			return model, humanoid
		end
		model = model:FindFirstAncestorOfClass("Model")
	end
	return nil, nil
end

local function canDamage(caster: Player, targetCharacter: Model): boolean
	if Config.FriendlyFire then
		return true
	end
	local targetPlayer = Players:GetPlayerFromCharacter(targetCharacter)
	if not targetPlayer or caster.Neutral or targetPlayer.Neutral then
		return true
	end
	return caster.Team ~= targetPlayer.Team
end

local function spawnProjectile(player: Player, character: Model, spell, origin: Vector3, direction: Vector3)
	nextProjectileId += 1
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { character }

	local projectile: Projectile = {
		Id = nextProjectileId,
		Spell = spell,
		Caster = player,
		CasterCharacter = character,
		Position = origin,
		Velocity = direction * spell.Speed,
		Age = 0,
		Params = params,
	}
	projectiles[projectile.Id] = projectile

	fxRemote:FireAllClients("Projectile", {
		Id = projectile.Id,
		SpellId = spell.Id,
		CasterUserId = player.UserId,
		Origin = origin,
		Velocity = projectile.Velocity,
		Gravity = spell.Gravity or 0,
		Lifetime = spell.Lifetime,
	})
end

local function onProjectileHit(projectile: Projectile, result: RaycastResult)
	local spell = projectile.Spell
	local targetCharacter, targetHumanoid = findHumanoid(result.Instance)

	if targetHumanoid and targetCharacter and targetHumanoid.Health > 0
		and canDamage(projectile.Caster, targetCharacter)
	then
		local healthBefore = targetHumanoid.Health
		targetHumanoid:TakeDamage(spell.Damage) -- respeta ForceField
		local damageDealt = healthBefore - targetHumanoid.Health

		if spell.OnHit then
			-- task.spawn: los efectos pueden esperar (quemadura, ralentización)
			-- y un error en un hechizo no rompe el bucle de proyectiles.
			task.spawn(spell.OnHit, {
				Spell = spell,
				Caster = projectile.Caster,
				CasterCharacter = projectile.CasterCharacter,
				TargetCharacter = targetCharacter,
				TargetHumanoid = targetHumanoid,
				HitInstance = result.Instance,
				Position = result.Position,
				Normal = result.Normal,
				Damage = damageDealt,
			})
		end
	end

	fxRemote:FireAllClients("Impact", {
		Id = projectile.Id,
		SpellId = spell.Id,
		Position = result.Position,
		Normal = result.Normal,
	})
end

RunService.Heartbeat:Connect(function(dt)
	for id, projectile in projectiles do
		local spell = projectile.Spell
		projectile.Age += dt

		local velocity = projectile.Velocity - Vector3.new(0, (spell.Gravity or 0) * dt, 0)
		local displacement = velocity * dt
		local result = Workspace:Spherecast(projectile.Position, spell.Radius, displacement, projectile.Params)

		if result then
			projectiles[id] = nil
			onProjectileHit(projectile, result)
		else
			projectile.Position += displacement
			projectile.Velocity = velocity
			if projectile.Age >= spell.Lifetime then
				projectiles[id] = nil
				fxRemote:FireAllClients("Expire", { Id = id, Position = projectile.Position })
			end
		end
	end
end)

--------------------------------------------------------------------------------
-- Peticiones de los clientes
--------------------------------------------------------------------------------

local function onCharge(player: Player, spellId: any)
	if type(spellId) ~= "string" or not Registry.Get(spellId) then
		return
	end
	if not getCasterParts(player, spellId) then
		return
	end
	local state = getState(player)
	local now = os.clock()
	if now - state.LastCharge < 0.2 then
		return
	end
	state.LastCharge = now
	state.Charging = true
	-- El lanzador ya dibuja su propia carga; solo avisamos a los demás.
	fireAllExcept(player, "Charge", { CasterUserId = player.UserId, SpellId = spellId })
end

local function onRelease(player: Player, spellId: any, aimPosition: any)
	if type(spellId) ~= "string" or typeof(aimPosition) ~= "Vector3" then
		return
	end
	if aimPosition ~= aimPosition then -- NaN
		return
	end
	local spell = Registry.Get(spellId)
	if not spell then
		return
	end
	local character, _, rootPart = getCasterParts(player, spellId)
	if not character then
		return
	end

	local state = getState(player)
	local now = os.clock()
	local lastCast = state.LastCast[spellId]
	if lastCast and now - lastCast < spell.Cooldown - Config.CooldownLeniency then
		return
	end
	state.LastCast[spellId] = now
	state.Charging = false

	-- Origen: la mano derecha (R15) o el brazo derecho (R6).
	local hand = character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm")
	local origin = if hand and hand:IsA("BasePart") then hand.Position else rootPart.Position + Vector3.new(0, 1.5, 0)
	if (origin - rootPart.Position).Magnitude > 8 then
		origin = rootPart.Position + Vector3.new(0, 1.5, 0)
	end

	local direction = aimPosition - origin
	if direction.Magnitude < 0.01 then
		direction = rootPart.CFrame.LookVector
	end
	direction = direction.Unit
	origin += direction * Config.SpawnForwardOffset

	spawnProjectile(player, character, spell, origin, direction)
end

castRemote.OnServerEvent:Connect(function(player, action, ...)
	if action == "Charge" then
		onCharge(player, ...)
	elseif action == "Release" then
		onRelease(player, ...)
	elseif action == "Cancel" then
		local state = getState(player)
		if state.Charging then
			state.Charging = false
			fireAllExcept(player, "ChargeEnd", { CasterUserId = player.UserId })
		end
	end
end)
