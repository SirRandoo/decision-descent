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
import importlib
import inspect
import logging
import os

from PyQt5 import QtCore, QtWidgets

from ..errors import MethodMissingError, SignalMissingError
from ..modules import remove_module_and_submodules

__all__ = ['Extension']


# noinspection PyBroadException
class Extension:
    """A wrapper class for an extension package
    for Decision Descent: Client.  This class should
    serve as a reference for required methods every
    extension should provide.  Likewise, this should
    serve as a reference for optional methods every
    extension should provide."""

    __slots__ = ['_entry', '_inst', '_meta', '_logger', '_name', '_version']
    
    def __init__(self, entry_point: str):
        # Internal Attributes #
        self._entry = os.path.normpath(entry_point)
        self._logger = logging.getLogger(f'core.extensions')
        self._inst = None
        self._name = self._entry
        self._version = (0, 1, 0)  # major.minor.patch
        
        # We can just insert the entry's parent directory into
        # sys.path, but that has its own problems.
        if os.sep in self._entry:
            self._entry = self._entry.replace(os.sep, '.')
            
            if " " in self._entry:
                raise ValueError('Import paths cannot contain a space!')
        
        elif "." not in self._entry:
            raise ValueError(f'Extension path not supported! ({self._entry})')
    
    # Metadata Properties #
    @property
    def name(self):
        """Returns the extension's name."""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Sets the extension's name."""
        self._name = str(value)
    
    @name.deleter
    def name(self):
        """Deletes the custom name for the extension."""
        self._name = self._entry
    
    # Utility Methods #
    def load(self, *args, **kwargs):
        """Loads the integration at the entry site."""
        self._logger.info(f'Loading extension at site {self._entry}...')
        extension = importlib.import_module(self._entry)
        construct = getattr(extension, 'construct', None)

        if construct is not None:
            try:
                construct(*args, **kwargs)
            
            except Exception as e:
                self._logger.warning(f"Extension at site {self._entry}'s "
                                     f'construct method failed with exception: {str(e)}')
                raise ValueError
            
            else:
                self._logger.info(f'Extension "{self.name}"\'s construct method completed successfully!')
        
        else:
            remove_module_and_submodules(extension)
            del extension
            raise MethodMissingError(f'Extension at site {self.name} is missing a construct method!')

        self._logger.info(f'Extension "{self.name}" successfully loaded!')
    
    def unload(self, *args, **kwargs):
        """Unloads the extension at the entry site."""
        self._logger.info(f'Unloading extension at site {self._entry}')
        destruct = getattr(self._inst, 'destruct', None)
    
        if destruct is not None:
            self._logger.info(f"Calling {self.name}'s destruct method...")
            
            try:
                destruct(*args, **kwargs)
            
            except Exception as e:
                self._logger.warning(f"{self.name}'s destruction method failed with exception: {str(e)}")
                raise ValueError
            
            else:
                self._logger.info(f"{self.name}'s destruction method completed successfully!")
        
        try:
            remove_module_and_submodules(inspect.getmodule(self._inst))
        
        except AssertionError:
            pass
        
        self._cleanup(self._inst)
        self._inst = None
    
        self._logger.info(f'Extension at site {self._entry} unloaded successfully!')
    
    def _cleanup(self, obj):
        """Cleans up an instance's Qt objects."""
        self._logger.info('Cleaning up extension...')
        
        for attr, attr_inst in inspect.getmembers(obj):
            if isinstance(attr_inst, QtCore.QObject) or isinstance(attr_inst, QtWidgets.QWidget):
                self._cleanup(attr_inst)

                stop = getattr(attr_inst, 'stop', None)
                delete_later = getattr(attr_inst, 'deleteLater', None)

                if stop is not None:
                    stop()

                if delete_later is not None:
                    delete_later()
    
    # Wrapper Methods #
    def send(self, message: str) -> bool:
        """Sends `message` to the extension's supported platform(s)."""
        self._logger.info(f"Attempting to send message to {self.name}'s supported platform(s)...")
        method = getattr(self._inst, 'check_for_updates', None)

        if method is not None:
            self._logger.info('Extension has a send method!')
            self._logger.info("Invoking extension's send method...")
            
            try:
                method(message)
            
            except Exception as e:
                self._logger.warning(f"Extension at site {self._entry}'s "
                                     f'send method failed with exception: {str(e)}')
                return False
            
            else:
                self._logger.info("Extension's send method completed successfully!")
                return True
        
        else:
            self._logger.warning(f'Extension at site {self._entry} does not have a send method!')
            raise MethodMissingError(f'Extension at site {self._entry} does not have a send method!')

    def check_for_updates(self, updater):
        """Calls the extension's update checker."""
        self._logger.info(f"Attempting to call {self.name}'s update checker...")
        method = getattr(self._inst, 'check_for_updates', None)

        if method is not None:
            self._logger.info('Extension has a check_for_updates method!')
            self._logger.info("Invoking extension's check_for_updates method...")

            try:
                method(updater)

            except Exception as e:
                self._logger.warning(f"Extension at site {self._entry}'s "
                                     f'send method failed with exception: {str(e)}')

            else:
                self._logger.info("Extension's check_for_updates method completed successfully!")

        else:
            self._logger.warning(f'Extension at site {self._entry} does not have a check_for_updates method!')
            raise MethodMissingError(f'Extension at site {self._entry} does not have a check_for_updates method!')
    
    # Wrapper Signals #
    @property
    def on_message(self) -> QtCore.pyqtSignal:
        """Returns the extension's on_message signal."""
        method = getattr(self._inst, 'on_message', None)

        if method is not None:
            if isinstance(method, QtCore.pyqtSignal):
                return method
            
            else:
                raise TypeError(f"Extension at site {self._entry}'s "
                                f'on_message attribute is not a valid signal object!')
        
        else:
            raise SignalMissingError(f'Extension at site {self._entry} does not have an on_message attribute!')
