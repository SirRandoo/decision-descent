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

---
--- A utility function for awarding players items.
---
--- If the item is a passive item, the item is directly given to the player.
--- If the item is an active item, the item is spawned in the current room.
---
---@param collectible number  @The ID of the collectible to be awarded to the player.
---@param forceSpawn boolean  @Whether or not to forcibly spawn the collectible, even if it's a passive item.
local function spawnOrGiveCollectible(collectible, forceSpawn)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    local itemConfig = Isaac.GetItemConfig()
    local player = Isaac.GetPlayer(0)
    local game = Game()
    local itemPool = game:GetItemPool()
    
    if collectible > 0 then
        local collectibleData = itemConfig:GetCollectible(collectible)
    
        if collectibleData.Type == ItemType.ITEM_ACTIVE or forceSpawn then
            local room = game:GetRoom()
            local spawnLocation = room:FindFreePickupSpawnPosition(player.Position, 1, true)
            
            game:Spawn(EntityType.ENTITY_PICKUP, PickupVariant.PICKUP_COLLECTIBLE, spawnLocation, Vector(0, 0), player, collectible, room:GetAwardSeed())
        elseif player:CanAddCollectible() then
            player:AddCollectible(collectible, 0)
        end
        
        itemPool:RemoveCollectible(collectible)
    end
end

local function spawnOrGiveTrinket(trinket, forceSpawn)
    if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
    if type(trinket) == "string" then trinket = Isaac.GetItemIdByName(trinket) end
    
    local player = Isaac.GetPlayer(0)
    local game = Game()
    
    if trinket > 0 then
        if player:GetTrinket(0) == -1 and not forceSpawn then
            player:AddTrinket(trinket)
        elseif player:GetMaxTrinkets() > 1 and player:GetTrinket(1) == -1 then
            player:AddTrinket(trinket)
        else
            game:Spawn(EntityType.ENTITY_PICKUP, PickupVariant.PICKUP_TRINKET, spawnLocation, Vector(0, 0), player, trinket, room:GetAwardSeed())
        end
    end
end


--[[  Intents  ]]--
---
--- A key↔value table for assigning intents to their respective functions.
---
local intents = {}


--[[ Player Intents  ]]--
---
--- Returns the number of bone hearts the player currently has.
---
---@return number
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

---
--- Returns the number of black hearts the player currently has.
---
---@return number
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

---
--- Returns whether or not the player can currently pick up black hearts.
---
---@return boolean
intents["player.query.heart.black.obtainable"] = function() return Isaac.GetPlayer(0):CanPickBlackHearts() end

---
--- Returns the amount of eternal hearts the player currently has.
---
--- * This function should only return be 1 or 0.
---
---@return number
intents["player.query.heart.eternal.amount"] = function() return Isaac.GetPlayer(0):GetEternalHearts() end

---
--- Returns whether or not the player can currently pick up eternal hearts.
---
--- * This should always return true.
---
---@return boolean
intents["player.query.heart.eternal.obtainable"] = function() return true end

---
--- Returns the amount of golden hearts the player currently has.
---
---@return number
intents["player.query.heart.golden.amount"] = function() return Isaac.GetPlayer(0):GetGoldenHearts() end

---
--- Returns whether or not the player can currently pick up golden hearts.
---
---@return boolean
intents["player.query.heart.golden.obtainable"] = function() return Isaac.GetPlayer(0):CanPickGoldenHearts() end

---
--- Returns the number of soul hearts the player has.
---
--- * Note: This *only* includes soul hearts, not black hearts.
---
---@return number
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

---
--- Returns whether or not the player can currently pick up soul hearts.
---
---@return boolean
intents["player.query.heart.soul.obtainable"] = function() return Isaac.GetPlayer(0):CanPickSoulHearts() end

---
--- Returns the number of red hearts the player currently has.
---
---@return number
intents["player.query.heart.red.amount"] = function() return Isaac.GetPlayer(0):GetMaxHealth() end

---
--- Returns whether or not the player can currently pick up red hearts.
---
---@return boolean
intents["player.query.heart.red.obtainable"] = function() return Isaac.GetPlayer(0):CanPickRedHearts() end

