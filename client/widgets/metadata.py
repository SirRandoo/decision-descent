# This file is part of Decision Descent: Client.
#
# Decision Descent: Client is free software:
# you can redistribute it and/or
# modify it under the terms of the 
# GNU General Public License as 
# published by the Free Software 
# Foundation, either version 3 of 
# the License, or (at your option) 
# any later version.
#
# Decision Descent: Client is 
# distributed in the hope that it 
# will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied 
# warranty of MERCHANTABILITY or 
# FITNESS FOR A PARTICULAR PURPOSE.  
# See the GNU General Public License 
# for more details.
#
# You should have received a copy of
# the GNU General Public License along 
# with Decision Descent: Client.  
# If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtWidgets, QtGui

from .uis import MetadataUi


class MetadataDialog(QtWidgets.QDialog):
    """A simple dialog for displaying metadata about Decision Descent."""
    
    def __init__(self, **kwargs):
        # Super Call #
        super(MetadataDialog, self).__init__(parent=kwargs.get("parent"))
        
        # "Private" Attributes #
        self._ui = MetadataUi()
        self._ui.setupUi(self)
        self._shutting_down = False
        
        # Assignments #
        if "name" in kwargs:
            self.setProjectName(kwargs.pop("name"))
        
        if "version" in kwargs:
            self.setProjectVersion(kwargs.pop("version"))
        
        if "license" in kwargs:
            self.setProjectLicense(kwargs.pop("license"), kwargs.pop("license_url", None))
        
        if "authors" in kwargs:
            self.setProjectAuthors(*kwargs.pop("authors"))
        
        if "website" in kwargs:
            self.setProjectWebsite(kwargs.pop("website"))
        
        if "docs" in kwargs:
            self.setProjectDocs(kwargs.pop("docs"))
    
    def setProjectName(self, name: str) -> 'MetadataDialog':
        """Sets the name of the project.  This is displayed in the "name" row."""
        self._ui.name.setText(name)
        
        return self
    
    def setProjectVersion(self, version: str) -> 'MetadataDialog':
        """Sets the version of the project.  This is displayed in the "version" row."""
        self._ui.version.setText(version)
        
        return self
    
    def setProjectLicense(self, license_: str, license_url: str = None) -> 'MetadataDialog':
        """Sets the license of the project.  This is displayed in the "license" row."""
        if license_url is not None:
            self._ui.license.setText(f'<a href="{license_url}">{license_}</a>')
        
        else:
            self._ui.license.setText(license_)
        
        return self
    
    def setProjectAuthors(self, *authors: str) -> 'MetadataDialog':
        """Sets the authors of the project.  This is displayed in the
        "created by" row."""
        self._ui.created_by.setText("; ".join([str(a) for a in authors]))
        
        return self
    
    def setProjectWebsite(self, website: str) -> 'MetadataDialog':
        """Sets the project's website.  This is displayed in the "website" row."""
        self._ui.website.setText(f'<a href="{website}">{website}</a>')
        
        return self
    
    def setProjectDocs(self, docs: str) -> 'MetadataDialog':
        """Sets the project's documentation website.  This is displayed
        in the "docs" row."""
        self._ui.docs.setText(f'<a href="{docs}">{docs}</a>')
        
        return self
    
    def quit(self):
        """Called when the client should shutdown."""
        self._shutting_down = True
        self.close()
    
    def showEvent(self, a0: QtGui.QShowEvent):
        self.adjustSize()
        a0.accept()
    
    def closeEvent(self, a0: QtGui.QCloseEvent):
        if self._shutting_down:
            a0.accept()
        
        else:
            a0.ignore()
            self.hide()