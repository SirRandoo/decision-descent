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
import inspect
import json
import logging
import typing
from distutils import version

from PyQt5 import QtCore, QtGui, QtHelp, QtNetwork, QtWidgets

from QtUtilities import requests, settings
from QtUtilities.utils import should_create_widget
from QtUtilities.widgets import progress
from utils.dataclasses import Integration
from .about import About

__all__ = ['Client']


# noinspection PyArgumentList,PyCallByClass
class Client(QtWidgets.QMainWindow):
    """The heart of Decision Descent."""
    
    # These variables aren't expected to change at any point.
    LICENSE = 'GNU General Public License 3 or later'
    AUTHORS = {'SirRandoo'}
    RESOURCES = QtCore.QDir('resources')
    ASSETS = QtCore.QDir(RESOURCES.filePath('assets'))
    REPOSITORY = QtCore.QUrl('https://github.com/sirrandoo/decision-descent')
    
    # These variables are assigned dynamically from the application's
    # metadata.  If you rely on these for any reason, you should adjust
    # accordingly or grab data directly from the application itself.
    NAME = None
    VERSION = None
    
    def __init__(self, **kwargs):
        # Super Call #
        super(Client, self).__init__(parent=kwargs.get("parent"), flags=QtCore.Qt.Window)

        # Ui Declarations #
        self.central_tabs: QtWidgets.QTabWidget = None

        self.client_tab: QtWidgets.QWidget = None
        self.client_log: QtWidgets.QTextBrowser = None
        self.client_filter: QtWidgets.QComboBox = None
        self.client_filter_label: QtWidgets.QLabel = None
        self.client_filter_vessel: QtWidgets.QWidget = None

        self.isaac_tab: QtWidgets.QWidget = None
        self.isaac_log: QtWidgets.QTextBrowser = None
        self.isaac_filter: QtWidgets.QTextBrowser = None
        self.isaac_filter_label: QtWidgets.QLabel = None
        self.isaac_filter_vessel: QtWidgets.QWidget = None
        self.isaac_filter_augment: QtWidgets.QCheckBox = None

        self.menu_bar: QtWidgets.QMenuBar = None
        #
        self.file_menu: QtWidgets.QMenu = None
        self.settings_action: QtWidgets.QAction = None
        self.quit_action: QtWidgets.QAction = None
        #
        self.help_menu: QtWidgets.QMenu = None
        self.help_action: QtWidgets.QAction = None
        self.about_action: QtWidgets.QAction = None
        self.update_action: QtWidgets.QAction = None
        
        # "Public" Attributes #
        self.settings: settings.Display = settings.Display()
        self.help_engine: QtHelp.QHelpEngineCore = QtHelp.QHelpEngineCore(self.RESOURCES.filePath('docs.qhcp'))
        
        # "Private" Attributes #
        self._logger = logging.getLogger("core")
        self._request_factory: requests.Factory = None
        self._settings_file = QtCore.QFile('settings.json')
        self._loggers: typing.List[logging.Logger] = list()
        self._integrations: typing.List[Integration] = list()
        
        # Internal Calls #
        # noinspection PyTypeChecker
        QtCore.QTimer.singleShot(1, self.setup)
    
    # Ui Methods #
    def setup(self, *, popup: bool = None):
        """Sets up the client.
        
        If `popup` is enabled, a progress dialog will be displayed to inform
        the user."""
        app = QtWidgets.QApplication.instance()
        self._request_factory = requests.Factory(manager=app.network_access_manager())
        
        if popup:
            with progress.Context() as p_ctx:
                p_ctx.set_text('Loading settings...')
                self.load_settings()
                
                p_ctx.set_text('Applying settings...')
                self.apply_settings()
                
                p_ctx.set_text('Setting up UI...')
                self.setup_ui(p_ctx=p_ctx)
                
                p_ctx.set_text('Done!')
                self.show()
        
        else:
            self.load_settings()
            self.apply_settings()
            self.setup_ui()
            self.show()
    
    def setup_ui(self, *, p_ctx: progress.Context = None):
        """Sets up the client's UI."""
        self.setDocumentMode(True)
        
        if should_create_widget(self.menu_bar):
            self.menu_bar = QtWidgets.QMenuBar()
            self.menu_bar.setNativeMenuBar(True)
            
            self.setMenuBar(self.menu_bar)
        
        if should_create_widget(self.central_tabs):
            self.central_tabs = QtWidgets.QTabWidget()
            self.central_tabs.setMovable(True)
            self.central_tabs.setTabBarAutoHide(True)
            self.central_tabs.setTabPosition(self.central_tabs.West)
            self.central_tabs.setDocumentMode(True)
            
            self.setCentralWidget(self.central_tabs)
        
        for name, inst in inspect.getmembers(self):
            if name.startswith("setup_") and name.endswith("_ui") and name != "setup_ui":
                inst(p_ctx=p_ctx)
    
    # noinspection PyArgumentList
    def setup_client_ui(self, *, p_ctx: progress.Context = None):
        """Sets up the client tab's ui."""
        if p_ctx is not None:
            p_ctx.set_text("Setting up client UI...")
        
        # noinspection PyArgumentList
        if should_create_widget(self.client_tab):
            self.client_tab = QtWidgets.QWidget(parent=self.central_tabs, flags=QtCore.Qt.Widget)
            
            if should_create_widget(self.client_filter):
                self.client_filter = QtWidgets.QComboBox()
                self.client_filter.addItems(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])
            
            if should_create_widget(self.client_filter_label):
                self.client_filter_label = QtWidgets.QLabel("Log Level")
                self.client_filter_label.setWordWrap(True)
            
            if should_create_widget(self.client_log):
                self.client_log = QtWidgets.QTextBrowser()
                self.client_log.setWordWrapMode(QtGui.QTextOption.NoWrap)
            
            if should_create_widget(self.client_filter_vessel):
                self.client_filter_vessel = QtWidgets.QWidget(flags=QtCore.Qt.Widget)
                
                v_layout = QtWidgets.QFormLayout(self.client_filter_vessel)
                v_layout.addRow(self.client_filter_label, self.client_filter)
                v_layout.setLabelAlignment(QtCore.Qt.AlignRight)
                v_layout.setContentsMargins(0, 0, 0, 0)
            
            layout = QtWidgets.QVBoxLayout(self.client_tab)
            layout.addWidget(self.client_filter_vessel)
            layout.addWidget(self.client_log)
            
            self.central_tabs.addTab(self.client_tab, "Client")
    
    # noinspection PyArgumentList
    def setup_isaac_ui(self, *, p_ctx: progress.Context = None):
        """Sets up the isaac tab's ui."""
        if p_ctx is not None:
            p_ctx.set_text("Setting up isaac UI...")
        
        if should_create_widget(self.isaac_tab):
            self.isaac_tab = QtWidgets.QWidget(parent=self.central_tabs, flags=QtCore.Qt.Widget)
            
            if should_create_widget(self.isaac_filter):
                self.isaac_filter = QtWidgets.QComboBox()
                self.isaac_filter.addItems(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])
            
            if should_create_widget(self.isaac_filter_augment):
                self.isaac_filter_augment = QtWidgets.QCheckBox('Mod only?')
            
            if should_create_widget(self.isaac_filter_label):
                self.isaac_filter_label = QtWidgets.QLabel("Log Level")
                self.isaac_filter_label.setWordWrap(True)
            
            if should_create_widget(self.isaac_log):
                self.isaac_log = QtWidgets.QTextBrowser()
                self.isaac_log.setWordWrapMode(QtGui.QTextOption.NoWrap)
            
            if should_create_widget(self.isaac_filter_vessel):
                self.isaac_filter_vessel = QtWidgets.QWidget(flags=QtCore.Qt.Widget)
                
                v_layout = QtWidgets.QFormLayout(self.isaac_filter_vessel)
                v_layout.addRow(self.isaac_filter_label, self.isaac_filter)
                v_layout.addWidget(self.isaac_filter_augment)
                v_layout.setLabelAlignment(QtCore.Qt.AlignRight)
                v_layout.setContentsMargins(0, 0, 0, 0)
            
            layout = QtWidgets.QVBoxLayout(self.isaac_tab)
            layout.addWidget(self.isaac_filter_vessel)
            layout.addWidget(self.isaac_log)
            
            self.central_tabs.addTab(self.isaac_tab, "Isaac")
    
    def setup_menu_ui(self, *, p_ctx: progress.Context = None):
        """Sets up the menu bar ui."""
        if p_ctx is not None:
            p_ctx.set_text("Setting up menu bar UI...")
        
        if should_create_widget(self.file_menu):
            self.file_menu = QtWidgets.QMenu("File")
            
            if should_create_widget(self.settings_action):
                self.settings_action = QtWidgets.QAction(QtGui.QIcon(self.ASSETS.filePath("write-icon.png")),
                                                         "Settings...")
                self.settings_action.triggered.connect(self.settings.show)
            
            if should_create_widget(self.quit_action):
                self.quit_action = QtWidgets.QAction("Quit")
                self.quit_action.triggered.connect(self.close)
        
        if should_create_widget(self.help_menu):
            self.help_menu = QtWidgets.QMenu("Help")
            
            if should_create_widget(self.help_action):
                self.help_action = QtWidgets.QAction("Help")
                self.help_action.triggered.connect(self.help)
            
            if should_create_widget(self.about_action):
                self.about_action = QtWidgets.QAction("About")
                self.about_action.triggered.connect(self.about)
            
            if should_create_widget(self.update_action):
                self.update_action = QtWidgets.QAction(QtGui.QIcon(self.ASSETS.filePath("restock-icon.png")),
                                                       "Check for Updates...")
                self.update_action.triggered.connect(self.check_for_updates)
        
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        
        self.file_menu.addAction(self.quit_action)
        #
        #
        self.help_menu.addAction(self.help_action)
        self.help_menu.addSeparator()
        
        self.help_menu.addAction(self.update_action)
        self.help_menu.addAction(self.about_action)
        #
        #
        self.menu_bar.addMenu(self.file_menu)
        self.menu_bar.addMenu(self.help_menu)
    
    # Menu Methods #
    def help(self):
        """Shows the help dialog for Decision Descent."""
        self._logger.info('Preparing help display...')

        self._logger.warning('Help display has not been implemented yet!')
    
    def about(self):
        """Shows the about dialog for Decision Descent."""
        self._logger.info('Preparing about display...')

        # Declarations #
        about = About()
        application = QtWidgets.QApplication.instance()
        domain = application.organizationDomain()
        website = f'http://{domain}' if not domain.startswith('http') else domain
        repo = self.REPOSITORY.toDisplayString()
        repo = f'http://{repo}' if not repo.startswith('http') else repo

        # Metadata #
        self._logger.info('Population about display...')
        about.name.setText(f'<a href="{repo}">{application.applicationName()}</a>')
        about.display_name.setText(application.applicationDisplayName())
        about.version.setText(application.applicationVersion())
        about.integrations.setText('{0} out of {0} integrations loaded'.format(len(self._integrations)))
        about.website.setText(f'<a href="{website}">{domain}</a>')
        about.authors.setText(', '.join(self.AUTHORS))
        about.license.setText(self.LICENSE)

        # Invocation #
        self._logger.info('About display prepared!')
        about.adjustSize()
        about.exec()
    
    def check_for_updates(self, *, automatic: bool = None):
        """Checks for new updates to dependencies, the mod, and extensions."""
        if automatic is None:
            automatic = False
        
        self._logger.info('Preparing update checker...')
        
        self._logger.info('Gathering application metadata...')
        application = QtWidgets.QApplication.instance()
        app_version = version.StrictVersion(application.applicationVersion())
        stable_only = self.settings['client']['system']['updates']['stable_only'].value
        
        self._logger.info('Checking for updates...')
        
        if self.REPOSITORY.host() == 'github.com':
            path: str = self.REPOSITORY.path().lstrip('/')
            repo_owner, repo_slug, *_ = path.split('/')
            
            self._logger.debug('Pinging Github...')
            response = self._request_factory.get(f'https://api.github.com/repos/{repo_owner}/{repo_slug}/tags',
                                                 headers={'Accept': 'application/vnd.github.v3+json'})
            
            if response.is_ok():
                self._logger.debug('Decoding content...')
                
                try:
                    content = response.json()
                
                except ValueError:
                    self._logger.warning('Could not decode response! Is it valid JSON?')
                
                else:
                    self._logger.debug('Content decoded!')
                    
                    if len(content) > 0:
                        self._logger.debug('There are {} releases of {}'.format(len(content), self.NAME))
                        
                        for release in content:
                            prerelease = release.get('prerelease', False)
                            
                            if prerelease and not stable_only:
                                if version.StrictVersion(release['name'].lstrip('v')) > app_version:
                                    markdown_response = self._request_factory.post('https://api.github.com/markdown',
                                                                                   params={
                                                                                       'text': release['body'],
                                                                                       'mode': 'gfm',
                                                                                       'context': f'{repo_owner}/'
                                                                                       f'{repo_slug}'
                                                                                   })
                                    
                                    if markdown_response.is_ok():
                                        pass
                                
                                else:
                                    if not automatic:
                                        info_dialog = QtWidgets.QMessageBox(
                                            QtWidgets.QMessageBox.Information,
                                            'Update Checker',
                                            f'You are on the most recent version of {self.NAME}',
                                            QtWidgets.QMessageBox.Ok,
                                            self
                                        )
                                        
                                        info_dialog.exec()
                                    
                                    else:
                                        self._logger.info(f'This is the most recent version of {self.NAME}')
                                
                                break  # End after the first pre-release
                            
                            elif not prerelease:
                                if version.StrictVersion(release['name'].lstrip('v')) > app_version:
                                    pass  # Show changelog
                                
                                else:
                                    if not automatic:
                                        info_dialog = QtWidgets.QMessageBox(
                                            QtWidgets.QMessageBox.Information,
                                            'Update Checker',
                                            f'You are on the most recent version of {self.NAME}',
                                            QtWidgets.QMessageBox.Ok,
                                            self
                                        )
                                        
                                        info_dialog.exec()
                                    
                                    else:
                                        self._logger.info(f'This is the most recent version of {self.NAME}')
                                
                                break  # End after the first stable release
                    
                    else:
                        self._logger.warning('There are no releases!')
            
            else:
                self._logger.warning(f'Could not fetch versions from Github!')
                self._logger.warning(f'Reason: {response.error_string()}')
                
                if response.error_code() == QtNetwork.QNetworkReply.ContentAccessDenied:
                    self._logger.warning('Possible reasons:')
                    self._logger.warning('The update checker does not support private repositories.')
                    self._logger.warning('You have exceeded your maximum number of requests per hour.')
                    self._logger.warning('If it is the latter, you can try again in an hour.')
        
        else:
            # Since we don't know what the API for anything other than Github is
            self._logger.warning(f'Unsupported host "{self.REPOSITORY.host()}"!')
            self._logger.warning(f'To enable update checks, please ask the maintainers of {self.NAME} to add '
                                 f'support for their host.')
    
    # Settings Methods #
    def load_settings(self):
        """Loads the client's settings."""
        if self._settings_file.exists():
            if not self._settings_file.isOpen():
                self._settings_file.open(QtCore.QFile.Text | QtCore.QFile.ReadOnly)
            
            if self._settings_file.isReadable():
                d: QtCore.QByteArray = self._settings_file.readAll()
                
                if not d.isEmpty():
                    try:
                        data = json.loads(d.data().decode())
                    
                    except ValueError as e:
                        self._logger.warning(f'Could not decode file "{self._settings_file.fileName()}')
                        self._logger.warning(f'Exception Cause: {e.__cause__}')
                    
                    else:
                        complete = True
                        
                        for s in data:
                            try:
                                setting: settings.Setting = settings.Setting.from_data(s)
                            
                            except ValueError as e:
                                self._logger.warning('Aborting settings load!')
                                self._logger.warning(f'Could not decode setting "{s.get("name")}"')
                                self._logger.warning(f'Exception Cause: {e.__cause__}')
                                complete = True
                                break
                            
                            else:
                                self.settings.register(setting)
                        
                        if complete:
                            self.validate_settings()
                            return
                    
                    finally:
                        if self._settings_file.isOpen():
                            self._settings_file.close()
                
                else:
                    self._logger.warning(f'File "{self._settings_file.fileName()}" is empty!')
            
            else:
                self._logger.warning(f'File "{self._settings_file.fileName()}" is not readable!')
                self._logger.warning(f'Reason: #{self._settings_file.error()} - {self._settings_file.errorString()}')
        
        else:
            self._logger.warning('Settings file does not exist!')
            self._logger.warning('Is this a first run?')
        
        # Generate settings
        for s in self.generate_settings():
            self.settings.register(s)
    
    def generate_settings(self) -> typing.List[settings.Setting]:
        """Generates a fresh config for Decision Descent."""
        domains = {
            'client': settings.Setting("client", tooltip='Settings related to the client.'),
            'isaac': settings.Setting("isaac", tooltip='Settings related to the Afterbirth+ mod.')
        }
        
        # Client Settings #
        c_display = settings.Setting("display", tooltip='Settings related to the visual display of the client.')
        c_window = settings.Setting("window", tooltip='Settings related to the literal window of the client.')
        c_extensions = settings.Setting("extensions", tooltip='Settings related to the extension framework.')
        c_system = settings.Setting("system", tooltip='Settings related to Decision Descent as a whole.')
        c_s_updates = settings.Setting('updates', tooltip='Settings related to the update checker.')
        
        # client.display Settings #
        
        # client.window Settings #
        c_window.add_children(
            settings.Setting(
                'x', self.x(),
                display_name='Window X',
                read_only=True,
                tooltip='The top-left position the main window '
                        'will be along the X axis.'
            ),
            
            settings.Setting(
                'y', self.y(),
                display_name='Window Y',
                read_only=True,
                tooltip='The top-left position the main window '
                        'will be along the Y axis.'
            ),
            
            settings.Setting(
                'width', self.width(),
                display_name='Window Width',
                read_only=True,
                tooltip='The width of the main window.'
            ),
            
            settings.Setting(
                'height', self.height(),
                display_name='Window Height',
                read_only=True,
                tooltip='The height of the main window.'
            )
        )
        
        # client.extensions Settings #
        c_extensions.add_children(
            settings.Setting(
                'directory', 'extensions',
                display_name='Extension Directory',
                tooltip='The directory extensions are located in.',
                converter=settings.converters.qfile
            )
        )
        
        # client.system Settings #
        c_system.add_children(
            settings.Setting(
                'debug_mode', False,
                display_name='Debug Mode?',
                tooltip='Whether or not Decision Descent is in '
                        'debug mode.'
            )
        )
        
        # client.system.updates Settings #
        c_s_updates.add_children(
            settings.Setting(
                'auto', True,
                display_name='Automatic update checks?',
                tooltip='Whether or not Decision Descent will include '
                        'pre-releases in its update check.'
            ),
            
            settings.Setting(
                'stable_only', True,
                display_name='Stable releases only?',
                tooltip='Whether or not Decision Descent will include '
                        'pre-releases in its update check.'
            )
        )
        
        # Stitching #
        c_system.add_children(c_s_updates)
        domains["client"].add_children(c_display, c_window, c_extensions, c_system)
        
        return list(domains.values())
    
    def validate_settings(self):
        """Verifies the loaded settings with the generated settings."""
    
    def apply_settings(self):
        """Applies settings to the client.  This method is responsible for
        applying settings, like theme changes, to the client."""
        # Window Settings
        self.move(self.settings["client"]["window"]["x"].value, self.settings["client"]["window"]["y"].value)
        self.resize(self.settings["client"]["window"]["width"].value, self.settings["client"]["window"]["height"].value)
        
        # Update Settings
        if self.settings['client']['system']['updates'].value:
            # noinspection PyTypeChecker
            QtCore.QTimer.singleShot(1, functools.partial(self.check_for_updates, automatic=True))
    
    # Event Overrides #
    def moveEvent(self, event: QtGui.QMoveEvent):
        """An override to ensure the window's current position persists
        through instances."""
        position: QtCore.QPoint = event.pos()
        
        self.settings["client"]["window"]["x"].value = position.x()
        self.settings["client"]["window"]["y"].value = position.y()
        
        x_display = getattr(self.settings['client']['window']['x'], '_display', None)
        y_display = getattr(self.settings['client']['window']['y'], '_display', None)
        
        if x_display:
            x_display.setValue(position.x())
        
        if y_display:
            y_display.setValue(position.y())
        
        super(Client, self).moveEvent(event)
    
    def resizeEvent(self, event: QtGui.QResizeEvent):
        """An override to ensure the window's current size persists
        through instances."""
        size: QtCore.QSize = event.size()
        
        self.settings["client"]["window"]["width"].value = size.width()
        self.settings["client"]["window"]["height"].value = size.height()
        
        height_display = getattr(self.settings['client']['window']['height'], '_display', None)
        width_display = getattr(self.settings['client']['window']['width'], '_display', None)
        
        if height_display:
            height_display.setValue(size.height())
        
        if width_display:
            width_display.setValue(size.width())
        
        super(Client, self).resizeEvent(event)
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        """An override to QMainWindow's closeEvent.  This event is responsible
        for performing closing operations, such as saving settings."""
        try:
            d = json.dumps(self.settings.to_data())

        except ValueError as e:
            self._logger.warning('Settings could not be serialized!')
            self._logger.warning(f'Reason: {e.__cause__}')

        else:
            if not self._settings_file.isOpen():
                self._settings_file.open(QtCore.QFile.Text | QtCore.QFile.WriteOnly | QtCore.QFile.Truncate)
    
            if self._settings_file.isWritable():
                self._settings_file.write(d.encode(encoding='UTF-8'))
    
            else:
                self._logger.warning('Settings could not be saved!')
                self._logger.warning(f'Reason: #{self._settings_file.error()} - {self._settings_file.errorString()}')

        finally:
            if self._settings_file.isOpen():
                self._settings_file.close()


