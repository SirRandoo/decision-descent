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
import logging

from PyQt5 import QtCore

from .client import Handler
from .isaac import Isaac

__all__ = ['Handler', 'Isaac', 'qmessage_handler']


def qmessage_handler(message_type: int, context: QtCore.QMessageLogContext, message: str):
    """A custom message handler for Qt."""
    logger = logging.getLogger('core')
    
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
    
    else:
        record = logger.makeRecord(
            name='Qt5',
            level=logging.NOTSET,
            fn=getattr(context, 'function', 'undefined'),
            lno=getattr(context, 'line', -1),
            msg=message,
            args={},
            exc_info=None
        )
        
        logger.handle(record)
