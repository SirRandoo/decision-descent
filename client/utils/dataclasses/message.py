# This file is part of Decision Descent: Client.
#
# Decision Descent: Client is free software: you can
# redistribute it and/or modify it under the
# terms of the GNU General Public License as
# published by the Free Software Foundation,
# either version 3 of the License, or (at
# your option) any later version.
#
# Decision Descent: Client is distributed in the hope
# that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU
# General Public License along with
# Decision Descent: Client.  If not,
# see <http://www.gnu.org/licenses/>.
#
# Author: RandomShovel
# File Date: 11/25/2017
import json
import logging
import traceback
import typing

__all__ = {"Message"}


class Message:
    """A "physical" representation of a message to and from the client's
    other half.  Compatibility between the two halves should look to this
    class for a rough reference."""
    
    def __init__(self, intent: str, *args, **kwargs):
        self._intent = intent
        self._args = args
        self._kwargs = kwargs
        self._reply = None
        self._logger = logging.getLogger("client.http.messages")
    
    def invoke(self, registered_intents: dict) -> object:
        """Invokes the message's invoke method with the specified arguments."""
        intent_segments = self.intent.split(".")
        cursor = registered_intents  # type: typing.Callable or dict
        
        while intent_segments:
            segment = intent_segments.pop(0)
            
            if segment.lower() not in cursor:
                self._logger.warning(f'Intent "{self.intent}" could not be found!')
                raise IndexError
            
            else:
                cursor = cursor.get(segment.lower(), dict())
        
        if callable(cursor):
            try:
                response = cursor(self.reply or "ignore.this.message", *list(self.args), **self.kwargs)
            
            except Exception as e:
                self._logger.warning(f'Intent "{self.intent}" failed with the following errors:')
                self._logger.warning(str(e))
                raise ValueError from e
            
            else:
                self._logger.info(f'Intent "{self.intent}" invoked successfully!')
                return response
        
        else:
            self._logger.warning(f'Intent "{self.intent}" could not be found!')
    
    @property
    def intent(self) -> str:
        """The intent string.  An intent string is a period separated string of
        words pointing to a callable on the other side.  When the callable is
        invoked, any arguments specified is passed to it."""
        return self._intent
    
    @property
    def args(self) -> list:
        return list(self._args)
    
    @property
    def kwargs(self) -> dict:
        return self._kwargs
    
    @property
    def reply(self) -> str:
        return self._reply
    
    @reply.setter
    def reply(self, value: str):
        self._reply = value
    
    @reply.deleter
    def reply(self):
        self._reply = None
    
    # Conversions
    @classmethod
    def from_json(cls, message: dict) -> 'Message':
        """Converts a raw decoded message to a Message object."""
        kwargs = message.pop("kwargs")
        
        if not isinstance(kwargs, dict):
            kwargs = dict()
        
        returnable = cls(message.pop("intent"), *message.pop("args"), **kwargs)
        returnable.reply = message.get("reply")
        
        return returnable
    
    def to_dict(self) -> dict:
        """Converts a Response object to a JSON response."""
        return dict(sender=0, intent=self.intent, args=self.args, kwargs=self.kwargs, reply=self.reply)
    
    # Magic Methods #
    def __repr__(self):
        return '<{} intent="{}" args=[{}] kwargs={} reply={}>'.format(
            self.__class__.__name__, self.intent, ",".join(self.args),
            json.dumps(self.kwargs), self.reply
        )
