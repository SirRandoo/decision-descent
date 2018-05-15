# This file is part of Decision Descent: Client.
#
# Decision Descent: Client is free software:
# you can redistribute it and/or
# modify it under the terms of the 
# GNU General Public License as 
# published by the Free Software 
# Foundation, either version 3 of 
# the License, or (at your option) 
# any later version.
#
# Decision Descent: Client is 
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
# with Decision Descent: Client.  
# If not, see <http://www.gnu.org/licenses/>.
import logging

from PyQt5 import QtWidgets

__all__ = {"QApplication"}


class QApplication(QtWidgets.QApplication):
    """A custom application for making things easier."""
    logger = logging.getLogger("client.app")
    possible_unload_methods = ("quit", "shutdown", "unload")
    
    def exec(self) -> int:
        """Enters the main event loop and waits until exit() is called, then
        returns the value that was set to exit() (which is 0 if exit() is called
        via quit()).
        
        - Taken from QApplication's Qt5 docs."""
        for widget in self.allWidgets() + self.allWindows():
            if not isinstance(widget, self.__class__):
                for unload_method in self.possible_unload_methods:
                    attr_inst = getattr(widget, unload_method, getattr(widget, f"_{unload_method}", None))
                    
                    if attr_inst is not None:
                        self.logger.info(f"Binding {widget.__class__.__name__}'s "
                                         f"\"{unload_method}\" slot to aboutToQuit...")
                        self.aboutToQuit.connect(attr_inst)
                        self.logger.info("Bound!")
        
        return super(QApplication, self).exec()
