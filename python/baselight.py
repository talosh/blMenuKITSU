import os
import sys
import time
import threading
import inspect
import re
import traceback

from PyQt5 import QtGui, QtWidgets, QtCore

from pprint import pprint, pformat

class appBaselightConnector(object):
    def __init__(self, framework):
        self.name = self.__class__.__name__
        self.framework = framework
        self.app_name = framework.app_name
        self.prefs = self.framework.prefs
        self.connector = self
        self.mbox = QtWidgets.QMessageBox()

        self.log('waking up')
        self.flapi = self.import_flapi()
    
    def log(self, message):
        self.framework.log('[' + self.name + '] ' + str(message))

    def log_debug(self, message):
        self.framework.log_debug('[' + self.name + '] ' + str(message))

    def import_flapi(self):
        flapi_module_path = '/Applications/Baselight/Current/Utilities/Resources/share/flapi/python/flapi'
        if not os.path.isdir(flapi_module_path):
            from . import flapi
        else:
            self.log_debug('importing flapi from %s' % flapi_module_path)
            try:
                if not flapi_module_path in sys.path:
                    sys.path.insert(0, flapi_module_path)
                import flapi
                return flapi
            except Exception as e:
                msg = f'unable to import filmlight api python module from: {flapi_module_path}\n'
                self.mbox.setText(msg + pformat(e))
                self.mbox.exec_()
