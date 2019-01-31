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
# TODO: If the user chooses to download the update later, insert a QAction into the menubar.
# TODO: Possibly parse markdown into html
import logging

from PyQt5 import QtCore, QtWidgets

from QtUtilities import requests
from QtUtilities.utils import should_create_widget
from QtUtilities.widgets import progress


# noinspection PyArgumentList
class Update(QtWidgets.QDialog):
    """Displays a changelog for the specified update, and gives the
    user an option to download the update now or later."""
    logger = logging.getLogger('core.updater')
    
    def __init__(self, release_data: dict, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Update, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.changelog: QtWidgets.QTextBrowser = None
        self.update_now: QtWidgets.QPushButton = None
        self.update_later: QtWidgets.QPushButton = None
        
        # "Private" Attributes #
        self._update_action: QtWidgets.QAction = None
        self._progress_widget: progress.ProgressWidget = None
        self._stacked: QtWidgets.QStackedWidget = None
        self._surrogate: QtWidgets.QWidget = None
        self._button_container: QtWidgets.QWidget = None
        self._data = release_data
    
    # Display Methods #
    def prep_display(self):
        """Preps the display."""
        if should_create_widget(self.changelog):
            self.changelog = QtWidgets.QTextBrowser()
            self.changelog.setTabStopWidth(40)
            self.changelog.setPlaceholderText('No changelog provided!')
            self.changelog.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
            self.changelog.setText(self._data.get('body'))
        
        if should_create_widget(self.update_now):
            self.update_now = QtWidgets.QPushButton('Update Now')
            self.update_now.clicked.connect(self.initialize_update)
        
        if should_create_widget(self.update_later):
            self.update_later = QtWidgets.QPushButton('Update Later')
            self.update_later.clicked.connect(self.postpone_update)
        
        if should_create_widget(self._progress_widget):
            self._progress_widget = progress.ProgressWidget()
            self._progress_widget.set_range(0, 0)
        
        if should_create_widget(self._button_container):
            self._button_container = QtWidgets.QWidget()
            
            button_layout = QtWidgets.QHBoxLayout(self._button_container)
            button_layout.addStretch()
            button_layout.addWidget(self.update_now)
            button_layout.addWidget(self.update_later)
        
        if should_create_widget(self._surrogate):
            self._surrogate = QtWidgets.QWidget()
            
            layout = QtWidgets.QVBoxLayout(self._surrogate)
            layout.addWidget(self.changelog)
            layout.addWidget(self._button_container)
        
        if should_create_widget(self._stacked):
            self._stacked = QtWidgets.QStackedWidget()
            self._stacked.setContentsMargins(0, 0, 0, 0)
            
            layout = QtWidgets.QGridLayout(self)
            layout.addWidget(self._stacked)
            
            self._stacked.addWidget(self._surrogate)
            self._stacked.addWidget(self._progress_widget)
            
            self._stacked.setCurrentWidget(self._surrogate)
    
    # Update Methods #
    def initialize_update(self):
        """Starts the update sequence."""
        self.setModal(True)
        self._stacked.setCurrentWidget(self._progress_widget)
        self.adjustSize()
        
        # noinspection PyArgumentList
        app = QtWidgets.QApplication.instance()
        client = app.client()
        self._progress_widget.set_display_text(f'Downloading {app.applicationName()} {self._data["tag_name"]}')
        factory = getattr(client, '_request_factory', requests.Factory(manager=app.network_access_manager()))
        
        response = factory.get(self._data['zipball_url'])
        
        if response.is_ok():
            file = QtCore.QFile(f'{app.applicationName()}-{self._data["tag_name"]}.zip')
            
            if not file.isOpen():
                file.open(file.WriteOnly)
            
            if file.isWritable():
                self._progress_widget.set_display_text('Writing contents to file...')
                self.logger.info('Writing data to file...')
                file.write(response.raw())
                
                if file.isOpen():
                    file.close()
                
                self._progress_widget.set_display_text('Unpacking...')
            
            else:
                self.logger.warning('Could not write to disk!')
                self.logger.warning(f'Reason: {file.errorString()}')
        
        else:
            self.logger.warning('Could not fetch latest release!')
            self.logger.warning(f'Reason: {response.error_string()}')
            self.logger.warning(f'If this problem persists, you can manually download the latest release @ '
                                f'{self._data["html_url"]}')
