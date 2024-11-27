import os
import sys
import inspect
import platform

from urllib.parse import urljoin, urlparse

import flapi

from pprint import pprint, pformat

settings = {
    'menu_group_name': 'Kitsu',
    'debug': False,
    'app_name': 'blMenuKITSU',
    'version': 'v0.0.2.dev.002',
}

packages_folder = os.path.join(
    os.path.dirname(inspect.getfile(lambda: None)),
    f'{settings["app_name"]}.packages'
)

if packages_folder not in sys.path:
    sys.path.append(packages_folder)
try:
    import gazu
except Exception as e:
    print (f'[{settings.get("app_name")}]: Unable to import Gazu: {e}')
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
        self.load_prefs()

    def log(self, message):
        print(f'[{self.bundle_name}] {message}')

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
            self.log_debug('preferences contents:\n' + json.dumps(self, indent=4))
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
            print(f'Unable to save preferences to {prefs_file_path}: {e}')
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


class FLAPIManager():
# A class to manage FLAPI calls
    def __init__(self):

        try:
            self.conn = flapi.Connection.get() 
        except flapi.FLAPIException as ex:
            print( "Could not connect to FLAPI: %s" % ex, flush=True)

        try:
            self.app = self.conn.Application.get()
        except flapi.FLAPIException as ex:
            print( "Could not get Application instance: %s" % ex , flush=True)


class KitsuManager():
    # A class to manage Kitsu client calls

    def __init__(self):

        self.LOGGED_OUT_STATE = 0
        self.LOGGING_IN_STATE = 1
        self.LOGGED_IN_STATE = 2

        self.state = self.LOGGED_OUT_STATE

        self.login_request_in_progress = False

        self.kitsu_client = None
        self.kitsu_user = None
        self.kitsu_account_name = None

        self.kitsu_account_id = None
        self.kitsu_token = None
        self.authenticated = False
        self.data_hierarchy = {}
        self.data_hierarchy_idx = None
        self.uuid = None
        self.dev_token = None
        self.data_layers = ['accounts', 'teams', 'projects', 'flat_pathed_folders', 'assets', 'comments']
        self.data_hierarchy = {k:[] for k in self.data_layers}
        self.data_hierarchy_idx = 0

        self.possibly_missing_assets = []

        self.log_debug = prefs.log

    def login(self, host, user, password):
        try:
            # Ensure the host URL ends with '/api/'
            parsed_host = urlparse(host)
            if not parsed_host.scheme:
                return {'status': None, 'message': f'Invalid host URL: {host}'}

            if not host.endswith('/api/'):
                host = urljoin(host.rstrip('/') + '/', 'api/')

            # Create the client and check if the host is up
            self.kitsu_client = gazu.client.create_client(host)
            if not gazu.client.host_is_up(client=self.kitsu_client):
                return {'status': None, 'message': f'Host {host} is unreachable'}

            # Attempt to log in
            result = gazu.log_in(user, password, client=self.kitsu_client)
            
            if not result:
                return {'status': None, 'message': 'Invalid username or password'}

            # Fetch the current user details
            self.kitsu_user = gazu.client.get_current_user(client=self.kitsu_client)
            self.kitsu_account_name = self.kitsu_user.get('full_name')
            self.log_debug(f'Connected to Kitsu as {self.kitsu_account_name}')
            self.state = self.LOGGED_IN_STATE
            return {'status': True, 'message': 'Login successful'}
        #except gazu.exception.AuthFailedException:
        #    self.kitsu_client = None
        #    self.kitsu_user = None
        #    self.kitsu_account_name = None
        #    return {'status': None, 'message': 'Invalid name or password'}
        except Exception as e:
            self.kitsu_client = None
            self.kitsu_user = None
            self.kitsu_account_name = None
            self.state = self.LOGGED_OUT_STATE
            exception_name = e.__class__.__name__
            message = f'{exception_name} {str(e)}'
            return {'status': None, 'message': message}

    def logout(self):
        self.state = self.LOGGED_OUT_STATE
        self.kitsu_client = None
        self.kitsu_user = None
        self.kitsu_account_name = None

    '''
    def login(self, host, user, password):
        try:
            if not host.endswith('/api/'):
                if self.kitsu_host.endswith('/'):
                    host = host + 'api/'
                else:
                    host = host + '/api/'
            elif host.endswith('/api'):
                host = host + ('/')
                self.kitsu_client = gazu.client.create_client(host)
                if not gazu.client.host_is_up(client = self.kitsu_client):
                    return {'status': None, 'message': f'Host {host} is unreachable'}
                result = gazu.log_in(user, password, client = self.kitsu_client)
                self.kitsu_user = gazu.client.get_current_user(client = self.kitsu_client)
                self.kitsu_account_name = self.user.get('full_name')
                self.log_debug('connected to kitsu as %s' % self.user_name)
                return {'status': True, 'message': 'Testing loop only'}
        except Exception as e:
            self.gazu_client = None
            self.user = None
            self.user_name = None
            return {'status': None, 'message': pformat(e)}
    '''


class KitsuCommandsMenu:
    menu = None

    def __init__(self):
        self.menu = flapiManager.conn.Menu.create()
        self.menuItem = flapiManager.conn.MenuItem.create("Kitsu", "uk.ltd.filmlight.kitsu.actions")
        self.menuItem.register(flapi.MENULOCATION_SCENE_MENU)
        self.menuItem.set_sub_menu(self.menu)


