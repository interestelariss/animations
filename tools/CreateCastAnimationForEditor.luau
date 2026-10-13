--[[
	Script para la BARRA DE COMANDOS de Roblox Studio (View > Command Bar).
	No es un Script del juego: copia todo el contenido y pégalo en la barra.

	Genera la KeyframeSequence "SpellCast" (la misma que usa el sistema en Studio)
	para que puedas retocarla y publicarla:

	1. Inserta un rig R15 (Avatar > Rig Builder > R15) y selecciónalo en Explorer.
	2. Ejecuta este script. La animación queda en <Rig>/AnimSaves/SpellCast.
	   Si no hay rig seleccionado, queda en ServerStorage/SpellCast.
	3. Publicar:
	   a) Animation Editor: selecciona el rig > botón "..." > Load > SpellCast,
	      ajústala si quieres y luego "..." > Publish to Roblox, o
	   b) Clic derecho sobre la KeyframeSequence en Explorer > Save to Roblox.
	4. Copia el ID resultante en Config.DefaultCastAnimationId
	   ("rbxassetid://TU_ID").

	Si creas tu propia animación desde cero, añade un evento/marcador llamado
	"Release" en el fotograma en que debe salir la bola (Animation Editor >
	botón de eventos > Add Animation Event > nombre "Release").
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Selection = game:GetService("Selection")
local ServerStorage = game:GetService("ServerStorage")

local CastAnimation = require(ReplicatedStorage.SpellSystem.CastAnimation)

local sequence = CastAnimation.Build()
local rig = Selection:Get()[1]

if rig and rig:IsA("Model") and rig:FindFirstChildOfClass("Humanoid") then
	-- El Animation Editor busca las animaciones guardadas en <Rig>/AnimSaves.
	local saves = rig:FindFirstChild("AnimSaves")
	if not saves then
		saves = Instance.new("ObjectValue")
		saves.Name = "AnimSaves"
		saves.Parent = rig
	end
	local old = saves:FindFirstChild(sequence.Name)
	if old then
		old:Destroy()
	end
	sequence.Parent = saves
	print("[SpellSystem] Animación creada en", sequence:GetFullName())
else
	sequence.Parent = ServerStorage
	print("[SpellSystem] No hay rig seleccionado. Animación creada en", sequence:GetFullName())
end

Selection:Set({ sequence })
