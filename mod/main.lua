------------------------------------------------
-- This file is part of Decision Descent.
--
-- Decision Descent is free software:
-- you can redistribute it
-- and/or modify it under the
-- terms of the GNU General
-- Public License as published by
-- the Free Software Foundation,
-- either version 3 of the License,
-- or (at your option) any later
-- version.
--
-- Decision Descent is distributed in
-- the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without
-- even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A
-- PARTICULAR PURPOSE.  See the GNU
-- General Public License for more details.
--
-- You should have received a copy of the
-- GNU General Public License along with
-- Decision Descent.  If not,
-- see <https://www.gnu.org/licenses/>.
------------------------------------------------

--[[ Imports ]]--
local statusConfig, config = pcall(require, "config")
local statusJson, json = pcall(require, "json")
local statusHttp, http = pcall(require, "http")
local statusUtils, utils = pcall(require, "utils")
local statusIntents, _ = pcall(require, "intents")
local statusScheduler, scheduler = pcall(require, "scheduler")
local statusConstants, const = pcall(require, "constants")


--[[ Environment Validation ]]--
if not statusConfig or not statusJson or not statusIntents or not statusConstants or not statusHttp or not statusUtils or not statusScheduler or not debug then
    ---@param message string
    local function printError(message) Isaac.DebugString(string.format("[DescentIsaac] %s", tostring(message))) end
    
    ---@param condition boolean
    ---@param ifTrue any
    ---@param ifFalse any
    ---@return any
    local function conditional(condition, ifTrue, ifFalse) if condition then return ifTrue else return ifFalse end end
    
    ---@param module table
    ---@return string
    local function isFound(module) return conditional(module, "FOUND", "MISSING") end
    
    printError("+----------------------------------------------------------------------------------")
    printError("| Your Isaac environment doesn't appear to be right.")
    printError("| In order to run Decision Descent, you'll need to correct the following problems:")
    printError("|   • DEBUG LIBRARIES » " .. isFound(debug))
    printError("|   • CONFIG          » " .. isFound(statusConfig))
    printError("|   • JSON            » " .. isFound(statusJson))
    printError("|   • HTTP            » " .. isFound(statusHttp))
    printError("|   • UTILS           » " .. isFound(statusUtils))
    printError("|   • INTENTS         » " .. isFound(statusIntents))
    printError("|   • SCHEDULER       » " .. isFound(statusScheduler))
    printError("|   • CONSTANTS       » " .. isFound(statusConstants))
    printError("+----------------------------------------------------------------------------------")
    printError("| If the 'json' or 'http' libraries are missing, you can try...")
    printError("|   1. Closing the game if you haven't already")
    printError("|   2. Navigating to \"The Binding of Isaac: Rebirth\" in your Steam library")
    printError("|   3. Open the context menu via right-clicking on the game in the list")
    printError("|   4. Click on \"Properties\"")
    printError("|   5. Click on the \"LOCAL FILES\" tab at the top of the dialog")
    printError("|   6. Click on the \"VERIFY INTEGRITY OF GAME FILES...\" button")
    printError("|   7. Launching Isaac when the files are done verifying")
    printError("+----------------------------------------------------------------------------------")
    printError("| If the 'debug' or 'http' libraries are missing, you must do the following:")
    printError("|   1. Closing the game if you haven't already")
    printError("|   2. Navigating to \"The Binding of Isaac: Rebirth\" in your Steam library")
    printError("|   3. Open the context menu via right-clicking on the game in ths list")
    printError("|   4. Click \"Properties\"")
    printError("|   5. Click on the \"SET LAUNCH OPTIONS...\" button")
    printError("|   6. Type \"--luadebug\" into the text field, excluding the quotation marks")
    printError("|   7. Click the \"OK\" button")
    printError("|   8. Launch Isaac")
    printError("| ")
    printError("| The debug libraries are currently required for Decision Descent to function")
    printError("| properly due to the HTTP library being locked behind the \"--luadebug\" flag.")
    printError("+----------------------------------------------------------------------------------")
    printError("| If the 'utils', 'intents', 'scheduler', 'constants, or 'config'")
    printError("| libraries are missing, you can try the following...")
    printError("|   1. Unsubscribing from the mod on the Steam workshop")
    printError("|   2. Launching Isaac")
    printError("|   3. Resubscribing to the mod on the Steam workshop")
    printError("|   4. Launching Isaac")
    printError("+----------------------------------------------------------------------------------")
    printError("| If any of the above didn't solve your problem, you can submit an issue on the")
    printError("| mod's GitHub page @ https://github.com/sirrandoo/decision-descent")
    printError("|")
    printError("| Before you submit a new issue, there are a couple of things you could do first:")
    printError("|   • Search for your problem on the issue tracker --- You might find a solution")
    printError("|")
    printError("| If you still want to proceed with submitting a new issue, you should include...")
    printError("|   • Your log file")
    printError("|   • Your OS --- Isaac behaves differently on different OSes!")
    printError("|   • Your mod version")
    printError("|      • Your mod version can be found in the config.lua file, under 'meta.version'")
    printError("+----------------------------------------------------------------------------------")
    
    return error("Mod environment is not set up correctly", 0)
