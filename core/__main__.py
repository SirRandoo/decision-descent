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
import functools
import logging
import sys

# noinspection PyUnresolvedReferences
from PyQt5 import QtCore, QtGui, QtWebEngineWidgets

from utils.handlers import Handler, qmessage_handler
# noinspection PyUnresolvedReferences,PyProtectedMember
from widgets import Client, QApplication

# Declarations
application = QApplication(sys.argv)
app = Client()

# Signals
application.applicationDisplayNameChanged.connect(functools.partial(
    app.setWindowTitle,
    application.applicationDisplayName()
))

# Metadata
application.setApplicationDisplayName("Decision Descent: Client")
application.setApplicationName("decision-descent")
application.setApplicationVersion("0.3.0")
application.setWindowIcon(QtGui.QIcon("resources/assets/icon.png"))
application.setOrganizationName("SirRandoo")
application.setOrganizationDomain("sirrandoo.github.io")

# Logging
if app is None:
    level = logging.INFO

else:
    if app.settings is not None:
        try:
            level = logging.DEBUG if app.settings["client"]["system"]["debug_mode"].value else logging.INFO
        
        except KeyError:
            level = logging.INFO
    
    else:
        level = logging.INFO

# Invocations
application.set_client(app)
QtCore.qInstallMessageHandler(qmessage_handler)

logging.basicConfig(
    datefmt='%H:%M:%S', style='{', level=level,
    format='[{asctime}][{levelname}][{name}][{filename}:{funcName}:{lineno}] {message}',
    handlers=[logging.StreamHandler(), logging.FileHandler(application.applicationName() + '.log', mode='w'),
              Handler(app.client_log)]
)

application.exec()
