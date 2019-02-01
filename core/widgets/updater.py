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
# TODO: Possibly parse markdown into html
import logging
import os
import shutil
import sys
import traceback
import typing
import zipfile
from collections import namedtuple

from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

from QtUtilities import requests, signals
from QtUtilities.utils import should_create_widget

__all__ = ['Updater', 'ReleaseData']

ReleaseData = namedtuple('ReleaseData', ['zip', 'changelog'])


class ZipWorker(QtCore.QObject):
    """A class for unpacking zip files without blocking the main Qt thread."""
    
    def __init__(self, zip_location: str = None):
        super(ZipWorker, self).__init__()
        
        # "Private" Attributes #
        self._zip = zip_location
    
    # Getters #
    def zip(self) -> str:
        """The current zip file."""
        return self._zip
    
    # Setters #
    def set_zip(self, file: str):
        """Sets the current zip file."""
        self._zip = file
    
    def unpack(self):
        """Unpacks a zip file in a QThread."""
        directory, _ = os.path.splitext(self._zip)
        
        try:
            with zipfile.ZipFile(self._zip) as INFILE:
                INFILE.extractall(path=directory)
        
        except ValueError as e:
            Updater.logger.warning('Could not unzip file!')
            Updater.logger.warning(f'Reason: {e.__class__.__name__}: {e.__context__}')
        
        except zipfile.BadZipFile as e:
            Updater.logger.warning('Could not unzip file!')
            Updater.logger.warning(f'Reason: {e.__class__.__name__}: {e.__context__}')
        
        finally:
            return self.thread().quit()