class LoginMenuitem():
    def __init__(self):
        self.menuItem = flapiManager.conn.MenuItem.create('Login to Kitsu', 'uk.ltd.filmlight.kitsu.login')
        kitsuCommandsMenu.menu.add_item(self.menuItem)
        self.menuItem.connect( 'MenuItemSelected', self.handle_select_signal )
        self.menuItem.connect( 'MenuItemUpdate', self.handle_update_signal )

    def handle_select_signal( self, sender, signal, args ):
        if kitsuManager.state == kitsuManager.LOGGED_OUT_STATE:
            kitsuManager.logout()
            flapiManager.app.message_dialog( 
                'Kitsu',
                f'Logout succesful',
                ["OK"]
                )
            self.menuItem.set_title('Login to Kitsu')
            return
            
        self.items = [
            flapi.DialogItem(Key="Server", Label="Server", Type=flapi.DIT_STRING, Default = prefs.get('Server', "")),
            flapi.DialogItem(Key="User", Label="User", Type=flapi.DIT_STRING, Default = prefs.get('User', "")),
            flapi.DialogItem(Key="Password", Label="Password", Type=flapi.DIT_STRING, Default = "", Password = 1),
        ]

        self.settings = {
            "Server": prefs.get('Server', ""),
            "User": prefs.get('User', ""),
            "Password": "",
        }

        self.dialog = flapiManager.conn.DynamicDialog.create( 
            "KITSU Login",
            self.items,
            self.settings
        )

        result =  self.dialog.show_modal(-200, -50)

        if result:
            # Show results
            #
            # Need to fetch an instance of the Application class to
            # use the message_dialog method
            #
            '''
            flapiManager.app.message_dialog( 
                "Dialog Done",
                "Server: %s, User: %s, Pass %s." % (result['Server'], result['User'], result['Password']),
                ["OK"]
            )
            '''
            prefs['Server'] = result['Server']
            prefs['User'] = result['User']
            prefs.save_prefs()

            login_result = kitsuManager.login(
                result['Server'],
                result['User'],
                result['Password']
            )

            if login_result['status'] is None:
                flapiManager.app.message_dialog( 
                    'Unable to Login',
                    f'Server: {result["Server"]}\nUser: {result["User"]}\nReason: {login_result["message"]}',
                    ["OK"]
                )
            else:
                flapiManager.app.message_dialog( 
                    'Login succesful',
                    f'Server: {result["Server"]}\n{login_result["message"]}',
                    ["OK"]
                )

            if kitsuManager.state == kitsuManager.LOGGED_OUT_STATE:
                self.menuItem.set_title('Login to Kitsu')
            elif kitsuManager.state == kitsuManager.LOGGING_IN_STATE:
                self.menuItem.set_title('Logging in ...')
            else:
                self.menuItem.set_title(f'Logout {kitsuManager.kitsu_account_name}')

    def handle_update_signal(self, sender, signal, args):
        self.menuItem.set_enabled('gazu' in sys.modules)


class AboutMenuItem():
    def __init__(self):
        self.menuItem = flapiManager.conn.MenuItem.create(f'Version {settings.get("version")}', 'uk.ltd.filmlight.kitsu.about')
        kitsuCommandsMenu.menu.add_item(self.menuItem)
        self.menuItem.connect( "MenuItemSelected", self.handle_select_signal )


    def handle_select_signal( self, sender, signal, args ):
        
        try:
            packages_folder = os.path.join(
                os.path.dirname(inspect.getfile(lambda: None)),
                f'{settings["app_name"]}.packages'
            )
            if packages_folder not in sys.path:
                sys.path.append(packages_folder)
            import gazu
            if packages_folder in sys.path:
                sys.path.remove(packages_folder)
            gazu_str = f'Gazu version: {gazu.__version__}'
        except Exception as e:
            gazu_str = f'Unable to import Gazu: {e}'

        major = sys.version_info.major
        minor = sys.version_info.minor
        micro = sys.version_info.micro
        python_str = f"Baselight's Python version: {major}.{minor}.{micro}"

        flapiManager.app.message_dialog( 
            f'Baselight to Kitsu connector',
            f'{settings.get("app_name")}: {settings.get("version")}\n{gazu_str}\n{python_str}',
            ["OK"]
        )


scene = None

prefs = Prefs(**settings)

flapiManager = FLAPIManager()
kitsuManager = KitsuManager()

kitsuCommandsMenu = KitsuCommandsMenu()
loginMenuItem = LoginMenuitem()
aboutMenuItem = AboutMenuItem()

'''

def onListDialogMenuItemUpdate(sender, signal, args):
    global scene
    # Enable menu item only if a scene is open
    scene = app.get_current_scene()
    list_dialog_menu_item.set_enabled(scene != None)

# Connect to FLAPI
conn = flapi.Connection.get() 
conn.connect()

# Get application
app = conn.Application.get()


# Place menu item on Scene menu
list_dialog_menu_item = conn.MenuItem.create("Show Dialog")
list_dialog_menu_item.register(flapi.MENULOCATION_SCENE_MENU)

# Connect up both the 'MenuItemSelected' and 'MenuItemUpdate' signals
list_dialog_menu_item.connect("MenuItemSelected", onListDialogMenuItemSelected)
list_dialog_menu_item.connect("MenuItemUpdate", onListDialogMenuItemUpdate)
'''
