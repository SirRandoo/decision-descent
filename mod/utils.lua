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


--[[  Logger Class Definitions  ]]--
---@type table<string, Logger>
local loggers = {}

---@class Logger
---
---@field fmt string  @The format to use for log messages
---@field name string  @The name of the logger
local Logger = {}
Logger.__index = Logger

---@param name string
---@return Logger
function Logger.new(name)
    if not name then name = "root" end
    
    return setmetatable({ name = name, fmt = "[{name}][{level}] {message}" }, Logger)
end

---@param level string
---@param message string
---@return string
function Logger:format(level, message)
    local t = self.fmt
    
    for m in string.gmatch(self.fmt, "{(%w+)}") do
        local p = "{" .. m .. "}"
        
        if m == "level" then
            t = string.gsub(t, p, level)
        elseif m == "name" then
            t = string.gsub(t, p, self.name)
        elseif m == "message" then
            t = string.gsub(t, p, message)
        end
    end
end

---@param level string
---@param message string
function Logger:log(level, message) Isaac.DebugString(self:format(level, message)) end

---@param message string
function Logger:debug(message)	self:log("DEBUG", message) end

---@param message string
function Logger:info(message) self:log("INFO", message) end

---@param message string
function Logger:warning(message) self:log("WARNING", message) end

---@param message string
function Logger:error(message) self:log("ERROR", message) end

---@param message string
function Logger:critical(message) self:log("CRITICAL", message) end




return {
    ---@param intent string
    ---@return table<string>
    splitIntent = function(intent)
        local t = {}
        
        for segment in intent:gmatch("%w+") do
            t[#t + 1] = segment
        end
        
        return segments
    end,
    
    ---@param name string
    ---@return Logger
    getLogger = function(name)
        if not name then name = "root" end
        if loggers[name] == nil then loggers[name] = logger.new(name) end
        
        return loggers[name]
    end,
    
    ---
    --- Gets the bottom-right position of the screen
    ---
    --- Author  » kilburn
    ---@return number, number
    getScreenSize = function()
        local room = Game():GetRoom()
        local pos = room:WorldToScreenPosition(Vector(0, 0)) - room:GetRenderScrollOffset() - Game().ScreenShakeOffset
        
        local rx = pos.X + 60 * 26 / 40
        local ry = pos.Y + 140 * (26 / 40)
        
        return rx * 2 + 13 * 26, ry * 2 + 7 * 26
    end
}