# noinspection PyArgumentList,PyProtectedMember
class Updater(QtWidgets.QDialog):
    """Displays a changelog for the specified update, and gives the
    user an option to download the update now or later."""
    logger = logging.getLogger('core.updater')

    def __init__(self, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Updater, self).__init__(parent=parent)
        
        # "Private" Attributes #
        self._update_action: QtWidgets.QAction = None
        self._update_now: QtWidgets.QPushButton = None
        self._update_list: QtWidgets.QListWidget = None
        self._button_container: QtWidgets.QWidget = None
        self._update_later: QtWidgets.QPushButton = None
        self._container: QtWidgets.QStackedWidget = None
        self._default_changelog: QtWidgets.QTextBrowser = None
        self._changelog_container: QtWidgets.QStackedWidget = None

        # "Internal" Attributes #
        self._releases: typing.Dict[str, typing.Dict] = {}
        self._io_thread: QtCore.QThread = None
        
        # Internal Calls
        self.prep_display()

    # Release Methods #
    def add_release(self, identifier: str, data: ReleaseData):
        """Adds a release to the updater queue."""
        if identifier.lower() in self._releases:
            raise KeyError(f'{identifier} is already added!')
        
        else:
            self._releases[identifier.lower()] = {'data': data}
    
        item: QtWidgets.QListWidgetItem = QtWidgets.QListWidgetItem(identifier)
        item.setData(QtCore.Qt.ItemIsUserCheckable, 1)
        item.setCheckState(QtCore.Qt.Checked)
    
        self._update_list.addItem(item)
    
        if data.changelog:
            changelog = QtWidgets.QTextBrowser()
            changelog.setText(data.changelog)
        
            self._changelog_container.addWidget(changelog)
            self._releases[identifier.lower()]['changelog'] = changelog
        
        else:
            self._releases[identifier.lower()]['changelog'] = self._default_changelog
    
        self._releases[identifier.lower()]['item'] = item
        self.adjust_list_width()

    def remove_release(self, identifier: str):
        """Removes a release from the updater queue."""
        if identifier.lower() not in self._releases:
            raise KeyError(f'{identifier} was not previously added!')
    
        release = self._releases[identifier.lower()]
    
        self._update_list.removeItemWidget(release['item'])
    
        if release['changelog'] != self._default_changelog:
            self._changelog_container.removeWidget(release['changelog'])
            release['changelog'].deleteLater()
    
        del release
        del self._releases[identifier.lower()]
    
        self.adjust_list_width()

    def has_pending_releases(self) -> bool:
        """Whether or not there are releases pending."""
        return len(self._releases) > 0
    
    # Display Methods #
    def prep_display(self):
        """Preps the display."""
        if should_create_widget(self._update_action):
            self._update_action = QtWidgets.QAction('Update')
            self._update_action.triggered.connect(self.show)

        if should_create_widget(self._update_list):
            self._update_list = QtWidgets.QListWidget()
            self._update_list.setWordWrap(True)
            self._update_list.setMaximumWidth(100)
            self._update_list.setAcceptDrops(False)
            self._update_list.setUniformItemSizes(True)
            self._update_list.setDropIndicatorShown(False)
            self._update_list.setFrameShadow(QtWidgets.QFrame.Plain)
            self._update_list.setViewMode(QtWidgets.QListWidget.ListMode)
            self._update_list.setFrameShape(QtWidgets.QListWidget.NoFrame)
            self._update_list.setEditTriggers(QtWidgets.QListWidget.NoEditTriggers)
    
            self._update_list.currentItemChanged.connect(self.user_watcher)

        if should_create_widget(self._default_changelog):
            self._default_changelog = QtWidgets.QTextBrowser()
            self._default_changelog.setText('No changelog provided!')
        
        if should_create_widget(self._button_container):
            self._button_container = QtWidgets.QWidget()

            b_layout = QtWidgets.QHBoxLayout(self._button_container)
            b_layout.addStretch()

            if should_create_widget(self._update_now):
                self._update_now = QtWidgets.QPushButton('Update Now')
                self._update_now.clicked.connect(self.initialize_update)

            if should_create_widget(self._update_later):
                self._update_later = QtWidgets.QPushButton('Update Later')
                self._update_later.clicked.connect(self.postpone_update)

            b_layout.addWidget(self._update_now, 0)
            b_layout.addWidget(self._update_later, 0)
            b_layout.setContentsMargins(0, 0, 0, 0)

        if should_create_widget(self._changelog_container):
            self._changelog_container = QtWidgets.QStackedWidget()
            self._changelog_container.addWidget(self._default_changelog)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self._update_list, 0, 0)
        layout.addWidget(self._changelog_container, 0, 1)
        layout.addWidget(self._button_container, 1, 1)
        
        self.setModal(True)
        self.adjustSize()

    # Update Methods #
    def initialize_update(self):
        """Starts the update sequence."""
        # Modify ui
        self._button_container.hide()
        self._changelog_container.hide()
        self._update_list.setMaximumWidth(850128)
    
        # Declarations
        app = QtWidgets.QApplication.instance()
        stash = QtCore.QDir()
    
        cli = getattr(app, 'client', None)
        nam = getattr(app, 'network_access_manager', None)
    
        manager = nam() if nam is not None else QtNetwork.QNetworkAccessManager()
        factory = getattr(cli(), '_request_factory') if cli is not None else requests.Factory(manager=manager)
        assets = getattr(cli(), 'ASSETS') if cli is not None else QtCore.QDir('resources/assets')
    
        context = {
            'assets': {
                'failed': QtGui.QIcon(assets.filePath('red-x.png')),
                'pending': QtGui.QIcon(assets.filePath('hour-glass.png')),
                'written': QtGui.QIcon(assets.filePath('stone-chest.png')),
                'writing': QtGui.QIcon(assets.filePath('parchment-and-quill.png')),
                'succeeded': QtGui.QIcon(assets.filePath('green-check-mark.png')),
                'installing': QtGui.QIcon(assets.filePath('stone-chest-open.png')),
                'downloading': QtGui.QIcon(assets.filePath('blue-down-arrow.png'))
            },
        
            'stash': stash,
            'factory': factory,
            'core': [app.applicationName(), app.applicationDisplayName()]
        }
    
        # Prep download folder
        if not stash.exists('.download'):
            stash.mkdir('.download')
    
        stash.cd('.download')
    
        # Purge list
        for identifier in list(self._releases.keys()):
            if self._releases[identifier]['item'].checkState() == QtCore.Qt.Unchecked:
                self._update_list.takeItem(self._update_list.row(self._releases[identifier]['item']))
            
                if self._releases[identifier]['changelog'] != self._default_changelog:
                    self._changelog_container.removeWidget(self._releases[identifier]['changelog'])
                    self._releases[identifier]['changelog'].deleteLater()
            
                del self._releases[identifier]
        
            else:
                self._releases[identifier]['item'].setCheckState(QtCore.Qt.Unchecked)
                self._releases[identifier]['item'].setData(QtCore.Qt.CheckStateRole, None)
                self._releases[identifier]['item'].setIcon(context['assets']['pending'])
    
        # Installation sequences
        try:
            self.download_releases(context)
    
        except Exception as e:  # TODO: Replace broad exception capture
            self.logger.warning('A fatal error prevented the updater from continuing!')
            self.logger.warning(f'Reason: {e.__class__.__name__}: {e.__context__}')
        
            traceback.print_exc()
            return
    
        try:
            self.install_releases(context)
    
        except Exception as e:  # TODO: Replace broad exception capture
            self.logger.warning('A fatal error prevented the updater from continuing!')
            self.logger.warning(f'Reason: {e.__class__.__name__}: {e.__context__}')
        
            traceback.print_exc()
            return
    
        if stash.removeRecursively():
            self.logger.debug('Update directory successfully removed!')
    
        self.hide()
    
        message = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.NoIcon,
            'Restart Required',
            'Your chosen updates were installed!\n\nWould you like to restart the application?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
    
        if message.exec() == QtWidgets.QMessageBox.Yes:
            if cli is not None:
                cli().close()
        
            os.execv(f'{sys.executable}', ['core'] + sys.argv)

    def postpone_update(self):
        """Postpones the update."""
        app = QtWidgets.QApplication.instance()
        client = getattr(app, 'client', None)
    
        if client is not None:
            cli = client()
            cli.menuBar().addAction(self._update_action)
        
            self.hide()

    def download_releases(self, context: dict):
        """Downloads all the releases the user has accepted."""
        for identifier, data in self._releases.copy().items():
            # Get the list item
            item: QtWidgets.QListWidgetItem = data['item']
        
            # Update the item to reflect the release's current state
            item.setIcon(context['assets']['downloading'])
            item.setText(f'(Downloading) {identifier}')
        
            self.logger.debug(f'Downloading release from {data["data"].zip} ...')
            response = context['factory'].get(data['data'].zip)
        
            # Validate the response
            if not response.is_ok():
                item.setIcon(context['assets']['failed'])
                item.setText(f'(Download Failed) {identifier}')
                item.setToolTip(f'Reason: {response.error_string()}')
                continue
        
            # Open the file
            item.setIcon(context['assets']['writing'])
            item.setText(f'(Writing) {identifier}')
        
            file = QtCore.QFile(context['stash'].filePath(f'{identifier}.zip'))
        
            # Truly open the file
            if not file.isOpen():
                file.open(file.WriteOnly | file.Truncate)
        
            # Validate the file
            if not file.isWritable():
                item.setIcon(context['assets']['failed'])
                item.setText(f'(Write Failed) {identifier}')
            
                item.setToolTip(f'Reason: {response.error_string()}')
                continue
        
            # Write to file
            response._content.seek(0)
            length = response._content.seek(os.SEEK_END)
            current = 0
            response._content.seek(0)
        
            while True:
                content = response._content.read(1024)
            
                if content:
                    current += file.write(content)
                    item.setToolTip('{}%'.format(round(current / length, 2)))
            
                else:
                    break
        
            # Close the file
            item.setIcon(context['assets']['written'])
            item.setText(f'(Written) {identifier}')
        
            if file.isOpen():
                file.flush()
                file.close()

    def install_releases(self, context: dict):
        """Installs all releases in the stash directory."""
        thread = QtCore.QThread()
        worker = ZipWorker()
    
        worker.moveToThread(thread)
        thread.started.connect(worker.unpack)
    
        for identifier, data in self._releases.copy().items():
            # Get the list item
            item: QtWidgets.QListWidgetItem = data['item']
            file_path: str = context['stash'].filePath(f'{identifier}.zip')
        
            # Update the item to reflect the release's current state
            item.setIcon(context['assets']['pending'])
            item.setText(f'(Unpacking) {identifier}')
            item.setToolTip('')
        
            # Unpack the zip
            self.logger.debug(f'Unpacking release from {file_path} ...')
            worker.set_zip(file_path)
            QtCore.QTimer.singleShot(1, thread.start)
        
            # Wait for the thread to finish
            signals.wait_for_signal(thread.finished)
        
            # Validate the result
            if not context['stash'].exists(identifier):
                item.setIcon(context['assets']['failed'])
                item.setText(f'(Unpack Failed) {identifier}')
                continue
        
            item.setIcon(context['assets']['installing'])
            item.setText(f'(Unpacked) {identifier}')
        
            # Install release
            item.setText(f'(Installing) {identifier}')
        
            # TODO: Work on cleaning up files that may not exist in the next release
            destination = os.getcwd() if identifier in context['core'] else 'extensions'
        
            for directory, subdirectories, files in os.walk(context['stash'].filePath(identifier)):
                # Validate the directory tree
                for subdir in subdirectories:
                    dir_path = os.path.join(directory, subdir)
                    dest_path = os.path.join(destination,
                                             os.path.relpath(dir_path, context['stash'].filePath(identifier)))
                
                    if not os.path.exists(dest_path):
                        os.mkdir(dest_path)
            
                # Validate the files
                for file in files:
                    f_path = os.path.join(directory, file)
                    d_path = os.path.join(destination, os.path.relpath(f_path, context['stash'].filePath(identifier)))
                
                    if os.path.exists(d_path):
                        os.unlink(d_path)
                
                    shutil.copy(f_path, d_path)
        
            item.setText(f'(Installed) {identifier}')
            item.setIcon(context['assets']['succeeded'])

    # Signals
    def user_watcher(self):
        """Invoked when the user clicks a release."""
        item: QtWidgets.QListWidgetItem = self._update_list.currentItem()
    
        if item:
            self._changelog_container.setCurrentWidget(self._releases[item.text().lower()]['changelog'])

    def adjust_list_width(self):
        """Invoked when a new item gets added through this class."""
        max_text = ''
        min_text = 'abcdefghijklmnopqrstuvwxyz'
    
        # Get longest identifier
        for identifier in list(self._releases.keys()):
            if len(identifier) > len(max_text):
                max_text = identifier
        
            elif len(identifier) < len(min_text):
                min_text = identifier
    
        # Measure the Qt width
        metrics: QtGui.QFontMetrics = self.fontMetrics()
        max_width = metrics.width(max_text)
        min_width = metrics.width(min_text)
    
        self._update_list.setMinimumWidth(min_width)
        self._update_list.setMaximumWidth(max_width)


if __name__ == '__main__':
    a = QtWidgets.QApplication([])
    a.setStyle('fusion')
    
    a.setApplicationName('decision-descent')
    a.setApplicationDisplayName('Decision Descent')
    
    u = Updater()
    u.show()
    
    a.exec()
