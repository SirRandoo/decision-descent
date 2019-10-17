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
local const = require("constants")
local config = require("config")


--[[ Types ]]--
---@class Payload
---@field intent string
---@field args any[]
---@field kwargs table<string, any>
---@field reply string
local Payload = {}


--[[  Classes  ]]--
---
--- This class attempts to mimic a proper WebSocket in terms of non-blocking
--- reading and writing.  Any reads are converted to a Lua table, internally
--- known as intent payloads, then processed into functional intent calls.
---@class PseudoWS
---
---@field public host string @The address to connect to when `PseudoWS:connect` is called
---@field public port number @The port to connect to when `PseudoWS:connect` is called
---@field socket table
---@field listener thread
---@field queue Payload[]
---@field logger Logger
---@field intents table<string, function>
local PseudoWS = {}
PseudoWS.__index = PseudoWS

---
--- Creates a new pseudo WebSocket.
---
---@public
---@return PseudoWS
---@see PseudoWS#connect
function PseudoWS.create()
    local self = {
        host = "",
        port = 0,
        socket = nil,
        listener = nil,
        queue = {},
        logger = utils.getLogger(const.meta.id .. ".http"),
        intents = require("intents")
    }
    setmetatable(self, PseudoWS)
    
    return self
end

---
--- Sends a message through the socket.
---
---@param intent string
---@param arguments any[]
---@param kwargs table<string, any>
---@param reply string
function PseudoWS:sendMessage(intent, arguments, kwargs, reply)
    -- Ensure the arguments passed are valid
    if not intent or type(intent) ~= "string" then return self.logger:warning("Attempted to send a message with an invalid intent!") end
    if not arguments or type(arguments) ~= "table" then arguments = {} end
    if not kwargs or type(kwargs) ~= "table" then kwargs = {} end
    if reply and type(reply) ~= "string" then reply = nil end
    
    -- Create a payload
    local payload = { sender = const.sides.ISAAC, intent = intent }
    
    -- Populate the payload with optional content
    -- This is to reduce packet bloat
    if arguments then payload.args = arguments end
    if kwargs then payload.kwargs = kwargs end
    if reply then payload.reply = reply end
    
    -- Send the message to the other side.
    local s, m = self.socket:send(json.encode(payload))
    
    if not s and (m == "closed" or m == "Socket is not connected") then
        self:connect("127.0.0.1", config.http.port)
        self:sendMessage(intent, arguments, kwargs, reply)
        
        return
    end
    
    -- If the message couldn't be sent, we'll log the error.
    if not s then
        self.logger:warning("Could not send message to client!")
        self.logger:warning(string.format("Error message: %s", m))
        self.logger:info("Falling back to queuing message...")
        table.insert(self.queue, payload)
        return
    end
    
    -- If the message was sent, we'll log the number of bytes sent.
    self.logger:info(string.format("%d bytes sent!", tonumber(s)))
    
    -- Clear queued messages
    while #self.queue > 0 do
        local queued = self.queue[1]
        
        local status, message = self.socket:send(json.encode(queued))
        
        if not status then
            break
        end
        
        table.remove(self.queue, 1)
    end
end

---
--- Decodes a message from the other side.
---
---@param message string
---@return Payload|nil
function PseudoWS:decodeMessage(message)
    -- Attempt to decode the message.
    local s, m = pcall(json.decode, tostring(message))
    
    -- If the message couldn't be decoded, we'll log the message.
    if not s then return self.logger:warning(string.format("Could not decode message \"%s\" !", tostring(message))) end
    
    -- If the message could be decoded, we'll return it.
    m.intent = string.lower(m.intent)
    return m
end

