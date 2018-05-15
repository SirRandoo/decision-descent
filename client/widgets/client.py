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
# File Creation Date: 7/18/2017
# TODO: Clean up attributes
import inspect
import logging
import os

from PyQt5 import QtCore, QtGui, QtWidgets

from client import utils
from client.utils import dataclasses
from . import http, info, metadata, tray
from .uis import ClientUi

__all__ = {"Client"}


class Client(QtWidgets.QMainWindow):
    """The heart of Decision Descent: Client."""
    
    def __init__(self, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Client, self).__init__(parent=parent)
        
        # Ui Call #
        self.ui = ClientUi()
        self.ui.setupUi(self)
        
        # "Public" Attributes #
        self.config = dict(settings=utils.Config("settings.ini"), descent=utils.Config("descent.ini"))
        self.handlers = [logging.FileHandler("log.txt", encoding="UTF-8", mode="w"),
                         utils.Log(self.ui.log)]
        self.formatter = logging.Formatter(fmt="[{asctime}]"
                                               "[{levelname}]"
                                               "[{name}]"
                                               "[{funcName}] {message}",
                                           datefmt="%H:%M:%S",
                                           style="{")
        self.logger = self.setup_logger("client")  # type: logging.Logger
        self.integrations = list()
        
        self.metadata = metadata.MetadataDialog(name="Decision Descent: Client",
                                                version="0.1.0",
                                                license="GPLv3+",
                                                license_url="https://github.com/SirRandoo/"
                                                            "decision-descent/blob/master/LICENSE",
                                                website="https://github.com/SirRandoo/decision-descent",
                                                docs="https://sirrandoo.github.io/decision-descent",
                                                authors=["SirRandoo"])
        self.display = info.Info(parent=self)
        self.tray = tray.TrayIcon(parent=self)
        self.show_action = QtWidgets.QAction("Show", parent=self.tray.menu)
        self.http = http.HttpListener(parent=self)
        self.data = utils.DescentData(self.http, self.config, parent=self)
        
        # "Private" Attributes #
        self._shutting_down = False
        
        # Internal Calls #
        self.setup_logger("QtTwitch")
        self.tray.show()
        
        self.bind()
        self.mirror_menubar()
        self.load_integrations()
        self.http.connect()
        
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))
        self.tray.tray.setIcon(self.windowIcon())
    
    # Integration Methods #
    def load_integrations(self, path: str = None):
        """Loads all integrations in `path`.  Integrations should refer to the
        integration dataclass for a reference."""
        failed = 0
        
        if path is None:
            path = self.config["settings"]["locations"]["integrations"]
            
            if not path:
                path = "integrations"
        
        self.logger.info(f"Loading integrations from {path}...")
        for item in os.listdir(path):
            item_path = os.path.normpath(os.path.join(path, item))
            item_path = ".".join(item_path.split(os.sep))
            integration = dataclasses.Integration(item_path)
            
            try:
                integration.load(self)
            
            except client.utils.errors.MethodMissingError as e:
                self.logger.warning(f'Integration "{item_path}" could not be loaded!')
                self.logger.warning(str(e))
                failed += 1
            
            else:
                self.integrations.append(integration)
        
        self.logger.info("Successfully loaded {} integrations!".format(len(self.integrations)))
        
        if failed:
            self.logger.warning(f"{failed} integrations could not be loaded!")
    
    def unload_integrations(self):
        """Unloads all currently loaded integrations."""
        self.logger.warning("Unloading {} integrations...".format(len(self.integrations)))
        failed = 0
        
        for integration in self.integrations:  # type: dataclasses.Integration
            try:
                integration.unload()
            
            except ValueError:
                failed += 1
        
        self.logger.warning("Unloading {} integrations!".format(len(self.integrations) - failed))
        self.integrations.clear()
        
        if failed:
            self.logger.warning(f"{failed} integrations failed to unload properly!")
            self.logger.warning("There may be left over objects!")
    
    # Bind Methods #
    def bind(self):
        """Calls all methods in this class that start with bind_."""
        self.logger.info("Binding signals to their respective slots...")
        
        for attr, inst in inspect.getmembers(self):
            if attr.startswith("bind_") or attr.startswith("_bind_"):
                inst()
        
        self.logger.info("All signals bound to their respective slots!")
    
    def bind_menubar(self):
        """Binds all menubar objects to their respective slots."""
        self.logger.info("Binding menubar actions to their respective slots...")
        
        self.logger.info("Binding quit action...")
        self.ui.menu_quit.triggered.connect(lambda: QtWidgets.qApp.exit(0))
        self.logger.info("Bound!")
        
        self.logger.info("Binding help action...")
        self.ui.help_help.triggered.connect(self.help)
        self.logger.info("Bound!")
        
        self.logger.info("Binding about action...")
        self.ui.help_about.triggered.connect(self.about)
        self.logger.info("Bound!")
        
        self.logger.info("Binding license action...")
        self.ui.help_license.triggered.connect(self.license)
        self.logger.info("Bound!")
        
        self.logger.info("Menubar actions to their respective slots!")
    
    def bind_tray(self):
        """Binds all tray actions to their respective slots."""
        self.logger.info("Binding tray events to their respective slots...")
        
        self.logger.info("Binding clicked signal...")
        self.tray.clicked.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Binding middle-clicked signal...")
        self.tray.middle_clicked.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Binding double-clicked event...")
        self.tray.double_clicked.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Tray events bound to their respective slots!")
        self.logger.info("Binding tray signals to their respective slots...")
        
        self.logger.info("Binding show signal...")
        self.show_action.triggered.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Tray signals bound to their respective slots!")
    
    def bind_http(self):
        """Binds all http signals to their respective slots."""
        self.logger.info("Binding HTTP signals to their respective slots...")
        
        self.logger.info("Bound on_response signal...")
        self.http.on_response.connect(self.data.process_message)
        self.logger.info("Bound!")
        
        self.logger.info("Bound all HTTP signals to their respective slots!")
    
    # Help Methods #
    def help(self):
        """Displays the Decision Descent: Wiki"""
        self.logger.info("Opening Decision Descent's documentation...")
        # TODO: Compile a .qch file and display it.  If the file doesn't exist, open the online documentation.
    
    def about(self):
        """Displays information about Decision Descent."""
        self.logger.info("Displaying Decision Descent's metadata...")
        self.metadata.show()
        self.logger.info("Metadata successfully displayed!")
    
    def license(self):
        """Displays the full license for Decision Descent: Client."""
        if not os.path.isfile("LICENSE"):
            self.logger.warning("Decision Descent: Client always ships with its license file.")
            self.logger.warning("If this package wasn't shipped with one, submit an issue on the Github repository.")
            self.logger.warning("If this package did not come from SirRandoo's Decision Descent, ask your distributor "
                                "to include one.")
        
        else:
            file = QtCore.QFile("LICENSE")
            
            if not file.isOpen():
                file.open(file.ReadOnly | file.Text)
            
            if file.isReadable():
                contents = file.readAll().data().decode()
                self.display.show_text(contents)
            
            else:
                self.logger.warning("License file could not be opened for reading!")
                self.logger.warning("Error code {} : {}".format(file.error(), file.errorString()))
            
            if file.isOpen():
                file.close()
    
    def quit(self):
        """A custom close method that allows the client to accept closeEvents."""
        self.logger.info("Shutting down Decision Descent: Client...")
        self.logger.warning("This does not shutdown Decision Descent: Mod!")
        
        self._shutting_down = True
        super(Client, self).close()
    
    # Utility Methods #
    def setup_logger(self, name: str) -> logging.Logger:
        """Sets up the logger passed."""
        can_log = hasattr(self, "logger")
        logger = logging.getLogger(name)
        
        if logger.hasHandlers() and can_log:
            self.logger.warning(f'Logger `{name}` already has handlers attached!')
        
        if can_log:
            self.logger.info(f'Adding handlers to `{name}`...')
        
        for handler in self.handlers:
            if handler not in logger.handlers:
                logger.addHandler(handler)
                
                if handler.formatter is None:
                    handler.setFormatter(self.formatter)
        
        if can_log:
            self.logger.info(f'Setting logger level to client\'s level...')
        
        logger.setLevel(logging.DEBUG if self.config["settings"]["debug"]["enabled"] else logging.INFO)
        
        return logger
    
    def mirror_menubar(self):
        """Changes the tray icon's menu to mimic the application's menubar."""
        self.logger.warning("Discarding current tray menu...")
        self.tray.menu.clear()
        self.logger.info("Discarded!")
        
        self.logger.info("Mirroring application's menubar...")
        
        self.logger.info("Inserting show action into tray menu...")
        self.tray.menu.addAction(self.show_action)
        self.logger.info("Inserted!")
        
        for action in self.ui.menu_bar.actions():  # type: QtWidgets.QAction
            self.logger.info('Inserting action "{}" and its children to tray menu...'.format(action.text()))
            self.tray.menu.addAction(action)
        
        self.logger.info("Mirror complete!")
    
    # Qt Events #
    def closeEvent(self, a0: QtGui.QCloseEvent):
        """An override to allow the application to have special closing
        operations.  If the application was not closed via the menu action,
        the application will simply hide.  If it was, the application will
        perform closing operations.  To reopen the application, the taskbar
        icon can be used."""
        self.logger.warning("Client received a closeEvent!")
        self.logger.warning("Was this an accident?")
        
        if self._shutting_down:
            self.logger.warning("Performing closing operations...")
            
            self.logger.info("Saving configs...")
            for key, value in self.config.items():
                self.logger.info(f'Saving config "{key}"...')
                value.write()
                self.logger.info("Saved!")
            
            if not a0.isAccepted():
                a0.accept()
            self.logger.info("Configs saved!")
        
        else:
            self.logger.warning("We're not actually closing, right?")
            self.logger.warning("To actually close this application, please use "
                                "Menu→Quit or use the shortcut {}".format(self.ui.menu_quit.shortcut().toString()))
            
            a0.ignore()
            self.hide()
