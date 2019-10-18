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
import json
import logging
import typing

from ..logic import errors

__all__ = ['Message']

bases = typing.Union[str, int, float, list, dict]


@dataclasses.dataclass(frozen=True)
class Message:
    """A message from the other half."""
    LOGGER: typing.ClassVar[logging.Logger] = logging.getLogger("extensions.DescentClient.data.messages")
    
    intent: str
    args: typing.Tuple[bases]
    kwargs: typing.Dict[str, bases]
    reply: typing.Optional[str]
    
    @classmethod
    def from_json(cls, message: dict) -> 'Message':
        """Converts a raw decoded message into a Message object."""
        kwargs: typing.Dict[str, bases] = message.pop('kwargs', {})
        
        if not isinstance(kwargs, dict):
            kwargs = {}
        
        return cls(message.pop('intent'), message.get('args', tuple()), kwargs, message.get('reply'))
    
    def to_dict(self) -> dict:
        """Converts a message instance into a dict."""
        return dataclasses.asdict(self)
    
    def __str__(self):
        return json.dumps(dataclasses.asdict(self))
    
    def __call__(self, intents: typing.Dict[str, typing.Callable]):
        """Runs the message's requested intent with the specified arguments."""
        func = intents[self.intent]
        
        if not callable(func):
            self.LOGGER.warning(f'Intent "{self.intent}" is not a callable!')
            raise ValueError
        
        try:
            r = func(self.reply or 'ignore.this.message', *self.args, **self.kwargs)
        
        except Exception as e:
            self.LOGGER.warning(
                f'Intent "{self.intent}" failed with the following errors:  {e.__class__.__name__}({e!s})')
            raise errors.DescentError from e
        
        else:
            self.LOGGER.info(f'Intent "{self.intent}" invoked successfully!')
            return r
    
    def __repr__(self):
        return (f'<{self.__class__.__name__} '
                f'intent="{self.intent}" '
                f'args=[{",".join(self.args)}] '
                f'kwargs={{{json.dumps(self.kwargs)}}} '
                f'reply="{self.reply}">')
