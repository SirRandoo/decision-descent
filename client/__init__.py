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
import typing

__all__ = ['DescentClient']

from PyQt5 import QtCore
from . import logic, widgets as descent_widgets, dataclasses as descent_dataclasses
from core import utils
from QtUtilities import settings as qsettings


class DescentClient(utils.dataclasses.Extension):
    DISPLAY_NAME = 'Decision Descent'
    VERSION = QtCore.QVersionNumber(1, 0, 0)
    WEBSITE = QtCore.QUrl('https://github.com/sirrandoo/decision-descent')
    DOCUMENTATION = QtCore.QUrl('https://github.com/sirrandoo/decision-descent/wiki')
    AUTHORS = {'SirRandoo'}

    # noinspection PyProtectedMember
    def __post_init__(self, parent: QtCore.QObject = None):
        # Super call
        super(DescentClient, self).__post_init__(parent=parent)
        
        # Internal attributes
        self._arbiter = logic.Arbiter(self.bot, parent=self)
        
        # Internal calls
        self._arbiter.pollCreated.connect(self.broadcast)
        self.bot.aboutToStart.connect(self._arbiter._http.connect)
        self.bot.aboutToStop.connect(self._arbiter._http.disconnect)
    
    # Settings methods
    def register_settings(self):
        """Registers Decision Descent specific settings to the settings dialog."""
        self.LOGGER.debug(f'Checking existence of {self.DISPLAY_NAME} settings...')
        
        if self.NAME not in self.bot.settings['extensions']:
            self.LOGGER.warning(f'{self.DISPLAY_NAME} settings do not exist!  Generating defaults...')
            
            self.LOGGER.debug(f'Creating {self.NAME} setting category...')
            t = qsettings.Setting(self.NAME,
                                  display_name=self.DISPLAY_NAME,
                                  tooltip='Settings related to the Decision Descent extension.')
            
            t.add_children(*self.generate_settings())
            
            self.LOGGER.debug(f'Adding {self.DISPLAY_NAME} setting category to extension category...')
            self.bot.settings['extensions'].add_child(t)
        
        else:
            self.LOGGER.warning(f'{self.DISPLAY_NAME} settings exist!  Validating settings...')
            self.validate_settings()
        
        self.stitch_settings()
    
    def stitch_settings(self):
        """Stitches the settings' signals to their respective slots."""
    
    def validate_settings(self):
        """Validates the extension's settings."""
    
    @staticmethod
    def generate_settings() -> typing.List[qsettings.Setting]:
        """Generates a default list of settings for the Decision Descent extension."""
        # Declarations
        top = {
            'rng': qsettings.Setting('rng', display_name='RNG',
                                     tooltip='Settings related to the RNG aspect of the mod.'),
            'polls': qsettings.Setting('polls', tooltip='Settings related to the poll aspect of the mod.'),
            'hud': qsettings.Setting('hud', tooltip='Settings related to the HUD of the mod.')
        }
        
        # rng.rooms
        top['rng'].add_child(
            qsettings.Setting('rooms', tooltip='Settings related to the room RNG aspect of the mod.'),
            qsettings.Setting('items', tooltip='Settings related to the item RNG aspect of the mod.')
        )
        
        # polls.choices
        top['polls'].add_children(
            qsettings.Setting('choices', tooltip='Settings related to poll choices.'),
            qsettings.Setting('duration', 35, tooltip='The number of seconds polls should run before being concluded.'),
            qsettings.Setting('chat', True, display_name='Output to chat',
                              tooltip='Whether or not new polls will be posted in chat.')
        )
        
        # polls.choices settings
        top['polls']['choices'].add_children(
            qsettings.Setting('maximum', 3,
                              tooltip='The maximum number of choices that can be in a given poll.  '
                                      'Polls are permitted to exceed this limit if special choices '
                                      'are present, but standard choices will adhere to this setting.')
        )
        
        # hud settings
        top['hud'].add_children(
            qsettings.Setting('enabled', True,
                              tooltip='Whether or not the HUD is enabled.\n\n'
                                      'The hud is a "small" overlay that displays information about the mod.')
        )
        
        # Return values
        return list(top.values())
    
    # Platform methods
    def broadcast(self, poll: descent_widgets.Poll):
        """Broadcasts a new poll to all available platforms."""
        if self.bot.settings['extensions']['descentisaac']['polls']['chat'].value:
            for ext in self.bot.extensions:
                if isinstance(ext, utils.dataclasses.Platform):
                    for choice in poll.get_choices():
                        ext.send_message(f'[#{choice.id}] {choice.name}')
    
    # Lifecycle methods
    def setup(self):
        """Sets up Decision Descent."""
        self.LOGGER.info(f'Setting up {self.DISPLAY_NAME}...')
        
        self.LOGGER.info('Registering settings...')
        self.register_settings()
        
        self.LOGGER.info('Stitching settings...')
        self.stitch_settings()
        
        self.LOGGER.info('Setting up bindings...')
        
        self.LOGGER.debug('Binding ShovelBot.aboutToStart » HTTP.connect')
        self.bot.aboutToStart.connect(self._http.connect)
        
        self.LOGGER.debug('Binding ShovelBot.aboutToStop » HTTP.disconnect')
        self.bot.aboutToStop.connect(self._http.disconnect)
        
        self.set_state(utils.enums.ExtensionStates.SET_UP)
        self.LOGGER.info(f'{self.DISPLAY_NAME} successfully set up!')
    
    def teardown(self):
        """Tears down Decision Descent."""
        self.LOGGER.warning('Disconnecting from client...')
        self._http.disconnect()
        
        super(DescentClient, self).teardown()