end


--[[ Class Declarations ]]--
---@class Version
---@field major number
---@field minor number
---@field micro number
local Version = {
    __eq = function(this, that)
        if type(this) ~= type(that) then return false end
        if type(this) == type(that) then return true end
        
        return this.major == that.major and this.minor == that.minor and this.micro == that.micro
    end,
    __lt = function(this, that)
        if type(this) ~= type(that) then return false end
        if this.major > that.major then return false end
        if this.minor > that.minor then return false end
        if this.micro > that.micro then return false end
        
        return true
    end,
    __gt = function(this, that)
        if type(this) ~= type(that) then return false end
        if this.major < that.major then return false end
        if this.minor < that.minor then return false end
        if this.micro < that.micro then return false end
        
        return true
    end,
    __le = function(this, that)
        if type(this) ~= type(that) then return false end
        if this.major > that.major then return false end
        if this.minor > that.minor then return false end
        if this.micro > that.micro then return false end
        
        return true
    end,
    __ge = function(this, that)
        if type(this) ~= type(that) then return false end
        if this.major < that.major then return false end
        if this.minor < that.minor then return false end
        if this.micro < that.micro then return false end
        
        return true
    end
}
Version.__index = Version

---
--- Creates a new Version object.
---
---@param major number
---@param minor number
---@param micro number
function Version.new(major, minor, micro)
    local self = { major = major, minor = minor, micro = micro }
    setmetatable(self, Version)
    
    return self
end

---
--- Creates a new Version object a version string.
---
---@param version string
---@return Version
function Version.fromString(version)
    local t = {}  ---@type string[]
    
    for s in string.gmatch(version, "%d+") do table.insert(t, tonumber(s)) end
    
    return Version.new(table.unpack(t))
end

---
--- Returns the version as a string.
---
---@return string
function Version:toString() return string.format("%d.%d.%d", self.major, self.minor, self.micro) end


---@field id string
---@field name string
---@field version Version
---@field api Version
---@class Metadata
local Metadata = {}
Metadata.__index = Metadata

---
--- Creates a new Metadata object.
---
---@param id string
---@param name string
---@param version Version
---@param api number
---@return Metadata
function Metadata.new(id, name, version, api)
    local self = { id = id, name = name, version = version, api = api }
    setmetatable(self, Metadata)
    
    return self
end

---
--- Returns the ID.
---
---@return string
function Metadata:getId() return self.id end

---
--- Returns the name.
---
---@return string
function Metadata:getName() return self.name end

---
--- Returns the version.
---
---@return Version
function Metadata:getVersion() return self.version end

---
--- Returns the API version.
---
---@return number
function Metadata:getApiVersion() return self.api end

---@class DescentIsaac
---
---@field inst table
---@field scheduler Scheduler
---@field logger Logger
---@field http PseudoWS
---@field state number
---@field metadata Metadata
local DescentIsaac = {}
DescentIsaac.__index = DescentIsaac

---
--- Creates a new instance of DescentIsaac.
---
--- • There should only ever be **ONE** instance of this class.
---
---@return DescentIsaac
function DescentIsaac.create()
    local self = {
        inst = nil,
        scheduler = scheduler.new(),
        logger = utils.getLogger(const.meta.id),
        http = http.create(),
        state = const.states.None,
        metadata = Metadata.new(const.meta.id, const.meta.name, Version.fromString(const.meta.version), 1.0)
    }
    setmetatable(self, DescentIsaac)
    
    return self
end

---
--- Prepares the mod for basic functionality.
---
function DescentIsaac:prepare()
    self.logger:info("Preparing Decision Descent...")
    self.state = const.states.SETTING_UP
    
    self.logger:info("Creating mod instance...")
    self.inst = RegisterMod(self.metadata:getName(), self.metadata:getApiVersion())
    
    self.logger:info("Injecting config intent...")
    self.http.intents.state = {
        config = {
            ---@param c table
            update = function(c)
                local rng = config.rng  -- TODO: Implement RNG settings in client
                
                config = c
                c.rng = rng
                
                self.logger:info("Config updated!")
            end
        }
    }
