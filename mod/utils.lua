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

---
--- A class for displaying simple formatted log statements to Isaac's log file.
---
---@class Logger
---
---@field fmt string  @The format to use for log messages
---@field name string  @The name of the logger
---@field file file  @The file to output log statements to
local Logger = {}
Logger.__index = Logger

---@param name string
---@return Logger
function Logger.new(name)
    if not name then name = "root" end
    local self = { name = name, fmt = "[{name}][{level}] {message}", file = nil }
    setmetatable(self, Logger)
    
    return self
end

---
--- Formats log message components into the format defined in `fmt`.
---
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
    
    return t
end

---
--- Writes a log statement to the log file.
---
---@param level string
---@param message string
function Logger:log(level, message)
    local f = Isaac.DebugString
    
    if self.file ~= nil then
        f = function(content)
            self.file:write(content .. "\r\n")
        end
    end
    
    f(self:format(level, message))
end

---
--- Displays a DEBUG log statement to the log file.
---
---@param message string
function Logger:debug(message) self:log("DEBUG", message) end

---
--- Displays an INFO log statement to the log file.
---
---@param message string
function Logger:info(message) self:log("INFO", message) end

---
--- Displays a WARNING log statement to the log file.
---
---@param message string
function Logger:warning(message) self:log("WARNING", message) end

---
--- Displays an ERROR log statement to the log file.
---
---@param message string
function Logger:error(message) self:log("ERROR", message) end

---
--- Displays a CRITICAL log statement to the log file.
---
---@param message string
function Logger:critical(message) self:log("CRITICAL", message) end

--[[ Library Variables ]]--

local logFile


--[[ Functions ]]--

---
--- Gets the directory this file is currently in.
---
---@return string
local function getDirectory()
    return debug.getinfo(1, 'S').source:sub(2):match('(.*[/\\])')
end


return {
    ---
    --- Separates an intent string into segments.
    ---
    ---@param intent string
    ---@return table<string>
    splitIntent = function(intent)
        local t = {}
        
        for segment in intent:gmatch("%w+") do
            t[#t + 1] = segment
        end
        
        return segments
    end,
    
    ---
    --- Gets a logger.
    ---
    --- If the logger doesn't exist, a new one will be created.
    ---
    ---@param name string
    ---@return Logger
    getLogger = function(name)
        if not name then name = "root" end
    
        if not logFile then
            local handle, message, _ = io.open(getDirectory() .. "/log.txt", "w+")
            Isaac.DebugString(tostring(handle))
        
            if handle == nil then
                Isaac.DebugString('Could not open log.txt file for writing!  Reason: ' .. message)
                logFile = nil
            else
                logFile = handle
                handle:write('Testing\r\n')
            end
        end
        
        if loggers[name] == nil then loggers[name] = Logger.new(name) end
        
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
