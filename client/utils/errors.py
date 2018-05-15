#  This file is part of Decision Descent: Client.
#
#  Decision Descent: Client is free software: you can 
#  redistribute it and/or modify it under the 
#  terms of the GNU General Public License as 
#  published by the Free Software Foundation, 
#  either version 3 of the License, or (at 
#  your option) any later version.
#
#  Decision Descent: Client is distributed in the hope 
#  that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty 
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License 
#  for more details.
#
#  You should have received a copy of the GNU
#  General Public License along with 
#  Decision Descent: Client.  If not, 
#  see <http://www.gnu.org/licenses/>.
#  
#  Author: RandomShovel
#  File Creation Date: 7/19/2017


__all__ = {"MethodMissingError", "DependencyError", "IntegrationError", "IntegrationInvokeError",
           "IntegrationLoadError", "IntegrationUnloadError", "ModError", "ModInitError", "ModPostInitError",
           "ModPreInitError", "SignalMissingError"}


#  Generic Exceptions  #
class ModError(Exception):
    """The 'generic' exception for any mod-related
    errors.  This shouldn't be used if a more
    specific error is available."""


class IntegrationError(Exception):
    """The 'generic' exception for any integration-
    related errors.  This shouldn't be used if a
    more specific error is available."""


class DependencyError(Exception):
    """Raised when a required dependency wasn't
    present in the Python environment.  Generally
    if you receive this error, you should run the
    installer again.  If the installer doesn't
    install the dependency, you will be shown which
    dependency is missing and can manually add it."""


#  Mod Exceptions  #
class ModPreInitError(ModError):
    """Raised when the mod encountered an error
    during the pre-init phase."""


class ModInitError(ModError):
    """Raised when the mod encountered an error
    during the init phase."""


class ModPostInitError(ModError):
    """Raised when the mod encountered an error
    during the post-init phase."""


#  Integration Exceptions  #
class IntegrationLoadError(IntegrationError):
    """Raised when an integration failed to load."""


class IntegrationUnloadError(IntegrationError):
    """Raised when an integration failed to unload
    properly.  The mod will attempt to aggressively
    clean up artifacts."""


class IntegrationInvokeError(IntegrationError):
    """Raised when the mod invoked an integration's
    method and an exception was raised."""


class SignalMissingError(IntegrationError):
    """Raised when an integration is missing a
    required signal."""


class MethodMissingError(IntegrationError):
    """Raised when an integration is missing a
    required method."""
