# This file is part of Decision Descent.
#
# Decision Descent is free software:
# you can redistribute it
# and/or modify it under the
# terms of the GNU General
# Public License as published by
# the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later
# version.
#
# Decision Descent is distributed in
# the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with
# Decision Descent.  If not,
# see <https://www.gnu.org/licenses/>.


class DescentError(Exception):
    """The base class for all Decision Descent exceptions."""


class IntentNotFoundError(KeyError):
    """The intent requested was not registered with the arbiter."""


class IntentExistsError(KeyError):
    """The intent requested was already registered to the arbiter.
    
    Overriding intents should only be done if you know what you're doing."""
