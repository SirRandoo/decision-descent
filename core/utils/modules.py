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
import modulefinder
import sys

__all__ = {"remove_module_and_imports", "remove_module_and_submodules"}


def remove_module_and_imports(_module, *, excludes: list = None):
    """Removes a module and its imports.  This
    can also remove in-use modules other modules
    need.  Use with caution!
    
    :param _module: The module to probe
    :param excludes: A list of packages to exclude
    when removing `_module`'s imports.  These must
    be in import format `foo.bar.baz`"""
    assert inspect.ismodule(_module), "A module must be passed!"
    assert not inspect.isbuiltin(_module), "You cannot remove a built-in module!"
    
    if excludes is None:
        excludes = []
    
    _finder = modulefinder.ModuleFinder()
    _finder.run_script(_module.__file__)
    
    for key, value in _finder.modules.items():
        if key in sys.modules and key not in excludes:
            del sys.modules[key]


def remove_module_and_submodules(_module, *, excludes: list = None):
    """Removes a module and it's submodules.  This
    can also remove in-use modules other modules
    need.  Use with caution!
    
    :param _module: The module to probe
    :param excludes: A list of packages to exclude
    when removing `module`'s submodules.  These must
    be in import format `foo.bar.baz`."""
    assert inspect.ismodule(_module), "A module must be passed!"
    assert not inspect.isbuiltin(_module), "You cannot remove a built-in module!"
    
    if excludes is None:
        excludes = []
    
    _temp = _module.__name__
    for key in tuple(sys.modules.keys()):
        if key.startswith(_temp) and key not in excludes:
            del sys.modules[key]