---
--- Dispatches an intent payload from the other half to the mod's intent system.
---
---@param payload string
function PseudoWS:dispatch(payload)
    -- Attempt to decode the payload message
    local dPayload = self:decodeMessage(payload)
    
    -- If the payload couldn't be decoded, the payload will be logged.
    if not dPayload then return self.logger:warning(string.format("Could not dispatch payload \"%s\" !", payload)) end
    
    -- If the payload is a message from this half, we'll ignore it.
    if dPayload.sender == const.sides.ISAAC then self.logger:info("Received payload from ourselves!  Ignoring...") end
    
    self.logger:info(string.format("Processing payload with intent \"%s\" ...", dPayload.intent))
    
    self.logger:debug("Splitting intent into segments...")
    local segs = {}  ---@type string[]
    local c = self.intents
    
    -- Split the intent into segments, and insert them into the above array for use momentarily.
    for s in string.gmatch(dPayload.intent, "%w+") do segs[#segs] = s end
    
    -- Attempt to locate the intent in the intent database
    self.logger:debug("Attempting to find intent...")
    
    while #segs > 0 do
        local seg = segs[1]
        
        if c[seg] == nil then return self.logger:warning(string.format("Could not locate intent \"%s\" !", dPayload.intent)) end
        if type(c[seg]) == "function" then return self.logger:warning(string.format("Intent \"%s\" has no callable!", dPayload.intent)) end
        
        c = c[seg]
        table.remove(segs, 1)
    end
    
    
    -- Attempt to invoke the requested intent with the payload data.
    self.logger:info(string.format("Attempting to invoke intent \"%s\" with arguments {%s}", dPayload.intent, table.concat(dPayload.args, ", ")))
    
    ---@type number
    local snap = socket.gettime()
    local s, m = pcall(c, table.unpack(dPayload.args))
    
    if not s then return self.logger:warning("Intent failed with the following error: " .. tostring(m)) end
    
    self.logger:info(string.format("Intent execution took %d seconds.", socket.gettime() - snap))
    
    -- If the payload requested a response post-execution, we'll send the intent's output.
    if dPayload.reply then
        self.logger:info("The other side requested a reply!  Sending intent result...")
        self:sendMessage(dPayload.reply, { m })
    end
end

---
--- Processes any messages received through the socket.
---
function PseudoWS:processMessage()
    -- Attempt to retrieve a line from the socket.
    local s, m = self.socket:receive()
    
    -- If we couldn't read from the socket, we'll log it, then return.
    if s == nil and m ~= "timeout" then
        self.logger:warning("Could not retrieve from socket!  Reason: " .. tostring(m))
        
        if m == "closed" then
            self:connect("127.0.0.1", config.http.port)
        end
    end
    if s == '' or (s == nil and m == "timeout") then return end  -- Ignore empty responses
    
    -- If we could successfully read from the socket, we'll dispatch the payload.
    self.logger:info("Retrieved message: " .. tostring(s))
    self:dispatch(tostring(s))
end

---
--- Initiates a connection to a remote.
---
---@param host string
---@param port number
---@return boolean|string
function PseudoWS:connect(host, port)
    -- If either the `host` or the `port` are different from the values stored
    -- in the mod's fields, we'll update them to ensure the socket reconnects
    -- to the proper point should the socket need to be reconnected.
    if self.host ~= host then self.host = host end
    if self.port ~= port then self.port = port end
    
    -- If the socket hasn't been created yet, we'll create a new instance.
    -- Once the instance has been created, we'll set it to non-blocking,
    -- and enable "keepalive" on the socket.  Hopefully the latter will
    -- ensure the socket doesn't randomly close.
    if self.socket == nil then
        self.socket = socket.tcp()
    
        if not self.socket:setoption("keepalive", true) then self.logger:warning("Could not set socket to \"keepalive\"!  The socket may unexpectedly close.") end
    end
    
    -- Attempt to connect to the remote specified.
    local s, m = self.socket:connect(self.host, tonumber(self.port))
    
    -- If we couldn't connect, we'll log it, then return.
    if s == nil then
        self.logger:warning(string.format("Could not connect to %s:%d !  Reason: %s", tostring(host), tonumber(port), tostring(m)))
        return m
    end
    
    self.socket:settimeout(0)
    return tonumber(s) == 1  -- This should always be true, but we'll add this check just in case.
end

---
--- Disconnects from the remote.
---
function PseudoWS:disconnect()
    if self.socket ~= nil then self.socket:close() end
    if self.listener ~= nil then self.listener = nil end
end

return PseudoWS
