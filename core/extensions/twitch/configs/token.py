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
import os

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets, sip

from QtUtilities import settings


class TokenOption(QtCore.QObject):
    """A token option for the client's settings dialog.  This class handles
    generating a oauth token when requested."""
    
    def __init__(self, option: settings.Option, *, parent: QtCore.QObject = None):
        # Super Call #
        super(TokenOption, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.id = "tokenoption"
        
        # "Private" Attributes #
        self._host = None  # type: QtWidgets.QWidget
        self._layout = None  # type: QtWidgets.QHBoxLayout
        self._button = None  # type: QtWidgets.QPushButton
        self._display = None  # type: QtWidgets.QLineEdit
        self._view = None  # type: QtWebEngineWidgets.QWebEngineView
        self._option = option
        self._last_hash = None  # type: QtCore.QByteArray
        
        self.update_widget(self._option._widget)
    
    # Properties #
    @property
    def value(self) -> str:
        if self._display is not None:
            return self._display.text()
        
        else:
            return str()
    
    # Ui Methods #
    def update_display(self):
        """Updates the config display."""
        self.prepare()
        
        self._option.set_widget(self._host, from_manager=True)
    
    def prepare(self):
        """Prepares the manager's widgets for display."""
        self._prepare_host()
        self._prepare_button()
        self._prepare_view()
        self._prepare_display()
        
        if self._layout.indexOf(self._display) == -1:
            self._layout.insertWidget(0, self._display, alignment=QtCore.Qt.AlignLeft)
        
        if self._layout.indexOf(self._button) == -1:
            self._layout.insertWidget(1, self._button, alignment=QtCore.Qt.AlignRight)
    
    def _prepare_host(self):
        """Prepares the host widget for display."""
        if self._host is None or sip.isdeleted(self._host):
            self._host = QtWidgets.QWidget()
            self._layout = QtWidgets.QHBoxLayout(self._host)
            self._layout.setContentsMargins(0, 0, 0, 0)
    
    def _prepare_button(self):
        """Prepares the QPushButton for display."""
        if self._button is None or sip.isdeleted(self._button):
            self._button = QtWidgets.QPushButton("Generate...", parent=self._host)
            self._button.clicked.connect(self.generate)
            
            self._layout.insertWidget(1, self._button)
            self._button.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    
    def _prepare_view(self):
        """Prepares the QWebEngineView for display."""
        if self._view is None or sip.isdeleted(self._view):
            self._view = QtWebEngineWidgets.QWebEngineView()
            self._view.urlChanged.connect(self._url_watcher)
    
    def _prepare_display(self):
        """Prepares the display for display."""
        if self._display is None or sip.isdeleted(self._display):
            self._display = QtWidgets.QLineEdit(parent=self._host)
            self._display.setEchoMode(self._display.Password)
            self._layout.insertWidget(0, self._display)
            self._display.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        
        elif self._display is not None:
            self._display.setEchoMode(self._display.Password)
            self._layout.insertWidget(0, self._display)
            self._display.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
    
    # Signal Methods #
    def generate(self):
        """Generates a new OAuth token for use in
        Decision Descent's Twitch extension."""
        self._prepare_view()
        
        query = QtCore.QUrlQuery()
        url = QtCore.QUrl("https://id.twitch.tv/oauth2/authorize")
        self._last_hash = self.generate_state()
        
        query.addQueryItem("client_id", "dsosx6yjehb9jihl5u0c72lxjo36wns")
        query.addQueryItem("redirect_uri", "http://localhost")
        query.addQueryItem("response_type", "token")
        query.addQueryItem("scopes", "chat_login")
        query.addQueryItem("force_verify", "true")
        query.addQueryItem("state", self._last_hash.data().hex())
        
        url.setQuery(query)
        
        self._view.load(url)
        self._view.show()
    
    def _url_watcher(self, url: QtCore.QUrl):
        """Watches the view for changes."""
        if url.host() == "localhost":
            self._view.hide()
            self._view.setUrl(QtCore.QUrl("about:blank"))
            self._view.history().clear()
            
            if url.hasFragment():
                query = url.fragment()  # type: str
                
                segments = query.split("&")
                segment_dict = dict()
                
                for segment in segments:
                    key, value = segment.split("=")
                    segment_dict[key] = value
                
                if segment_dict["state"] == self._last_hash.data().hex():
                    self._display.setText(segment_dict["access_token"])
    
    # Utility Methods #
    @staticmethod
    def generate_state() -> QtCore.QByteArray:
        """Generates a state token."""
        for widget in QtWidgets.qApp.allWidgets():
            if widget.__class__.__name__ == "Client":
                sequence = "{}-{}-{}".format(
                    widget.NAME,
                    ".".join([str(i) for i in widget.VERSION]),
                    ".".join(widget.AUTHORS)
                )
                
                return QtCore.QCryptographicHash.hash(sequence.encode(), QtCore.QCryptographicHash.Sha3_256)
        
        return QtCore.QCryptographicHash.hash(f"{os.name}-decision_descent.twitch.token".encode(),
                                              QtCore.QCryptographicHash.Sha3_256)
    
    # Manager Methods #
    @classmethod
    def new(cls, option: settings.Option) -> 'TokenOption':
        """Returns a new TokenOption instance."""
        return cls(option)
    
    def update_widget(self, new_widget: QtWidgets.QLineEdit):
        """Updates the QLineEdit object in this instance."""
        self._display = new_widget
        self.update_display()