end

---
--- Initializes the mod for advanced functionality.
---
function DescentIsaac:initialize()
    self.logger:info("Initializing Decision Descent...")
    self.logger:info(string.format("Decision Descent v%s", self.metadata:getVersion():toString()))
    
    if not self.scheduler.running then
        self.logger:info("Starting scheduler...")
        self.scheduler:start()
    end
    
    if not self.http.socket then
        self.logger:info("Connecting to remote...")
        self.http:connect(config.http.host, config.http.port)
    end
    
    self.state = const.states.SET_UP
end

---
--- Schedules tasks for recurring execution.
---
function DescentIsaac:schedule()
    self.logger:info("Scheduling recurring tasks...")
    
    self.logger:info("Scheduling reoccurring HTTP reader...")
    self.scheduler:schedule(
            function()
                self.http:processMessage()
            end,
            true
    )
end

---
--- Automatically registers all callbacks defined in this class.
--- This method iterates over the members of this class to look
--- for keys in the ModCallbacks table, then automatically registers
--- them as a callback.
---
function DescentIsaac:registerCallbacks()
    self.logger:info("Registering callbacks...")
    local c = 0
    
    for k, v in pairs(DescentIsaac) do
        if ModCallbacks[k] ~= nil then
            self.logger:info(string.format("Registering callback \"%s\"...", k))
            self.inst:AddCallback(ModCallbacks[k], v)
            
            c = c + 1
        end
    end
    
    self.logger:info(string.format("Registered %d callbacks!", tonumber(c)))
end

---
--- Schedules a new collectible poll to be sent to the
--- other half.
---
---@param choices string[]
---@param aliases table
function DescentIsaac:sendCollectiblePoll(choices, aliases)
    if aliases == nil then aliases = {} end
    
    self.scheduler:schedule(function()
        self.http:sendMessage("polls.create", choices, aliases, "player.grant.collectible")
    end, false)
end

---
--- Schedules a new multi-collectible poll to be sent to
--- the other half.
---
---@param choices string[]
---@param aliases table
function DescentIsaac:sendMultiCollectiblePoll(choices, aliases)
    if aliases == nil then aliases = {} end
    
    self.scheduler:schedule(function()
        self.http:sendMessage("polls.multi.create", choices, aliases, "player.grant.collectible")
    end, false)
end

---
--- Schedules a new devil poll to be sent to the other half.
---
---@param choices string[]
---@param aliases table
function DescentIsaac:sendDevilPoll(choices, aliases)
    if aliases == nil then aliases = {} end
    
    self.scheduler:schedule(function()
        self.http:sendMessage("polls.multi.create", choices, aliases, "player.grant.devil")
    end, false)
end

