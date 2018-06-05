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
import traceback
import typing
import win32gui

from PyQt5 import QtCore, QtGui, QtWidgets

import utils
from utils import dataclasses
from . import http, info, metadata, tray
from .uis import ClientUi

__all__ = {"Client"}


class Client(QtWidgets.QMainWindow):
    """The heart of Decision Descent: Client."""
    LICENSE = "GNU General Public License 3 or later"
    NAME = "Decision Descent: Client"
    AUTHORS = ["SirRandoo"]
    VERSION = (0, 3, 0)
    
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
        self.formatter = utils.DescentFormatter(fmt="[{asctime}][{levelname}][{name}][{funcName}] {message}",
                                                datefmt="%H:%M:%S",
                                                style="{")
        self.logger = logging.getLogger("client")
        self.integrations = list()
        self.loggers = list()
        
        self.display = info.Info(parent=self)
        self.tray = tray.TrayIcon(parent=self)
        self.http = http.HttpListener(parent=self)
        self.metadata = metadata.MetadataDialog(parent=self)
        self.data = utils.DescentData(self, parent=self)
        self.show_action = QtWidgets.QAction("Show", parent=self.tray.menu)

        self.isaac_timer = QtCore.QTimer(parent=self)
        self.isaac_window_size = QtCore.QSize()
        self.isaac_log = self.find_isaac_log()
        self.isaac_log_restriction = "all"
        self.isaac_size = QtCore.QSize(0, 0)
        self.isaac_log_size = 0
        
        # "Private" Attributes #
        self._shutting_down = False
        
        # Internal Calls #
        self.setup_logger("client")
        self.setup_logger("QtTwitch")
        self.ui.menu_bar.raise_()  # Fixes the menubar not showing actions
        self.tray.show()

        # Called before bind() so we don't unnecessarily repopulate the log
        self.ui.client_filter.setCurrentIndex(self.ui.client_filter.findText("All"))
        self.ui.isaac_filter.setCurrentIndex(self.ui.isaac_filter.findText("All"))
        self.ui.isaac_filter_modifier.setChecked(False)

        # Set acceptable close methods
        self.ui.menu_quit.setShortcut(QtGui.QKeySequence(QtCore.Qt.CTRL | QtCore.Qt.Key_Q,
                                                         QtCore.Qt.ALT | QtCore.Qt.Key_F4))
        
        self.bind()
        self.mirror_menubar()
        self.setup_metadata()
        self.load_integrations()
        self.http.connect()

        self.isaac_timer.start(1000)
        self.ui.client_log.verticalScrollBar().setValue(self.ui.client_log.verticalScrollBar().maximum())
        self.ui.isaac_log.verticalScrollBar().setValue(self.ui.isaac_log.verticalScrollBar().maximum())
        
        self.setWindowIcon(QtGui.QIcon('assets/icon.png'))
        self.tray.tray_icon.setIcon(self.windowIcon())

        if self.isaac_log is not None:
            if not self.isaac_log.isOpen():
                self.isaac_log.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
    
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

        self.logger.info("Binding menu_settings.triggered action...")
        self.ui.menu_settings.triggered.connect(lambda: self.logger.info("The settings menu is currently disabled."))
        self.logger.info("Bound!")

        self.logger.info("Binding menu_quit.triggered action...")
        self.ui.menu_quit.triggered.connect(lambda: QtWidgets.qApp.exit(0))
        self.logger.info("Bound!")

        self.logger.info("Binding help_help.triggered action...")
        self.ui.help_help.triggered.connect(self.help)
        self.logger.info("Bound!")

        self.logger.info("Binding help_about.triggered action...")
        self.ui.help_about.triggered.connect(self.about)
        self.logger.info("Bound!")

        self.logger.info("Binding help_license.triggered action...")
        self.ui.help_license.triggered.connect(self.license)
        self.logger.info("Bound!")
        
        self.logger.info("Menubar actions to their respective slots!")
    
    def bind_tray(self):
        """Binds all tray actions to their respective slots."""
        self.logger.info("Binding tray events to their respective slots...")

        self.logger.info("Binding tray.clicked signal...")
        self.tray.clicked.connect(self.showNormal)
        self.logger.info("Bound!")

        self.logger.info("Binding tray.middle_clicked signal...")
        self.tray.middle_clicked.connect(self.showNormal)
        self.logger.info("Bound!")

        self.logger.info("Binding tray.double_clicked event...")
        self.tray.double_clicked.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Tray events bound to their respective slots!")
        self.logger.info("Binding tray signals to their respective slots...")

        self.logger.info("Binding show_action.triggered signal...")
        self.show_action.triggered.connect(self.showNormal)
        self.logger.info("Bound!")
        
        self.logger.info("Tray signals bound to their respective slots!")
    
    def bind_http(self):
        """Binds all http signals to their respective slots."""
        self.logger.info("Binding HTTP signals to their respective slots...")

        self.logger.info("Binding http.on_response signal...")
        self.http.on_response.connect(self.data.process_message)
        self.logger.info("Bound!")

        self.logger.info("Binding http.on_connection_received signal...")
        self.http.on_connection_received.connect(self.data.process_new_connection)
        self.logger.info("Bound!")
        
        self.logger.info("Bound all HTTP signals to their respective slots!")

    def bind_attributes(self):
        """Binds all attribute signals to their respective slots."""
        self.logger.info("Binding attribute signals to their respective slots...")

        if self.isaac_log is not None:
            self.logger.info("Binding isaac_timer.timeout signal...")
            self.isaac_timer.timeout.connect(self.process_isaac_tasks)
            self.logger.info("Bound!")

        self.logger.info("Bound all attribute signals to their respective slots!")

    def bind_log(self):
        """Binds all log-related widgets to their respective slots."""
        self.logger.info("Binding log-related widgets to their respective slots....")
    
        self.logger.info("Binding client_filter.currentIndexChanged to its respective slot...")
        self.ui.client_filter.currentIndexChanged.connect(self.adjust_client_log_filter)
        self.logger.info("Bound!")
    
        self.logger.info("Binding isaac_filter.currentIndexChanged to its respective slot...")
        self.ui.isaac_filter.currentIndexChanged.connect(self.adjust_isaac_log_filter)
        self.logger.info("Bound!")
    
        self.logger.info("Binding isaac_filter_modifier.clicked to its respective slot...")
        self.ui.isaac_filter_modifier.clicked.connect(self.adjust_isaac_log_filter)
        self.logger.info("Bound!")
    
        self.logger.info("Bound all log-related widgets to their respective slots...")
    
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
    
    # Utility Methods #
    def setup_logger(self, name: str) -> logging.Logger:
        """Sets up the logger passed."""
        logger = logging.getLogger(name)

        if logger.hasHandlers():
            self.logger.warning(f'Logger `{name}` already has handlers attached!')

        self.logger.info(f'Adding handlers to `{name}`...')
        for handler in self.handlers:
            if handler not in logger.handlers:
                logger.addHandler(handler)
                
                if handler.formatter is None:
                    handler.setFormatter(self.formatter)

        self.logger.info(f'Setting logger level to client\'s level...')
        logger.setLevel(logging.DEBUG if self.configs["settings"]["debug"].as_bool("enabled") else logging.INFO)
        
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
        if QtWidgets.qApp.platformName() == "windows":
            user_directory = os.getenv("USERPROFILE")
            isaac_directory = os.path.join(user_directory, "Documents\\My Games\\Binding of Isaac Afterbirth+")

            return QtCore.QFile(os.path.join(isaac_directory, "log.txt"), self)

        else:
            return None

    def adjust_client_log_filter(self):
        """Adjusts the client log's filter level."""
        self.logger.debug("Adjusting client log...")
    
        requested_filter = self.ui.client_filter.currentText().lower()
        color_filter = requested_filter.upper()
        filter_check = "[{}]".format(requested_filter.title())
    
        self.logger.debug("Finding color matrix...")
        for handler in self.handlers:
            if isinstance(handler, utils.Log):
                self.logger.debug("Found!")
            
                self.logger.debug("Enforcing filter on future messages...")
                handler.restriction = requested_filter
                self.logger.debug("Done!")
            
                self.logger.debug("Clearing log...")
                self.ui.client_log.clear()
                self.logger.debug("Cleared!")
            
                self.logger.debug("Repopulating log display...")
                log = QtCore.QFile("log.txt")
            
                if not log.isOpen():
                    log.open(log.Text | log.ReadOnly)
            
                while not log.atEnd():
                    data = log.readLine()  # type: QtCore.QByteArray
                
                    if not data.isEmpty():
                        data = data.data().decode()
                    
                        if data[len("[HH:MM:SS]"):].startswith(filter_check):
                            self.ui.client_log.append(f'<span style="color: #{handler.colors[color_filter]}">'
                                                      f'{data}</span><br/>')
                    
                        elif requested_filter == "all":
                            for level, color in handler.colors.items():
                                if data[len("[HH:MM:SS]"):].startswith(f'[{level.title()}]'):
                                    self.ui.client_log.append(f'<span style="color: #{color}">{data}</span><br/>')
                
                    QtWidgets.qApp.processEvents()
            
                if log.isOpen():
                    log.close()

    def adjust_isaac_log_filter(self):
        """Adjusts Isaac log's filter level."""
        if self.isaac_log is not None:
            self.logger.debug("Adjusting Isaac log...")
        
            requested_filter = self.ui.isaac_filter.currentText().lower()
            only_companion = self.ui.isaac_filter_modifier.isChecked()
            filter_check = "[{}]".format(requested_filter.title())
        
            self.logger.debug("Finding color matrix...")
            for handler in self.handlers:
                if isinstance(handler, utils.Log):
                    self.logger.debug("Found!")
                
                    self.logger.debug("Enforcing filter on future messages...")
                    handler.restriction = requested_filter
                    self.logger.debug("Done!")
                
                    self.logger.debug("Clearing log...")
                    self.ui.isaac_log.clear()
                    self.logger.debug("Cleared!")
                
                    self.logger.debug("Repopulating log display...")
                    log = QtCore.QFile(self.isaac_log.fileName())
                
                    if not log.isOpen():
                        log.open(log.Text | log.ReadOnly)
                
                    while not log.atEnd():
                        data = log.readLine()  # type: QtCore.QByteArray
                    
                        if not data.isEmpty():
                            formatted_data, is_mod = utils.format_isaac(data.data().decode())
                        
                            if formatted_data is not None:
                                stripped_data = formatted_data[32:len(formatted_data) - 12]
                            
                                if stripped_data[len("[HH:MM:SS]"):].startswith(filter_check):
                                    if only_companion and is_mod:
                                        self.ui.isaac_log.append(formatted_data)
                                
                                    elif not only_companion:
                                        self.ui.isaac_log.append(formatted_data)
                            
                                elif requested_filter == "all":
                                    if only_companion and is_mod:
                                        self.ui.isaac_log.append(formatted_data)
                                
                                    elif not only_companion:
                                        self.ui.isaac_log.append(formatted_data)
                    
                        QtWidgets.qApp.processEvents()
                
                    if log.isOpen():
                        log.close()
    
    # Slots #
    def process_isaac_tasks(self):
        """Processes Isaac-related tasks."""
        if self.isaac_log is not None:
            if self.isaac_log.isReadable():
                if self.isaac_log_size > self.isaac_log.size():  # Let's assume the log was overwritten
                    self.isaac_log_size = self.isaac_log.size()
                    self.ui.isaac_log.clear()
                    self.isaac_log.seek(0)
    
                while not self.isaac_log.atEnd():
                    data = self.isaac_log.readLine()  # type: QtCore.QByteArray
                    
                    if not data.isEmpty():
                        data, is_mod = utils.format_isaac(data.data().decode())
                        
                        if data is not None:
                            if self.ui.isaac_filter_modifier.isChecked() and is_mod:
                                self.ui.isaac_log.append(data)
    
                            elif not self.ui.isaac_filter_modifier.isChecked():
                                self.ui.isaac_log.append(data)
                    QtWidgets.qApp.processEvents()
    
                self.isaac_log_size = self.isaac_log.size()
    
        isaac_window = win32gui.FindWindow(None, "Binding of Isaac: Afterbirth+")
    
        if isaac_window > 0:
            window_rect = win32gui.GetWindowRect(isaac_window)
            window_width = abs(window_rect[0] - window_rect[2])
            window_height = abs(window_rect[1] - window_rect[3])
        
            if window_width != self.isaac_size.width():
                self.logger.warning("Isaac dimensions differ from our cache!")
                self.logger.info("Sending new dimensions to mod...")
            
                self.isaac_size = QtCore.QSize(window_width, window_height)
                self.http.send_message(utils.dataclasses.Message.from_json(dict(intent="state.dimensions.update",
                                                                                args=[window_width, window_height])))
        
            elif window_height != self.isaac_size.height():
                self.logger.warning("Isaac dimensions differ from our cache!")
                self.logger.info("Sending new dimensions to mod...")
            
                self.isaac_size = QtCore.QSize(window_width, window_height)
                self.http.send_message(utils.dataclasses.Message.from_json(dict(intent="state.dimensions.update",
                                                                                args=[window_width, window_height])))
    
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