---
--- Awards the player a collectible.
---
---@param collectible number  @The ID of the collectible being awarded.
intents["player.grant.collectible"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    spawnOrGiveCollectible(collectible)
end

---
--- Awards the player a devil collectible.
---
---@param collectible number  @The ID of the collectible being awarded.
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
    
    if player:GetPlayerType() ~= PlayerType.PLAYER_THELOST then
        if player:GetMaxHearts() > price or (player:GetSoulHearts() > 0 and player:GetMaxHearts() > 0) then
            player:AddMaxHearts(-price)
    
            spawnOrGiveCollectible(collectible)
        elseif player:GetSoulHearts() > 6 or hasExtraLives or grantsHealth or grantsLives then
            player:AddSoulHearts(-6)
    
            spawnOrGiveCollectible(collectible)
        end
    else
        spawnOrGiveCollectible(collectible)
    end
end

---
--- Awards the player a trinket.
---
---@param trinket number  @THe ID of the trinket being awarded.
intents["player.grant.trinket"] = function(trinket)
    if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
    if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
    
    if trinket > 0 then spawnOrGiveTrinket(trinket) end
end

---
--- Awards the player by filling a heart container.
---
---@param amount number  @The number of health, in half hearts, to increase the player's life-points by.
intents["player.grant.heart.red"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THESOUL then player = player:GetSubPlayer() end
    
    player:AddHearts(amount)
end

---
--- Awards the player with bone hearts.
---
---@param amount number  @The number of bone hearts to give to the player.
intents["player.grant.heart.bone"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THESOUL then player = player:GetSubPlayer() end
    
    player:AddBoneHearts(amount)
end

---
--- Awards the player with soul hearts.
---
---@param amount number  @The number of soul hearts, in half hearts, to give to the player.
intents["player.grant.heart.soul"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THEFORGOTTEN then player = player:GetSubPlayer() end
    
    player:AddSoulHearts(amount)
end

---
--- Awards the player with black hearts.
---
---@param amount number  @The number of black hearts, in half hearts, to give to the player.
intents["player.grant.heart.black"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THEFORGOTTEN then player = player:GetSubPlayer() end
    
    player:AddBlackHearts(amount)
end

---
--- Awards the player with golden hearts.
---
---@param amount number  @The number of golden hearts to give to the player.
intents["player.grant.heart.golden"] = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(amount) end

---
--- Awards the player with eternal hearts.
---
---@param amount number  @The number of eternal hearts to give to the player.  2 hearts will automatically be converted into a new heart container.
intents["player.grant.heart.eternal"] = function(amount) Isaac.GetPlayer(0):AddEternalHearts(amount) end

---
--- Awards the player with heart containers.
---
---@param amount number  @The number of heart containers to give to the player.
intents["player.grant.heart.container"] = function(amount) Isaac.GetPlayer(0):AddMaxHearts(amount * 2) end

---
--- Awards the player with keys.
---
---@param amount number  @The number of keys to give to the player.
---@param golden boolean  @Whether or not the player should be given a golden key.  If this is true, `amount` will be ignored.
intents["player.grant.key"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:AddGoldenKey() else player:AddKeys(amount) end
end

---
--- Awards the player with bombs.
---
---@param amount number  @The number of bombs to give to the player.
---@param golden boolean  @Whether or not the player should be given a golden bomb.  If this is true, `amount` will be ignored.
intents["player.grant.bomb"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:AddGoldenBomb() else player:AddBombs(amount) end
end

---
--- Awards the player with coins.
---
---@param amount number  @The number of coins to give to the player.
intents["player.grant.coin"] = function(amount) Isaac.GetPlayer(0):AddCoins(amount) end

---
--- Removes a collectible from the player, if they have it.
---
---@param collectible number  @The ID of the collectible to remove.
intents["player.revoke.collectible"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    local player = Isaac.GetPlayer(0)
    
    if collectible > 0 and player:HasCollectible(collectible) then player:RemoveCollectible(collectible) end
end

---
--- Removes a trinket from the player, if they have it.
---
---@param trinket number  @The ID of the trinket to remove.
intents["player.revoke.trinket"] = function(trinket)
    if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
    if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
    local player = Isaac.GetPlayer(0)
    
    if trinket > 0 and player:HasTrinket(trinket) then player:TryRemoveTrinket(trinket) end
end

---
--- Removes red hearts from the player.
---
--- * This does not remove heart containers.
---
---@param amount number  @The number of health, in half hearts, to remove from the player.
intents["player.revoke.heart.red"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THESOUL then player = player:GetSubPlayer() end
    
    player:AddHearts(-amount)
end

---
--- Removes soul hearts from the player.
---
---@param amount number  @The amount of soul hearts, in half hearts, to remove from the player.
intents["player.revoke.heart.soul"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THEFORGOTTEN then player = player:GetSubPlayer() end
    
    player:AddSoulHearts(-amount)
end

---
--- Removes bone hearts from the player.
---
---@param amount number  @The amount of bone hearts to remove from the player.
intents["player.revoke.heart.bone"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THESOUL then player = player:GetSubPlayer() end
    
    player:AddBoneHearts(-amount)
end

---
--- Removes black hearts from the player.
---
---@param amount number  @The amount of black hearts, in half hearts, to remove from the player.
intents["player.revoke.heart.black"] = function(amount)
    local player = Isaac.GetPlayer(0)
    
    if player.Type == PlayerType.PLAYER_THEFORGOTTEN then player = player:GetSubPlayer() end
    
    player:AddBlackHearts(-amount)
end

---
--- Removes golden hearts from the player.
---
---@param amount number  @The number of golden hearts to remove from the player.
intents["player.revoke.heart.golden"] = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(-amount) end

---
--- Removes eternal hearts from the player.
---
---@param amount number  @The number of eternal hearts to remove from the player.  This should only ever remove 1 eternal heart.
intents["player.revoke.heart.eternal"] = function(amount) Isaac.GetPlayer(0):AddEternalHearts(-amount) end

---
--- Removes heart containers from the player.
---
---@param amount number  @The number of heart containers to remove from the player.
intents["player.revoke.heart.container"] = function(amount) Isaac.GetPlayer(0):AddMaxHearts(-amount * 2) end

---
--- Removes keys from the player.
---
---@param amount number  @The number of keys to remove from the player.
---@param golden boolean  @Whether or not the player should lose their golden key, if they have one.  If this is true, `amount` is ignored.
intents["player.revoke.key"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:RemoveGoldenKey() else player:AddKeys(-amount) end
end

---
--- Removes bombs from the player.
---
---@param amount number  @The number of bombs to remove from the player.
---@param golden boolean  @Whether or not the player should lose their golden bomb, if they have one.  If this is true, `amount` is ignored.
intents["player.revoke.bomb"] = function(amount, golden)
    local player = Isaac.GetPlayer(0)
    
    if golden then player:RemoveGoldenBomb() else player:AddBombs(-amount) end
end

---
--- Removes coins from the player.
---
---@param amount number  @The number of coins to remove from the player.
intents["player.revoke.coin"] = function(amount) Isaac.GetPlayer(0):AddCoins(-amount) end


--[[  Isaac Intents  ]]--

---
--- Returns whether or not the current run is a challenge.
---
---@return number
intents["isaac.challenge"] = function() return Game().Challenge end

---
--- Returns the current difficulty of the game.
---
---@return number
intents["isaac.difficulty"] = function() return Game().Difficulty end

---
--- Spawns an entity in the center of the current room.
---
---@param entityType EntityType  @The type of entity to spawn.
---@param entityVariant number  @The variant of the entity.
---@param entitySubType number  @The subtype of the entity.
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
---
--- Returns the number of heart containers an item would cost were it to be a
--- devil deal.
---
--- * This is only the heart containers.  All items are automatically 3 spectral
--- hearts if the player does not have heart containers.
--- * This should be used in tandem with the intent `player.query.heart.red.amount`
--- to get the true price of the item in a given moment.
---
intents["collectible.query.cost.devil"] = function(collectible)
    if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
    if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
    
    return Isaac.GetItemConfig():GetCollectible(collectible).DevilPrice * 2
end

return intents
