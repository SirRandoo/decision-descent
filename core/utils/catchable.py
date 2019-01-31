# This file is part of Decision Descent.
#
# Decision Descent is free software:
# you can redistribute it and/or
# modify it under the terms of the
# GNU General Public License as
# published by the Free Software
# Foundation, either version 3 of
# the License, or (at your option)
# any later version.
#
# Decision Descent is
# distributed in the hope that it
# will be useful, but WITHOUT ANY
# WARRANTY; without even the implied
# warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License
# for more details.
#
# You should have received a copy of
# the GNU General Public License along
# with Decision Descent.
# If not, see <http://www.gnu.org/licenses/>.
import traceback
import typing

__all__ = {"catchable"}


def catchable(func: typing.Callable):
    """A custom decorator to catch exceptions that may
    originate from decorated methods."""
    
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        
        except:
            traceback.print_exc()
    
    return decorator
