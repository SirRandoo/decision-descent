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
# Author: RandomShovel
# File Date: 12/13/2017


__all__ = {"RoomLayout"}


class RoomLayout:
    def __init__(self, room_width: int, room_height: int, doors: dict, **options):
        self._width = room_width
        self._height = room_height
        self._doors = doors
        
        self._force_path = options.get("force_path")
