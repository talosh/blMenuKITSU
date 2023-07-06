import os
import sys
import time
import threading
import inspect
import re
import traceback
import getpass

from PyQt5 import QtGui, QtWidgets, QtCore

from pprint import pprint, pformat

class appBaselightConnector(object):
    def __init__(self, framework):
        self.name = self.__class__.__name__
        self.framework = framework
        self.app_name = framework.app_name
        self.prefs = self.framework.prefs
        self.connector = self
        self.mbox = self.framework.mbox

        self.log('waking up')
        self.flapi = self.import_flapi()
        self.flapi_host = self.prefs.get('flapi_host', 'localhost')
        self.flapi_user = self.prefs.get('flapi_user', getpass.getuser())
        self.flapi_key = self.prefs.get('flapi_key', '')
        self.conn = None
        self.fl_connect()
    
    def log(self, message):
        self.framework.log('[' + self.name + '] ' + str(message))

    def log_debug(self, message):
        self.framework.log_debug('[' + self.name + '] ' + str(message))

    def import_flapi(self):
        from . import flapi
        return flapi

        '''
        flapi_module_path = '/Applications/Baselight/Current/Utilities/Resources/share/flapi/python/'
        if not os.path.isdir(flapi_module_path):
            from . import flapi
            return flapi
        else:
            self.log_debug('importing flapi from %s' % flapi_module_path)
            try:
                if not flapi_module_path in sys.path:
                    sys.path.insert(0, flapi_module_path)
                import flapi
                pprint (dir(flapi))
                return flapi
            except Exception as e:
                msg = f'unable to import filmlight api python module from: {flapi_module_path}\n'
                self.mbox.setText(msg + pformat(e))
                self.mbox.exec_()
        '''

    def fl_connect(self, *args, **kwargs):
        msg = kwargs.get('msg')
        flapi = self.flapi
        
        self.flapi_host = self.prefs.get('flapi_host', 'localhost')
        self.flapi_user = self.prefs.get('flapi_user', getpass.getuser())
        self.flapi_key = self.prefs.get('flapi_key', '')

        self.log_debug('opening flapi connection to %s' % self.flapi_host)
        self.log_debug('flapi user: %s' % self.flapi_user)
        self.log_debug('flapi token: %s' % self.flapi_key)

        try:
            self.log_debug('creating Flapi connection object')
            self.conn = flapi.Connection(
                self.flapi_host,
                username=self.flapi_user,
                token=self.flapi_key
            )
            self.log_debug('trying to connect to: %s' % self.flapi_host)
            self.conn.connect()
            jobs = self.conn.JobManager.get_jobs(self.flapi_host)
            self.log_debug('connected to %s' % self.flapi_host)
        except flapi.FLAPIException as e:
            if msg:
                self.mbox.setText(pformat(e))
                self.mbox.exec_()
            self.conn = None
        except Exception as e:
            if msg:
                self.mbox.setText(pformat(e))
                self.mbox.exec_()
            self.conn = None

    def fl_disconnect(self, *args, **kwargs):
        msg = kwargs.get('msg')
        flapi = self.flapi
        try:
            self.conn.close()
            self.conn = None
        except flapi.FLAPIException as e:
            if msg:
                self.mbox.setText(pformat(e))
                self.mbox.exec_()
            self.conn = None
        except Exception as e:
            if msg:
                self.mbox.setText(pformat(e))
                self.mbox.exec_()
            self.conn = None
        self.log_debug('disconnected from %s' % self.flapi_host)

    def fl_create_kitsu_menu(self):
        def onMenuItem1Selected(sender, signal, args):
            result = app.message_dialog("You clicked 'Menu Item 1'", "", ['OK'])

        def onMenuItem2Selected(sender, signal, args):
            result = app.message_dialog("You clicked 'Menu Item 2'", "", ['OK'])

        flapi = self.flapi
        conn = self.conn

        return

        # Connect to FLAPI
        # conn = flapi.Connection.get() 
        # conn.connect()

        def onSceneOpen( sender, signal, args ):
            curSceneName = app.get_current_scene_name()
            allSceneNames = app.get_open_scene_names()
            # Display a message dialog containing scene info
            app.message_dialog(
                "Open Scenes",
                "You just opened the scene '%s'.\n\nThere are %i scenes open, including galleries:\n\n%s."\
                    % (curSceneName, len(allSceneNames), ", ".join(allSceneNames).rstrip(", ")),
                    ["OK"])




        # Get application
        app = conn.Application.get()

        # Subscribe to 'SceneOpen' signal
        app.connect( "SceneOpened", onSceneOpen )

        pprint (app)
        pprint (app.get_open_scene_names())
        return
        
        # Place menu items
        holder_menu = conn.Menu.create()

        menu_items_label = conn.MenuItem.create("My Top Level Menu")
        menu_items_label.register(flapi.MENULOCATION_EDIT_MENU)
        menu_items_label.set_sub_menu(holder_menu)

        menu_item_1 = conn.MenuItem.create("Menu Item 1")
        menu_item_1.connect("MenuItemSelected", onMenuItem1Selected)
        holder_menu.add_item(menu_item_1)

        menu_item_2 = conn.MenuItem.create("Menu Item 2")
        menu_item_2.connect("MenuItemSelected", onMenuItem2Selected)
        holder_menu.add_item(menu_item_2)