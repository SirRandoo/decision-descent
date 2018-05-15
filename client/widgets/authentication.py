#  This file is part of Decision Descent Client - Python.
#
#  Decision Descent Client - Python is free software: you can
#  redistribute it and/or modify it under the 
#  terms of the GNU General Public License as 
#  published by the Free Software Foundation, 
#  either version 3 of the License, or (at 
#  your option) any later version.
#
#  Decision Descent Client - Python is distributed in the hope
#  that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty 
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License 
#  for more details.
#
#  You should have received a copy of the GNU
#  General Public License along with 
#  Decision Descent Client - Python.  If not,
#  see <http://www.gnu.org/licenses/>.
#  
#  Author: RandomShovel
#  File Creation Date: 7/17/2017
import logging

from .uis import AuthUi
from PyQt5 import QtWidgets, QtCore, QtGui

__all__ = {"AuthScreen"}


class AuthScreen(QtWidgets.QDialog):
    """Represents an authentication screen for
    Decision Descent: Client."""
    __slots__ = ("ui",)
    
    def __init__(self, parent=None):
        """Assigns attributes to `AuthScreen`.
        :param parent: The QObject to create a
        parent-child relationship to."""
        #  Super call  #
        super(AuthScreen, self).__init__(parent=parent)
        
        #  Internal attributes  #
        self._quitting = False
        
        #  External attributes  #
        self.ui = AuthUi()
        self.ui.setupUi(self)
    
    #  Methods  #
    def load(self, url: QtCore.QUrl):
        """Opens the dialog to the specified `url`."""
        self.ui.View.load(url)
        self.show()
    
    #  Slots  #
    def quit(self):
        logging.warning("Performing shutdown operations...")
        self._quitting = True
        logging.warning("Shutdown operations complete!")
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        """Overrides the base close event to ensure
        this dialog doesn't get garbage collected.
        If the internal flag `_quitting` is set to
        true, the dialog will allow itself to be
        garbage collected.  If it isn't, the dialog
        will ignore the event and hide so it's
        inaccessible."""
        if self._quitting:
            event.accept()
        
        else:
            event.ignore()
            self.hide()
