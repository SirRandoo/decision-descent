# This file is part of Decision Descent: Client.
#
# Decision Descent: Client is free software: you can
# redistribute it and/or modify it under the
# terms of the GNU General Public License as
# published by the Free Software Foundation,
# either version 3 of the License, or (at
# your option) any later version.
#
# Decision Descent: Client is distributed in the hope
# that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU
# General Public License along with
# Decision Descent: Client.  If not,
# see <http://www.gnu.org/licenses/>.
#
# Author: RandomShovel
# File Date: 11/24/2017
import json
import logging

from PyQt5 import QtCore, QtNetwork

from utils.dataclasses import Message

__all__ = {"HttpListener"}


class HttpListener(QtCore.QObject):
    """The ears of Decision Descent: Client."""
    
    on_response = QtCore.pyqtSignal(Message)
    on_connection_received = QtCore.pyqtSignal()
    
    def __init__(self, parent: QtCore.QObject = None):
        # Super Call #
        super(HttpListener, self).__init__(parent=parent)
        
        # Internal Attributes #
        self._port = 25565
        self._socket = QtNetwork.QTcpServer(parent=self)  # Afterbirth+ only provides TCP/UDP sockets.
        self._client = None  # type: QtNetwork.QTcpSocket
        
        # External Attributes #
        self.logger = logging.getLogger("core.http")
        
        # Internal Calls #
        self._socket.newConnection.connect(self.on_new_connection)
        self._socket.acceptError.connect(self.on_connection_error)
        self._socket.setMaxPendingConnections(2)
    
    # Connection Methods #
    def connect(self, *, port: int = None):
        """Connects the socket to the specified host
        and port.  If host and port are omitted, the
        most recent host:port will be used."""
        if port is None:
            port = self._port
        
        self._port = port
        
        if self._socket.listen(QtNetwork.QHostAddress.LocalHost, self._port):
            self.logger.info(f"HTTP server bound to port {port}")
            self.logger.info("Full connection address: 127.0.0.1:{}".format(self._socket.serverPort()))
        
        else:
            self.logger.critical(f"Could not create a server on port {self._port}")
            self.logger.critical("Error message: {}".format(self._socket.errorString()))
    
    def send_message(self, message: Message):
        """Sends a message to the Lua half."""
        self.logger.info("Transforming Message to dict...")
        unencoded_message = message.to_dict()
        
        self.logger.info("Transforming message dict to string...")
        unencoded_message = json.dumps(unencoded_message)  # type: str
        
        if not unencoded_message.endswith("\r\n"):
            unencoded_message += "\r\n"
        
        self.logger.info("Sending message to Isaac...")
        if self._client is not None:
            if self._client.state() == self._client.ConnectedState and self._client.isWritable():
                bytes_written = self._client.write(unencoded_message.encode())
        
                if bytes_written == -1:
                    self.logger.warning("Message could not be sent!")
                    self.logger.warning("Error message: {}".format(self._client.errorString()))
                    self.logger.warning("Error code: {}".format(self._client.error()))
        
                else:
                    self.logger.info(f"{bytes_written} bytes sent!")

        else:
            self.logger.warning("No client has connected yet!")
    
    # Slots #
    def on_message(self):
        """Handles all messages received from the socket."""
        self.logger.info("Message received from socket.")
        if self._client.canReadLine():
            data = self._client.readLine()  # type: QtCore.QByteArray
    
            if not data.isEmpty():
                data = data.data().decode()  # type: str
        
                try:
                    json_data = json.loads(data)  # type: dict
        
                except ValueError:
                    self.logger.warning("Received non-JSON response from connected client!")
                    self.logger.warning(f'Received "{data}"!')
        
                else:
                    self.logger.info("Received JSON response from connected client!")
                    self.on_response.emit(Message.from_json(json_data))
    
    def on_new_connection(self):
        """Called whenever the server receives a new connection."""
        self.logger.info("New connection received!")

        if self._client is not None:
            self.logger.warning("We already have a connected client!")
            self.logger.warning("Disconnecting old client...")
            self._client.close()
    
            self.logger.info("Disconnecting signals...")
            self._client.readyRead.disconnect()
            self._client.deleteLater()

        self._client = self._socket.nextPendingConnection()
        self._client.readyRead.connect(self.on_message)
        self.on_connection_received.emit()
    
    def on_connection_error(self, error: int):
        """Called whenever an incoming connection results in an error."""
        self.logger.warning("Connection failed!")
        self.logger.warning("Error code: {}".format(error))
