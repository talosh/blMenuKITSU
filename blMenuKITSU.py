import os
import sys
from PyQt5 import QtWidgets, QtCore

from pprint import pprint, pformat

from python.app import blMenuKITSU
from python.framework import AppFramework


'''
from python.config import get_config_data
from python.config import config_reader
from python.tailon import tailon
from python.metadata_fields import set_metadata_fields
from python.sequence import sequence_sync
from python.util import RobotLog
from python.baselight import baselight_process
'''

APP_NAME = 'blMenuKITSU'
DEBUG=False

__version__ = 'v0.0.1.dev.003'

def main():
    fw = AppFramework(
        app_name = APP_NAME,
        version = __version__,
        debug = DEBUG
    )

    app = blMenuKITSU([], framework = fw)
    
    window = app.main_window()
    window.show()

    app.exec_()
    return app

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    fw = AppFramework(
        app_name = f'{APP_NAME} {__version__}',
        version = __version__,
        debug = DEBUG
    )
    ex = blMenuKITSU([], framework = fw)
    sys.exit(app.exec_())

    
    # main()