# class Client_2(QtWidgets.QMainWindow):
#     """The heart of Decision Descent: Client."""
#     LICENSE = "GNU General Public License 3 or later"
#     NAME = "Decision Descent: Client"
#     AUTHORS = ["SirRandoo"]
#     VERSION = (0, 0, 0)
#
#     # noinspection PyArgumentList
#     def __init__(self, parent: QtWidgets.QWidget = None):
#         # Super Call #
#         super(Client_2, self).__init__(parent=parent)
#
#         # Ui Call #
#         self.ui = ClientUi()
#         self.ui.setupUi(self)
#
#         # "Public" Attributes #
#         self.converters = settings.Converter()
#         self.config = self.load_config()
#         self.handlers = [logging.FileHandler("log.txt", encoding="UTF-8", mode="w"), utils.Log(self.ui.client_log)]
#         self.formatter = utils.DescentFormatter(fmt="[{asctime}][{levelname}][{name}][{funcName}] {message}",
#                                                 datefmt="%H:%M:%S",
#                                                 style="{")
#         self.logger = logging.getLogger("core")
#         self.integrations = list()
#         self.loggers = list()
#
#         self.display = info.Info(parent=self)
#         self.tray = tray.TrayIcon(parent=self)
#         self.http = http.HttpListener(parent=self)
#         self.metadata = metadata.MetadataDialog(parent=self)
#         self.data = utils.DescentData(self, parent=self)
#         self.show_action = QtWidgets.QAction("Show", parent=self.tray.menu)
#
#         self.isaac_timer = QtCore.QTimer(parent=self)
#         self.isaac_window_size = QtCore.QSize()
#         self.isaac_log = self.find_isaac_log()
#         self.isaac_log_restriction = "all"
#         self.isaac_size = QtCore.QSize(0, 0)
#         self.isaac_log_size = 0
#
#         # "Private" Attributes #
#
#         # Internal Calls #
#         self.setup_logger("core")
#         self.setup_logger("QtTwitch")
#         self.ui.menu_bar.raise_()  # Fixes the menubar not showing actions
#
#         # Called before bind() so we don't unnecessarily repopulate the log
#         self.ui.client_filter.setCurrentIndex(self.ui.client_filter.findText("All"))
#         self.ui.isaac_filter.setCurrentIndex(self.ui.isaac_filter.findText("All"))
#         self.ui.isaac_filter_modifier.setChecked(False)
#
#         self.bind()
#         self.mirror_menubar()
#         self.setup_metadata()
#         self.load_integrations()
#         self.http.connect()
#
#         self.isaac_timer.start(1000)
#         self.ui.client_log.verticalScrollBar().setValue(self.ui.client_log.verticalScrollBar().maximum())
#         self.ui.isaac_log.verticalScrollBar().setValue(self.ui.isaac_log.verticalScrollBar().maximum())
#
#         self.setWindowIcon(QtGui.QIcon('assets/icon.png'))
#         self.tray.tray_icon.setIcon(self.windowIcon())
#         self.tray.show()
#
#         if self.isaac_log is not None:
#             if not self.isaac_log.isOpen():
#                 self.isaac_log.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
#
#     # Integration Methods #
#     def load_integrations(self, path: str = None):
#         """Loads all integrations in `path`.  Integrations should refer to the
#         integration dataclass for a reference."""
#         failed = 0
#
#         if path is None:
#             path = self.config["client"]["paths"]["integrations"].value
#
#             if not path:
#                 path = "integrations"
#
#         self.logger.info(f"Loading integrations from {path}...")
#         for item in os.listdir(path):
#             if not item.startswith("_") and not item.startswith("."):
#                 item_path = os.path.normpath(os.path.join(path, item))
#                 item_path = ".".join(item_path.split(os.sep))
#                 integration = dataclasses.Integration(item_path)
#
#                 try:
#                     integration.load(self)
#
#                 except utils.errors.MethodMissingError as e:
#                     self.logger.warning(f'Integration "{item_path}" could not be loaded!')
#                     self.logger.warning(str(e))
#                     failed += 1
#
#                 else:
#                     self.integrations.append(integration)
#
#         self.logger.info("Successfully loaded {} integrations!".format(len(self.integrations)))
#
#         if failed:
#             self.logger.warning(f"{failed} integrations could not be loaded!")
#
#     def unload_integrations(self):
#         """Unloads all currently loaded integrations."""
#         self.logger.warning("Unloading {} integrations...".format(len(self.integrations)))
#         failed = 0
#
#         for integration in self.integrations:  # type: dataclasses.Integration
#             try:
#                 integration.unload()
#
#             except ValueError:
#                 failed += 1
#
#         self.logger.warning("Unloading {} integrations!".format(len(self.integrations) - failed))
#         self.integrations.clear()
#
#         if failed:
#             self.logger.warning(f"{failed} integrations failed to unload properly!")
#             self.logger.warning("There may be left over objects!")
#
#     # Bind Methods #
#     def bind(self):
#         """Calls all methods in this class that start with bind_."""
#         self.logger.info("Binding signals to their respective slots...")
#
#         for attr, inst in inspect.getmembers(self):
#             if attr.startswith("bind_") or attr.startswith("_bind_"):
#                 inst()
#
#         self.logger.info("All signals bound to their respective slots!")
#
#     def bind_menubar(self):
#         """Binds all menubar objects to their respective slots."""
#         self.logger.info("Binding menubar actions to their respective slots...")
#
#         self.logger.info("Binding menu_settings.triggered action...")
#         self.ui.menu_settings.triggered.connect(self.config.show)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding menu_quit.triggered action...")
#         self.ui.menu_quit.triggered.connect(self.close)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding help_help.triggered action...")
#         self.ui.help_help.triggered.connect(self.help)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding help_about.triggered action...")
#         self.ui.help_about.triggered.connect(self.about)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding help_license.triggered action...")
#         self.ui.help_license.triggered.connect(self.license)
#         self.logger.info("Bound!")
#
#         self.logger.info("Menubar actions to their respective slots!")
#
#     def bind_tray(self):
#         """Binds all tray actions to their respective slots."""
#         self.logger.info("Binding tray events to their respective slots...")
#
#         self.logger.info("Binding tray.clicked signal...")
#         self.tray.clicked.connect(self.showNormal)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding tray.middle_clicked signal...")
#         self.tray.middle_clicked.connect(self.showNormal)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding tray.double_clicked event...")
#         self.tray.double_clicked.connect(self.showNormal)
#         self.logger.info("Bound!")
#
#         self.logger.info("Tray events bound to their respective slots!")
#         self.logger.info("Binding tray signals to their respective slots...")
#
#         self.logger.info("Binding show_action.triggered signal...")
#         self.show_action.triggered.connect(self.showNormal)
#         self.logger.info("Bound!")
#
#         self.logger.info("Tray signals bound to their respective slots!")
#
#     def bind_http(self):
#         """Binds all http signals to their respective slots."""
#         self.logger.info("Binding HTTP signals to their respective slots...")
#
#         self.logger.info("Binding http.on_response signal...")
#         self.http.on_response.connect(self.data.process_message)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding http.on_connection_received signal...")
#         self.http.on_connection_received.connect(self.data.process_new_connection)
#         self.logger.info("Bound!")
#
#         self.logger.info("Bound all HTTP signals to their respective slots!")
#
#     def bind_attributes(self):
#         """Binds all attribute signals to their respective slots."""
#         self.logger.info("Binding attribute signals to their respective slots...")
#
#         if self.isaac_log is not None:
#             self.logger.info("Binding isaac_timer.timeout signal...")
#             self.isaac_timer.timeout.connect(self.process_isaac_tasks)
#             self.logger.info("Bound!")
#
#         self.logger.info("Bound all attribute signals to their respective slots!")
#
#     def bind_log(self):
#         """Binds all log-related widgets to their respective slots."""
#         self.logger.info("Binding log-related widgets to their respective slots....")
#
#         self.logger.info("Binding client_filter.currentIndexChanged to its respective slot...")
#         self.ui.client_filter.currentIndexChanged.connect(self.adjust_client_log_filter)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding isaac_filter.currentIndexChanged to its respective slot...")
#         self.ui.isaac_filter.currentIndexChanged.connect(self.adjust_isaac_log_filter)
#         self.logger.info("Bound!")
#
#         self.logger.info("Binding isaac_filter_modifier.clicked to its respective slot...")
#         self.ui.isaac_filter_modifier.clicked.connect(self.adjust_isaac_log_filter)
#         self.logger.info("Bound!")
#
#         self.logger.info("Bound all log-related widgets to their respective slots...")
#
#     # Menu Methods #
#     def help(self):
#         """Displays the Decision Descent: Wiki"""
#         self.logger.info("Opening Decision Descent's documentation...")
#         # TODO: Compile a .qch file and display it.  If the file doesn't exist, open the online documentation.
#
#     def about(self):
#         """Displays information about Decision Descent."""
#         self.logger.info("Displaying Decision Descent's metadata...")
#         self.metadata.show()
#         self.logger.info("Metadata successfully displayed!")
#
#     def license(self):
#         """Displays the full license for Decision Descent: Client."""
#         if not os.path.isfile("LICENSE"):
#             self.logger.warning("Decision Descent: Client always ships with its license file.")
#             self.logger.warning("If this package wasn't shipped with one, submit an issue on the Github repository.")
#             self.logger.warning("If this package did not come from SirRandoo's Decision Descent, ask your distributor "
#                                 "to include one.")
#
#         else:
#             file = QtCore.QFile("LICENSE")
#
#             if not file.isOpen():
#                 file.open(file.ReadOnly | file.Text)
#
#             if file.isReadable():
#                 contents = file.readAll().data().decode()
#                 self.display.show_text(contents)
#
#             else:
#                 self.logger.warning("License file could not be opened for reading!")
#                 self.logger.warning("Error code {} : {}".format(file.error(), file.errorString()))
#
#             if file.isOpen():
#                 file.close()
#
#     # Utility Methods #
#     def setup_logger(self, name: str) -> logging.Logger:
#         """Sets up the logger passed."""
#         logger = logging.getLogger(name)
#
#         if logger.hasHandlers():
#             self.logger.warning(f'Logger `{name}` already has handlers attached!')
#
#         self.logger.info(f'Adding handlers to `{name}`...')
#         for handler in self.handlers:
#             if handler not in logger.handlers:
#                 logger.addHandler(handler)
#
#                 if handler.formatter is None:
#                     handler.setFormatter(self.formatter)
#
#         self.logger.info(f'Setting logger level to client\'s level...')
#         logger.setLevel(logging.DEBUG if self.config["isaac"]["debug"]["enabled"].value else logging.INFO)
#
#         return logger
#
#     def mirror_menubar(self):
#         """Changes the tray icon's menu to mimic the application's menubar."""
#         self.logger.warning("Discarding current tray menu...")
#         self.tray.menu.clear()
#         self.logger.info("Discarded!")
#
#         self.logger.info("Mirroring application's menubar...")
#
#         self.logger.info("Inserting show action into tray menu...")
#         self.tray.menu.addAction(self.show_action)
#         self.logger.info("Inserted!")
#
#         for action in self.ui.menu_bar.actions():  # type: QtWidgets.QAction
#             self.logger.info('Inserting action "{}" and its children to tray menu...'.format(action.text()))
#             self.tray.menu.addAction(action)
#
#         self.logger.info("Mirror complete!")
#
#     def setup_metadata(self):
#         """Populates the metadata dialog."""
#         self.metadata.set_project_name(self.NAME)
#         self.metadata.set_project_version(".".join([str(i) for i in self.VERSION]))
#         self.metadata.set_project_authors(*self.AUTHORS)
#         self.metadata.set_project_website("https://github.com/sirrandoo/decision-descent")
#         self.metadata.set_project_docs("https://sirrandoo.github.io/decision-descent")
#         self.metadata.set_project_license(self.LICENSE,
#                                           "https://github.com/sirrandoo/decision-descent/blob/master/LICENSE")
#
#     def find_isaac_log(self) -> typing.Union[QtCore.QFile, None]:
#         """Attempts to find Isaac's log file."""
#         if QtWidgets.qApp.platformName() == "windows":
#             user_directory = os.getenv("USERPROFILE")
#             isaac_directory = os.path.join(user_directory, "Documents\\My Games\\Binding of Isaac Afterbirth+")
#
#             return QtCore.QFile(os.path.join(isaac_directory, "log.txt"), self)
#
#         else:
#             return None
#
#     def adjust_client_log_filter(self):
#         """Adjusts the client log's filter level."""
#         self.logger.debug("Adjusting client log...")
#
#         requested_filter = self.ui.client_filter.currentText().lower()
#         color_filter = requested_filter.upper()
#         filter_check = "[{}]".format(requested_filter.title())
#
#         self.logger.debug("Finding color matrix...")
#         for handler in self.handlers:
#             if isinstance(handler, utils.Log):
#                 self.logger.debug("Found!")
#
#                 self.logger.debug("Enforcing filter on future messages...")
#                 handler.restriction = requested_filter
#                 self.logger.debug("Done!")
#
#                 self.logger.debug("Clearing log...")
#                 self.ui.client_log.clear()
#                 self.logger.debug("Cleared!")
#
#                 self.logger.debug("Repopulating log display...")
#                 log = QtCore.QFile("log.txt")
#
#                 if not log.isOpen():
#                     log.open(log.Text | log.ReadOnly)
#
#                 while not log.atEnd():
#                     data = log.readLine()  # type: QtCore.QByteArray
#
#                     if not data.isEmpty():
#                         data = data.data().decode()
#
#                         if data[len("[HH:MM:SS]"):].startswith(filter_check):
#                             self.ui.client_log.append(f'<span style="color: #{handler.colors[color_filter]}">'
#                                                       f'{data}</span><br/>')
#
#                         elif requested_filter == "all":
#                             for level, color in handler.colors.items():
#                                 if data[len("[HH:MM:SS]"):].startswith(f'[{level.title()}]'):
#                                     self.ui.client_log.append(f'<span style="color: #{color}">{data}</span><br/>')
#
#                     QtWidgets.qApp.processEvents()
#
#                 if log.isOpen():
#                     log.close()
#
#     def adjust_isaac_log_filter(self):
#         """Adjusts Isaac log's filter level."""
#         if self.isaac_log is not None:
#             self.logger.debug("Adjusting Isaac log...")
#
#             requested_filter = self.ui.isaac_filter.currentText().lower()
#             only_companion = self.ui.isaac_filter_modifier.isChecked()
#             filter_check = "[{}]".format(requested_filter.title())
#
#             self.logger.debug("Finding color matrix...")
#             for handler in self.handlers:
#                 if isinstance(handler, utils.Log):
#                     self.logger.debug("Found!")
#
#                     self.logger.debug("Enforcing filter on future messages...")
#                     handler.restriction = requested_filter
#                     self.logger.debug("Done!")
#
#                     self.logger.debug("Clearing log...")
#                     self.ui.isaac_log.clear()
#                     self.logger.debug("Cleared!")
#
#                     self.logger.debug("Repopulating log display...")
#                     log = QtCore.QFile(self.isaac_log.fileName())
#
#                     if not log.isOpen():
#                         log.open(log.Text | log.ReadOnly)
#
#                     while not log.atEnd():
#                         data = log.readLine()  # type: QtCore.QByteArray
#
#                         if not data.isEmpty():
#                             formatted_data, is_mod = utils.format_isaac(data.data().decode())
#
#                             if formatted_data is not None:
#                                 stripped_data = formatted_data[32:len(formatted_data) - 12]
#
#                                 if stripped_data[len("[HH:MM:SS]"):].startswith(filter_check):
#                                     if only_companion and is_mod:
#                                         self.ui.isaac_log.append(formatted_data)
#
#                                     elif not only_companion:
#                                         self.ui.isaac_log.append(formatted_data)
#
#                                 elif requested_filter == "all":
#                                     if only_companion and is_mod:
#                                         self.ui.isaac_log.append(formatted_data)
#
#                                     elif not only_companion:
#                                         self.ui.isaac_log.append(formatted_data)
#
#                         QtWidgets.qApp.processEvents()
#
#                     if log.isOpen():
#                         log.close()
#
#     def load_config(self):
#         """Loads config files into a single dialog."""
#         # noinspection PyTypeChecker
#         config = settings.QSettings()
#         config_file = QtCore.QFile(config.file_name)
#
#         if config_file.exists():
#             if not config_file.isOpen():
#                 config_file.open(QtCore.QFile.ReadOnly)
#
#             if config_file.isReadable():
#                 data = config_file.readAll()  # type: QtCore.QByteArray
#
#                 if not data.isEmpty():
#                     data = data.data().decode()
#
#                     try:
#                         json_data = json.loads(data)
#
#                     except ValueError:
#                         self.logger.warning("Could not read current settings file!")
#                         self.logger.warning("If this problem persists, please open a new issue on "
#                                             "Decision Descent's Github page.")
#
#                     else:
#                         for domain in json_data:
#                             domain_obj = settings.Domain.deserialize(domain, self.converters)
#                             config.add_domain(domain_obj)
#
#                 else:
#                     self.logger.warning("Config file is empty!")
#                     self.logger.warning("If this problem persists, please open a new issue on "
#                                         "Decision Descent's Github page.")
#
#             else:
#                 self.logger.warning("Could not read config file!")
#                 self.logger.warning("Reason: {}".format(config_file.errorString()))
#
#         else:
#             # Client Domain Config
#             client_domain = settings.Domain("client")
#
#             # client.location Section
#             paths = settings.Section("paths")
#             paths.add_option(settings.Option("integrations", "integrations").set_display_name("Integrations Directory"))
#             paths.add_option(settings.Option("configs", "configs").set_display_name("Configs Directory"))
#
#             # client.debug Section
#             debug_section = settings.Section("debug")
#             debug_section.add_option(settings.Option("enabled", False).set_display_name("Is enabled?"))
#
#             # client.extensions Section
#             extension_section = settings.Section("extensions")
#
#             # Add sections to client domain
#             client_domain.add_section(paths)
#             client_domain.add_section(debug_section)
#             client_domain.add_section(extension_section)
#
#             # Descent Domain Config
#             isaac_domain = settings.Domain("isaac")
#
#             # isaac.core Section
#             core_section = settings.Section("core")
#
#             # isaac.core.polls Section
#             polls_section = settings.Section("polls")
#             polls_section.add_option(settings.Option("limit", -1).set_display_name("Poll Limit"))
#             polls_section.add_option(settings.Option("duration", 20).set_display_name("Poll Duration"))
#             polls_section.add_option(settings.Option("maximum_choices", 4).set_display_name("Choice Limit"))
#
#             # Add sub-sections to core section
#             core_section.add_section(polls_section)
#
#             # isaac.debug Section
#             isaac_debug_section = settings.Section("debug")
#             isaac_debug_section.add_option(settings.Option("enabled", False).set_display_name("Is enabled?"))
#
#             # isaac.display Section
#             isaac_display = settings.Section("display")
#
#             # isaac.display.hud Section
#             hud_section = settings.Section("hud").set_display_name("HUD")
#             hud_section.add_option(settings.Option("enabled", False).set_display_name("Is enabled?"))
#
#             # isaac.display.hud.text Section
#             text_section = settings.Section("text")
#             text_section.add_option(settings.Option("width", 0.8).set_display_name("Text Width"))
#             text_section.add_option(settings.Option("height", 0.8).set_display_name("Text Height"))
#             text_section.add_option(settings.Option("color", "FFFFFF").set_display_name("Text Color"))
#
#             # Add sub-section to hud section
#             hud_section.add_section(text_section)
#
#             # Add sub-sections to display section
#             isaac_display.add_section(hud_section)
#
#             # Add sub-sections to isaac section
#             isaac_domain.add_section(core_section)
#             isaac_domain.add_section(isaac_debug_section)
#             isaac_domain.add_section(isaac_display)
#
#             # Add domains to config
#             config.add_domain(client_domain)
#             config.add_domain(isaac_domain)
#
#         return config
#
#     # Slots #
#     def process_isaac_tasks(self):
#         """Processes Isaac-related tasks."""
#         if self.isaac_log is not None:
#             if self.isaac_log.isReadable():
#                 if self.isaac_log_size > self.isaac_log.size():  # Let's assume the log was overwritten
#                     self.isaac_log_size = self.isaac_log.size()
#                     self.ui.isaac_log.clear()
#                     self.isaac_log.seek(0)
#
#                 while not self.isaac_log.atEnd():
#                     data = self.isaac_log.readLine()  # type: QtCore.QByteArray
#
#                     if not data.isEmpty():
#                         data, is_mod = utils.format_isaac(data.data().decode())
#
#                         if data is not None:
#                             if self.ui.isaac_filter_modifier.isChecked() and is_mod:
#                                 self.ui.isaac_log.append(data)
#
#                             elif not self.ui.isaac_filter_modifier.isChecked():
#                                 self.ui.isaac_log.append(data)
#                     QtWidgets.qApp.processEvents()
#
#                 self.isaac_log_size = self.isaac_log.size()
#
#         isaac_window = win32gui.FindWindow(None, "Binding of Isaac: Afterbirth+")
#
#         if isaac_window > 0:
#             window_rect = win32gui.GetWindowRect(isaac_window)
#             window_width = abs(window_rect[0] - window_rect[2])
#             window_height = abs(window_rect[1] - window_rect[3])
#
#             if window_width != self.isaac_size.width():
#                 self.logger.warning("Isaac dimensions differ from our cache!")
#                 self.logger.info("Sending new dimensions to mod...")
#
#                 self.isaac_size = QtCore.QSize(window_width, window_height)
#                 self.http.send_message(utils.dataclasses.Message.from_json(dict(intent="state.dimensions.update",
#                                                                                 args=[window_width, window_height])))
#
#             elif window_height != self.isaac_size.height():
#                 self.logger.warning("Isaac dimensions differ from our cache!")
#                 self.logger.info("Sending new dimensions to mod...")
#
#                 self.isaac_size = QtCore.QSize(window_width, window_height)
#                 self.http.send_message(utils.dataclasses.Message.from_json(dict(intent="state.dimensions.update",
#                                                                                 args=[window_width, window_height])))
#
#     # Qt Events #
#     def closeEvent(self, a0: QtGui.QCloseEvent):
#         """An override to allow the application to have special closing
#         operations.  If the application was not closed via the menu action,
#         the application will simply hide.  If it was, the application will
#         perform closing operations.  To reopen the application, the taskbar
#         icon can be used."""
#         self.logger.warning("Performing closing operations...")
#
#         self.logger.info("Saving configs...")
#         self.config.quit()
#         self.logger.info("Configs saved!")
#
#         if not a0.isAccepted():
#             a0.accept()
