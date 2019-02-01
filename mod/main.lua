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

--[[  Mini Config  ]]--
local config = {
    -- HTTP settings
    http = { host = "127.0.0.1", port = 25565 },
    
    -- RNG Rooms
    rooms = {
        [tostring(RoomType.ROOM_ERROR)] = { minimum = 7, maximum = 28, devil = 3 },
        [tostring(RoomType.ROOM_CURSE)] = { minimum = 2, maximum = 25 }
    },
    
    -- Items that revive the player
    revivable = {
        CollectibleType.COLLECTIBLE_DEAD_CAT,
        CollectibleType.COLLECTIBLE_ONE_UP,
        CollectibleType.COLLECTIBLE_JUDAS_SHADOW,
        CollectibleType.COLLECTIBLE_LAZARUS_RAGS,
        CollectibleType.COLLECTIBLE_ANKH
    }
}

--[[  Initial Declarations  ]]--
local name, version, apiVersion = "Decision Descent", "0.4.0", 1.0
local Descent = RegisterMod(name, apiVersion)
local fLogger = {  -- Fallback logger
    info = function(message) Isaac.DebugString(string.format("[descent][INFO] %s", tostring(message))) end,
    warning = function(message) Isaac.DebugString(string.format("[descent][WARN] %s", tostring(message))) end,
    critical = function(message) Isaac.DebugString(string.format("[descent][CRITICAL] %s", tostring(message))) end,
    debug = function(message) Isaac.DebugString(string.format("[descent][DEBUG] %s", tostring(message))) end,
    fatal = function(message) Isaac.DebugString(string.format("[descent][FATAL] %s", tostring(message))) end,
    log = function(message) Isaac.DebugString(string.format("[descent][LOG] %s", tostring(message))) end
}


--[[  Requires  ]]--
local json_imported, json = pcall(require, "json")
local utils_imported, utils = pcall(require, "utils")
local http_imported, http = pcall(require, "http")


--[[  Environment Checks  ]]--
if not debug then
    fLogger.fatal("Did you make sure to enable luadebug?")
    fLogger.fatal("You can enable luadebug with the following steps...")
    fLogger.fatal("    - Navigate to Isaac in your Steam library")
    fLogger.fatal("    - Right-click Isaac")
    fLogger.fatal("    - Click properties")
    fLogger.fatal("    - Click \"SET LAUNCH OPTIONS...\"")
    fLogger.fatal("    - Type \"--luadebug\" info the text field (without quotations)")
    fLogger.fatal("    - Click OK")
    fLogger.fatal("    - Press CLOSE")
    fLogger.fatal("    - Launch Isaac as normal")

    error("Debug libraries are required to use Decision Descent!")
end

if not json_imported then
    fLogger.fatal("Isaac's JSON library could not be imported!")
    fLogger.fatal("You can verify Isaac's local files with the following steps...")
    fLogger.fatal("    - Navigate to Isaac in your Steam library")
    fLogger.fatal("    - Right-click Isaac")
    fLogger.fatal("    - Click the \"LOCAL FILES\" tab")
    fLogger.fatal("    - Click \"VERIFY INTEGRITY OF GAME FILES...\"")
    fLogger.fatal("    - Launch Isaac as normal")
    fLogger.fatal("")

    fLogger.fatal("Error message:")
    fLogger.fatal(json)
    fLogger.fatal("")

    error("Isaac's JSON library is required to use Decision Descent!")
end

if not http_imported then
    fLogger.fatal("Decision Descent's HTTP library is missing!")
    fLogger.fatal("Isaac should have retrieved this file during launch!")
    fLogger.fatal("You can get this file with any of the following options...")
    fLogger.fatal("    - Relaunch Isaac")
    fLogger.fatal("    - Download it from Decision Descent's Github @ https://github.com/SirRandoo/decision-descent")
    fLogger.fatal("")

    fLogger.fatal("Error message:")
    fLogger.fatal(http)
    fLogger.fatal("")

    error("Decision Descent's HTTP library is required to use Decision Descent!")
