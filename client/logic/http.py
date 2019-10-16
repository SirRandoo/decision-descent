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
import json
import logging
import typing

from PyQt5 import QtCore, QtNetwork

from .. import dataclasses as descent_dataclasses

if typing.TYPE_CHECKING:
    from core.utils import custom

__all__ = ['HTTP']


class HTTP(QtCore.QObject):
    """Connects to the other half of the mod.
    
    This class is responsible for ensuring the mod's logic is processed, then
    returned to the mod for displaying."""
    # Signals
    onResponse = QtCore.pyqtSignal(object)
    onConnectionReceived = QtCore.pyqtSignal()
    
    # Class variables
    LOGGER: logging.Logger = logging.getLogger("extensions.DescentClient.http")
    
    def __init__(self, parent: QtCore.QObject = None):
        # Super call
        super(HTTP, self).__init__(parent=parent)
        
        # Internal attributes
        self._socket: QtNetwork.QTcpServer = QtNetwork.QTcpServer(parent=self)
        self._client: typing.Optional[QtNetwork.QTcpSocket] = None
        
        # Internal calls
        self._socket.newConnection.connect(self.process_new_client)
        self._socket.acceptError.connect(self.process_connection_error)
        self._socket.setMaxPendingConnections(2)
    
    # Connection methods
    def connect(self):
        """Connects the socket to the specified host and port.  If host and port
        are omitted, the most recent host:port will be used."""
        app: custom.QApplication = custom.QApplication.instance()
        port = app.client.settings['extensions']['descentisaac']['http']['port'].value

        if not self._socket.listen(QtNetwork.QHostAddress.LocalHost, port):
            self.LOGGER.critical(f'Could not create a server on port {port}')
            return self.LOGGER.critical(f'Error message:  {self._socket.errorString()}')

        self.LOGGER.info(f'Client bound to port {port}')
        self.LOGGER.debug(f'Full connection address: {self._socket.serverAddress()}:{self._socket.serverPort()}')

    def disconnect(self):
        """Disconnects the socket."""
        self._socket.disconnect()
    
    def send_message(self, message: descent_dataclasses.Message):
        """Sends a message to any connected clients."""
        if self._client is None or self._client.state() != self._client.ConnectedState:
            raise ConnectionError('No client connected!')
        
        if not self._client.isWritable():
            raise ConnectionError('Cannot write to client!')
        
        self.LOGGER.info('Transforming message to sendable message...')
        payload = f'{message!s}\r\n'
        
        self.LOGGER.info('Sending message to the other side...')
        sent = self._client.write(payload.encode())
        
        if sent == -1:
            return self.LOGGER.warning(f"Couldn't send message!  "
                                       f"Error #{self._client.error()} » {self._client.errorString()}")
        
        self.LOGGER.info(f'{sent} bytes sent!')
    
    # Slots
    def process_message(self):
        """Handles all messages received from the socket."""
        if not self._client.canReadLine():
            return self.LOGGER.info('Client has data available, but not open for reading!')
        
        self.LOGGER.debug('Message received from socket!')
        d = self._client.readLine().decode()
        
        try:
            data = json.loads(d)
        
        except ValueError as e:
            self.LOGGER.warning(f'Received invalid JSON response from connected client!  {e!s}')
            self.LOGGER.warning(f'Received "{d}"')
        
        else:
            self.LOGGER.debug('Received payload from connected client!')
            self.onResponse.emit(descent_dataclasses.Message.from_json(data))
    
    def process_new_client(self):
        """Called whenever the server receives a new connection!"""
        self.LOGGER.info('New connection received!')
        
        if self._client is not None:
            self.LOGGER.warning('A client was already connected!')
            self.LOGGER.warning('Disconnecting old client...')
            self._client.close()
            
            self.LOGGER.info('Disconnecting signals...')
            self._client.readyRead.disconnect()
            self._client.deleteLater()
        
        self._client = self._socket.nextPendingConnection()
        self._client.readyRead.connect(self.process_message)
        self.onConnectionReceived.emit()
    
    def process_connection_error(self, error: int):
        """Called whenever an incoming connection results in an error."""
        self.LOGGER.warning('Connection failed!')
        
        for member, inst in inspect.getmembers(QtNetwork.QAbstractSocket):
            if inst != error:
                continue
            
            self.LOGGER.warning(f'Error code #{error} » {member}')
