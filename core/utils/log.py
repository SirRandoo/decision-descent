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
import datetime
import logging
import typing

from PyQt5 import QtCore, QtWidgets

__all__ = {'Log', 'DescentFormatter', 'format_isaac', 'qmessage_handler'}


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
        self.restriction = "all"
    
    def emit(self, record: logging.LogRecord):
        color_msg = self.format(record)
        level_name = record.levelname.upper()

        if level_name in self.colors:
            color_msg = f'<span style="color: #{self.colors[level_name]}">{color_msg}</span><br/>'
        
        if self.log_object is not None:  # type: QtWidgets.QTextBrowser
            if record.levelname.lower() == self.restriction or self.restriction.lower() == "all":
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


def format_isaac(input_text: str) -> typing.Tuple[typing.Union[None, str], bool]:
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
        return f'<span style="color: #{Log.colors["INFO"]}">{_temp}</span><br/>', False
    
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
            return f'<span style="color: #{Log.colors["WARNING"]}">{_temp}</span><br/>', False
        
        elif input_text.startswith("[INFO] - There was an error running the lua file:"):
            input_text = input_text.replace("[INFO] - ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="WARNING",
                name="isaac",
                function="api",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["WARNING"]}">{_temp}</span><br/>', False
        
        elif input_text.startswith("[INFO] - Lua Debug: ["):
            input_text = input_text.replace("[INFO] - Lua Debug: ", "", 1)
            
            for level, color in Log.colors.items():
                if input_text.startswith(f"[{level}]"):
                    input_text = "[{}]{}".format(
                        datetime.datetime.now().strftime("%H:%M:%S"),
                        input_text.strip()
                    )

                    return f'<span style="color: #{color}">{input_text}</span><br/>', True
        
        elif input_text.startswith("[INFO] - Lua Debug: "):
            input_text = input_text.replace("[INFO] - Lua Debug: ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="DEBUG",
                name="isaac",
                function="LuaDebug",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["DEBUG"]}">{_temp}</span><br/>', False
        
        elif input_text.startswith("[INFO]"):
            input_text = input_text.replace("[INFO] - ", "", 1)
            _temp = log_format.format(
                time=datetime.datetime.now().strftime("%H:%M:%S"),
                level="INFO",
                name="isaac",
                function="core",
                message=input_text.strip()
            )
            return f'<span style="color: #{Log.colors["INFO"]}">{_temp}</span><br/>', False

        else:
            return None, False


def qmessage_handler(message_type: int, context: QtCore.QMessageLogContext, message: str):
    """A custom message handler for Qt."""
    logger = logging.getLogger('core.qt')
    
    if message_type == QtCore.QtDebugMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.DEBUG,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
    
    elif message_type == QtCore.QtCriticalMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.CRITICAL,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
    
    elif message_type == QtCore.QtWarningMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.WARNING,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
    
    elif message_type == QtCore.QtInfoMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.INFO,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
    
    elif message_type == QtCore.QtFatalMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.FATAL,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
    
    elif message_type == QtCore.QtSystemMsg:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.INFO,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
