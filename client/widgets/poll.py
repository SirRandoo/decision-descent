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
import dataclasses
import difflib
import inspect
import logging
import random
import typing

from PyQt5 import QtCore, QtWidgets

from QtUtilities.widgets import QCircleProgressBar

__all__ = ['Poll']


@dataclasses.dataclass()
class Choice:
    display: QtWidgets.QLabel = dataclasses.field(init=False, default_factory=QtWidgets.QLabel)
    id: str
    name: str
    aliases: typing.List[str] = dataclasses.field(default_factory=list)
    
    def __post_init__(self):
        super(Choice, self).__init__()
        
        self.display.setText(f'[#{self.id}] {self.name}')
    
    def fuzzy_match(self, subject: str) -> bool:
        """Attempts to match an string passed to any id, name, or alias
        registered to this choice."""
        return any([i(subject.lower()) for n, i in inspect.getmembers(self)
                    if callable(i) and n.startswith('fuzzy_') and n != 'fuzzy_match'])
    
    def fuzzy_similar(self, subject: str) -> bool:
        """Attempts to match a string to any id, name, or alias registered to
        this choice.

        Method: similarity"""
        return len(difflib.get_close_matches(
            subject, [self.id.lower(), self.name.lower()] + [a.lower() for a in self.aliases], 1, 0.95
        )) > 0

    def fuzzy_case(self, subject: str) -> bool:
        """Attempts to match a string to any id, name, or alias registered
        to this choice."""
        return subject == self.id.lower() \
               or subject == self.name.lower() \
               or any([subject == a.lower() for a in self.aliases])


