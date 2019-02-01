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
import traceback
import typing
from collections import namedtuple

from PyQt5 import QtCore, QtGui

from . import catchable, dataclasses

__all__ = {"DescentData"}

Poll = namedtuple("Poll", ["instance", "intent"])


class DescentData(QtCore.QObject):
    on_poll_created = QtCore.pyqtSignal(object)

    def __init__(self, client, parent: QtCore.QObject = None):
        # Super Call #
        super(DescentData, self).__init__(parent=parent)
        
        # "Public" Attributes #
        self.logger = logging.getLogger("core.data")
        
        # "Private" Attributes #
        self._timer = QtCore.QTimer(parent=self)
        self._client = client
        self._http = client.http
        self._config = client.config
        self._tear_effects = list()
        self._level_master = None
        self._players = list()  # Plural since Antibirth/True Co-op support is planned
        self._babies = list()
        self._polls = list()  # type: typing.List[Poll]
        self._layout = None
        
        self._intents = {
            "polls": {
                "create": self.polls_create,
                "multi": {
                    "create": self.polls_multi_create
                },
                "delete": self.unregister_poll
            }
        }

        self._timer.timeout.connect(self.unregister_closed_polls)
        self._timer.start(1000)
    
    # Intent Methods #
    def register_intent(self, intent_string: str, intent_callable: typing.Callable):
        """Registers an intent to the internal intent cache."""
        if not self.intent_registered(intent_string):
            intent_segments = intent_string.lower().split(".")
            cursor = self._intents
            
            for segment in intent_segments:
                cursor = cursor[segment] = dict()
            
            cursor = intent_callable
        
        else:
            raise LookupError("Intent is already registered!")
    
    def unregister_intent(self, intent_string: str):
        """Unregisters an intent from the internal cache."""
        if self.intent_registered(intent_string):
            intent_segments = intent_string.lower().split(".")
            cursor = self._intents
            
            for segment in intent_segments[:-1]:
                if segment in cursor:
                    cursor = cursor[segment]
                
                else:
                    raise IndexError("Intent could not be found!")
            
            cursor.pop(intent_segments[-1])
        
        else:
            raise IndexError("Intent could not be found!")
    
    def intent_registered(self, intent_string: str) -> bool:
        """Returns whether or not an intent is registered."""
        intent_segments = intent_string.lower().split(".")
        cursor = self._intents
        
        for segment in intent_segments[:-1]:
            if segment in cursor:
                cursor = cursor[segment]
            
            else:
                return False
        
        return intent_segments[-1] in cursor
    
    def get_intent(self, intent_string: str) -> typing.Callable:
        """Returns the intent's callable if it exists.  If the intent does not
        exist, IndexError will be raised."""
        if self.intent_registered(intent_string):
            intent_segments = intent_string.lower().split(".")
            cursor = self._intents
            
            for segment in intent_segments[:-1]:
                if segment in cursor:
                    cursor = cursor[segment]
                
                else:
                    raise IndexError
            
            if intent_segments[-1] in cursor:
                return cursor[intent_segments[-1]]
            
            else:
                raise IndexError
        
        else:
            raise IndexError

    #
    @catchable.signal
    def polls_create(self, intent: str, *choices: str, **aliases):
        """The callable for intent "polls.create"."""
        tmp_ipoll = self.register_poll(intent, *choices, **aliases)
        tmp_ipoll.start(self._config["isaac"]["core"]["polls"]["duration"].value)
        self.on_poll_created.emit(tmp_ipoll)

    @catchable.signal
    def polls_multi_create(self, intent: str, *choices: str, **aliases):
        """The callable for intent "polls.multi.create"."""
        tmp_impoll = self.register_multi_poll(intent, *choices, **aliases)
        tmp_impoll.start(self._config["isaac"]["core"]["polls"]["duration"].value)
        self.on_poll_created.emit(tmp_impoll)

    @catchable.signal
    def polls_delete(self, identifier_or_alias: str):
        """The callable for intent "polls.delete"."""
        if identifier_or_alias == "*":
            self.logger.warning("Deleting all polls...")
        
            for poll in self._polls.copy():
                poll.instance.stop()
                poll.instance.deleteLater()
        
            self._polls.clear()
    
        else:
            self.logger.warning(f'Deleting poll with choice "{identifier_or_alias}"...')
        
            for index, poll in enumerate(self._polls.copy()):
                if poll.instance.is_choice(identifier_or_alias):
                    poll.instance.stop()
                    poll.instance.deleteLater()
                    del self._polls[index]
                    break
    
    # Poll Methods #
    @catchable.signal
    def register_poll(self, intent: str, *choices: str, **aliases) -> dataclasses.Poll:
        """Registers a poll to the internal poll cache."""
        if aliases is None:
            aliases = dict()
        
        intent = intent.lower()
        choices = [c.lower() for c in choices]
        
        self.logger.info(f'Registering poll to intent "{intent}"...')
        tmp_rpoll = dataclasses.Poll(parent=self)
        
        for choice in choices:
            self.logger.info(f'Registering poll choice "{choice}"...')
            tmp_rpoll.add_choice(choice, *aliases.get(choice, list()))
        
        self._polls.append(Poll(instance=tmp_rpoll, intent=intent))
        tmp_rpoll.concluded.connect(self.process_poll)

        return tmp_rpoll

    @catchable.signal
    def register_multi_poll(self, intent: str, *choices: str, **aliases) -> dataclasses.Poll:
        """Registers a multiple choice poll."""
        tmp_rmpoll = self.register_poll(intent, *choices, **aliases)
        tmp_rmpoll.multiple_choice = True
        
        return tmp_rmpoll
    
    def unregister_poll(self, instance: dataclasses.Poll):
        """Unregisters a poll from the internal poll cache."""
        for index, temp_upoll in enumerate(self._polls):
            if temp_upoll.instance == instance:
                del self._polls[index]
                break
    
    def get_poll(self, identifier_or_alias: str) -> Poll:
        """Returns a poll from the internal poll cache."""
        for temp_gpoll in self._polls.copy():
            if temp_gpoll.instance.is_choice(identifier_or_alias):
                return temp_gpoll
    
    def get_polls(self) -> typing.List[Poll]:
        """Returns all polls this class manages."""
        return self._polls

    @catchable.signal
    def unregister_closed_polls(self):
        """Cleans up spent polls."""
        _before = len(self._polls)
        self._polls = [poll for poll in self._polls if poll.instance.active]
        difference = _before - len(self._polls)
    
        if difference > 0:
            self.logger.info(f'Cleaned up {difference} polls!')
    
    # Slots #
    @catchable.signal
    def process_message(self, message: dataclasses.Message):
        """Processes messages from the Lua half."""
        self.logger.info(f'Invoking callable "{message.intent}"...')
        
        try:
            response = message.invoke(self._intents.copy())
        
        except IndexError or ValueError:
            pass
        
        else:
            if message.reply:
                self.logger.info('Sending response to Isaac...')
                
                if isinstance(response, typing.Iterable):
                    self._http.send_message(dataclasses.Message(message.reply, [i for i in response], dict()))
                
                elif response is not None:
                    self._http.send_message(dataclasses.Message(message.reply, [response], dict()))

    @catchable.signal
    def process_new_connection(self):
        """Invoked when the HTTP listener receives a new connection."""
        self.logger.info("Sending config to Isaac...")

        conf_alias = self._config["isaac"]
        poll_alias = conf_alias["core"]["polls"]
        hud_alias = conf_alias["display"]["hud"]
        hud_text_alias = hud_alias["text"]

        if hud_text_alias["color"].value.startswith("#"):
            color = QtGui.QColor(hud_text_alias["color"].value)

        else:
            color = QtGui.QColor(f'#{hud_text_alias["color"].value}')

        color_r, color_g, color_b, color_a = color.getRgb()
        
        self._http.send_message(dataclasses.Message.from_json(dict(
            intent="state.config.update", args=[dict(
                core=dict(maximum_choices=poll_alias["maximum_choices"].value),
                hud=dict(
                    enabled=hud_alias["enabled"].value,
                    text_color=dict(r=color_r / 255, g=color_g / 255, b=color_b / 255),
                    alpha=color_a,
                    width=hud_text_alias["width"].value,
                    height=hud_text_alias["height"].value),
                debug=dict(enabled=conf_alias["debug"]["enabled"].value))
            ])))

        self._http.send_message(dataclasses.Message.from_json(dict(
            intent="state.dimensions.update", args=[self._client.isaac_size.width(), self._client.isaac_size.height()]
        )))

    @catchable.signal
    def process_poll(self, poll_id: str):
        """Processes signals from polls."""
        poll = self.get_poll(poll_id)
        
        if poll is not None:
            try:
                intent = self.get_intent(poll.intent)

            except:
                self.logger.warning("Could not process poll!")
                self.logger.warning("Reason: Intent is not registered!")
                self.logger.info("Maybe Isaac has this intent?")
                
                try:
                    self._http.send_message(dataclasses.Message(poll.intent, poll_id))

                except:
                    traceback.print_exc()
            
            else:
                try:
                    intent(poll_id)
                
                except BaseException as e:
                    self.logger.warning("Intent invocation failed with error: {}".format(str(e)))
