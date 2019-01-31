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
import random
import typing
from collections import namedtuple

from PyQt5 import QtCore

__all__ = {"Poll"}

PollChoice = namedtuple("PollChoice", ["aliases", "id"])


class Poll(QtCore.QObject):
    """A physical representation of a poll in Decision
    Descent.  This dataclass is designed be automatic."""
    concluded = QtCore.pyqtSignal(str)
    
    def __init__(self, choices: typing.List[PollChoice] = None, parent: QtCore.QObject = None):
        # Super Call#
        super(Poll, self).__init__(parent=parent)
        
        # "Private" Variables #
        self._timer = QtCore.QTimer(parent=self)
        self._initial, self._current = -1, -1
        self._participants = dict()
        self._choices = choices or list()
        self._multiple_choice = False
        
        # Internal Calls #
        self._timer.timeout.connect(self.decrement)
    
    # Properties #
    @property
    def multiple_choice(self):
        """Whether or not the poll is multiple choice.  Multiple choice polls
        emit a concluded signal for every choice in the event of a tie."""
        return self._multiple_choice
    
    @multiple_choice.setter
    def multiple_choice(self, value: bool):
        self._multiple_choice = value
    
    @multiple_choice.deleter
    def multiple_choice(self):
        self._multiple_choice = False

    @property
    def active(self) -> bool:
        """Returns whether or not the poll has concluded."""
        return self._timer.isActive()
    
    # Choice Methods #
    def add_choice(self, identifier: str, *aliases: str):
        """Adds a choice to the poll's internal cache."""
        for index, choice in enumerate(self._choices):
            aliases = [a.lower() for a in aliases if a not in choice.aliases]
            
            if choice.id == identifier:
                _aliases = [a.lower() for a in aliases if a not in choice.aliases]
                self._choices[index] = PollChoice(aliases=_aliases + choice.aliases, id=identifier.lower())
                return
        
        self._choices.append(PollChoice(aliases=aliases, id=identifier.lower()))
        self.reset()
    
    def remove_choice(self, identifier_or_alias: str):
        """Removes a choice to the poll's internal cache."""
        for index, choice in enumerate(self._choices.copy()):
            if choice.id == identifier_or_alias:
                del self._choices[index]
                self.reset_timer()
                return
            
            for alias in choice.aliases:
                if alias == identifier_or_alias:
                    del self._choices[index]
                    self.reset_timer()
                    return
    
    def is_choice(self, identifier_or_alias: str) -> bool:
        """Returns whether or not the choice is already registered."""
        for choice in self._choices.copy():
            if choice.id == identifier_or_alias:
                return True
            
            for alias in choice.aliases:
                if alias == identifier_or_alias:
                    return True
        
        return False
    
    def get_choices(self) -> typing.List[PollChoice]:
        """Returns the poll's internal choice cache."""
        return self._choices.copy()
    
    # Participant Methods #
    def add_participant(self, name: str, choice: typing.Union[PollChoice, str]):
        """Adds a participant to the poll's internal participant cache."""
        name = name.lower()
        
        if isinstance(choice, PollChoice):
            self._participants[name] = choice
        
        elif isinstance(choice, str) and self.is_choice(choice):
            choice = choice.lower()
            
            for c in self._choices.copy():
                if c.id == choice:
                    self._participants[name] = c
                    return
                
                for alias in c.aliases:
                    if alias == choice:
                        self._participants[name] = c
                        return
    
    def remove_participant(self, name: str):
        """Removes a participant from the poll's internal participant cache."""
        name = name.lower()
        
        if self.is_participant(name):
            self._participants.pop(name)
        
        else:
            raise IndexError("Participant not found!")
    
    def is_participant(self, name: str) -> bool:
        """Returns whether or not the participant is registered to the poll's
        internal participant cache."""
        return name.lower() in self._participants
    
    def get_participants(self) -> typing.List[str]:
        """Returns the poll's participants."""
        return list(self._participants.keys())
    
    # Timer Methods #
    def start(self, seconds: int = None):
        """Starts the poll's timer."""
        if seconds is not None:
            self._initial = seconds
            self._current = seconds
            self._timer.start(1000)
        
        elif self._initial > 0:
            self._current = self._initial
            self._timer.start(1000)
        
        else:
            raise ValueError("Timer's seconds have not been set!")
    
    def stop(self):
        """Stops the poll's timer."""
        if self._timer.isActive():
            self._timer.stop()
    
    def reset(self):
        """Resets the poll's timer."""
        if self._initial > 0:
            self._current = self._initial
    
    def increment(self):
        """Adds a second to the poll's timer.  The poll's timer can never
        surpass the poll's starting timer."""
        if self._current < self._initial:
            self._current += 1
    
    def decrement(self):
        """Removes a second from the poll's timer.  When the poll's timer
        reaches 0, the winning choice(s) will be emitted via the concluded
        signal."""
        if self._current > 0:
            self._current -= 1
        
        else:
            choice_tally = {c.id: 0 for c in self._choices.copy()}

            for participant, choice in self._participants.items():
                if choice.id not in choice_tally:
                    choice_tally[choice.id] = 0

                else:
                    choice_tally[choice.id] += 1

            largest_count = max(choice_tally.values(), key=lambda x: int(x))
            if self._multiple_choice:
                for choice, count in choice_tally.items():
                    if count == largest_count:
                        self.concluded.emit(choice)

                self.stop()

            else:
                choices = [choice for choice, votes in choice_tally.items() if votes == largest_count]
    
                self.concluded.emit(random.choice(choices))
                self.stop()
    
    # Magic Methods #
    def __repr__(self):
        return "<{0} multi={1} choices=[{2}]>".format(
            self.__class__.__name__, self._multiple_choice, ", ".join([i.id for i in self._choices.copy()])
        )