---
--- Schedules a poll to be generated.
---
function DescentIsaac:generatePoll()
    self.scheduler:schedule(
            function()
                self.logger:info("Generating poll...")
                
                local mChoices = config.polls.choices.maximum
                local game = Game()
                local room = game:GetRoom()
                local rType = room:GetType()
                local rSeed = room:GetAwardSeed()
                local iConfig = Isaac.GetItemConfig()
                local iPool = game:GetItemPool()
                local rng = RNG()
                local choices = {}
    
                self.logger:debug("Setting RNG seed...")
                rng:SetSeed(rSeed, 0)
    
                self.logger:debug("Finding maximum number of choices...")
                if config.polls == nil or config.polls.choices.maximum == nil then mChoices = 10 end
                if config.polls.choices.maximum < 0 then mChoices = 10 end
                if config.polls.choices.maximum >= 0 then mChoices = config.polls.choices.maximum end
    
                self.logger:debug("Getting room item pool...")
                local rPool = iPool:GetPoolForRoom(rType, rSeed)
    
                self.logger:debug("Getting item defs for room...")
                local rSpecs = config.rng.rooms[tostring(rType)]
                
                if rSpecs ~= nil and rng:RandomInt(rSpecs.maximum) > rSpecs.minimum then return end
                
                
                -- Since Isaac doesn't let you peek at item pools, we'll
                -- have to constantly get new items until unique ones
                -- pop up.
                local t = 0
    
                self.logger:debug("Gathering choices...")
                while #choices < mChoices do
                    local c = iPool:GetCollectible(rPool, false, rSeed)
                    
                    if c == nil then t = t + 1 end
                    if t >= 3 then break end
                    
                    local i = iConfig:GetCollectible(c)
                    local dup = false
                    
                    for a = 1, #choices do
                        if choices[a] == c then
                            dup = true
                        end
                    end
        
                    if not dup and i ~= nil then table.insert(choices, { id = i.ID, name = i.Name }) end
                end
                
                if #choices <= 1 then return self.logger:warning("Could not generate enough options for a poll!") end
                
                
                -- Iterate over the choices so we can alias item IDs to their item names.
                -- Transforming the item name into aliases should be handled by the other half.
                local dChoices = {}
                local aliases = {}
                for _, item in ipairs(choices) do
                    local dChoice = tostring(item.id)
                    table.insert(dChoices, dChoice)
                    
                    if aliases[dChoice] == nil then aliases[dChoice] = {} end
        
                    table.insert(aliases[dChoice], item.name)
                end
    
                self.logger:debug("Sending poll params...")
                -- Time for the mess that is poll generation
                if rSpecs == nil then
                    -- If there is no spec defined for the room, we'll use the defaults
                    -- which are:
                    --
                    -- DEVIL / BLACK MARKET » Send a devil poll
                    -- ANYTHING ELSE        » Send a regular poll
                    if rType ~= RoomType.ROOM_DEVIL then
                        self.http:sendMessage("polls.create", dChoices, aliases, "player.grant.collectible")
                    elseif rType == RoomType.ROOM_DEVIL or rType == RoomType.ROOM_BLACK_MARKET then
                        self.http:sendMessage("polls.multi.create", dChoices, aliases, "player.grant.devil")
                    end
                else
                    -- If there is a spec for the room, we'll use that instead.
                    --
                    -- If the spec says a devil poll can be generated, we'll roll
                    -- the RNG to see if a non-devil room is going to be one.
                    --
                    -- If the spec doesn't define a devil poll value, or the value
                    -- is false, we'll use the defaults.
                    if rSpecs.devil then
                        if rType ~= RoomType.ROOM_DEVIL then
                            if rng:RandomInt(rSpecs.maximum) <= rSpecs.devil then
                                self.http:sendMessage("polls.multi.create", dChoices, aliases, "player.grant.devil")
                            else
                                self.http:sendMessage("polls.create", dChoices, aliases, "player.grant.collectible")
                            end
                        elseif rType == RoomType.ROOM_DEVIL or rType == RoomType.ROOM_BLACK_MARKET then
                            self.http:sendMessage("polls.multi.create", dChoices, aliases, "player.grant.devil")
                        end
                    else
                        if rType ~= RoomType.ROOM_DEVIL then
                            self.http:sendMessage("polls.create", dChoices, aliases, "player.grant.collectible")
                        elseif rType == RoomType.ROOM_DEVIL or roomType == RoomType.ROOM_BLACK_MARKET then
                            self.http:sendMessage("polls.multi.create", dChoices, aliases, "player.grant.devil")
                        end
                    end
                end
            end,
            false
    )
end


--[[ Declarations ]]--

local Mod = DescentIsaac.create()


--[[  Callbacks  ]]--
---
--- Invoked when the player starts a new run.
---
--- This callback is responsible for notifying the other half to remove any
--- current polls running.
---
function DescentIsaac.MC_POST_GAME_STARTED(isSave)
    if isSave then return end
    
    Mod:schedule(function()
        Mod:sendMessage("polls.delete", { "*" })
    end, false)
end

---
--- Invoked when the player exits a run.
---
--- This callback is responsible for notifying the other half to perform logical
--- closing operations, such as ending all running polls.
---
function DescentIsaac.MC_PRE_GAME_EXIT(shouldSave)
    if shouldSave then
        Mod:schedule(function()
            Mod:sendMessage("client.close")
        end, false)
    end
end

---
--- Invoked when the player enters a new level.
---
--- This callback is responsible for alerting the other half that the player
--- changed levels.
---
function DescentIsaac.MC_POST_NEW_LEVEL()
    Mod:schedule(function()
        Mod:sendMessage("client.state.level.changed")
    end, false)
end

