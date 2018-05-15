# This file is part of Decision Descent: Client.
#
# Decision Descent: Client is free software: you can
# redistribute it and/or modify it under the
# terms of the GNU General Public License as
# published by the Free Software Foundation,
# either version 3 of the License, or (at
# your option) any later version.
#
# Decision Descent: Client is distributed in the hope
# that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU
# General Public License along with
# Decision Descent: Client.  If not,
# see <http://www.gnu.org/licenses/>.
#
# Author: RandomShovel
# File Date: 11/29/2017
from PyQt5 import QtCore

__all__ = {"Player"}


class Player(QtCore.QObject):
    """The limbs of Decision Descent: Client.
    This class' job is to keep track of changes on
    a player level."""
    data_changed = QtCore.pyqtSignal(object)  # Emits self
    
    @classmethod
    def new(cls, **state) -> 'Player':
        """Constructs a new player dataclass."""
        
        obj = cls.__new__(cls)
        
        health = state.get("health", -1)
        luck = state.get("luck", -1)
        flying = state.get("flight", False)
        variant = state.get("variant", 0)
        subtype = state.get("subtype", 0)
        speed = state.get("speed", -1)
        range = state.get("range", -1)
        damage = state.get("damage", -1)
        shot_speed = state.get("shot_speed", -1)
        tears = state.get("max_fire_delay", -1)
        active_item = state.get("active_item", None)
        collectibles = state.get("collectibles", list())
        trinkets = state.get("trinkets", list())
        pocket_contents = state.get("pocket_contents", list())
        
        return obj
