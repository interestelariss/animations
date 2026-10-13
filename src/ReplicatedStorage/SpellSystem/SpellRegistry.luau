-- Carga todos los módulos de SpellSystem/Spells y los ordena por su campo Order.
-- El orden determina la tecla del inventario: Order 1 -> tecla 1, etc.
-- Para añadir un hechizo nuevo basta con crear otro ModuleScript en Spells.

local Registry = {}

local byId = {}
local ordered = {}

for _, module in script.Parent:WaitForChild("Spells"):GetChildren() do
	if module:IsA("ModuleScript") then
		local spell = require(module)
		assert(type(spell.Id) == "string", `El hechizo {module.Name} no tiene Id`)
		assert(byId[spell.Id] == nil, `Id de hechizo duplicado: {spell.Id}`)
		byId[spell.Id] = spell
		table.insert(ordered, spell)
	end
end

table.sort(ordered, function(a, b)
	return (a.Order or math.huge) < (b.Order or math.huge)
end)

function Registry.Get(spellId: string)
	return byId[spellId]
end

function Registry.GetAll()
	return ordered
end

return Registry
