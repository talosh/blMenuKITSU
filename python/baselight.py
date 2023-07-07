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
            self.framework.message_queue.put(
                {'type': 'setText',
                'widget': 'UI_lbl_FlapiStatus',
                'text': 'Connecting...'}
            )
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
                self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': pformat(e)}
                )
            self.conn = None
            return None
        except Exception as e:
            if msg:
                self.framework.message_queue.put(
                    {'type': 'mbox',
                    'message': pformat(e)}
                )
            self.conn = None
            return None

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

    def fl_get_scene_path(self, blpath):
        flapi = self.flapi
        try:
            blpath_components = blpath.split(':')
            bl_hostname = blpath_components[0]
            bl_jobname = blpath_components[1]
            bl_scene_name = blpath_components[-1]
            bl_scene_path = ':'.join(blpath_components[2:])
            bl_scenes_folder = ''.join(blpath_components[2:-1])

            if '*' in bl_scene_name:
                # find the most recent scene
                import re
                self.log('finding most recent baselight scene for pattern: %s' % blpath)
                existing_scenes = self.conn.JobManager.get_scenes(bl_hostname, bl_jobname, bl_scenes_folder)
                matched_scenes = []
                for scene_name in existing_scenes:
                    if re.findall(bl_scene_name, scene_name):
                        matched_scenes.append(scene_name)

                if not matched_scenes:
                    self.log('no matching scenes found for: %s' % blpath)
                    return None
                else:
                    # TODO
                    # this to be changed to actually checking the most recently modified scene
                    # instead of just plain alphabetical sorting and taking the last one

                    scene_name = sorted(matched_scenes)[-1]
                    self.log('Alphabetically recent scene: %s' % scene_name)
                    bl_scene_path = bl_scenes_folder + ':' + scene_name
                    blpath = bl_hostname + ':' + bl_jobname + ':' + bl_scene_path

            else:
                # we have full scene path and need to check if scene exists

                self.log('checking baselight scene: %s' % blpath)

                if not self.conn.JobManager.scene_exists(bl_hostname, bl_jobname, bl_scene_path):
                    self.log('baselight scene: %s does not exist' % blpath)
                    return None
                else:
                    self.log('baselight scene: %s exists' % blpath)

            
            try:
                scene_path = self.conn.Scene.parse_path(blpath)
            except flapi.FLAPIException as ex:
                self.log('Can not parse scene: %s' % blpath)
                return None

            return scene_path
        except:
            self.log('unable to get scene path from: %s' % blpath)
            return None
