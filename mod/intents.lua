-------------------------------------------------
-- This file is part of Decision Descent.      --
--                                             --
-- Decision Descent is free software: you can  --
-- redistribute it and/or modify it under the  --
-- terms of the GNU General Public License as  --
-- published by the Free Software Foundation,  --
-- either version 3 of the License, or (at     --
-- your option) any later version.             --
--                                             --
-- Decision Descent is distributed in the      --
-- hope that it will be useful, but WITHOUT    --
-- ANY WARRANTY; without even the implied      --
-- warranty of MERCHANTABILITY or FITNESS FOR  --
-- A PARTICULAR PURPOSE.  See the GNU General  --
-- Public License for more details.            --
--                                             --
-- You should have received a copy of the GNU  --
-- General Public License along with Decision  --
-- Descent.                                    --
-- If not, see <http://www.gnu.org/licenses/>. --
-------------------------------------------------

local function spawnOrGive(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    local itemConfig = Isaac.GetItemConfig()
    local player = Isaac.GetPlayer(0)
    local game = Game()
    local itemPool = game:GetItemPool()
    
    if collectible > 0 then
        local collectibleData = itemConfig:GetCollectible(collectible)
        
        if collectibleData.Type == ItemType.ITEM_ACTIVE then
            local room = game:GetRoom()
            local spawnLocation = room:FindFreePickupSpawnPosition(player.Position, 1, true)
            
            game:Spawn(EntityType.ENTITY_PICKUP, PickupVariant.PICKUP_COLLECTIBLE, spawnLocation, Vector(0, 0), player, collectible, room:GetAwardSeed())
        elseif player:CanAddCollectible() then
            player:AddCollectible(collectible, 0)
        end
        
        itemPool:RemoveCollectible(collectible)
    end
end

local function spawn(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    local player = Isaac.GetPlayer(0)
    local game = Game()
    local itemPool = game:GetItemPool()
    
    if collectible > 0 then
        local room = game:GetRoom()
        local spawnLocation = room:FindFreePickupSpawnPosition(player.Position, 1, true)
        
        game:Spawn(EntityType.ENTITY_PICKUP, PickupVariant.PICKUP_COLLECTIBLE, spawnLocation, Vector(0, 0), player, collectible, room:GetAwardSeed())
        itemPool:RemoveCollectible(collectible)
    end
end


--[[  Intents  ]]--
local intents = {}


--[[ Player Intents  ]]--
intents["player.query.heart.bone.amount"] = function()
    local player = Isaac.GetPlayer(0)
    local health = player:GetMaxHealth() + player:GetSoulHearts()
    local count = 0
    
    for a = 1, health do
        if player:IsBoneHeart(a) then
            count = count + 1
        end
    end
    
    return count
end

intents["player.query.heart.black.amount"] = function()
    local player = Isaac.GetPlayer(0)
    local health = player:GetMaxHealth() + player:GetSoulHearts()
    local count = 0
    
    for a = 1, health do
        if player:IsBlackHeart(a) then
            count = count + 1
        end
    end
    
    return count
end

intents["player.query.heart.black.pickable"] = function() return Isaac.GetPlayer(0):CanPickBlackHearts() end

intents["player.query.heart.eternal.amount"] = function() return Isaac.GetPlayer(0):GetEternalHearts() end
intents["player.query.heart.eternal.pickable"] = function() return true end

intents["player.query.heart.golden.amount"] = function() return Isaac.GetPlayer(0):GetGoldenHearts() end
intents["player.query.heart.golden.pickable"] = function() return Isaac.GetPlayer(0):CanPickGoldenHearts() end

intents["player.query.heart.soul.amount"] = function()
    local player = Isaac.GetPlayer(0)
    local health = player:GetMaxHealth() + player:GetSoulHearts()
    local count = 0
    
    for a = 1, health do
        if not player:IsBoneHeart(a) and not player:IsBlackHeart(a) then
            count = count + 1
        end
    end
    
    return count
end

intents["player.query.heart.soul.pickable"] = function() return Isaac.GetPlayer(0):CanPickSoulHearts() end

intents["player.query.heart.red.amount"] = function() return Isaac.GetPlayer(0):GetMaxHealth() end
intents["player.query.heart.red.pickable"] = function() return Isaac.GetPlayer(0):CanPickRedHearts() end

intents["player.grant.collectible"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    spawnOrGive(collectible)
end

intents["player.grant.devil"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    local player = Isaac.GetPlayer(0)
    local itemConfig = Isaac.GetItemConfig()
    local item = itemConfig:GetCollectible(collectible)
    local price = item.DevilPrice * 2
    local grantsHealth = (item.AddMaxHearts + item.AddSoulHearts + item.AddBlackHearts) > 0
    local grantsLives = false
    local hasExtraLives = player:GetExtraLives() > 0
    local revivable = {
        CollectibleType.COLLECTIBLE_DEAD_CAT,
        CollectibleType.COLLECTIBLE_ONE_UP,
        CollectibleType.COLLECTIBLE_LAZARUS_RAGS,
        CollectibleType.COLLECTIBLE_JUDAS_SHADOW,
        CollectibleType.COLLECTIBLE_ANKH
    }
    
    for a = 1, #revivable do
        if collectible == revivable[a] then
            grantsLives = true
            break
        end
    end
    
    if player:GetPlayerType() == PlayerType.PLAYER_THEFORGOTTEN then player:GetSubPlayer() end
    
    if player:GetPlayerType() ~= PlayerType.PLAYER_THELOST then
        if player:GetMaxHearts() > price or (player:GetSoulHearts() > 0 and player:GetMaxHearts() > 0) then
            player:AddMaxHearts(-price)
            
            spawnOrGive(collectible)
        elseif player:GetSoulHearts() > 6 or hasExtraLives or grantsHealth or grantsLives then
            player:AddSoulHearts(-6)
            
            spawnOrGive(collectible)
        end
    end
end

intents["player.grant.trinket"] = function(trinket)
    if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
    if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
    
    local player = Isaac.GetPlayer(0)
    
    if trinket > 0 then player:AddTrinket(trinket) end
end

intents["player.grant.heart.red"] = function(amount) Isaac.GetPlayer(0):AddHearts(amount) end
intents["player.grant.heart.bone"] = function(amount) Isaac.GetPlayer(0):AddBoneHearts(amount) end
intents["player.grant.heart.soul"] = function(amount) Isaac.GetPlayer(0):AddSoulHearts(amount) end
intents["player.grant.heart.black"] = function(amount) Isaac.GetPlayer(0):AddBlackHearts(amount) end
intents["player.grant.heart.golden"] = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(amount) end
intents["player.grant.heart.eternal"] = function(amount) Isaac.GetPlayer(0):AddEternalHearts(amount) end
intents["player.grant.heart.container"] = function(amount) Isaac.GetPlayer(0):AddMaxHearts(amount * 2) end

intents["player.grant.key"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:AddGoldenKey() else player:AddKeys(amount) end
end

intents["player.grant.bomb"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:AddGoldenBomb() else player:AddBombs(amount) end
end

intents["player.grant.coin"] = function(amount) Isaac.GetPlayer(0):AddCoins(amount) end

intents["player.revoke.collectible"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    local player = Isaac.GetPlayer(0)
    
    if collectible > 0 and player:HasCollectible(collectible) then player:RemoveCollectible(collectible) end
end

intents["player.revoke.trinket"] = function(trinket)
    if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
    if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
    local player = Isaac.GetPlayer(0)
    
    if trinket > 0 and player:HasTrinket(trinket) then player:TryRemoveTrinket(trinket) end
end

intents["player.revoke.heart.red"] = function(amount) Isaac.GetPlayer(0):AddHearts(-amount) end
intents["player.revoke.heart.soul"] = function(amount) Isaac.GetPlayer(0):AddSoulHearts(-amount) end
intents["player.revoke.heart.bone"] = function(amount) Isaac.GetPlayer(0):AddBoneHearts(-amount) end
intents["player.revoke.heart.black"] = function(amount) Isaac.GetPlayer(0):AddBlackHearts(-amount) end
intents["player.revoke.heart.golden"] = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(-amount) end
intents["player.revoke.heart.eternal"] = function(amount) Isaac.GetPlayer(0):AddEternalHearts(-amount) end
intents["player.revoke.heart.container"] = function(amount) Isaac.GetPlayer(0):AddMaxHearts(-amount * 2) end

intents["player.revoke.key"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:RemoveGoldenKey() else player:AddKeys(-amount) end
end

intents["player.revoke.bomb"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:RemoveGoldenBomb() else player:AddBombs(-amount) end
end

intents["player.revoke.coin"] = function(amount) Isaac.GetPlayer(0):AddCoins(-amount) end


--[[  Isaac Intents  ]]--
intents["isaac.challenge"] = function() return Game().Challenge end
intents["isaac.difficulty"] = function() return Game().Difficulty end

intents["isaac.spawn"] = function(entityType, entityVariant, entitySubType)
    local game = Game()
    local room = game:GetRoom()
    local center = room:GetCenterPos()
    
    if tonumber(entityType) ~= nil then entityType = tonumber(entityType) end
    if tonumber(entityVariant) ~= nil then entityVariant = tonumber(entityVariant) end
    if tonumber(entitySubType) ~= nil then entitySubType = tonumber(entitySubType) end
    
    if type(entityType) == "string" then entityType = Isaac.GetEntityTypeByName(entityType) end
    if type(entityVariant) == "string" then entityVariant = Isaac.GetEntityVariantByName(entityType) end
    if type(entitySubType) ~= "number" then entitySubType = 0 end
    
    game:Spawn(entityType, entityVariant, center, Vector(0, 0), Isaac.GetPlayer(0), entitySubType, room:GetSpawnSeed())
end


--[[  Collectible Intents  ]]--
intents["collectible.query.cost.devil"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    return Isaac.GetItemConfig():GetCollectible(collectible).DevilPrice * 2
end