class Poll(QtWidgets.QWidget):
    """A semi-automated class for declaring chat polls."""
    LOGGER = logging.getLogger('extensions.DescentClient.polls')
    onConclude = QtCore.pyqtSignal(str)
    
    def __init__(self, intent: str, *, parent: QtWidgets.QWidget = None):
        # Super call
        super(Poll, self).__init__(parent=parent)
        
        # Public attributes
        self.intent: str = intent
        
        # Private attributes
        self._timer: QtCore.QTimer = QtCore.QTimer(parent=self)
        self._label: QtWidgets.QLabel = QtWidgets.QLabel(parent=self)
        self._time_indicator: QCircleProgressBar = QCircleProgressBar(parent=self)
        
        self._choices: typing.List[Choice] = []
        self._participants: typing.Dict[str, Choice] = {}
        self._multi: bool = False
        self._current: typing.Optional[int] = None  # Current timer tick
        self._initial: typing.Optional[int] = None  # Initial timer tick
        
        # Internal calls
        self._timer.timeout.connect(self.decrement)
        
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self._time_indicator, 0, 0)
    
    # Properties
    def is_multi(self) -> bool:
        """The poll's multi flag's value."""
        return self._multi
    
    def set_multi(self, value: bool):
        """Updates the poll's multi flag."""
        self._multi = value
    
    def is_active(self) -> bool:
        """Whether or not the poll is currently running."""
        return self._timer.isActive()
    
    # Choice methods
    def add_choice(self, identifier: str, name: str, *aliases: str):
        """Adds a choice to the poll.

        * Note: If the poll's timer is currently ticking, any calls made via
        this method will reset it."""
        for choice in self._choices.copy():
            if choice.id != identifier.lower():
                continue
            
            choice.aliases = [a.lower() for a in aliases]
            return
        
        c = Choice(identifier, name, list(aliases))
        c.display = QtWidgets.QLabel(f'[#{identifier}] {name}')
        
        layout: QtWidgets.QGridLayout = self.layout()
        
        self._choices.append(Choice(identifier, name, list(aliases)))
        layout.addWidget(c.display, layout.rowCount(), 1)

        if self._timer.isActive():
            self.reset()
    
    def remove_choice(self, target: str):
        """Removes a choice from the poll.

        * Note: If a poll's timer is currently ticking, any calls made via
        this method will reset."""
        for choice in self._choices.copy():
            if choice.id.lower() == target.lower() \
                    or any([a == target.lower() for a in choice.aliases]) or choice.name == target.lower():
                try:
                    c = self._choices.pop(self._choices.index(choice))
                    
                    layout: QtWidgets.QGridLayout = self.layout()
                    layout.removeWidget(c.display)
                
                except IndexError:
                    pass  # It's already been removed
                
                finally:
                    return self.reset_timer()
    
    def is_choice(self, target: str) -> bool:
        """Checks whether or not the passed target is currently assigned to any
        choice in this poll."""
        for choice in self._choices.copy():
            if choice.fuzzy_match(target):
                return True
        
        return False
    
    def get_choices(self) -> typing.List[Choice]:
        """Returns a copy of the poll's choices."""
        return self._choices.copy()

    def get_nearest_choice(self, target: str) -> Choice:
        """Attempts to get the closest matching choice from the query given."""
        if target.startswith('#'):
            try:
                index = int(target.lstrip('#'))
    
            except ValueError:
                pass
    
            else:
                if index > len(self._choices) or index < 0:
                    raise ValueError('Index out of range!')
        
                return self._choices[index]
        
        for choice in self._choices.copy():
            if choice.fuzzy_match(target):
                return choice
    
        raise ValueError('No valid choices could be found!')
    
    # Participants methods
    def add_participant(self, name: str, target: typing.Union[Choice, str]):
        """Adds a participant to the poll."""
        name = name.lower()
        
        # If the choice passed was a string, we'll convert it to a PollChoice
        # object.
        #
        # If the choice passed wasn't a valid poll choice, we'll raise a ValueError.
        if isinstance(target, str):
            target = target.lower()
            
            if not self.is_choice(target):
                raise ValueError
            
            for choice in self._choices:
                if choice.id == target or any([a == target for a in choice.aliases]) or choice.name == target:
                    target = choice
                    break
        
        self._participants[name] = target
    
    def remove_participant(self, name: str):
        """Removes a participant from the poll."""
        self._participants.pop(name)
    
    def has_participated(self, name: str) -> bool:
        """Checks whether or not a target has participated in this poll."""
        return name.lower() in self._participants
    
    def get_participants(self) -> typing.List[str]:
        """Returns a copy of the poll's participants."""
        return list(self._participants.keys())
    
    # Timer methods
    def start(self, seconds: int = None):
        """Starts the poll's timer."""
        if seconds is None and self._initial is None:
            self.LOGGER.warning('Cannot start poll without starting time!')
            raise ValueError
        
        if seconds is not None:
            self._initial = seconds
            self._current = seconds
        
        else:
            self._current = self._initial
        
        self._timer.start(1000)
    
    def stop(self):
        """Stops the poll's timer."""
        if self._timer.isActive():
            return self._timer.stop()
        
        self.LOGGER.warning('Poll already stopped!')
    
    def reset(self):
        """Resets the poll's timer."""
        if self._initial is None:
            self.LOGGER.warning('Cannot reset timer!  Starting time is null!')
            raise ValueError
        
        self._current = self._initial
    
    def increment(self):
        """Increments the poll's timer.

        * The poll's timer can never surpass the poll's upper limit."""
        if self._current < self._initial:
            self._current += 1
    
    def decrement(self):
        """Decrements the poll's timer.

        * The poll's timer can never drop below 0."""
        if self._current > 0:
            self._current -= 1
            self._time_indicator.setValue(self._current)
            return
        
        # Stop the poll's timer from running
        self.stop()
        
        self.LOGGER.info('Poll concluded!  Tallying votes...')
        t: typing.Dict[str, int] = {c.id: 0 for c in self._choices}
        
        for participant, choice in self._participants.items():
            if choice.id not in t:
                self.LOGGER.warning("Participant's choice isn't a valid choice!  This shouldn't have happened.")
                continue
            
            t[choice.id] += 1
        
        highest_voted: int = max(t.values(), key=lambda x: int(x))
        winners: typing.List[str] = [c for c, v in t.items() if v == highest_voted]
        
        if self._multi:
            for c in winners:
                self.onConclude.emit(c)
        
        else:
            self.onConclude.emit(random.choice(winners))
        
        # Magic methods
        def __repr__(self):
            return f'<{self.__class__.__name__} is_multi={self._multi} choices=[{",".join([i.id for i in self._choices])}]>'
    
    # Utility methods
    def delete(self):
        """Deletes this poll cleanly."""
        if self._timer.isActive():
            self._timer.stop()
        
        self.deleteLater()
