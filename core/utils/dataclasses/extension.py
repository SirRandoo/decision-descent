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
import logging
import typing

__all__ = ['Extension']


@dataclasses.dataclass()
class Extension:
    """A dataclass for representing extensions.  Extensions should implement
    this class in order to get set up."""
    NAME: typing.ClassVar[str]
    AUTHORS: typing.ClassVar[typing.Set[str]]
    VERSION: typing.ClassVar[typing.Tuple[int]] = (1, 0, 0)
    LICENSE: typing.ClassVar[str] = 'All rights reserved'
    
    logger: logging.Logger = dataclasses.field(init=False)
    
    def __post_init__(self):
        """Called immediately after __init__."""
        self.logger = logging.getLogger(f'extensions.{self.NAME}')
        
        if self.NAME is None:
            self.NAME = self.__class__.__name__.lower()
    
    # Abstract methods #
    def check_for_updates(self, updater):
        """Invoked when an update check has been requested for this extension.
        
        If this method were to be overridden, the implementation should check
        for an update to their extension.  It's recommended you use the
        requests factory from QtUtilities as to not block the main QEventLoop.
        Alternatively, you can use requests in a QThread.  Should you choose the
        former, you can receive a factory from the Client class passed during
        initialization.
        
        Should your extension have a newer release, you should add it via
        updater's "add_release" method.  The "identifier" parameter should be
        a unique identifier for your extension, usually your extension name, and
        the "data" parameter should be a ReleaseData namedtuple.  You can get
        the ReleaseData tuple from the "updater" module in "widgets" package.
        
        The "zip" attribute should be a url pointing to a flat zip file.  If
        your release contains a root directory, the updater will *only* unpack
        the root folder.
        
        The "changelog" attribute should be a string, optionally with XHTML
        tags, that will be displayed in the updater prompt.  If your changelog
        is raw markdown, it will not be transformed."""
