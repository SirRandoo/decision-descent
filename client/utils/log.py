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
import datetime
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


def format_isaac(input_text: str) -> str:
    log_format = "[{time}][{level}][{name}][{function}] {message}"
    input_text = input_text.strip()
    
    if not input_text.startswith("["):
        _temp = log_format.format(
            time=datetime.datetime.now().strftime("%H:%M:%S"),
            level="INFO",
            name="isaac",
            function="core",
            message=input_text.strip()
        )
        return f'<span style="color: #{Log.colors["INFO"]}">{_temp}</span><br/>'
    
    else:
        if input_text.startswith("[INFO] - ERR"):
            input_text = input_text.replace("[INFO] - ERR: ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="WARNING",
                name="isaac",
                function="api",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["WARNING"]}">{_temp}</span><br/>'
        
        elif input_text.startswith("[INFO] - There was an error running the lua file:"):
            input_text = input_text.replace("[INFO] - ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="WARNING",
                name="isaac",
                function="api",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["WARNING"]}">{_temp}</span><br/>'
        
        elif input_text.startswith("[INFO] - Lua Debug: ["):
            input_text = input_text.replace("[INFO] - Lua Debug: ", "", 1)
            
            for level, color in Log.colors.items():
                if input_text.startswith(f"[{level}]"):
                    input_text = "[{}]{}".format(
                        datetime.datetime.now().strftime("%H:%M:%S"),
                        input_text.strip()
                    )
                    
                    return f'<span style="color: #{color}">{input_text}</span><br/>'
        
        elif input_text.startswith("[INFO] - Lua Debug: "):
            input_text = input_text.replace("[INFO] - Lua Debug: ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="DEBUG",
                name="isaac",
                function="LuaDebug",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["DEBUG"]}">{_temp}</span><br/>'
        
        elif input_text.startswith("[INFO]"):
            input_text = input_text.replace("[INFO] - ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="INFO",
                name="isaac",
                function="core",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["INFO"]}">{_temp}</span><br/>'
