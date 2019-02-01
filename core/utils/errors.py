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


__all__ = {"MethodMissingError", "DependencyError", "ExtensionError", "ExtensionInvokeError",
           "ExtensionLoadError", "IntegrationUnloadError", "ModError", "ModInitError", "ModPostInitError",
           "ModPreInitError", "SignalMissingError"}


#  Generic Exceptions  #
class ModError(Exception):
    """The 'generic' exception for any mod-related errors.  This shouldn't be
    used if a more specific error is available."""


class ExtensionError(Exception):
    """The 'generic' exception for any extension- related errors.  This
    shouldn't be used if a more specific error is available."""


class DependencyError(Exception):
    """Raised when a required dependency wasn't present in the Python
    environment.  Generally if you receive this error, you should run the
    installer again.  If the installer doesn't install the dependency, you will
    be shown which dependency is missing and can manually add it."""


#  Mod Exceptions  #
class ModPreInitError(ModError):
    """Raised when the mod encountered an error during the pre-init phase."""


class ModInitError(ModError):
    """Raised when the mod encountered an error during the init phase."""


class ModPostInitError(ModError):
    """Raised when the mod encountered an error during the post-init phase."""


#  Integration Exceptions  #
class ExtensionLoadError(ExtensionError):
    """Raised when an extension failed to load."""


class IntegrationUnloadError(ExtensionError):
    """Raised when an extension failed to unload properly.  The mod will
    attempt to aggressively clean up artifacts."""


class ExtensionInvokeError(ExtensionError):
    """Raised when the mod invoked an extension's method and an exception was
    raised."""


class SignalMissingError(ExtensionError):
    """Raised when an extension is missing a required signal."""


class MethodMissingError(ExtensionError):
    """Raised when an extension is missing a required method."""
