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

from PyQt5 import QtNetwork, QtWidgets, sip

from .client import Client

__all__ = {"QApplication"}


class QApplication(QtWidgets.QApplication):
    """A custom application for making things easier."""
    logger = logging.getLogger("core.app")
    possible_unload_methods = ("quit", "shutdown", "unload")

    def __init__(self, *args, **kwargs):
        # Super Call #
        super(QApplication, self).__init__(*args, **kwargs)
    
        # "Private" Attribute #
        self._client: Client = None
        self._network_manager: QtNetwork.QNetworkAccessManager = None

    # Getters #
    def client(self) -> Client:
        """The client for Decision Descent.
        
        - There should only ever be one."""
        return self._client

    def network_access_manager(self) -> QtNetwork.QNetworkAccessManager:
        """Returns the QNetworkAccessManager all network traffic should use."""
        if self._network_manager is None:
            self._network_manager = QtNetwork.QNetworkAccessManager()
    
        return self._network_manager

    # Setters #
    def set_client(self, cli: Client):
        """Sets the client for Decision Descent."""
        self._client = cli
    
        # Apply metadata #
        version = self.applicationVersion()
        segments = version.split('.')
        finalized = []
    
        for segment in segments:
            if segment.isnumeric():
                finalized.append(int(segment))
        
            else:
                finalized.append(segment)
    
        cli.VERSION = segments
        cli.NAME = self.applicationDisplayName()

    def set_network_access_manager(self, manager: QtNetwork.QNetworkAccessManager):
        """Sets the QNetworkAccessManager for the application."""
        if not sip.isdeleted(self._network_manager):
            self._network_manager.deleteLater()
    
        self._network_manager = manager

    # Overrides #
    def exec(self) -> int:
        """Enters the main event loop and waits until exit() is called, then
        returns the value that was set to exit() (which is 0 if exit() is called
        via quit()).
        
        - Taken from QApplication's Qt5 docs."""
        if self._client is None:
            self.set_client(Client())
        
        for widget in self.allWidgets() + self.allWindows():
            if not isinstance(widget, self.__class__):
                for unload_method in self.possible_unload_methods:
                    attr_inst = getattr(widget, unload_method, getattr(widget, f"_{unload_method}", None))
                    
                    if attr_inst is not None:
                        self.logger.info(f"Binding {widget.__class__.__name__}'s "
                                         f"\"{unload_method}\" slot to aboutToQuit...")
                        self.aboutToQuit.connect(attr_inst)
                        self.logger.info("Bound!")

        self.setStyle("fusion")
        return super(QApplication, self).exec()
