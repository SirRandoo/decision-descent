#  This file is part of Decision Descent: Client.
#
#  Decision Descent: Client is free software: you can 
#  redistribute it and/or modify it under the 
#  terms of the GNU General Public License as 
#  published by the Free Software Foundation, 
#  either version 3 of the License, or (at 
#  your option) any later version.
#
#  Decision Descent: Client is distributed in the hope 
#  that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty 
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License 
#  for more details.
#
#  You should have received a copy of the GNU
#  General Public License along with 
#  Decision Descent: Client.  If not, 
#  see <http://www.gnu.org/licenses/>.
#  
#  Author: RandomShovel
#  File Creation Date: 7/21/2017
from configobj import ConfigObj

__all__ = {"Config"}


class Config(ConfigObj):
    """A wrapper class for ConfigObj.  This class has preset values that effect
    the way ConfigObj operates.  Said values can be overridden by passing them
    to this class."""
    
    def __init__(self, config_file, **kwargs):
        params = dict(raise_errors=True, create_empty=True,
                      indent_type="  ", write_empty_values=True)
        
        params.update(kwargs)
        super(Config, self).__init__(config_file, **params)
