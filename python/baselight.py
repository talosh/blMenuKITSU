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
        # self.fl_connect()
    
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

    def get_baselight_scene_shots(self, scene_path):
        flapi = self.flapi
        conn = self.conn
        log = self.log
        log_debug = self.log_debug
        blpath = self.conn.Scene.path_to_string(scene_path)
        log ('---')
        log ('--- Collecting metadata of Baselight shots in: %s' % blpath)
            
        if not conn:
            return []

        if not scene_path:
            return []

        try:
            log('loading scene: %s' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
        except flapi.FLAPIException as ex:
            log( "Error loading scene: %s" % ex )
            return []

        baselight_shots = []

        nshots = scene.get_num_shots()
        log( "Found %d shot(s)" % nshots )

        md_keys = set()
        mddefns = scene.get_metadata_definitions()

        for mdfn in mddefns:
            md_keys.add(mdfn.Key)
        
        if nshots > 0:
            shots = scene.get_shot_ids(0, nshots)
            log('Querying Baselight metadata')
            for shot_ix, shot_inf in enumerate(shots):
                # log( "\r Querying Baselight metadata for shot %d of %s" % (shot_ix + 1, nshots), end="" )
                log(f'Querying shot {shot_ix + 1} of {nshots}')
                # log.verbose("Shot %d:" % shot_ix)
                shot = scene.get_shot(shot_inf.ShotId)
                shot_md = shot.get_metadata(md_keys)
                for key in md_keys:
                    if type(shot_md[key]) is list:
                        for list_ix, list_inf in enumerate(shot_md[key]):
                            shot_md[key + '.' + str(list_ix)] = list_inf
                        # print ('%15s: %s: %s:' % (key, type(shot_md[key]), shot_md[key]))
                # shot_md = shot.get_metadata_strings(md_keys)
                mark_ids = shot.get_mark_ids()
                categories = shot.get_categories()

                thumbnail_url = ''
                # thumbnail_url = conn.ThumbnailManager.get_poster_uri(shot, 1, {'DCSpace': 'sRGB'})
                # pprint (thumbnail_url)

                baselight_shots.append(
                    {
                        'shot_ix': shot_ix + 1,
                        'shot_id': shot_inf.ShotId,
                        'mddefns': mddefns,
                        'shot_md': shot_md,
                        'mark_ids': mark_ids,
                        'categories': categories,
                        'thumbnail_url': thumbnail_url
                    }
                )

                shot.release()

        '''
        test_tc = conn.Utilities.timecode_from_string('01:00:00:00')
        pprint (test_tc)
        pprint (str(test_tc))
        pprint (dir(test_tc))
        '''

        '''
        # show avaliable keys and their types
        mddefns = scene.get_metadata_definitions()
        for mdfn in mddefns:
            print ('%15s: %s, %s' % (mdfn.Key, mdfn.Name, mdfn.Type))
        cat_keys = scene.get_strip_categories()
        pprint (cat_keys)
        '''

        scene.close_scene()
        scene.release()

        return baselight_shots

    def check_or_add_kitsu_metadata_definition(self, scene_path):
        flapi = self.flapi
        conn = self.conn
        log = self.log
        log_debug = self.log_debug
        blpath = self.conn.Scene.path_to_string(scene_path)
        log ('---')
        log ('--- Checking KITSU metadata in: %s' % blpath)

        try:
            log('Opening scene: %s' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
        except flapi.FLAPIException as ex:
            log( "Error opening scene: %s" % ex )
            return None

        md_names = {}
        mddefns = scene.get_metadata_definitions()

        for mdfn in mddefns:
            md_names[mdfn.Name] = mdfn

        if 'kitsu-uid' in md_names.keys():
            log('kistu-uid metadata columnn already exists in scene: "%s"' % scene.get_scene_pathname())
            scene.close_scene()
            scene.release()
            return md_names['kitsu-uid']

        # the scene has no kitsu-id metadata defined
        # try to re-open the scene in rw mode and add this definition
        scene.close_scene()
        scene.release()

        try:
            log('Trying to open scene: %s in read-write mode' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path )
        except flapi.FLAPIException as ex:
            '''
            self.framework.message_queue.put(
                        {'type': 'mbox',
                        'message': f'Unable to open Baselight \
                        scene for writing: {pformat(ex)}\n\
                        Kitsu metadata will not be updated'}
                
                )
            '''
            log( "Error opening scene for writing: %s" % ex )
            return None

        log('Adding kitsu-uid metadata columnn to scene: "%s"' % scene.get_scene_pathname())
        scene.start_delta('Add kitsu-id metadata column')
        metadata_obj = scene.add_metadata_defn('kitsu-uid', 'String')
        scene.end_delta()
        scene.save_scene()
        scene.close_scene()
        scene.release()
        return metadata_obj
    
    def set_kitsu_metadata(self, scene_path, baselight_shots):
        log = self.log
        log_debug = self.log_debug
        flapi = self.flapi
        conn = self.conn

        try:
            log('Trying to open scene: %s in read-write mode' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path, {  flapi.OPENFLAG_DISCARD  })
        except flapi.FLAPIException as ex:
            log.error( "Error opening scene: %s" % ex )
            return None
        
        kitsu_uid_metadata_obj = None
        md_names = {}
        mddefns = scene.get_metadata_definitions()
        for mdfn in mddefns:
            md_names[mdfn.Name] = mdfn
        if 'kitsu-uid' in md_names.keys():
            kitsu_uid_metadata_obj = md_names['kitsu-uid']
        if not kitsu_uid_metadata_obj:
            return None

        scene.start_delta('Add kitsu metadata to shots')
        log ('Adding kitsu metadata to Baselight shots')
                
        for baselight_shot in baselight_shots:
            shot_id = baselight_shot.get('shot_id')
            shot = scene.get_shot(shot_id)
            kitsu_shot = baselight_shot.get('kitsu_shot')
            if not kitsu_shot:
                continue
            kitsu_shot_id = kitsu_shot.get('id')
            if not kitsu_shot_id:
                continue

            new_md_values = {
                kitsu_uid_metadata_obj.Key: kitsu_shot_id
            }

            shot.set_metadata( new_md_values )
            shot.release()

        scene.end_delta()
        scene.save_scene()
        scene.close_scene()
        scene.release()
