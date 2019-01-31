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
import inspect
import logging
import typing

from PyQt5 import QtGui, QtWidgets


class Isaac:
    """A class for stripping a part Isaac's log file into a suitable form."""
    
    def __init__(self, qtextbrowser: QtWidgets.QTextBrowser, **kwargs):
        # "Private" Attributes #
        self._qtextbrowser: qtextbrowser
        
        self._debug = QtGui.QColor(kwargs.get("debug_color", "#f333ff"))
        self._info = QtGui.QColor(kwargs.get("info_color", "#009900"))
        self._warning = QtGui.QColor(kwargs.get("warning_color", "#ff8810"))
        self._error = QtGui.QColor(kwargs.get("error_color", self._warning.darker(kwargs.get("error_factor", 150))))
        self._critical = QtGui.QColor(kwargs.get("critical_color",
                                                 self._error.darker(kwargs.get("critical_factor", 150))))
        
        self._qtextbrowser = qtextbrowser
        self._restriction = logging.INFO
        self._mod_only = False
    
    # Properties #
    def colors(self):
        """Returns all levels that will be colored."""
        return {n.replace("_color", ""): i for n, i in inspect.getmembers(self)}
    
    @property
    def debug_color(self) -> QtGui.QColor:
        """The color DEBUG level messages will be displayed in."""
        return self._debug
    
    @debug_color.setter
    def debug_color(self, value: typing.Union[str, QtGui.QColor]):
        self._debug = QtGui.QColor(value)
    
    @property
    def info_color(self) -> QtGui.QColor:
        """The color INFO level messages will be displayed in."""
        return self._info
    
    @info_color.setter
    def info_color(self, value: typing.Union[str, QtGui.QColor]):
        self._info = QtGui.QColor(value)
    
    @property
    def warning_color(self) -> QtGui.QColor:
        """The color WARNING level messages will displayed in."""
        return self._warning
    
    @warning_color.setter
    def warning_color(self, value: typing.Union[str, QtGui.QColor]):
        self._warning = QtGui.QColor(value)
    
    @property
    def error_color(self) -> QtGui.QColor:
        """The color ERROR level messages will be displayed in."""
        return self._error
    
    @error_color.setter
    def error_color(self, value: typing.Union[str, QtGui.QColor]):
        self._error = QtGui.QColor(value)
    
    @property
    def critical_color(self) -> QtGui.QColor:
        """The color CRITICAL level messages will be displayed in."""
        return self._critical
    
    @critical_color.setter
    def critical_color(self, value: typing.Union[str, QtGui.QColor]):
        self._critical = QtGui.QColor(value)
    
    @property
    def mod_only(self) -> bool:
        """Whether or not the object will only display messages originating
        from the Afterbirth+ mod."""
        return self._mod_only
    
    @mod_only.setter
    def mod_only(self, value: bool):
        self._mod_only = value
