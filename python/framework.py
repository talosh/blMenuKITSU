import os
import sys
import inspect
import queue
import re
import traceback

from pprint import pprint, pformat

class AppFramework(object):
    # flameAppFramework class takes care of preferences

    class prefs_dict(dict):
        # subclass of a dict() in order to directly link it 
        # to main framework prefs dictionaries
        # when accessed directly it will operate on a dictionary under a 'name'
        # key in master dictionary.
        # master = {}
        # p = prefs(master, 'app_name')
        # p['key'] = 'value'
        # master - {'app_name': {'key', 'value'}}
            
        def __init__(self, master, name, **kwargs):
            self.name = name
            self.master = master
            if not self.master.get(self.name):
                self.master[self.name] = {}
            self.master[self.name].__init__()

        def __getitem__(self, k):
            return self.master[self.name].__getitem__(k)
        
        def __setitem__(self, k, v):
            return self.master[self.name].__setitem__(k, v)

        def __delitem__(self, k):
            return self.master[self.name].__delitem__(k)
        
        def get(self, k, default=None):
            return self.master[self.name].get(k, default)
        
        def setdefault(self, k, default=None):
            return self.master[self.name].setdefault(k, default)

        def pop(self, k, v=object()):
            if v is object():
                return self.master[self.name].pop(k)
            return self.master[self.name].pop(k, v)
        
        def update(self, mapping=(), **kwargs):
            self.master[self.name].update(mapping, **kwargs)
        
        def __contains__(self, k):
            return self.master[self.name].__contains__(k)

        def copy(self): # don't delegate w/ super - dict.copy() -> dict :(
            return type(self)(self)
        
        def keys(self):
            return list(self.master[self.name].keys())

        @classmethod
        def fromkeys(cls, keys, v=None):
            return self.master[self.name].fromkeys(keys, v)
        
        def __repr__(self):
            return '{0}({1})'.format(type(self).__name__, self.master[self.name].__repr__())

        def master_keys(self):
            return list(self.master.keys())

    def __init__(self, *args, **kwargs):
        self.name = self.__class__.__name__
        self.app_name = kwargs.get('app_name', 'App')
        self.bundle_name = self.sanitize_name(self.app_name)
        self.version = kwargs.get('version', '0.0.0')
        self.debug = kwargs.get('debug', False)
        self.prefs = {}
                
        import socket
        self.hostname = socket.gethostname()
        
        if sys.platform == 'darwin':
            self.prefs_folder = os.path.join(
                os.path.expanduser('~'),
                 'Library',
                 'Preferences',
                 self.bundle_name)
        elif sys.platform.startswith('linux'):
            self.prefs_folder = os.path.join(
                os.path.expanduser('~'),
                '.config',
                self.bundle_name)

        self.prefs_folder = os.path.join(
            self.prefs_folder,
            self.hostname,
        )

        self.kitsu_data = {}
        self.baselight_data = {}

        self.log('[%s] waking up' % self.__class__.__name__)
        # self.load_prefs()
        self.mbox = self.setup_message_box()

        self.message_queue = queue.Queue()
        self.max_message_queue_size = 2048

    def log(self, message):
        try:
            message = f'[{self.bundle_name}] {str(message)}'
            print (message)
            if self.message_queue.qsize() < self.max_message_queue_size:
                item = {'type': 'console', 'message': message}
                self.message_queue.put(item)
        except:
            pass

    def log_debug(self, message):
        if self.debug:
            try:
                message = f'[DEBUG {self.bundle_name}] {str(message)}'
                print (message)
                if self.message_queue.qsize() < self.max_message_queue_size:
                    item = {'type': 'console', 'message': message}
                    self.message_queue.put(item)
            except:
                pass

    def load_prefs(self):
        import json
        
        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.prefs.json'

        try:
            with open(prefs_file_path, 'r') as prefs_file:
                self.prefs.update(json.load(prefs_file))
            self.log_debug('preferences loaded from %s' % prefs_file_path)
            self.log_debug('preferences contents:\n' + json.dumps(self.prefs, indent=4))
        except Exception as e:
            self.log('unable to load preferences from %s' % prefs_file_path)
            self.log_debug(e)

        return True

    def save_prefs(self):
        import json

        if not os.path.isdir(self.prefs_folder):
            try:
                os.makedirs(self.prefs_folder)
            except:
                self.log('unable to create folder %s' % self.prefs_folder)
                return False

        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.prefs.json'

        try:
            with open(prefs_file_path, 'w') as prefs_file:
                json.dump(self.prefs, prefs_file, indent=4)
            self.log_debug('preferences saved to %s' % prefs_file_path)
            self.log_debug('preferences contents:\n' + json.dumps(self.prefs, indent=4))
        except Exception as e:
            self.log('unable to save preferences to %s' % prefs_file_path)
            self.log_debug(e)
            
        return True

    def log_exception(self, e):
        self.log(pformat(e))
        self.log_debug(pformat(traceback.format_exc()))

    def sanitize_name(self, name_to_sanitize):
        if name_to_sanitize is None:
            return None
        
        stripped_name = name_to_sanitize.strip()
        exp = re.compile(u'[^\w\.-]', re.UNICODE)

        result = exp.sub('_', stripped_name)
        return re.sub('_\_+', '_', result)

    def setup_message_box(self):
        from PyQt5 import QtGui, QtWidgets, QtCore
        mbox = QtWidgets.QMessageBox()
        mbox.setWindowFlags(QtCore.Qt.Tool)
        mbox.setStyleSheet("""
            QMessageBox {
                background-color: #313131;
                color: #9a9a9a;
                text-align: center;
            }
            QMessageBox QPushButton {
                width: 80px;
                height: 24px;
                color: #9a9a9a;
                background-color: #424142;
                border-top: 1px inset #555555;
                border-bottom: 1px inset black
            }
            QMessageBox QPushButton:pressed {
                font:italic;
                color: #d9d9d9
            }
        """)
        return mbox

