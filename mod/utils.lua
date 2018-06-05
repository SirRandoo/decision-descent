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

--[[  Utility Methods  ]]--
function string:startswith(str) return string.sub(self, 1, string.len(str)) == str end
function string:endswith(str) return str == '' or string.sub(self, -string.len(str)) == str end
function string:isUpper() return string.upper(self) == self end
function string:isLower() return string.lower(self) == self end

local function splitIntent(intent)
    local segments = {}

    for segment in intent:gmatch("%w+") do
        Isaac.DebugString(segment)
        table.insert(segments, segment)
    end

    return segments
end

local function crawlStacktrace()
    local currentStack = 1

    while true do
        local stack = debug.getinfo(currentStack, "Snl")

        if stack == nil then
            break
        else
            if not stack.source:endswith("utils.lua") then
                local source, funcName, curLine = "(unknown file)", "(unknown function)", -1

                source = string.sub(stack.source, 2, string.len(stack.source))
                source, _ = source:gsub("(.*)[dD]ecision.[dD]escent%p", "")
                if stack.name then
                    funcName = stack.name
                end
                if stack.currentline then
                    curLine = stack.currentline
                end
                if string.len(source) > 60 then
                    source = string.sub(source, 1, 57) .. "..."
                end

                return source, funcName, curLine
            else
                currentStack = currentStack + 1
            end
        end
    end
end



----------------------------------------
-- Based on the Python logging module --
----------------------------------------


--[[  Logger Class Definitions  ]]--
local Logger = {}
local loggers = {}
Logger.__index = Logger


function Logger.new(loggerName)
    if loggerName == nil then
        loggerName = "root"
    end
    local returnable = {}

    returnable.name = loggerName
    returnable.msgFormat = "[{level}][{name}][{file}][{funcName}][Line #{line}] {message}"
    setmetatable(returnable, Logger)

    return returnable
end

function Logger:format(level, callerFile, callerName, callerLine, message)
    local returnString = self.msgFormat:gsub("{level}", level)
    returnString = returnString:gsub("{name}", self.name)
    returnString = returnString:gsub("{file}", callerFile)
    returnString = returnString:gsub("{funcName}", callerName)
    returnString = returnString:gsub("{line}", callerLine)
    returnString = returnString:gsub("{message}", tostring(message))

    return returnString
end

function Logger:setFormat(format) self.msgFormat = format end

function Logger:log(level, message)
    local callerFile, callerName, callerLine = crawlStacktrace()
    Isaac.DebugString(self:format(level, callerFile, callerName, callerLine, message))
end

function Logger:debug(message)	self:log("DEBUG", message) end
function Logger:info(message) self:log("INFO", message) end
function Logger:warning(message) self:log("WARNING", message) end
function Logger:error(message) self:log("ERROR", message) end
function Logger:critical(message) self:log("CRITICAL", message) end


--[[  Logger Functions  ]]--
local function getLogger(loggerName)
    if loggerName == nil then
        loggerName = "root"
    end

    if loggers[loggerName] ~= nil then
        return loggers[loggerName]
    else
        loggers[loggerName] = Logger.new(loggerName)

        return loggers[loggerName]
    end
end




return {
    ["crawlStacktrace"] = crawlStacktrace,
    ["log_levels"] = log_levels,
    ["logger"] = Logger,
    ["getLogger"] = getLogger,
    ["splitIntent"] = splitIntent
}