---
--- Invoked after the game is finished rendering its assets, so we can render
--- ours.
---
--- This callback is responsible for displaying the version text at the
--- bottom-center of the screen, and ensuring boss room collectibles are removed.
---
function DescentIsaac.MC_POST_RENDER()
    if config.hud.enabled then
        local sX, sY = utils.getScreenSize()
        
        -- Render the version if it's an alpha build
        local vText = string.format("Decision Descent v%s", Mod.metadata:getVersion():toString())
        local rX = math.abs(math.floor(tonumber(sX) / 3) - Isaac.GetTextWidth(vText))
        
        Isaac.RenderScaledText(vText, rX, sY - 35, 0.5, 0.5, 1.0, 1.0, 1.0, 0.8)
    end
    
    -- Every half an in-game second, we'll check to see if the player is in the
    -- boss room.  If they are, and they killed the boss, we'll remove the item
    -- that spawns.
    if Isaac.GetFrameCount() % 15 == 0 then
        local cRoom = Game():GetRoom()
    
        if cRoom:GetType() == RoomType.ROOM_BOSS and cRoom:GetAliveBossesCount() <= 0 then
            local rCenter = cRoom:GetCenterPos()
            local entities = Isaac.GetRoomEntities()
        
            for _, entity in pairs(entities) do
                if entity.Type == EntityType.ENTITY_PICKUP and entity.Variant == PickupVariant.PICKUP_COLLECTIBLE then
                    if Mod.metadata:getVersion().major < 0 then Isaac.RenderText("+", entity.Position.X, entity.Position.Y, 1.0, 1.0, 1.0, 1.0) end
    
                    -- TODO: Currently, this only works if the player doesn't have "more options"
                    if entity.Position.X == rCenter.X then
                        Mod.logger:warning("Collectible is within deletion zone!")
                        Mod.logger:warning(string.format("Removing collectible #%s...", tostring(entity.SubType)))
    
                        entity:Remove()
                    end
                end
            end
        end
    end
end

---
--- Invoked when the player switches rooms.
---
--- This callback is responsible for ensuring a poll is generated when the
--- player enters a *new*, supported room.
---
function DescentIsaac.MC_POST_NEW_ROOM()
    Mod.scheduler.schedule(function()
        Mod.http:sendMessage("client.state.room.changed")
    end, false)
    
    local game = Game()
    local cRoom = game:GetRoom()
    local cLevel = game:GetLevel()
    local rType = cRoom:GetType()
    local lType = cLevel:GetStage()
    
    -- Ensure the current room is supported
    local supported = rType == RoomType.ROOM_ERROR or rType == RoomType.ROOM_TREASURE or rType == RoomType.ROOM_BOSS or rType == RoomType.ROOM_CURSE or rType == RoomType.ROOM_DEVIL or rType == RoomType.ROOM_ANGEL or rType == RoomType.ROOM_BLACK_MARKET
    
    if not supported then return end
    if not cRoom:IsFirstVisit() then return end
    
    
    -- Now it's time for another mess that is level checks and room checks.
    if lType == LevelStage.STAGE7 then
        -- The Void checks
        if supported and cRoom:GetDeliriumDistance() > 0 then
            Mod:generatePoll()
        end
    elseif lType == LevelStage.STAGE5 or lType == LevelStage.STAGE6 then
        if supported and not cRoom:IsCurrentRoomLastBoss() then
            -- Ignore Isaac/Satan boss room
            Mod:generatePoll()
        end
    elseif lType == LevelStage.STAGE3_2 or (lType == LevelStage.STAGE3_1 and cLevel:GetCurses() == LevelCurse.CURSE_OF_LABYRINTH) then
        if supported and not cRoom:IsCurrentRoomLastBoss() then
            -- Ignore the Mom boss room
            Mod:generatePoll()
        end
    elseif lType == LevelStage.STAGE4_2 or (lType == LevelStage.STAGE4_1 and cLevel:GetCurses() == LevelCurse.CURSE_OF_LABYRINTH) then
        if supported and not currentRoom:IsCurrentRoomLastBoss() then
            -- Ignore the It Lives! / Mom's Heart boss room
            Mod:generatePoll()
        end
    elseif lType == LevelStage.STAGE4_3 then
        if supported and rType ~= RoomType.ROOM_BOSS then
            -- Ignore Hushy's room
            Mod:generatePoll()
        end
    elseif supported then
        Mod:generatePoll()
    end
end

---
--- Invoked when the game finishes processing events.
---
--- This callback is responsible for ensuring the scheduler is always running.
---
function DescentIsaac.MC_POST_UPDATE()
    if Isaac.GetFrameCount() % 30 == 0 then
        Mod.scheduler:start()  -- Ensure the scheduler is always running
    end
end


--[[  Main  ]]--

Mod:prepare()
Mod:initialize()
Mod:schedule()
Mod:registerCallbacks()
