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
	Isaac.DebugString(string.format("spawnOrGive collectible \"%s\"", collectible))
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


return {
	player = {
		query = {
			heart = {
				bone = {
					amount = function()
						local player = Isaac.GetPlayer(0)
						local health = player:GetMaxHealth() + player:GetSoulHearts()
						local count = 0

						for a=1, health do
							if player:IsBoneHeart(a) then
								count = count + 1
							end
						end

						return count
					end,
					pickable = function() return Isaac.GetPlayer(0):CanPickBoneHearts() end
				},

				black = {
					amount = function()
						local player = Isaac.GetPlayer(0)
						local health = player:GetMaxHealth() + player:GetSoulHearts()
						local count = 0

						for a=1, health do
							if player:IsBlackHeart(a) then
								count = count + 1
							end
						end

						return count
					end,
					pickable = function() return Isaac.GetPlayer(0):CanPickBlackHearts() end
				},

				eternal = {
					amount = function() return Isaac.GetPlayer(0):GetEternalHearts() end,
					pickable = function() return true end
				},

				golden = {
					amount = function() return Isaac.GetPlayer(0):GetGoldenHearts() end,
					pickable = function() return Isaac.GetPlayer(0):CanPickGoldenHearts() end
				},

				soul = {
					amount = function()
						local player = Isaac.GetPlayer(0)
						local health = player:GetMaxHealth() + player:GetSoulHearts()
						local count = 0

						for a=1, health do
							if not player:IsBoneHeart(a) and not player:IsBlackHeart(a) then
								count = count + 1
							end
						end

						return count
					end,
					pickable = function() return Isaac.GetPlayer(0):CanPickSoulHearts() end	
				},

				red = {
					amount = function() return Isaac.GetPlayer(0):GetMaxHealth() end,
					pickable = function() return Isaac.GetPlayer(0):CanPickRedHearts() end
				}
			}
		},

		grant = {
			collectible = function(collectible)
				if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
				if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
				spawnOrGive(collectible)
			end,

			devil = function(collectible)
				if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
				if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
				local player = Isaac.GetPlayer(0)
				local itemConfig = Isaac.GetItemConfig()
				local item = itemConfig:GetCollectible(collectible)
				local price = item.DevilPrice * 2
				if player:GetPlayerType() == PlayerType.PLAYER_THEFORGOTTEN then player = player:GetSubPlayer() end

				if player:GetPlayerType() ~= PlayerType.PLAYER_THELOST then
					if player:GetMaxHearts() > price or (player:GetSoulHearts() > 0 and player:GetMaxHearts() > 0)then
						player:AddMaxHearts(-price)
						spawnOrGive(collectible)
					elseif player:GetSoulHearts() > 6 then
						player:AddSoulHearts(-6)
						spawnOrGive(collectible)
					end
				else
					spawnOrGive(collectible)
				end
			end,

			trinket = function(trinket)
				if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
				if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
				local player = Isaac.GetPlayer(0)

				if trinket > 0 then player:AddTrinket(trinket) end
			end,

			heart = {
				red = function(amount) Isaac.GetPlayer(0):AddHearts(amount) end,
				soul = function(amount) Isaac.GetPlayer(0):AddSoulHearts(amount) end,
				black = function(amount) Isaac.GetPlayer(0):AddBlackHearts(amount) end,
				eternal = function(amount) Isaac.GetPlayer(0):AddEternalHearts(amount) end,
				container = function(amount) Isaac.GetPlayer(0):AddMaxHearts(amount) end,
				bone = function(amount) Isaac.GetPlayer(0):AddBoneHearts(amount) end,
				golden = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(amount) end
			},

			key = function(amount, golden)
				local player = Isaac.GetPlayer(0)

				if golden then player:AddGoldenKey() else player:AddKeys(amount) end
			end,

			bomb = function(amount, golden)
				local player = Isaac.GetPlayer(0)

				if golden then player:AddGoldenBomb() else player:AddBombs(amount) end
			end,

			coin = function(amount) Isaac.GetPlayer(0):AddCoins(amount) end
		},

		revoke = {
			collectible = function(collectible)
				if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
				if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
				local player = Isaac.GetPlayer(0)
				
				if collectible > 0 and player:HasCollectible(collectible) then
					player:RemoveCollectible(collectible)
				end
			end,

			trinket = function(trinket)
				if tonumber(trinket) ~= nil then trinket = tonumber(trinket) end
				if type(trinket) == "string" then trinket = Isaac.GetTrinketIdByName(trinket) end
				local player = Isaac.GetPlayer(0)

				if trinket > 0 and player:HasTrinket(trinket) then player:TryRemoveTrinket(trinket) end
			end,

			heart = {
				red = function(amount) Isaac.GetPlayer(0):AddHearts(-amount) end,
				soul = function(amount) Isaac.GetPlayer(0):AddSoulHearts(-amount) end,
				black = function(amount) Isaac.GetPlayer(0):AddBlackHearts(-amount) end,
				eternal = function(amount) Isaac.GetPlayer(0):AddEternalHearts(-amount) end,
				container = function(amount) Isaac.GetPlayer(0):AddMaxHearts(-amount) end,
				bone = function(amount) Isaac.GetPlayer(0):AddBoneHearts(-amount) end,
				golden = function(amount) Isaac.GetPlayer(0):AddGoldenHearts(-amount) end
			},

			key = function(amount, golden)
				local player = Isaac.GetPlayer(0)

				if golden then player:RemoveGoldenKey() else player:AddKeys(-amount) end
			end,

			bomb = function(amount, golden)
				local player = Isaac.GetPlayer(0)

				if golden then player:RemoveGoldenBomb() else player:AddBombs(-amount) end
			end,

			coin = function(amount) Isaac.GetPlayer(0):AddCoins(-amount) end
		}
	},

	isaac = {
		difficulty = function() return Game().Difficulty end,
		challenge = function() return Game().Challenge end,
		spawn = function(entityType, entityVariant, entitySubType)
			local game = Game()
			local room = game:GetRoom()
			local center = room:GetCenterPos()

			if tonumber(entityType) ~= nil then entityType = tonumber(entityType) end
			if tonumber(entityVariant) ~= nil then entityVariant = tonumber(entityVariant) end
			if tonumber(entitySubType) ~= nil then entitySubType = tonumber(entitySubType) end
			if type(entityType) == "string" then entityType = Isaac.GetEntityTypeByName(entityType) end
			if type(entityVariant) == "string" then entityVariant = Isaac.GetEntityVariantByName(entityVariant) end
			if type(entitySubType) ~= "number" then entitySubType = 0 end

			game:Spawn(entityType, entityVariant, center, Vector(0, 0), Isaac.GetPlayer(0), entitySubType, room:GetSpawnSeed())
		end
	},

	collectible = {
		query = {
			cost = {
				devil = function(collectible)
					if tonumber(collectible) ~= nil then collectible = tonumber(collectible) end
					if type(collectible) == "string" then collectible = Isaac.GetItemIdByName(collectible) end
					return Isaac.GetItemConfig():GetCollectible(collectible).DevilPrice
				end
			}
		}
	}
}