end

if not utils_imported then
    fLogger.fatal("Decision Descent's utils library is missing!")
    fLogger.fatal("Isaac should have retrieved this file during launch!")
    fLogger.fatal("You can get this file with any of the following options...")
    fLogger.fatal("    - Relaunch Isaac")
    fLogger.fatal("    - Download it from Decision Descent's Github @ https://github.com/SirRandoo/decision-descent")
    fLogger.fatal("")

    fLogger.fatal("Error message:")
    fLogger.fatal(utils)
    fLogger.fatal("")

    error("Decision Descent's utils library is required to use Decision Descent!")
end


--[[  Post-Check Variables  ]]--
Descent.logger = utils.getLogger("descent")
Descent.http = http.create()


--[[  Additional Intents  ]]--
Descent.http.intents.state = {
    config = {
        update = function(modConf)
            local httpConfig = config.http
            local roomConfig = config.rooms

            config = modConf
            config.http = httpConfig
            config.rooms = roomConfig
    
            Descent.logger:info("Config updated!")
        end
    },

    dimensions = {
        update = function(width, height)
            if tonumber(width) == nil then
                width = 0
            else
                width = tonumber(width)
            end
            if tonumber(height) == nil then
                height = 0
            else
                height = tonumber(height)
            end

            config.dimensions = { width = width, height = height }
    
            Descent.logger:info("Dimensions updated!")
        end
    }
}


--[[  HTTP Checks  ]]--
local succeeded, response = pcall(function() Descent.http:connect(config.http.host, config.http.port) end)

if not succeeded then
    Descent.logger:critical("Could not connect to client!")
    Descent.logger:critical("The Lua half of Decision Descent is merely the client's puppet, and cannot function on its own!")
    Descent.logger:critical(string.format("Error message: %s", response))
else
    Descent.logger:info("Successfully connected to the client!")
end


--[[  Utility Functions  ]]--
local function generatePoll()
    Descent.logger:info("Generating poll...")

    local maximumChoices = 3
    local game = Game()
    local room = game:GetRoom()
    local roomType = room:GetType()
    local roomSeed = room:GetAwardSeed()
    local itemConfig = Isaac.GetItemConfig()
    local itemPool = game:GetItemPool()
    local choices = {}

    if config.core then
        if config.core.maximum_choices < 0 then
            maximumChoices = 10  -- Reduced for obvious reasons
        elseif config.core.maximum_choices == 0 then
            maximumChoices = 0
        else
            maximumChoices = config.core.maximum_choices
        end
    end

    local roomPool = itemPool:GetPoolForRoom(roomType, roomSeed)
    local roomSpecs = config.rooms[tostring(roomType)]

    if roomSpecs ~= nil then
        local shouldGenerate = math.random(roomSpecs.maximum) <= roomSpecs.minimum

        if not shouldGenerate then
            return
        end
    end

    while #choices < maximumChoices do
        local choice = itemPool:GetCollectible(roomPool, false, roomSeed)

        if choice ~= nil then
            local item = itemConfig:GetCollectible(choice)
            local duplicate = false

            for a = 1, #choices do
                if choices[a] == choice then
                    duplicate = true
                end
            end

            if not duplicate then
                table.insert(choices, { item.ID, item.Name })
            end
        else
            break
        end
    end

    if #choices > 1 then
        local directChoices = {}
        local aliases = {}

        for _, itemArray in pairs(choices) do
            local directChoice = tostring(itemArray[1])
            table.insert(directChoices, directChoice)

            if aliases[directChoice] ~= nil then
                table.insert(aliases[directChoice], itemArray[2])
            else
                aliases[directChoice] = { itemArray[2] }
            end
        end

        if roomSpecs == nil then
            if roomType ~= RoomType.ROOM_DEVIL then
                Descent.http:sendMessage("polls.create", directChoices, aliases, "player.grant.collectible")
            elseif roomType == RoomType.ROOM_DEVIL or roomType == RoomType.ROOM_BLACK_MARKET then
                Descent.http:sendMessage("polls.multi.create", directChoices, aliases, "player.grant.devil")
            end
        else
            if roomSpecs.devil ~= nil then
                local isDevilPoll = math.random(roomSpecs.maximum) <= roomSpecs.devil

                if roomType ~= RoomType.ROOM_DEVIL then
                    if not isDevilPoll then
                        Descent.http:sendMessage("polls.create", directChoices, aliases, "player.grant.collectible")
                    else
                        Descent.http:sendMessage("polls.multi.create", directChoices, aliases, "player.grant.devil")
                    end
                elseif roomType == RoomType.ROOM_DEVIL or roomType == RoomType.ROOM_BLACK_MARKET then
                    Descent.http:sendMessage("polls.multi.create", directChoices, aliases, "player.grant.devil")
                end
            else
                if roomType ~= RoomType.ROOM_DEVIL then
                    Descent.http:sendMessage("polls.create", directChoices, aliases, "player.grant.collectible")
                elseif roomType == RoomType.ROOM_DEVIL or roomType == RoomType.ROOM_BLACK_MARKET then
                    Descent.http:sendMessage("polls.multi.create", directChoices, aliases, "player.grant.devil")
                end
            end
        end
    else
        Descent.logger:info("Insufficient choices!")
    end
