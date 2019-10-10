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
from os import path
from shutil import copytree

from PyQt5 import QtCore

if __name__ == '__main__':
    # Logging
    logging.basicConfig(format='[{levelname}][{name}] {message}', style='{', handlers=[logging.StreamHandler()])
    logger = logging.getLogger('core.test')
    
    # Declarations
    current_directory = QtCore.QDir.current()
    mods_directory = QtCore.QDir(
        path.join(QtCore.QDir.homePath(), 'Documents/My Games/Binding of Isaac Afterbirth+ Mods'))
    mod_directory = QtCore.QDir(mods_directory.path(), 'Decision Descent')
    
    # Validation
    logger.info('Checking current working directory...')
    if not current_directory.exists('core'):
        logger.warning("The current directory isn't the root Decision Descent directory!")
        logger.warning(f'The current directory is {current_directory.path()}')
        logger.warning('Moving up a directory...')
        
        current_directory.cdUp()
    
    else:
        logger.info('The current directory is the root Decision Descent directory!')
    
    logger.info('Checking mod directory...')
    if mod_directory.exists() and not mod_directory.isEmpty():
        logger.warning("The mod directory already exists!")
        logger.warning(f'Deleting {current_directory.path()} ...')
        
        if mod_directory.removeRecursively():
            logger.info('Mod directory successfully deleted!')
        
        else:
            logger.warning("Mod directory couldn't be deleted entirely!")
    
    else:
        logger.info('The mod directory is already deleted!')
    
    # Copy mods directory
    try:
        copytree(path.join(current_directory.path(), 'mod'), mod_directory.path())
    
    except OSError as e:
        logger.fatal(f'Could not copy mod to {mod_directory.path()} !')
        logger.fatal('Reason(s):')
        
        for arg in e.args:
            if isinstance(arg, list):
                for error in arg:
                    logger.fatal(f'- {error.__class__.__name__} - {error.__cause__}')
            
            else:
                logger.fatal(f'- {str(arg)}')
    
    else:
        logger.info(f'Mod tree successfully copied to {mod_directory.path()} !')
    
    finally:
        if mods_directory.exists('mod'):
            if mods_directory.rename('mod', 'Decision Descent'):
                logger.info('Mod folder was successfully renamed to "Decision Descent"!')
            
            else:
                logger.warning('Mod folder could not be renamed from "mod" to "Decision Descent"!')
