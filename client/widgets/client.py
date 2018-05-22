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
import inspect
import logging
import os
import platform
import traceback
import typing

from PyQt5 import QtCore, QtGui, QtWidgets

import utils
from utils import dataclasses
from . import http, info, metadata, settings, tray
from .uis import ClientUi

__all__ = {"Client"}


class Client(QtWidgets.QMainWindow):
    """The heart of Decision Descent: Client."""
    LICENSE = "GNU General Public License 3 or later"
    NAME = "Decision Descent: Client"
    AUTHORS = ["SirRandoo"]
    VERSION = (0, 2, 0)
    
    def __init__(self, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Client, self).__init__(parent=parent)
        
        # Ui Call #
        self.ui = ClientUi()
        self.ui.setupUi(self)
        
        # "Public" Attributes #
        self.configs = dict(settings=utils.Config("settings.ini", configspec=".meta/settings.ini"),
                            descent=utils.Config("descent.ini", configspec=".meta/descent.ini"))
        self.handlers = [logging.FileHandler("log.txt", encoding="UTF-8", mode="w"), utils.Log(self.ui.client_log)]
        self.formatter = logging.Formatter(fmt="[{asctime}][{levelname}][{name}][{funcName}] {message}",
                                           datefmt="%H:%M:%S",
                                           style="{")
        self.logger = self.setup_logger("client")  # type: logging.Logger
        self.integrations = list()
        
        self.display = info.Info(parent=self)
        self.tray = tray.TrayIcon(parent=self)
        self.http = http.HttpListener(parent=self)
        self.settings = settings.Settings(parent=self)
        self.metadata = metadata.MetadataDialog(parent=self)
        self.data = utils.DescentData(self.http, self.configs, parent=self)
        self.show_action = QtWidgets.QAction("Show", parent=self.tray.menu)
        self.isaac_timer = QtCore.QTimer(parent=self)
        self.isaac_log = self.find_isaac_log()
        self.isaac_size = 0
        
        # "Private" Attributes #
        self._shutting_down = False
        
        # Internal Calls #
        self.setup_logger("QtTwitch")
        self.ui.menu_bar.raise_()  # Fixes the menubar not showing actions
        self.tray.show()
        
        self.bind()
        self.mirror_menubar()
        self.setup_metadata()
        self.load_integrations()
        self.http.connect()
        
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))
        self.tray.tray_icon.setIcon(self.windowIcon())

        if self.isaac_log is not None:
            if not self.isaac_log.isOpen():
                self.isaac_log.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
                self.isaac_timer.start(500)
    
    # Integration Methods #
    def load_integrations(self, path: str = None):
        """Loads all integrations in `path`.  Integrations should refer to the
        integration dataclass for a reference."""
        failed = 0
        
        if path is None:
            path = self.configs["settings"]["locations"]["integrations"]
            
            if not path:
                path = "integrations"
        
        self.logger.info(f"Loading integrations from {path}...")
        for item in os.listdir(path):
            if not item.startswith("_") and not item.startswith("."):
                item_path = os.path.normpath(os.path.join(path, item))
                item_path = ".".join(item_path.split(os.sep))
                integration = dataclasses.Integration(item_path)
        
                try:
                    integration.load(self)
        
                except utils.errors.MethodMissingError as e:
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

        self.logger.info("Binding menubar action...")
        self.ui.menu_bar.triggered.connect(self.force_menu)
        self.logger.info("Bound!")
        
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

        self.logger.info("Binding on_response signal...")
        self.http.on_response.connect(self.data.process_message)
        self.logger.info("Bound!")

        self.logger.info("Binding on_connection_received signal...")
        self.http.on_connection_received.connect(self.data.process_new_connection)
        self.logger.info("Bound!")
        
        self.logger.info("Bound all HTTP signals to their respective slots!")

    def bind_attributes(self):
        """Binds all attribute signals to their respective slots."""
        self.logger.info("Binding attribute signals to their respective slots...")
    
        if self.isaac_log is not None:
            self.logger.info("Binding timeout signal...")
            self.isaac_timer.timeout.connect(self.process_log_changes)
            self.logger.info("Bound!")
    
        self.logger.info("Bound all attribute signals to their respective slots!")

    # Menu Methods #
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
        self.close()

    def force_menu(self, action: QtWidgets.QAction):
        """Forces the menubar's menu to be shown."""
    
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

        logger.setLevel(logging.DEBUG if self.configs["settings"]["debug"]["enabled"] else logging.INFO)
        
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

    def setup_metadata(self):
        """Populates the metadata dialog."""
        self.metadata.set_project_name(self.NAME)
        self.metadata.set_project_version(".".join([str(i) for i in self.VERSION]))
        self.metadata.set_project_authors(*self.AUTHORS)
        self.metadata.set_project_website("https://github.com/sirrandoo/decision-descent")
        self.metadata.set_project_docs("https://sirrandoo.github.io/decision-descent")
        self.metadata.set_project_license(self.LICENSE,
                                          "https://github.com/sirrandoo/decision-descent/blob/master/LICENSE")

    def find_isaac_log(self) -> typing.Union[QtCore.QFile, None]:
        """Attempts to find Isaac's log file."""
        if platform.system() == "Windows":
            user_directory = os.getenv("USERPROFILE")
            isaac_directory = os.path.join(user_directory, "Documents\\My Games\\Binding of Isaac Afterbirth+")
        
            return QtCore.QFile(os.path.join(isaac_directory, "log.txt"), self)
    
        else:
            return None

    # Slots #
    def process_log_changes(self):
        """Processes changes to the Isaac log file."""
        if self.isaac_log is not None:
            if self.isaac_log.isReadable():
                if self.isaac_size > self.isaac_log.size():  # Let's assume the log was overwritten
                    self.isaac_size = self.isaac_log.size()
                    self.ui.isaac_log.clear()
                    self.isaac_log.seek(0)
            
                while not self.isaac_log.atEnd():
                    data = self.isaac_log.readLine()
                
                    if not data.isEmpty():
                        data = utils.format_isaac(data.data().decode())
                    
                        if data is not None:
                            self.ui.isaac_log.append(data)
                    QtWidgets.qApp.processEvents()
            
                self.isaac_size = self.isaac_log.size()
    
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
            for key, value in self.configs.items():
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
