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
# TODO: Find Linux and MacOS's Afterbirth+ log file
import logging

from PyQt5 import QtCore, QtWidgets


class Isaac(QtCore.QObject):
    """Reads and processes the Isaac log file."""
    logger: logging.Logger = logging.getLogger("core.ext.isaac")
    
    def __init__(self, **kwargs):
        # Super Call #
        super(Isaac, self).__init__(parent=kwargs.get("parent"))
        
        # "Private" Attributes #
        self._log_object: QtWidgets.QTextBrowser = kwargs.get("log_object")
        self._log: QtCore.QUrl = kwargs.get("log_location", self.locate_log())
        self._file: QtCore.QFile = None
        
        if self._log is not None:
            self._file: QtCore.QFile = QtCore.QFile(self._log)
    
    # Getters #
    def get_log_object(self) -> QtWidgets.QTextBrowser:
        """The log object new data from the log file will be displayed on."""
        return self._log_object
    
    # Setters #
    def set_log_object(self, obj: QtWidgets.QTextBrowser):
        """Sets the new log object."""
        self._log_object = obj
    
    # Utility Methods #
    def locate_log(self):
        """Locates Isaac's log file."""
        app: QtWidgets.QApplication = QtCore.QCoreApplication.instance()
        
        if app is not None:
            current_path = QtCore.QDir.home()
            
            if app.platformName().lower() == "windows":
                current_path.cd("Documents")
                
                if current_path.exists("My Games"):
                    current_path.cd("My Games")
                    
                    if current_path.exists("Binding of Isaac Afterbirth+"):
                        current_path.cd("Binding of Isaac Afterbirth+")
                        
                        return QtCore.QUrl(current_path.filePath("log.txt"))
                    
                    else:
                        self._logger.warning("Afterbirth+ folder does not exist!")
                        self._logger.warning("Creating folder in {}...".format(current_path.path()))
                        
                        self._logger.warning("Decision Descent does not work on versions prior to Afterbirth+!")
                        self._logger.warning("If you do not own Afterbirth+, you will need to purchase it "
                                             "to use this mod.")
                        
                        current_path.mkdir("Binding of Isaac Afterbirth+")
                        return QtCore.QUrl(current_path.filePath("log.txt"))
                
                else:
                    self._logger.fatal("Documents\\My Games\\ does not exist!")
        
        else:
            self._logger.warning("QApplication instance does not exist!")
