import os
import sys
from PySide2 import QtWidgets, QtCore

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
DEBUG=True

__version__ = 'v0.0.1.dev.001'

def main():
    fw = AppFramework(
        app_name = APP_NAME,
        version = __version__,
        debug = DEBUG
    )

    app = blMenuKITSU([], framework = fw)

    window = QtWidgets.QWidget()
    window.setWindowTitle('Hello PySide2')
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()