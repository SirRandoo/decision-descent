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


--[[  Requires  ]]--
local socket = require("socket")
local json = require("json")
local utils = require("utils")


--[[  Classes  ]]--
psuedoWs = {}
psuedoWs.__index = psuedoWs


function psuedoWs.create()
    local returnable = setmetatable({}, psuedoWs)
    
    returnable.host, returnable.port = "", 0
    returnable.socket, returnable.listener, returnable.manager = nil, nil, nil
    returnable.logger = utils.getLogger("decision_descent.http")
    returnable.intents = require("intents")
    
    return returnable
end

function psuedoWs:sendMessage(intent, arguments, kwargs, reply)
    if arguments == nil then arguments = {} end
    if kwargs == nil then kwargs = {} end
    if reply == nil then reply = "" end
    if type(intent) ~= "string" then error("Intent must be a string!") end
    if type(arguments) ~= "table" then error("Arguments must be a table of neutral arguments!") end

    succeeded, message = self.socket:send(json.encode({sender = 1, intent = intent, args = arguments, kwargs = kwargs, reply = reply}) .. "\r\n")

    if succeeded == nil then
        self.logger:warning("Could not send message to client!")
        self.logger:warning(string.format("Error message: %s", message))
    else
        self.logger:info(string.format("%s bytes sent!", tostring(succeeded)))
    end
end

function psuedoWs:decodeMessage(message)
    local succeeded, response = pcall(json.decode, message)
    
    if succeeded then
        return response
    else
        self.logger:warning("Message could not be decoded!")
        return nil
    end
end

function psuedoWs:dispatch(rawMessage)
    local decodedMessage = self:decodeMessage(rawMessage)
    
    if decodedMessage ~= nil then
        if decodedMessage.sender == 1 then self.logger:info("Ignoring message from ourselves...") end
        self.logger:info(string.format("Processing message intent \"%s\"...", decodedMessage.intent))
        intent = string.lower(tostring(decodedMessage.intent))

        self.logger:info("Splitting intent into segments...")
        local intentSegments = {}
        local cursor = self.intents
        for segment in intent:gmatch("%w+") do table.insert(intentSegments, segment) end

        self.logger:info("Attempting to find intent...")
        while #intentSegments > 0 do
            local segment = intentSegments[1]

            if cursor[segment] ~= nil then
                cursor = cursor[segment]
                table.remove(intentSegments, 1)
            else
                self.logger:warning(string.format("Intent \"%s\" could not be found!", decodedMessage.intent))
            end
        end

        pcall(function() self.logger:info(string.format("Invoking intent \"%s\" with arguments \"%s\"", decodedMessage.intent, table.concat(decodedMessage.args, ", "))) end)
        local succeeded, response = pcall(cursor, table.unpack(decodedMessage.args))

        if succeeded then
            self.logger:info("Intent invoked without any errors!")

            if decodedMessage.reply then
                self.logger:info("Sending intent output to client...")
                self:sendMessage(decodedMessage.reply, {response})
            end
        else
            self.logger:warning("Intent failed with the following error:")
            self.logger:warning(response)
        end
    end
end

function psuedoWs:onMessage()
    while true do
        local readable, _, errored = socket.select({self.socket}, nil, 0)

        if #readable > 0 and errored == nil then
            local succeeded, response = self.socket:receive()

            if succeeded ~= nil then
                self.logger:info(succeeded)
                self:dispatch(succeeded)
            elseif response ~= "timeout" then
                self.logger:warning("Could not read message from client!")
                self.logger:warning(string.format("Error message: %s", response))
            end
        end

        coroutine.yield()
    end
end


function psuedoWs:connect(host, port)
    if self.socket == nil then
        self.socket = socket.tcp()
        self.socket:settimeout(0)
    end
    if self.host ~= host then self.host = host end
    if self.port ~= port then self.port = port end
    local success, response = self.socket:connect(self.host, tonumber(self.port))

    self.listener = coroutine.create(function()
                                     self.logger:info("Receiving....")
                                        local succeeded, response = self.socket:receive()

                                        if succeeded ~= nil then
                                            self.logger:info(succeeded)
                                            self:dispatch(succeeded)
                                        elseif response ~= "timeout" then
                                            self.logger:warning("Could not read message from client!")
                                            self.logger:warning(string.format("Error message: %s", response))
                                        end
                                     end)

    return success
end

function psuedoWs:disconnect()
    if self.socket ~= nil then self.socket:close() end
    if self.listener ~= nil then self.listener = nil end
end

return { create = psuedoWs.create }
