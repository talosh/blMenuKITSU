import os
import sys
import time
import threading
import inspect
import re
import traceback
import base64

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
        self.flapi_user = self.prefs.get('flapi_user', 'filmlight')
        self.flapi_key = self.prefs.get('flapi_key', '')
        encoded_flapi_pass = self.prefs.get('flapi_pass', '')
        if encoded_flapi_pass:
            self.flapi_pass = base64.b64decode(encoded_flapi_pass).decode("utf-8")
        self.conn = None
        # self.fl_connect()

        self.processing_flag = False
    
    def log(self, message):
        try:
            message = f'[{self.name}] {str(message)}'
            print (message)
            if self.framework.message_queue.qsize() < self.framework.max_message_queue_size:
                item = {'type': 'console', 'message': message}
                self.framework.message_queue.put(item)
        except:
            pass

        # self.framework.log('[' + self.name + '] ' + str(message))

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
        self.flapi_user = self.prefs.get('flapi_user', 'filmlight')
        self.flapi_key = self.prefs.get('flapi_key', '')
        encoded_flapi_pass = self.prefs.get('flapi_pass', '')
        if encoded_flapi_pass:
            self.flapi_pass = base64.b64decode(encoded_flapi_pass).decode("utf-8")

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
                thumbnail_url = conn.ThumbnailManager.get_poster_uri(shot, {'DCSpace': 'sRGB'})
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
            return f'Error opening scene: {pformat(ex)}'

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
            return f'Error opening scene for writing: {pformat(ex)}'

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
            log.error( "Error opening scene for writing: %s" % ex )
            return f'Error opening scene for writing: {pformat(ex)}'
        
        kitsu_uid_metadata_obj = None
        md_names = {}
        mddefns = scene.get_metadata_definitions()
        for mdfn in mddefns:
            md_names[mdfn.Name] = mdfn
        if 'kitsu-uid' in md_names.keys():
            kitsu_uid_metadata_obj = md_names['kitsu-uid']
        if not kitsu_uid_metadata_obj:
            return f'Error unable to find kitsu-uid metadata column in baselight scene: {self.conn.Scene.path_to_string(scene_path)}'

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

        return True

    def get_and_upload_thumbnails_from_kitsu_id(self, scene_path, kitsu_shots, kitsu_connector):
        flapi = self.flapi
        conn = self.conn
        log = self.log
        log_debug = self.log_debug
        self.processing_flag = True

        def waitForExportToComplete( qm, exportInfo ):
            for msg in exportInfo.Log:
                if (msg.startswith("Error")):
                    log("Export Submission Failed.  %s" % msg);
                    return

            log( "Waiting on render job to complete" )
            triesSinceChange = 0
            lastProgress = -1
            maxTries = 20
            while True:
                opstat = qm.get_operation_status( exportInfo.ID )
                triesSinceChange +=1 
                if opstat.Progress != lastProgress:
                    triesSinceChange = 0
                    lastProgress = opstat.Progress
                dots = ""
                if (triesSinceChange > 0):
                    dots = "..."[:(triesSinceChange%3)+1]
                else:
                    pass
                    # print("")

                # print( "\r  Status: {Status} {Progress:.0%} {ProgressText} ".format(**vars(opstat)), end=""), 
                # print("%s    " % dots, end=""),
                # sys.stdout.flush()
                if triesSinceChange > 0:
                    log( "  Status: {Status} {Progress:.0%} {ProgressText} ".format(**vars(opstat)))
                if opstat.Status == "Done":
                    # print( "\nExport complete" )
                    log( "Export complete" )
                    break
                if triesSinceChange == maxTries:
                    # print("\nStopped waiting for queue to complete.")
                    log("Stopped waiting for queue to complete.")
                    break
                time.sleep(0.5)

            exportLog = qm.get_operation_log( exportInfo.ID )
            for l in exportLog:
                log( "   %s %s: %s" % (l.Time, l.Message, l.Detail) )

            log( "Archiving operaton" )
            qm.archive_operation ( exportInfo.ID )

        blpath = self.conn.Scene.path_to_string(scene_path)
        log ('---')
        log ('--- Rendering thumbnails from Kitsu metadata: %s' % blpath)

        if not conn:
            return None

        if not scene_path:
            return None

        try:
            log('loading scene: %s' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path, { flapi.OPENFLAG_READ_ONLY } )
        except flapi.FLAPIException as ex:
            log( "Error loading scene: %s" % ex )
            return None

        md_names = {}
        md_keys = set()
        mddefns = scene.get_metadata_definitions()
        for mdfn in mddefns:
            md_keys.add(mdfn.Key)
            md_names[mdfn.Name] = mdfn

        if 'kitsu-uid' not in md_names.keys():
            log('No kistu-uid metadata columnn exists in scene: "%s"' % scene.get_scene_pathname())
            scene.close_scene()
            scene.release()
            return None

        nshots = scene.get_num_shots()
        if nshots == 0:
            log( "No shots founf in the scene %s" % scene.get_scene_pathname() )
            return None
        log( "Found %d shot(s)" % nshots )

        kitsu_shots_by_id = {x['id']: x for x in kitsu_shots}
        bl_shot_ids = scene.get_shot_ids(0, nshots)
        bl_shots_to_render = []
        for bl_shot_id in bl_shot_ids:
            if not self.processing_flag:
                continue

            shot = scene.get_shot(bl_shot_id.ShotId)
            kitsu_uid = ''
            try:
                kitsu_uid = shot.get_metadata_strings(md_names['kitsu-uid'])[md_names['kitsu-uid'].Key]
            except:
                shot.release()
                continue
            
            if kitsu_uid not in kitsu_shots_by_id:
                log(f'Can not find kitsu uid {kitsu_uid} in Kitsu episode')
                shot.release()
                continue

            bl_shots_to_render.append(shot)

        try:
            log( "Creating queue manager" )
            qm = conn.QueueManager.create_local()
        except flapi.FLAPIException as ex:
            log( "Can not create queue manager: %s" % ex )
            return None

        uploaded_thumbnails = []
        for shot_idx, shot in (enumerate(bl_shots_to_render)):
            if not self.processing_flag:
                continue

            try:
                kitsu_uid = shot.get_metadata_strings(md_names['kitsu-uid'])[md_names['kitsu-uid'].Key]
            except:
                shot.release()
                continue

            log (f'Rendering shot {shot_idx + 1} of {len(bl_shots_to_render)}')
            remote_temp_folder = '/var/tmp/'
            local_temp_folder = '/var/tmp'

            try:
                ex = conn.Export.create()
                ex.select_shot(shot)
                exSettings = flapi.StillExportSettings()
                exSettings.ColourSpace = "sRGB"
                exSettings.Format = "HD 1920x1080"
                exSettings.Overwrite = flapi.EXPORT_OVERWRITE_REPLACE
                exSettings.Directory = remote_temp_folder
                exSettings.Frames = flapi.EXPORT_FRAMES_FIRST 
                # exSettings.Filename = "%{Job}/%{Clip}_%{TimelineFrame}"
                # exSettings.Filename = str(shot_id)
                exSettings.Filename = kitsu_uid
                exSettings.Source = flapi.EXPORT_SOURCE_SELECTEDSHOTS

                # print ('')
                # print ('Baselight sequence: %s' % blpath)
                # print ('Generating thumbnail for: "%s" Shot name: "%s"' % (blpath, shot_name))
                log( "Submitting to queue" )
                exportInfo = ex.do_export_still( qm, scene, exSettings)
                waitForExportToComplete(qm, exportInfo)
                del ex
            except Exception as ex:
                log.error( "Can not export thumbnail: %s" % ex )

            local_file_path = self.get_file(
                os.path.join(remote_temp_folder, kitsu_uid + '.jpg'),
                local_temp_folder
            )

            if os.path.isfile(local_file_path):
                try:
                    kitsu_connector.upload_thumbnail(
                        kitsu_uid,
                        local_file_path
                    )
                    uploaded_thumbnails.append(local_file_path)
                except Exception as e:
                    log (f'Unable to upload thumbnail: {pformat(e)}')

                try:
                    os.remove(local_file_path)
                except Exception as e:
                    log (f'Unable to cleanup thumbnail temp file: {local_file_path}')
                    log (pformat(e))

            shot.release()

        log( "Closing QueueManager\n" )
        qm.release()
        scene.close_scene()
        scene.release()
        return uploaded_thumbnails

    def get_file(self, remote_path, local_folder):
        import paramiko
        log = self.log
        local_file_path =  os.path.join(
            local_folder,
            os.path.basename(remote_path)
            )
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add the server's SSH key (insecure)

        ssh.connect(
            self.flapi_host, 
            username=self.flapi_user, 
            password=self.flapi_pass)

        sftp = ssh.open_sftp()
        directory_contents = sftp.listdir(os.path.dirname(remote_path))

        if os.path.basename(remote_path) not in directory_contents:
            log (f'Unable to find file {self.flapi_user}@{self.flapi_host}:{remote_path}')
            sftp.close()
            ssh.close()
            return ''
        
        try:
            sftp.get(remote_path, local_file_path)
        except Exception as e:
            log (f'Unable to get file {self.flapi_user}@{self.flapi_host}:{remote_path}')
            log (pformat(e))
            sftp.close()
            ssh.close()
            return ''

        try:
            sftp.remove(remote_path)
        except Exception as e:
            log (f'Unable to remove file {self.flapi_user}@{self.flapi_host}:{remote_path}')
            log (pformat(e))
            sftp.close()
            ssh.close()
            return ''

        sftp.close()
        ssh.close()
        return local_file_path
