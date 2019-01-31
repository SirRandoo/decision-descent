# This file is part of Decision Descent.
#
# Decision Descent is free software:
# you can redistribute it and/or
# modify it under the terms of the
# GNU General Public License as
# published by the Free Software
# Foundation, either version 3 of
# the License, or (at your option)
# any later version.
#
# Decision Descent is
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
# with Decision Descent.
# If not, see <http://www.gnu.org/licenses/>.
import typing
from collections import namedtuple

from PyQt5 import QtWidgets

from QtUtilities.widgets import QCircleProgressBar

__all__ = {"Poll"}

Choice = namedtuple("Choice", ["display", "choice"])


# noinspection PyTypeChecker
class Poll(QtWidgets.QWidget):
    """A widget for displaying active polls."""
    
    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Poll, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.indicator = QCircleProgressBar(parent=self)
        self.choices = list()  # type: typing.List[Choice]
        self.label = QtWidgets.QLabel(parent=self)
    
    # Poll Methods #
    def increment_choice(self, choice_id: str):
        """Increments `choice_id`'s choice by one."""
        for choice in self.choices:
            if choice.choice.id == choice_id:
                pass