end


--[[  Callbacks  ]]--
function Descent.POST_GAME_STARTED(isSave)
    if not isSave then
        Descent.http:sendMessage("polls.delete", { "*" })
    end
end
function Descent.PRE_GAME_EXIT(shouldSave) if shouldSave then Descent.http:sendMessage("client.close") end end
function Descent.POST_NEW_LEVEL() Descent.http:sendMessage("client.state.level.changed") end
function Descent.POST_RENDER()
    local renderText = string.format("Decision Descent v%s", version)

    if config.dimensions ~= nil then
        local renderX = math.abs(math.floor(tonumber(config.dimensions.width) / 3) - Isaac.GetTextWidth(renderText))

        if config.hud ~= nil then
            if config.hud.enabled then
                local renderY = math.floor((tonumber(config.dimensions.height) / 2) - config.hud.height * 1.5) - 35

                Isaac.RenderScaledText(renderText, renderX, renderY, config.hud.width, config.hud.height, config.hud.text_color.r, config.hud.text_color.g, config.hud.text_color.b, config.hud.alpha)
            end
        else
            local renderY = math.floor(tonumber(config.dimensions.height) / 2)

            Isaac.RenderScaledText(renderText, renderX, renderY, 0.5, 0.5, 1.0, 1.0, 1.0, 0.8)
        end
    end

    if Isaac.GetFrameCount() % 15 == 0 then
        local currentRoom = Game():GetRoom()

        if currentRoom:GetType() == RoomType.ROOM_BOSS then
            local centerPos = currentRoom:GetCenterPos()
            local entities = Isaac.GetRoomEntities()

            for a = 1, #entities do
                local entity = entities[a]

                if entity.Type == EntityType.ENTITY_PICKUP and entity.Variant == PickupVariant.PICKUP_COLLECTIBLE then
                    Isaac.RenderText("+", entity.Position.X, entity.Position.Y, 1.0, 1.0, 1.0, 1.0)

                    if entity.Position.X == centerPos.X then
                        Descent.logger:warning("Collectible is within deletion zone!")
                        Descent.logger:warning(string.format("Removing collectible #%s...", tostring(entity.SubType)))

                        entity:Remove()
                    end
                end
            end
        end
    end
end
function Descent.POST_UPDATE()
    if Isaac.GetFrameCount() % 30 == 0 then
        local status = coroutine.status(Descent.http.listener)

        if status == "suspended" then
            coroutine.resume(Descent.http.listener)
        elseif status == "dead" then
            Descent.logger:critical("Listener coroutine is dead!")
            Descent.logger:critical("Reviving coroutine...")
            Descent.http.listener = coroutine.create(function()
                Descent.http:onMessage()
            end)
        end
    end
