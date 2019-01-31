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
from PyQt5 import QtCore, QtWidgets

from QtUtilities.utils import should_create_widget


class About(QtWidgets.QDialog):
    """A small dialog for displaying application information."""
    
    def __init__(self, **kwargs):
        # Super Call #
        super(About, self).__init__(parent=kwargs.get("parent"))
        
        # Ui Declarations #
        self.name: QtWidgets.QLabel = None
        self.display_name: QtWidgets.QLabel = None
        self.version: QtWidgets.QLabel = None
        self.integrations: QtWidgets.QLabel = None
        self.authors: QtWidgets.QLabel = None
        self.website: QtWidgets.QLabel = None
        self.license: QtWidgets.QLabel = None
        self.qt_version: QtWidgets.QLabel = None
        self.pyqt_version: QtWidgets.QLabel = None
        
        # Internal Calls #
        self.setup_ui()
    
    # Ui Methods #
    def setup_ui(self):
        layout = QtWidgets.QFormLayout(self)
        
        if should_create_widget(self.name):
            self.name = QtWidgets.QLabel()
            self.name.setOpenExternalLinks(True)
        
        if should_create_widget(self.display_name):
            self.display_name = QtWidgets.QLabel()
        
        if should_create_widget(self.version):
            self.version = QtWidgets.QLabel()
        
        if should_create_widget(self.integrations):
            self.integrations = QtWidgets.QLabel()
        
        if should_create_widget(self.authors):
            self.authors = QtWidgets.QLabel()
        
        if should_create_widget(self.website):
            self.website = QtWidgets.QLabel()
            self.website.setOpenExternalLinks(True)
        
        if should_create_widget(self.license):
            self.license = QtWidgets.QLabel()
        
        if should_create_widget(self.qt_version):
            self.qt_version = QtWidgets.QLabel(f'<a href="https://www.qt.io">{QtCore.QT_VERSION_STR}</a>')
            self.qt_version.setOpenExternalLinks(True)
        
        if should_create_widget(self.pyqt_version):
            self.pyqt_version = QtWidgets.QLabel(f'<a href="https://pypi.org/project/PyQt5">{QtCore.PYQT_VERSION_STR}'
                                                 f'</a>')
            self.pyqt_version.setOpenExternalLinks(True)
        
        layout.addRow('Name', self.name)
        layout.addRow('Display Name', self.display_name)
        layout.addRow('Version', self.version)
        layout.addRow('Authors', self.authors)
        layout.addRow('License', self.license)
        layout.addRow('Website', self.website)
        layout.addRow('Integrations', self.integrations)
        layout.addRow('Qt Version', self.qt_version)
        layout.addRow('PyQt Version', self.pyqt_version)
        
        layout.setHorizontalSpacing(20)
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        
        self.adjustSize()
        self.setFixedSize(self.size())
