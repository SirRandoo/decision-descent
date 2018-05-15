#  This file is part of Decision Descent: Client.
#
#  Decision Descent: Client is free software: you can 
#  redistribute it and/or modify it under the 
#  terms of the GNU General Public License as 
#  published by the Free Software Foundation, 
#  either version 3 of the License, or (at 
#  your option) any later version.
#
#  Decision Descent: Client is distributed in the hope 
#  that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty 
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License 
#  for more details.
#
#  You should have received a copy of the GNU
#  General Public License along with 
#  Decision Descent: Client.  If not, 
#  see <http://www.gnu.org/licenses/>.
#  
#  Author: RandomShovel
#  File Creation Date: 7/22/2017
import logging

from PyQt5 import QtCore, QtGui, QtWidgets

__all__ = {"TrayIcon"}


class TrayIcon(QtWidgets.QWidget):
    """Represents an icon on the system tray."""
    double_clicked = QtCore.pyqtSignal()
    middle_clicked = QtCore.pyqtSignal()
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        #  Super Call  #
        super(TrayIcon, self).__init__(parent=parent)
        
        #  External Attributes  #
        self.tray = QtWidgets.QSystemTrayIcon(parent=self)
        self.menu = QtWidgets.QMenu(parent=self)
        
        #  Internal Calls  #
        self.tray.setContextMenu(self.menu)
        self.tray.activated.connect(self.on_activation)
    
    def show(self):
        self.tray.show()
        super(TrayIcon, self).show()
    
    def show_message(self, title: str, message: str, icon=None):
        if icon is None:
            icon = QtWidgets.QSystemTrayIcon.Information
        
        else:
            if icon != QtWidgets.QSystemTrayIcon.NoIcon \
                    and icon != QtWidgets.QSystemTrayIcon.Information \
                    and icon != QtWidgets.QSystemTrayIcon.Warning \
                    and icon != QtWidgets.QSystemTrayIcon.Critical \
                    and not isinstance(icon, QtGui.QIcon):
                icon = QtWidgets.QSystemTrayIcon.Information
        
        if self.tray.supportsMessages():
            self.tray.showMessage(title, message, icon)
    
    def on_activation(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.Context:
            self.menu.show()
        
        elif reason == QtWidgets.QSystemTrayIcon.MiddleClick:
            self.middle_clicked.emit()
        
        elif reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.double_clicked.emit()
        
        elif reason == QtWidgets.QSystemTrayIcon.Trigger:
            self.clicked.emit()
    
    def quit(self):
        logging.info("Performing shutdown operations...")
        
        logging.info("Calling deleteLater on tray icon...")
        self.tray.deleteLater()
        logging.info("Called!")
        
        logging.info("Calling deleteLater on context menu...")
        self.menu.deleteLater()
        logging.info("Called!")
        
        logging.info("Shutdown operations complete!")
