#  This file is part of Decision Descent Client - Python.
#
#  Decision Descent Client - Python is free software: you can 
#  redistribute it and/or modify it under the 
#  terms of the GNU General Public License as 
#  published by the Free Software Foundation, 
#  either version 3 of the License, or (at 
#  your option) any later version.
#
#  Decision Descent Client - Python is distributed in the hope 
#  that it will be useful, but WITHOUT ANY 
#  WARRANTY; without even the implied warranty 
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
#  PURPOSE.  See the GNU General Public License 
#  for more details.
#
#  You should have received a copy of the GNU
#  General Public License along with 
#  Decision Descent Client - Python.  If not, 
#  see <http://www.gnu.org/licenses/>.
#  
#  Author: RandomShovel
#  File Creation Date: 7/17/2017
import logging
import sys

from PyQt5 import QtCore

from widgets import Client, QApplication

possible_unload_methods = ["quit", "shutdown", "unload"]

if __name__ == '__main__':
    ClientApplication = QApplication(sys.argv)
    
    ClientWidget = Client()
    ClientWidget.show()
    
    logger = logging.getLogger("client.app")
    
    logger.info("Looks like we're really doing this...")
    ClientApplication.exec()
