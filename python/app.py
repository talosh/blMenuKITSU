import os
import sys
from PySide2 import QtWidgets, QtCore

from pprint import pprint, pformat

class blMenuKITSU(QtWidgets.QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__([])
        self.framework = kwargs.get('framework')
