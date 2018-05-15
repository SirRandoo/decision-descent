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
#  File Creation Date: 7/21/2017
import logging
import os

from PyQt5 import QtWidgets

__all__ = {"Log", "DescentFormatter"}


class Log(logging.Handler):
    colors = {
        "INFO": "009900",
        "DEBUG": "F333FF",
        "WARNING": "FF8810",
        "ERROR": "990000",
        "CRITICAL": "FF0000"
    }
    
    def __init__(self, obj: QtWidgets.QTextBrowser):
        super(Log, self).__init__()
        self.log_object = obj  # type: QtWidgets.QTextBrowser
    
    def emit(self, record: logging.LogRecord):
        color_msg = self.format(record)
        
        if self.colors.get(record.levelname.upper()):
            color_msg = '<span style="color: #{}">{}</span><br/>'.format(self.colors.get(record.levelname), color_msg)
        
        if self.log_object is not None:  # type: QtWidgets.QTextBrowser
            try:
                self.log_object.append(color_msg)
            
            except RuntimeError:
                self.log_object = None


class DescentFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        item = super(DescentFormatter, self).format(record)
        
        item = item.replace(f"[{record.levelname}]", f"[{record.levelname.title()}]", 1)
        item = item.replace("[<module>]", "[__main__]", 1)
        
        return item
