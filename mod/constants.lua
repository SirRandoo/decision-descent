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

return {
    --- The metadata for the mod.
    meta = {
        ---
        --- The internal ID for the mod.
        --- * This is currently only used for logging purposes.
        ---
        ---@type string
        id = "DescentIsaac",
        
        ---
        --- The display name of the mod.  This is usually the same as its
        --- other half's, but may vary depending on release circumstances.
        ---
        ---@type string
        name = "Decision Descent",
        
        ---
        --- The version of the mod.  This is usually the same as its other half's,
        --- but may vary depending on release circumstances.
        ---
        ---@type string
        version = "1.0.0"
    },
    
    --- The various states the mod can be in.
    ---
    ---@type table<string, number>
    states = {
        ---
        --- The mod's default state.
        ---
        --- * This should never be used outside of initial declarations.
        ---
        NONE = 0,
        
        ---
        --- The mod is currently setting up.  This state will persist until the
        --- mod has established a connection with its other half.  Should they
        --- separate, the mod's state should revert to this value until they
        --- rejoin
        ---
        SETTING_UP = 1,
        
        ---
        --- The mod is currently set up.  This state is reached when the mod is
        --- actively connected to its other half.  Should they disconnect, the
        --- mod's state should revert to `SETTING_UP`.
        ---
        SET_UP = 2
    },
    
    --- The various errors the mod can generate.
    ---
    ---@type table<string, number>
    errors = {
        ---
        --- The mod could not find an appropriate value for this error. Should
        --- the value ever be raised, you should submit an issue report.
        ---
        UNKNOWN = 0,
        
        ---
        --- The mod could not decode a message sent from its other half.  These
        --- types of errors may impede the mod functionally.  If too many of
        --- these errors occur in a session, you should submit an issue report.
        ---
        MALFORMED_DATA = 1
    },
    
    --- The various sides of the HTTP connection.  There should only ever be 2 sides.
    ---
    ---@type table<string, number>
    sides = {
        ---
        --- The Isaac half ot he mod.  This half is responsible for displaying
        --- what the logical half sends to this half.
        ---
        ISAAC = 0,
        
        ---
        --- The Python half of the mod.  This half is responsible for all the
        --- logic, and stream communications.
        ---
        PYTHON = 1
    }
}
