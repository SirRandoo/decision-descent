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


--[[ Declarations  ]]--
local returnable = {}


--[[  Definitions  ]]--
function returnable.new()
    local obj = {}
    setmetatable(obj, returnable)
    
    obj.tasks = {}
    
    return obj
end

function returnable:schedule(func, keepAlive) table.insert(self.tasks, { ["func"] = func, ["keepAlive"] = keepAlive }) end

function returnable:invoke()
    local task = self.tasks[1]
    
    if task then
        pcall(task.func)
        table.remove(self.tasks, 1)
        
        if task.keepAlive then
            table.insert(self.tasks, task)
        end
    end
end

return returnable
