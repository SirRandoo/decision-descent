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

from .uis import InfoUi
from PyQt5 import QtWidgets, QtCore, QtGui

__all__ = {"Info"}


class Info(QtWidgets.QDialog):
    """Represents an information dialog for Decision
    Descent: Client.  This is considered a two-in-one
    dialog, but only one display can be enabled at
    a time should you use the built-in methods."""
    __slots__ = ("_shutting_down", "_text_display", "_web_display", "ui", "_decline", "_accept")
    
    accepted = QtCore.pyqtSignal()
    declined = QtCore.pyqtSignal()
    
    logger = logging.getLogger("client.info")
    
    def __init__(self, parent=None):
        # Super Call #
        super(Info, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.ui = InfoUi()
        self.ui.setupUi(self)
        
        self.display = self.ui.text_display  # type: QtWidgets.QTextBrowser
        
        # "Private" Attributes #
        self._shutting_down = False
        
        # Internal Calls #
        self.ui.confirmation_yes.clicked.connect(self.accepted.emit)
        self.ui.confirmation_yes.clicked.connect(self.close)
        self.ui.confirmation_no.clicked.connect(self.declined.emit)
        self.ui.confirmation_no.clicked.connect(self.close)
    
    def show_text(self, text: str, *, as_html: bool = False):
        """Displays the given text.  If `as_html` is true, the text will be
        treated as HTML instead of raw text."""
        if as_html:
            self.display.setHtml(text)
        
        else:
            self.display.setText(text)
        
        self.show()
    
    def show_buttons(self, *, positive: str = None, negative: str = None):
        """Displays the dialog's button set.  If the current page isn't set to
        the button page, the contents will be transferred."""
        if self.ui.pages.currentIndex() != self.ui.pages.indexOf(self.ui.confirmation_page):
            self.ui.pages.setCurrentIndex(self.ui.pages.indexOf(self.ui.confirmation_display))
        
        if self.ui.text_page.isAncestorOf(self.display):
            self.ui.confirmation_display.setHtml(self.ui.text_display.toHtml())
            self.ui.text_display.clear()
            self.display = self.ui.confirmation_display
        
        self.ui.confirmation_yes.setHidden(bool(positive))
        self.ui.confirmation_no.setHidden(bool(negative))
        
        if positive:
            self.ui.confirmation_yes.setText(str(positive))
        
        if negative:
            self.ui.confirmation_no.setText(str(negative))
        
        if not positive and not negative:
            self.ui.pages.setCurrentIndex(self.ui.pages.indexOf(self.ui.text_page))
            self.ui.text_display.setHtml(self.ui.confirmation_display.toHtml())
            self.ui.confirmation_display.clear()
            self.display = self.ui.text_display
            
            self.ui.confirmation_yes.setHidden(False)
            self.ui.confirmation_no.setHidden(False)
            
            self.ui.confirmation_yes.setText("OK")
            self.ui.confirmation_no.setText("Cancel")
        
        if not self.isVisible():
            self.show()
    
    def quit(self):
        """A wrapper method for `close`.  This method
        sets the internal flag `_quitting` to true so
        Qt can garbage collect it."""
        self.logger.info("Performing shutdown operations...")
        self._shutting_down = True
        self.logger.info("Shutdown operations complete!")
    
    #  Qt Slots  #
    
    def closeEvent(self, event: QtGui.QCloseEvent):
        if self._shutting_down:
            event.accept()
        
        else:
            self.declined.emit()
            event.ignore()
            self.hide()
            self.display.clear()
    
    # Events #
    def wheelEvent(self, event: QtGui.QWheelEvent):
        """An override to handle zooming in."""
        is_forward = event.angleDelta().y() > 0
        control_pressed = QtCore.Qt.ControlModifier == event.modifiers()
        
        if control_pressed:
            value = 0.1
        
        else:
            value = 0
        
        if is_forward:
            self.display.setFontPointSize(self.display.fontPointSize() + value)
        
        else:
            self.display.setFontPointSize(self.display.fontPointSize() - value)
        
        if control_pressed:
            event.accept()
