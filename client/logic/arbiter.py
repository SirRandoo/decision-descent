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
import typing

from PyQt5 import QtCore

from . import catchable, errors
from .http import HTTP
from .. import dataclasses as dataklasses, widgets as widgetz

if typing.TYPE_CHECKING:
    from widgets import ShovelBot

__all__ = ['Arbiter']


class Arbiter(QtCore.QObject):
    """Synchronizes data between the client and mod."""
    LOGGER = logging.getLogger("extensions.DescentClient.arbiter")
    
    pollCreated = QtCore.pyqtSignal(object)
    
    def __init__(self, client, parent: QtCore.QObject = None):
        # Super call
        super(Arbiter, self).__init__(parent=parent)
        
        # Private attributes
        self._http: HTTP = HTTP(parent=self)
        self._client: 'ShovelBot' = client
        
        self._layout = None
        self._level_master = None
        
        self._babies = []
        self._players = []
        self._tear_effects = []
        self._polls: typing.List[widgetz.Poll] = []
        
        # Intent map
        self._intents = {}
        
        # Internal calls
        self.add_intent('polls.create', self.polls_create)
        self.add_intent('polls.multi.create', self.polls_multi_create)
        self.add_intent('polls.delete', self.polls_delete)

        self._client.aboutToStart.connect(self._http.connect)
        self._client.aboutToStop.connect(self._http.disconnect)
        self._http.onResponse.connect(self.process_message)
    
    def add_intent(self, path: str, func: typing.Callable):
        """Registers an intent.
        
        :param path: A dot separated series of segments used to identify this
                     intent.  For example, the path for creating polls is
                     "polls.create".
        :param func: The callable that should be called when the intent is
                     invoked.  Any arguments the callable takes will be given
                     to the callable as passed from the mod."""
        path = path.lower()
        
        try:
            if path in self._intents:
                raise errors.IntentExistsError
            
            self._intents[path] = catchable.signal(func)
        
        except errors.IntentExistsError:
            self.LOGGER.warning(f'Intent "{path}" was already registered!')
            self.LOGGER.warning(f'Remapping {path} from {self._intents[path]!s} to {func!s}')
            
            self._intents[path] = catchable.signal(func)
    
    def remove_intent(self, path: str):
        """Unregisters an intent.
        
        :param path: A dot separated series of segments used to identify this
                     intent.  For example, the path for creating polls is
                     "polls.create"."""
        path = path.lower()
        
        if path not in self._intents:
            return self.LOGGER.warning(f"Intent \"{path}\" was't registered!")
        
        del self._intents[path]
    
    def get_intent(self, path: str) -> typing.Callable:
        """Gets a registered intent.
        
        :param path: A dot separated series of segments used to identify this
                     intent.  For example, the path for creating polls is
                     "polls.create"."""
        try:
            return self._intents[path]
        
        except KeyError as e:
            raise errors.IntentNotFoundError from e
    
    # Intents
    def polls_create(self, callback: str, *choices: str, **aliases: typing.Dict[str, typing.List[str]]):
        """Requests the arbiter to create a new poll.
        
        :param callback: The intent to invoke when the poll conclude."""
        p = self.add_poll(callback, *choices, **aliases)
        p.start(self._client.settings['extensions']['descentclient']['polls']['duration'].value)
        
        self.pollCreated.emit(p)
    
    def polls_multi_create(self, callback: str, *choices: str, **aliases: typing.Dict[str, typing.List[str]]):
        """Requests the arbiter to create a new multi poll.
        
        :param callback: The intent to invoke when the poll concludes."""
        p = self.add_multi_poll(callback, *choices, **aliases)
        p.start(self._client.settings['extensions']['descentclient']['polls']['duration'].value)
        
        self.pollCreated.emit(p)
    
    def polls_delete(self, target: str):
        if target == '*':
            self.LOGGER.warning('Received a request to delete all polls!')
            
            for poll in self._polls.copy():
                poll.delete()
            
            self._polls.clear()
            return
        
        self.LOGGER.warning(f'Attempting to locate first active poll with identifier "{target}"....')
        
        for poll in self._polls.copy():
            if poll.is_choice(target):
                poll.stop()
                del self._polls[self._polls.index(poll)]
                break
    
    # Poll methods
    def add_poll(self, callback: str, *choices: str, **aliases: typing.Dict[str, typing.List[str]]) -> widgetz.Poll:
        """Registers a poll with the arbiter.
        
        :param callback: The intent to invoke when the poll conclude."""
        callback = callback.lower()
        t = [c.lower() for c in choices]
        
        self.LOGGER.info(f'Received a request to register a new poll!')
        self.LOGGER.info(f'  - Callback > {callback}')
        self.LOGGER.info(f'  - Choices')

        for c in t:
            self.LOGGER.info(f'    - {c}')

        self.LOGGER.info(f'  - Aliases')
        
        for c, a in aliases.items():
            self.LOGGER.info(f'    - {c} > {", ".join(a)}')

        p = widgetz.Poll(callback)

        for c in t:
            p.add_choice(c, c, *aliases.get(c, []))
        
        self._polls.append(p)
        p.onConclude.connect(self.process_poll)
        
        return p
    
    def add_multi_poll(self, callback: str, *choices: str,
                       **aliases: typing.Dict[str, typing.List[str]]) -> widgetz.Poll:
        """Registers a multi poll with the arbiter.
        
        :param callback: The intent to invoke when the poll conclude."""
        p = self.add_poll(callback, *choices, **aliases)
        p.set_multi(True)
        
        return p
    
    def remove_poll(self, poll: widgetz.Poll):
        """Unregisters a poll from the arbiter."""
        del self._polls[self._polls.index(poll)]
    
    def get_poll(self, target: str) -> widgetz.Poll:
        """Gets a poll from the arbiter's poll registry."""
        for p in self._polls.copy():
            if p.is_choice(target):
                return p
    
    def get_polls(self) -> typing.List[widgetz.Poll]:
        """Gets a copy of the arbiter's poll registry."""
        return self._polls.copy()
    
    # Slots
    @catchable.signal
    def process_message(self, message: dataklasses.Message):
        """Processes a message from the mod."""
        self.LOGGER.info(f'Received a message from the mod: {message!s}')
        
        try:
            r = message(self._intents)

        except KeyError:
            self.LOGGER.warning(f'Intent "{message.intent} does not exist!  Ignoring...')
        
        except errors.DescentError as e:
            self.LOGGER.warning(f'Message could not be executed!  ({e.__class__.__name__}({e!s}))')
        
        else:
            if message.reply:
                self.LOGGER.info('Mod requested a reply post-execution!')
                
                if isinstance(r, typing.Iterable):
                    self._http.send_message(dataklasses.Message(message.reply, [i for i in r], {}))
                
                elif r is not None:
                    self._http.send_message(dataklasses.Message(message.reply, [r], {}))
    
    @catchable.signal
    def process_new_connection(self):
        """Invoked when the HTTP listener receives a new connection."""
        self.LOGGER.info('Received a new client!')
        c = {}
        
        self.LOGGER.info('Sending current config to Isaac...')
        alias = self._client.settings['extensions']['descentclient']
        
        c['http'] = {'host': '127.0.0.1', 'port': alias['http']['port'].value}
        c['hud'] = {'enabled': alias['hud']['enabled'].value}
        c['polls'] = {
            'choices': {
                'maximum': alias['polls']['choices']['maximum']
            },
            
            'duration': alias['polls']['duration']
        }
        
        self._http.send_message(dataklasses.Message.from_json({
            'intent': 'state.config.update',
            'args': [c]
        }))
    
    @catchable.signal
    def process_poll(self, id_: str):
        """Processes signals from polls."""
        p = self.get_poll(id_)
        
        if p is None:
            return self.LOGGER.warning(f"Received process request from poll id {id_}, but that poll doesnt exist!")
        
        try:
            i = self.get_intent(p.intent)

        except KeyError:
            self.LOGGER.info('Passing intent to mod...')
            self._http.send_message(dataklasses.Message(p.intent, (id_,), {}, None))
        
        except errors.DescentError as e:
            self.LOGGER.warning(f"Arbiter couldn't process poll {id_}.  {e.__class__.__name__}({e!s})")
        
        else:
            self.LOGGER.info(f'Passing poll results to {p.intent}...')
            
            try:
                i(id_)
            
            except errors.DescentError as e:
                self.LOGGER.warning(f"Arbiter couldn't execute intent {p.intent}!  {e.__class__.__name__}({e!s})")