end
function Descent.POST_NEW_ROOM()
    Descent.http:sendMessage("client.state.room.changed")

    local game = Game()
    local currentRoom = game:GetRoom()
    local currentLevel = game:GetLevel()
    local roomType = currentRoom:GetType()
    local levelType = currentLevel:GetStage()

    --[[  Room Checks  ]]--
    local isSupportedRoom = roomType == RoomType.ROOM_ERROR or roomType == RoomType.ROOM_TREASURE or roomType == RoomType.ROOM_BOSS or roomType == RoomType.ROOM_CURSE or roomType == RoomType.ROOM_DEVIL or roomType == RoomType.ROOM_ANGEL or roomType == RoomType.ROOM_BLACK_MARKET
    
    if currentRoom:IsFirstVisit() then
        local generator = coroutine.create(generatePoll)

        if levelType == LevelStage.STAGE7 then
            -- The Void checks
            if isSupportedRoom and currentRoom:GetDeliriumDistance() > 0 then
                coroutine.resume(generator)
            end
        elseif levelType == LevelStage.STAGE5 or levelType == LevelStage.STAGE6 then
            if isSupportedRoom and not currentRoom:IsCurrentRoomLastBoss() then
                -- Ignore Isaac/Satan boss room
                coroutine.resume(generator)
            end
        elseif levelType == LevelStage.STAGE3_2 or (levelType == LevelStage.STAGE3_1 and currentLevel:GetCurses() == LevelCurse.CURSE_OF_LABYRINTH) then
            if isSupportedRoom and not currentRoom:IsCurrentRoomLastBoss() then
                -- Ignore the Mom boss room
                coroutine.resume(generator)
            end
        elseif levelType == LevelStage.STAGE4_2 or (levelType == LevelStage.STAGE4_1 and currentLevel:GetCurses() == LevelCurse.CURSE_OF_LABYRINTH) then
            if isSupportedRoom and not currentRoom:IsCurrentRoomLastBoss() then
                -- Ignore the It Lives! / Mom's Heart boss room
                coroutine.resume(generator)
            end
        elseif levelType == LevelStage.STAGE4_3 then
            if isSupportedRoom and roomType ~= RoomType.ROOM_BOSS then
                -- Ignore Hushy's room
                coroutine.resume(generator)
            end
        elseif isSupportedRoom then
            coroutine.resume(generator)
        end
    end
end


--[[  Main  ]]--
Descent.logger:warning("Decision Descent current only supports Windows 10!")
Descent.logger:warning("If you are using Decision Descent on an operating system other than Windows 10, be sure to submit your issues on the Github page @ https://github.com/sirrandoo/decision-descent")

Descent.logger:info("Registering callbacks...")

Descent.logger:info("Registering MC_POST_GAME_STARTED callback...")
Descent:AddCallback(ModCallbacks.MC_POST_GAME_STARTED, Descent.POST_GAME_STARTED)

Descent.logger:info("Registering MC_PRE_GAME_EXIT callback...")
Descent:AddCallback(ModCallbacks.MC_PRE_GAME_EXIT, Descent.PRE_GAME_EXIT)

Descent.logger:info("Registering MC_POST_NEW_LEVEL callback...")
Descent:AddCallback(ModCallbacks.MC_POST_NEW_LEVEL, Descent.POST_NEW_LEVEL)

Descent.logger:info("Registering MC_POST_NEW_ROOM callback...")
Descent:AddCallback(ModCallbacks.MC_POST_NEW_ROOM, Descent.POST_NEW_ROOM)

Descent.logger:info("Registering MC_POST_RENDER callback...")
Descent:AddCallback(ModCallbacks.MC_POST_RENDER, Descent.POST_RENDER)

Descent.logger:info("Registering MC_POST_UPDATE callback...")
Descent:AddCallback(ModCallbacks.MC_POST_UPDATE, Descent.POST_UPDATE)

Descent.logger:info("Callbacks registered!")
Descent.logger:info(string.format("Decision Descent v%s loaded!", version))
