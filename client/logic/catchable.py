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
import inspect
import logging
import typing

from . import errors

__all__ = ['signal']


def signal(func: typing.Callable) -> typing.Callable:
    """A custom decorator to catch exception that may originate from Qt signals."""
    
    def decorator(*args, **kwargs) -> typing.Any:
        try:
            sig = inspect.signature(func)
            
            if sig.parameters:
                args = args[:len(sig.parameters)]
                
                return func(*args, **kwargs)
            
            else:
                return func()
        
        except errors.DescentError as e:
            logging.getLogger("extensions.DescentClient.signal_catcher").exception(
                f'Execution of {func!s} failed!', exc_info=e
            )
    
    return decorator
