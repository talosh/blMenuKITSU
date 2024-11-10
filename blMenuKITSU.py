import os
import sys

import flapi

from pprint import pprint, pformat

settings = {
    'menu_group_name': 'Kitsu',
    'debug': False,
    'app_name': 'blMenuKITSU',
    'version': 'v0.0.2.dev.001',
}

packages_folder = os.path.join(
    os.path.dirname(__file__),
    f'{settings["app+name"]}.packages'
)

if packages_folder not in sys.path:
    sys.path.append(packages_folder)
import gazu
if packages_folder in sys.path:
    sys.path.remove(packages_folder)

class Prefs(dict):
    # subclass of a dict()
        
    def __init__(self, *args, **kwargs):
        super(Prefs, self).__init__()
        self.name = self.__class__.__name__
        self.app_name = kwargs.get('app_name', 'App')
        self.bundle_name = self.sanitize_name(self.app_name)
        self.version = kwargs.get('version', '0.0.0')
        self.debug = kwargs.get('debug', False)
                
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

    def log_debug(self, message):
        if self.debug:
            try:
                message = f'[DEBUG {self.bundle_name}] {str(message)}'
                print (message)
            except:
                pass

    def load_prefs(self):
        import json
        
        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.prefs.json'

        try:
            with open(prefs_file_path, 'r') as prefs_file:
                self.update(json.load(prefs_file))
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
                print('unable to create folder %s' % self.prefs_folder)
                return False

        prefix = self.prefs_folder + os.path.sep + self.bundle_name
        prefs_file_path = prefix + '.prefs.json'

        try:
            with open(prefs_file_path, 'w') as prefs_file:
                json.dump(self, prefs_file, indent=4)
            self.log_debug('preferences saved to %s' % prefs_file_path)
            self.log_debug('preferences contents:\n' + json.dumps(self, indent=4))
        except Exception as e:
            print('unable to save preferences to %s' % prefs_file_path)
            self.log_debug(e)
            
        return True

    def sanitize_name(self, name_to_sanitize):
        import re
        if name_to_sanitize is None:
            return None
        
        stripped_name = name_to_sanitize.strip()
        exp = re.compile(u'[^\w\.-]', re.UNICODE)

        result = exp.sub('_', stripped_name)
        return re.sub('_\_+', '_', result)

class KitsuLoginDialog:
    def __init__(self, conn):
        self.conn = conn

        self.items = [
            flapi.DialogItem(Key="Server", Label="Server", Type=flapi.DIT_STRING, Default = ""),
            flapi.DialogItem(Key="User", Label="User", Type=flapi.DIT_STRING, Default = ""),
            flapi.DialogItem(Key="Password", Label="Password", Type=flapi.DIT_STRING, Default = ""),
        ]

        self.settings = {
            "Server": "",
            "User": "",
            "Password": "",
        }

        self.dialog = self.conn.DynamicDialog.create( 
            "KITSU Login",
            self.items,
            self.settings
        )

    def show(self):
        return self.dialog.show_modal(-200, -50)


'''
from python.config import get_config_data
from python.config import config_reader
from python.tailon import tailon
from python.metadata_fields import set_metadata_fields
from python.sequence import sequence_sync
from python.util import RobotLog
from python.baselight import baselight_process
'''

'''
def main():
    pass

if __name__ == "__main__":
    pass
'''