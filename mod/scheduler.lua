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

---@class Task
local Task = {}
Task.__index = {}

---
--- Creates a new task
---
---@param f function  @The function to call
---@param p boolean  @An indicator that this task should rejoin the queue once the function has been called.
---@return Task
function Task.new(f, p)
    local self = { func = f, persist = p, __call = f, __newindex = function() end }
    setmetatable(self, Task)
    
    return self
end

---
--- Whether or not the task should be revived.
---
---@return boolean
function Task:revivable() return p end

---
--- Schedulers are responsible for managing methods that should be called away
--- from the main thread.  Methods that do not request a revival will be removed
--- from the task list.
---
---@class Scheduler
---@field tasks Task[]
---@field thread thread
---@field running boolean
local Scheduler = {}
Scheduler.__index = Scheduler

---
--- Creates a new scheduler.
---
---@return Scheduler
function Scheduler.new()
    local self = { tasks = {}, thread = nil, running = false }
    setmetatable(self, Scheduler)
    
    return self
end

---
--- Schedules a function to be run in the coroutine system.
---
---@param f function
---@param revive boolean  @Whether or not the function should be re-queued when it finishes executing.
function Scheduler:schedule(f, revive)
    if type(f) ~= "function" then return end
    if revive == nil then revive = false end
    
    table.insert(self.tasks, Task.new(f, revive))
end

---
--- Initiates the scheduler.
---
function Scheduler:start()
    if self.thread ~= nil and coroutine.status(self.thread) == "running" then return end
    if self.thread ~= nil and coroutine.status(self.thread) == "paused" then return coroutine.resume(self.thread) end
    
    self.running = true
    
    self.thread = coroutine.create(function()
        while self.running do
            if self.tasks then
                local t = self.tasks[1]  ---@type Task
                
                pcall(t)
                table.remove(self.tasks, 1)
                
                if t:revivable() then
                    table.insert(self.tasks, t)
                end
            end
        end
    end)
    
    coroutine.start(self.thread)
end

---
--- Stops the scheduler.
---
function Scheduler:stop()
    if self.thread == nil then return false end
    
    self.running = false
end

return Scheduler
