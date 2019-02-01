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

from PyQt5 import QtWidgets

import QtTwitch
from QtUtilities import settings
from .configs import token


class Twitch(QtWidgets.QDialog):
    """Represents the Twitch extension for Decision Descent: Client"""
    __slots__ = ("_quitting", "config", "ui")
    
    def __init__(self, parent=None, client=None):
        """Sets attributes for `Twitch`."""
        #  Super call  #
        super(Twitch, self).__init__(parent=parent)
        
        # Public Attributes #
        self.logger = logging.getLogger("extensions.twitch")
        
        #  Internal attributes  #
        self._quitting = False
        self._client = client
        self._config = client.config  # type: settings.QSettings
        self._client_data = client.data

        self._twitch = QtTwitch.Client()
        
        # Internal Calls #
        self._twitch.on_raw_message.connect(self.process_message)
        self._client_data.on_poll_created.connect(self.process_new_poll)

        self.register_config()

    # Config Methods #
    def register_config(self):
        """Registers Twitch-specific settings to the config dialog."""
        # Declarations
        extensions = self._config["client"]["extensions"]  # type: settings.Section
    
        try:
            extensions["twitch"]
    
        except KeyError:
            twitch = settings.Section("twitch")
        
            # Population
            t = settings.Option("token", "foobar")
            t.set_manager(token.TokenOption.new)
        
            twitch.add_option(settings.Option("username", "justinfan123"))
            twitch.add_option(t)
            twitch.add_option(settings.Option("channel", "justinfan123"))
        
            # Add section to sub-section
            extensions.add_section(twitch)
    
        else:
            extensions["twitch"]["token"].set_manager(token.TokenOption.new)
    
        finally:
            self._config.repopulate()
    
    # Slots #
    def process_new_poll(self, poll):
        choice_segments = []
        message = "Pick an item! "
        
        for choice in poll.get_choices():
            if choice.aliases:
                # Let's assume this is an item poll...
                # because that's the only poll we're spewing right now..
                choice_segments.append("{} ({})".format(choice.aliases[0], choice.id))
            
            else:
                choice_segments.append(str(choice.id))
        
        message += " | ".join(choice_segments)
        
        if not message.endswith("Pick an item! "):
            try:
                self._twitch._irc_connection.send_message(message)
            
            except:
                traceback.print_exc()
    
    def process_message(self, message: QtTwitch.dataclasses.QMessage):
        polls = self._client_data.get_polls()
        
        for poll in polls.copy():
            poll_choices = poll.instance.get_choices()
            
            for choice in poll_choices:
                if message.content.lower().startswith(choice.id):
                    poll.instance.add_participant(message.author, choice.id)
                
                else:
                    for alias in choice.aliases:
                        if message.content.lower().startswith(alias):
                            poll.instance.add_participant(message.author, choice.id)

        self.logger.info(f"[Twitch] {message.author}: {message.content}")
