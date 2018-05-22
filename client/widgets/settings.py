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
import json
import logging
import os
import typing

from PyQt5 import QtWidgets, QtCore
import sys
from .uis import SettingsUi

__all__ = {"Settings"}


class Settings(QtWidgets.QDialog):
    """A dynamically generated settings dialog."""
    
    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Settings, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.logger = logging.getLogger("client.settings")
        
        # "Private" Attributes #
        self._ui = SettingsUi()
        
        self._conf = dict()
        self._pages = list()  # type: typing.List[typing.Tuple[QtWidgets.QTreeWidgetItem, QtWidgets.QWidget]]
        
        # Internal Calls #
        self._ui.setupUi(self)
        self._ui.overview.currentItemChanged.connect(self.adjust_page)
    
    # Page Methods #
    def create_page(self, header: str, parent: QtWidgets.QTreeWidgetItem = None) -> \
            typing.Tuple[QtWidgets.QTreeWidgetItem, QtWidgets.QWidget]:
        """Creates a new page.  If `parent` is specified, the page will be
        a sub-section of the parent."""
        if parent is None:
            parent = self._ui.overview
        
        obj = QtWidgets.QTreeWidgetItem(parent=parent)
        obj_page = QtWidgets.QWidget(parent=self._ui.settings_area)
        
        obj.setText(0, header)
        
        if isinstance(parent, QtWidgets.QTreeWidgetItem):
            parent.addChild(obj)
        
        self._ui.settings_area.addWidget(obj_page)
        return obj, obj_page
    
    def delete_page(self, identifier: typing.Union[QtWidgets.QTreeWidgetItem, QtWidgets.QWidget]):
        """Deletes a page from the settings dialog.  `identifier` should be
        the QTreeWidgetItem or the QWidget associated with the aforementioned
        QTreeWidgetItem."""
        if isinstance(identifier, QtWidgets.QTreeWidgetItem):
            self._ui.overview.removeItemWidget(identifier, 0)
            
            for index, tree_item, widget in enumerate(self._pages.copy()):
                if tree_item == identifier:
                    self._ui.settings_area.removeWidget(widget)
                    del self._pages[index]
                    break
        
        elif isinstance(identifier, QtWidgets.QWidget):
            self._ui.settings_area.removeWidget(identifier)
            
            for index, tree_item, widget in enumerate(self._pages.copy()):
                if widget == identifier:
                    self._ui.overview.removeItemWidget(tree_item)
                    del self._pages[index]
                    break
    
    def adjust_page(self):
        """Changes the page to align with the selected QTreeWidgetItem."""
        current_item = self._ui.overview.currentItem()
        
        for item, page in self._pages.copy():
            if item == current_item:
                self._ui.settings_area.setCurrentWidget(page)
                break
    
    # File System Methods #
    def load(self, file: str = None):
        """Loads a settings file."""
        if file is None:
            file = "settings.json"
        
        qfile = QtCore.QFile(file, parent=self)
        qfile.open(qfile.ReadOnly | qfile.Text)
        
        if qfile.exists() and qfile.isReadable():
            data = qfile.readAll()
            
            if not data.isEmpty():
                data = data.data().decode()
                
                try:
                    data = json.loads(data)
                
                except ValueError:
                    raise IOError("Settings file is malformed!")
                
                else:
                    self._conf = data
                
                finally:
                    if qfile.isOpen():
                        qfile.close()
        
        else:
            raise FileNotFoundError(qfile.errorString())
    
    def save(self, file: str = None):
        """Saves the current settings to a file."""
        if file is None:
            file = "settings.json"
        
        qfile = QtCore.QFile(file, parent=self)
        qfile.open(qfile.WriteOnly | qfile.Text | qfile.Truncate)
        
        if qfile.isWritable():
            try:
                data = json.dumps(self._conf)
            
            except TypeError:
                raise IOError("Settings file contains invalid data types!")
            
            else:
                qfile.write(data)
            
            finally:
                if qfile.isOpen():
                    qfile.close()
        
        else:
            raise IOError(qfile.errorString())
    
    # Conversion Methods #
    def visualize(self, settings: typing.Mapping = None, parent: QtWidgets.QTreeWidgetItem = None,
                  parent_widget: QtWidgets.QWidget = None):
        """Converts values from a dict to a QWidget on the tree."""
        if settings is None:
            settings = self._conf.copy()
        
        for key, value in settings.items():  # type: str, object
            if isinstance(value, typing.Mapping):
                if parent is None:
                    _parent, _parent_widget = self.create_page(key.title(), parent=self._ui.overview)
                
                else:
                    _parent, _parent_widget = self.create_page(key.title(), parent=parent)
                
                _parent_widget.setLayout(QtWidgets.QFormLayout())
                self._pages.append((_parent, _parent_widget))
                self.visualize(value, parent=_parent, parent_widget=_parent_widget)
            
            else:
                try:
                    _obj = self.convert(value)
                    _obj_label = QtWidgets.QLabel(parent=parent_widget)
                    _obj_label.setText(key.capitalize())
                
                except KeyError:
                    self.logger.warning('Value "{}" cannot be converted!'.format(type(value)))
                
                else:
                    _obj_label.setParent(parent_widget)
                    _obj.setParent(parent_widget)
                    _obj.layout().addRow(_obj_label, _obj)
    
    def convert(self, value: object) -> QtWidgets.QWidget:
        """Converts a Python value into a QWidget representation."""
        if isinstance(value, bool):
            obj = QtWidgets.QCheckBox(parent=self)  # General ownership
            obj.setChecked(value)
            
            return obj
        
        elif isinstance(value, str):
            obj = QtWidgets.QLineEdit(parent=self)  # General ownership
            obj.setText(value)
            
            return obj
        
        elif isinstance(value, float):
            obj = QtWidgets.QDoubleSpinBox(parent=self)  # You get the idea, right?
            obj.setMinimum(-sys.maxsize)
            obj.setMaximum(sys.maxsize)
            obj.setValue(value)
            
            return obj
        
        elif isinstance(value, int):
            obj = QtWidgets.QSpinBox(parent=self)  # You get the idea, right?
            obj.setMinimum(-sys.maxsize)
            obj.setMaximum(sys.maxsize)
            obj.setValue(value)
            
            return obj
        
        else:
            raise TypeError
    
    def iterable_to_radio(self, *values: str) -> typing.Tuple[QtWidgets.QWidget, typing.List[QtWidgets.QRadioButton]]:
        """Converts an iterable to a set of radio buttons.  The containing
        widget is returned, along with the list of radio buttons."""
        obj = QtWidgets.QWidget(parent=self)
        obj_layout = QtWidgets.QVBoxLayout(parent=obj)
        obj.setLayout(obj_layout)
        objs = []
        
        for value in values:
            _obj = QtWidgets.QRadioButton(parent=obj)
            _obj.setText(str(value))
            obj_layout.addChildWidget(_obj)
            
            objs.append(_obj)
        
        return obj, objs
