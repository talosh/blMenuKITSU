import os
import sys
import time
import threading
import inspect
import re
import traceback

import gazu

from PyQt5 import QtGui, QtWidgets, QtCore

from pprint import pprint, pformat

class KitsuConnectionError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class appKitsuConnector(object):
    def __init__(self, framework):
        self.name = self.__class__.__name__
        self.framework = framework
        self.app_name = framework.app_name
        self.prefs = self.framework.prefs
        self.connector = self
        self.log('waking up')
        self.gazu_client = None
        self.gazu = gazu
        self.user = None
        self.user_name = None

        self.mbox = self.framework.mbox
        # self.mbox = QtWidgets.QMessageBox()
        self.get_user()
        self.init_pipeline_data()
        self.scan_active_projects()

        '''    
        try:
            self.get_user()
        except Exception as e:
            pass
            #  pprint (e)
            # self.log_debug(pformat(e))
        '''

        '''
        self.prefs = self.framework.prefs_dict(self.framework.prefs, self.name)
        self.prefs_user = self.framework.prefs_dict(self.framework.prefs_user, self.name)
        self.prefs_global = self.framework.prefs_dict(self.framework.prefs_global, self.name)

        site_packages_folder = self.framework.site_packages_folder
        
        if not os.path.isdir(site_packages_folder):
            self.log('unable to find site packages folder at %s' % site_packages_folder)
            self.gazu = None
        else:
            sys.path.insert(0, site_packages_folder)
            import gazu
            self.gazu = gazu
            sys.path.pop(0)


        # defautl values are set here
        if not 'user signed out' in self.prefs_global.keys():
            self.prefs_global['user signed out'] = False

        self.user = None
        self.user_name = None

        if not self.prefs_global.get('user signed out', False):
            self.log_debug('requesting for user')
            try:
                self.get_user()
            except Exception as e:
                self.log_debug(pformat(e))

        if not self.prefs.get('storage_root'):
            self.prefs['storage_root'] = default_storage_root
            self.framework.save_prefs()

        self.flame_project = None
        self.linked_project = None
        self.linked_project_id = None

        self.init_pipeline_data()
        self.shot_code_field = shot_code_field

        self.check_linked_project()

        self.loops = []
        self.threads = True
        self.loops.append(threading.Thread(target=self.cache_loop, args=(8, )))

        # self.loops.append(threading.Thread(target=self.cache_short_loop, args=(8, )))
        # self.loops.append(threading.Thread(target=self.cache_long_loop, args=(8, )))
        # self.loops.append(threading.Thread(target=self.cache_utility_loop, args=(1, )))

        for loop in self.loops:
            loop.daemon = True
            loop.start()
        '''

    def log(self, message):
        self.framework.log('[' + self.name + '] ' + str(message))

    def log_debug(self, message):
        self.framework.log_debug('[' + self.name + '] ' + str(message))

    def get_user(self, *args, **kwargs):

        msg = kwargs.get('msg')

        # get saved credentials
        import base64
        self.gazu_client = None
        self.kitsu_host = self.prefs.get('kitsu_host', 'http://localhost/api/')
        self.kitsu_user = self.prefs.get('kitsu_user', 'user@host')
        self.kitsu_pass = ''
        encoded_kitsu_pass = self.prefs.get('kitsu_pass', '')
        if encoded_kitsu_pass:
            self.kitsu_pass = base64.b64decode(encoded_kitsu_pass).decode("utf-8")

        def login(msg=True):
            try:
                host = self.kitsu_host                
                if not host.endswith('/api/'):
                    if self.kitsu_host.endswith('/'):
                        host = host + 'api/'
                    else:
                        host = host + '/api/'
                elif host.endswith('/api'):
                    host = host + ('/')
                
                self.gazu_client = self.gazu.client.create_client(host)
                if not self.gazu.client.host_is_up(client = self.gazu_client):
                    raise KitsuConnectionError(f'Host {host} is unreachable')
                result = gazu.log_in(self.kitsu_user, self.kitsu_pass, client = self.gazu_client)
                self.user = self.gazu.client.get_current_user(client = self.gazu_client)
                self.user_name = self.user.get('full_name')
                self.log_debug('connected to kitsu as %s' % self.user_name)
                return True
            except Exception as e:
                self.gazu_client = None
                self.user = None
                self.user_name = None
                if msg:
                    self.mbox.setText(pformat(e))
                    self.mbox.exec_()
            return False

        login_status = login(msg)
        return login_status

        '''
        while not login_status:
            credentials = self.login_dialog()
            if not credentials:
                self.prefs_global['user signed out'] = True
                self.kitsu_pass = ''
                break
            else:
                self.kitsu_host = credentials.get('host')
                self.kitsu_user = credentials.get('user')
                self.kitsu_pass = credentials.get('password', '')
                login_status = login()
        '''

        # self.log_debug(pformat(self.user))
        # self.log_debug(self.user_name)

        # self.prefs['kitsu_host'] = self.kitsu_host
        # self.prefs['kitsu_user'] = self.kitsu_user
        # self.prefs['kitsu_pass'] = base64.b64encode(self.kitsu_pass.encode("utf-8"))
        # self.framework.save_prefs()

    def get_gazu_version(self):
        if not self.gazu:
            return None
        return self.gazu.__version__

    def get_api_version(self):
        if not self.gazu:
            return None
        if not self.gazu_client:
            return None
        try:
            return self.gazu.client.get_api_version(client = self.gazu_client)
        except:
            return None

    def clear_user(self, *args, **kwargs):
        try:
            self.gazu.log_out(client = self.gazu_client)
        except Exception as e:
            self.log(pformat(e))

        self.gazu_client = None
        self.user = None
        self.user_name = None
        self.prefs_user['kitsu_pass'] = ''
        self.framework.save_prefs()

    def check_linked_project(self, *args, **kwargs):
        try:
            import flame
        except:
            self.log_debug('no flame module avaliable to import')
            return False
        try:
            if self.flame_project != flame.project.current_project.name:
                self.log_debug('updating flame project name: %s' % flame.project.current_project.name)
                self.flame_project = flame.project.current_project.name
        except:
            return False

        try:
            if self.linked_project != flame.project.current_project.shotgun_project_name:
                self.log_debug('updating linked project: %s' % flame.project.current_project.shotgun_project_name)
                self.linked_project = flame.project.current_project.shotgun_project_name.get_value()
        except:
            return False

        if self.user:
            self.log_debug('updating project id')
            project = self.gazu.project.get_project_by_name(self.linked_project, client = self.gazu_client)
            if project:
                self.linked_project_id = project.get('id')
            else:
                self.log_debug('no project id found for project name: %s' % flame.project.current_project.shotgun_project_name)
        return True

    def init_pipeline_data(self):
        self.pipeline_data = self.framework.kitsu_data
        self.pipeline_data['active_projects'] = []
        self.pipeline_data['episodes_by_project_id'] = {}

        '''
        self.pipeline_data['current_project'] = {}
        self.pipeline_data['project_tasks_for_person'] = []
        self.pipeline_data['all_episodes_for_project'] = []
        self.pipeline_data['all_sequences_for_project'] = []
        self.pipeline_data['all_shots_for_project'] = []
        self.pipeline_data['all_assets_for_project'] = []
        self.pipeline_data['entitiy_keys'] = set()
        self.pipeline_data['tasks_by_entity_id'] = {}
        self.pipeline_data['preview_by_task_id'] = {}
        self.pipeline_data['all_task_types_for_project'] = []
        self.pipeline_data['all_task_statuses_for_project'] = []
        self.pipeline_data['entity_by_id'] = {}
        '''

    def cache_loop(self, timeout):
        avg_delta = timeout / 2
        recent_deltas = [avg_delta]*9
        while self.threads:
            start = time.time()                
            
            if (not self.user):
                time.sleep(1)
                continue

            self.scan_active_projects()
            project_names = new_list = [d.get('name', 'unnamed project') for d in self.pipeline_data['active_projects']]
            pprint (project_names)

            # projects_by_id = {x.get('id'):x for x in self.pipeline_data['active_projects']}
            
            # self.collect_pipeline_data(current_project=current_project, current_client=shortloop_gazu_client)

            # self.gazu.log_out(client = shortloop_gazu_client)

            # self.preformat_common_queries()

            delta = time.time() - start
            self.log_debug('cache_short_loop took %s sec' % str(delta))

            last_delta = recent_deltas[len(recent_deltas) - 1]
            recent_deltas.pop(0)
            
            if abs(delta - last_delta) > last_delta*3:
                delta = last_delta*3

            recent_deltas.append(delta)
            avg_delta = sum(recent_deltas)/float(len(recent_deltas))
            if avg_delta > timeout/2:
                self.loop_timeout(avg_delta*2, start)
            else:
                self.loop_timeout(timeout, start)

    def cache_short_loop(self, timeout):
        avg_delta = timeout / 2
        recent_deltas = [avg_delta]*9
        while self.threads:
            start = time.time()                
            
            if (not self.user) and (not self.linked_project_id):
                time.sleep(1)
                continue

            shortloop_gazu_client = None
            try:
                host = self.kitsu_host
                if not host.endswith('/api/'):
                    if self.kitsu_host.endswith('/'):
                        host = host + 'api/'
                    else:
                        host = host + '/api/'
                elif host.endswith('/api'):
                    host = host + ('/')
                shortloop_gazu_client = self.gazu.client.create_client(host)
                self.gazu.log_in(self.kitsu_user, self.kitsu_pass, client=shortloop_gazu_client)
                # self.cache_update(shortloop_gazu_client)
            except Exception as e:
                self.log_debug('error soft updating cache in cache_short_loop: %s' % e)

            if self.user and shortloop_gazu_client:
                try:
                    self.pipeline_data['active_projects'] = self.gazu.project.all_open_projects(client=shortloop_gazu_client)
                    if not self.pipeline_data['active_projects']:
                        self.pipeline_data['active_projects'] = [{}]
                except Exception as e:
                    self.log(pformat(e))

            if not self.linked_project_id:
                self.log_debug('short loop: no id')
                self.gazu.log_out(client = shortloop_gazu_client)
                time.sleep(1)
                continue
            
            active_projects = self.pipeline_data.get('active_projects')
            if not active_projects:
                self.log_debug('no active_projects')
                self.gazu.log_out(client = shortloop_gazu_client)
                time.sleep(1)
                continue

            projects_by_id = {x.get('id'):x for x in self.pipeline_data['active_projects']}
            current_project = projects_by_id.get(self.linked_project_id)
            
            self.collect_pipeline_data(current_project=current_project, current_client=shortloop_gazu_client)

            self.gazu.log_out(client = shortloop_gazu_client)

            # self.preformat_common_queries()

            delta = time.time() - start
            self.log_debug('cache_short_loop took %s sec' % str(delta))

            last_delta = recent_deltas[len(recent_deltas) - 1]
            recent_deltas.pop(0)
            
            if abs(delta - last_delta) > last_delta*3:
                delta = last_delta*3

            recent_deltas.append(delta)
            avg_delta = sum(recent_deltas)/float(len(recent_deltas))
            if avg_delta > timeout/2:
                self.loop_timeout(avg_delta*2, start)
            else:
                self.loop_timeout(timeout, start)

    def cache_long_loop(self, timeout):
        avg_delta = timeout / 2
        recent_deltas = [avg_delta]*9
        while self.threads:
            start = time.time()

            if (not self.user) and (not self.linked_project_id):
                time.sleep(1)
                continue

            longloop_gazu_client = None
            try:
                host = self.kitsu_host
                if not host.endswith('/api/'):
                    if self.kitsu_host.endswith('/'):
                        host = host + 'api/'
                    else:
                        host = host + '/api/'
                elif host.endswith('/api'):
                    host = host + ('/')
                longloop_gazu_client = self.gazu.client.create_client(host)
                self.gazu.log_in(self.kitsu_user, self.kitsu_pass, client=longloop_gazu_client)

                # main job body
                for entity_key in self.pipeline_data.get('entitiy_keys'):
                    self.collect_entity_linked_info(entity_key, current_client = longloop_gazu_client)
                
            except Exception as e:
                self.log_debug('error updating cache in cache_long_loop: %s' % e)

            self.gazu.log_out(client = longloop_gazu_client)
            
            # self.preformat_common_queries()

            self.log_debug('cache_long_loop took %s sec' % str(time.time() - start))
            delta = time.time() - start
            last_delta = recent_deltas[len(recent_deltas) - 1]
            recent_deltas.pop(0)
            
            if abs(delta - last_delta) > last_delta*3:
                delta = last_delta*3

            recent_deltas.append(delta)
            avg_delta = sum(recent_deltas)/float(len(recent_deltas))
            if avg_delta > timeout/2:
                self.loop_timeout(avg_delta*2, start)
            else:
                self.loop_timeout(timeout, start)

    def cache_utility_loop(self, timeout):
        while self.threads:
            start = time.time()                
            
            if (not self.user) and (not self.linked_project_id):
                time.sleep(1)
                continue

            # pprint (self.pipeline_data['current_project'])

            self.loop_timeout(timeout, start)

    def collect_pipeline_data(self, current_project = None, current_client = None):
        if not current_client:
            current_client = self.gazu_client

        self.scan_active_projects()
        self.get_episodes_for_projects()

        '''
        # query requests defined as functions

        def get_current_project():
            try:
                current_project = self.gazu.project.get_project(self.linked_project_id, client=current_client)
                self.pipeline_data['current_project'] = dict(current_project)
                self.pipeline_data['entity_by_id'][current_project.get('id')] = dict(current_project)
            except Exception as e:
                self.log(pformat(e))

        def project_tasks_for_person():
            try:
                all_tasks_for_person = self.gazu.task.all_tasks_for_person(self.user, client=current_client)
                all_tasks_for_person.extend(self.gazu.task.all_done_tasks_for_person(self.user, client=current_client))
                project_tasks_for_person = []
                for x in all_tasks_for_person:
                    if x.get('project_id') == self.linked_project_id:
                        project_tasks_for_person.append(x)
                self.pipeline_data['project_tasks_for_person'] = list(project_tasks_for_person)
                for task in project_tasks_for_person:
                    self.pipeline_data['entitiy_keys'].add((task.get('entity_type_name'), task.get('entity_id')))
            except Exception as e:
                self.log(pformat(e))

        def all_episodes_for_project():
            try:
                all_episodes_for_project = self.gazu.shot.all_episodes_for_project(current_project, client=current_client)
                if not isinstance(all_episodes_for_project, list):
                    all_episodes_for_project = []
                                 
                episodes = []
                for episode in all_episodes_for_project:
                    episode_assets = self.gazu.asset.all_assets_for_episode(episode, client=current_client)
                    if not isinstance(episode_assets, list):
                        episode_assets = []
                    episode_assets_by_id = {x.get('id'):x for x in episode_assets}
                    episode['assets'] = episode_assets
                    episode['assets_by_id'] = episode_assets_by_id
                    
                    episode_shots = self.gazu.shot.all_shots_for_episode(episode, client=current_client)
                    if not isinstance(episode_shots, list):
                        episode_shots = []
                    episode_shots_by_id = {x.get('id'):x for x in episode_shots}
                    episode['shots'] = episode_shots
                    episode['shots_by_id'] = episode_shots_by_id

                    episodes.append(episode)

                self.pipeline_data['all_episodes_for_project'] = list(episodes)
                for entity in all_episodes_for_project:
                    self.pipeline_data['entitiy_keys'].add((entity.get('type'), entity.get('id')))
                    self.pipeline_data['entity_by_id'][entity.get('id')] = entity
            except Exception as e:
                self.log(pformat(e))

        def all_assets_for_project():
            try:
                assets_with_modified_code = []
                all_assets_for_project = self.gazu.asset.all_assets_for_project(current_project, client=current_client)
                
                for asset in all_assets_for_project:
                    asset['code'] = asset['name']
                    if self.shot_code_field:
                        data = asset.get('data')
                        if data:
                            code = data.get(shot_code_field)
                            if code:
                                asset['code'] = code
                    assets_with_modified_code.append(asset)

                episodes = self.connector.pipeline_data.get('all_episodes_for_project')
                episodes_by_id = {x.get('id'):x for x in episodes}
                episode_id_by_entity_id = {}
                for episode in episodes:
                    episode_id = episode.get('id')
                    if not episode_id:
                        continue
                    episode_assets_by_id = episode.get('assets_by_id')
                    if not episode_assets_by_id:
                        episode_assets_by_id = {}
                    for asset_id in episode_assets_by_id.keys():
                        episode_id_by_entity_id[asset_id] = episode_id
                    episode_shots_by_id = episode.get('shots_by_id')
                    if not episode_shots_by_id:
                        episode_shots_by_id = {}
                    for shot_id in episode_shots_by_id.keys():
                        episode_id_by_entity_id[shot_id] = episode_id
                for asset in assets_with_modified_code:
                    asset_episode_id = episode_id_by_entity_id.get(asset.get('id'))
                    asset_episode_name = None
                    if asset_episode_id:
                        asset_episode = episodes_by_id.get(asset_episode_id)
                        if asset_episode:
                            asset_episode_name = asset_episode.get('name')
                    asset['episode_id'] = asset_episode_id
                    asset['episode_name'] = asset_episode_name

                
                self.pipeline_data['all_assets_for_project'] = list(assets_with_modified_code)
                for entity in assets_with_modified_code:
                    self.pipeline_data['entitiy_keys'].add((entity.get('type'), entity.get('id')))
                    self.pipeline_data['entity_by_id'][entity.get('id')] = entity
            except Exception as e:
                self.log(pformat(e))

        def all_shots_for_project():
            try:
                shots_with_modified_code = []
                all_shots_for_project = self.gazu.shot.all_shots_for_project(current_project, client=current_client)
                for shot in all_shots_for_project:
                    shot['code'] = shot['name']
                    if self.shot_code_field:
                        data = shot.get('data')
                        if data:
                            code = data.get(shot_code_field)
                            if code:
                                shot['code'] = code
                    shots_with_modified_code.append(shot)
            
                episodes = self.connector.pipeline_data.get('all_episodes_for_project')
                episodes_by_id = {x.get('id'):x for x in episodes}
                episode_id_by_entity_id = {}
                for episode in episodes:
                    episode_id = episode.get('id')
                    if not episode_id:
                        continue
                    episode_assets_by_id = episode.get('assets_by_id')
                    if not episode_assets_by_id:
                        episode_assets_by_id = {}
                    for asset_id in episode_assets_by_id.keys():
                        episode_id_by_entity_id[asset_id] = episode_id
                    episode_shots_by_id = episode.get('shots_by_id')
                    if not episode_shots_by_id:
                        episode_shots_by_id = {}
                    for shot_id in episode_shots_by_id.keys():
                        episode_id_by_entity_id[shot_id] = episode_id

                for shot in shots_with_modified_code:
                    shot_episode_id = episode_id_by_entity_id.get(shot.get('id'))
                    shot_episode_name = None
                    if shot_episode_id:
                        shot_episode = episodes_by_id.get(shot_episode_id)
                        if shot_episode:
                            shot_episode_name = shot_episode.get('name')
                    shot['episode_id'] = shot_episode_id
                    shot['episode_name'] = shot_episode_name

                self.pipeline_data['all_shots_for_project'] = list(shots_with_modified_code)
                for entity in shots_with_modified_code:
                    self.pipeline_data['entitiy_keys'].add((entity.get('type'), entity.get('id')))
                    self.pipeline_data['entity_by_id'][entity.get('id')] = entity
            except Exception as e:
                self.log(pformat(e))

        def all_sequences_for_project():
            try:
                all_sequences_for_project = self.gazu.shot.all_sequences_for_project(current_project, client=current_client)
                self.pipeline_data['all_sequences_for_project'] = list(all_sequences_for_project)
                for entity in all_sequences_for_project:
                    self.pipeline_data['entitiy_keys'].add((entity.get('type'), entity.get('id')))
                    self.pipeline_data['entity_by_id'][entity.get('id')] = entity
            except Exception as e:
                self.log(pformat(e))

        def all_task_types_for_project():
            try:
                all_task_types_for_project = self.connector.gazu.task.all_task_types_for_project(current_project, client=current_client)
                self.pipeline_data['all_task_types_for_project'] = list(all_task_types_for_project)
            except Exception as e:
                self.log(pformat(e))

        def all_task_statuses_for_project():
            try:
                all_task_types_for_project = self.connector.gazu.task.all_task_statuses_for_project(current_project, client=current_client)
                self.pipeline_data['all_task_statuses_for_project'] = list(all_task_types_for_project)
            except Exception as e:
                self.log(pformat(e))

        requests = []
        requests.append(threading.Thread(target=get_current_project, args=()))
        requests.append(threading.Thread(target=project_tasks_for_person, args=()))
        requests.append(threading.Thread(target=all_episodes_for_project, args=()))
        requests.append(threading.Thread(target=all_assets_for_project, args=()))
        requests.append(threading.Thread(target=all_shots_for_project, args=()))
        requests.append(threading.Thread(target=all_sequences_for_project, args=()))
        requests.append(threading.Thread(target=all_task_types_for_project, args=()))
        requests.append(threading.Thread(target=all_task_statuses_for_project, args=()))

        for request in requests:
            request.daemon = True
            request.start()

        for request in requests:
            request.join()

        # this block is to add episode id and name to shot or asset
        episodes = self.connector.pipeline_data.get('all_episodes_for_project')
        episodes_by_id = {x.get('id'):x for x in episodes}
        episode_id_by_entity_id = {}
        for episode in episodes:
            episode_id = episode.get('id')
            if not episode_id:
                continue
            episode_assets_by_id = episode.get('assets_by_id')
            if not episode_assets_by_id:
                episode_assets_by_id = {}
            for asset_id in episode_assets_by_id.keys():
                episode_id_by_entity_id[asset_id] = episode_id
            episode_shots_by_id = episode.get('shots_by_id')
            if not episode_shots_by_id:
                episode_shots_by_id = {}
            for shot_id in episode_shots_by_id.keys():
                episode_id_by_entity_id[shot_id] = episode_id
        for asset in self.connector.pipeline_data.get('all_assets_for_project'):
            asset_episode_id = episode_id_by_entity_id.get(asset.get('id'))
            asset_episode_name = None
            if asset_episode_id:
                asset_episode = episodes_by_id.get(asset_episode_id)
                if asset_episode:
                    asset_episode_name = asset_episode.get('name')
            asset['episode_id'] = asset_episode_id
            asset['episode_name'] = asset_episode_name
        for shot in self.connector.pipeline_data.get('all_shots_for_project'):
            shot_episode_id = episode_id_by_entity_id.get(shot.get('id'))
            shot_episode_name = None
            if shot_episode_id:
                shot_episode = episodes_by_id.get(shot_episode_id)
                if shot_episode:
                    shot_episode_name = shot_episode.get('name')
            shot['episode_id'] = shot_episode_id
            shot['episode_name'] = shot_episode_name
        '''

    def collect_entity_linked_info(self, entity_key, current_client = None):
        if not current_client:
            current_client = self.gazu_client

        entity_type, entity_id = entity_key

        if entity_type == 'Shot':
            shot_tasks = self.gazu.task.all_tasks_for_shot({'id': entity_id}, client = current_client)
            self.pipeline_data['tasks_by_entity_id'][entity_id] = shot_tasks
            for task in shot_tasks:
                task_preview_files = self.gazu.files.get_all_preview_files_for_task(
                    {'id': task.get('id')},
                    client = current_client)
                self.pipeline_data['preview_by_task_id'][task.get('id')] = task_preview_files

    def terminate_loops(self):
        self.threads = False
        
        for loop in self.loops:
            loop.join()

    def loop_timeout(self, timeout, start):
        time_passed = int(time.time() - start)
        if timeout <= time_passed:
            return
        else:
            for n in range(int(timeout - time_passed) * 10):
                if not self.threads:
                    self.log_debug('leaving loop thread: %s' % inspect.currentframe().f_back.f_code.co_name)
                    break
                time.sleep(0.1)

    def scan_active_projects(self):
        if self.user:
            try:
                self.pipeline_data['active_projects'] = self.gazu.project.all_open_projects(client=self.gazu_client)
                if not self.pipeline_data['active_projects']:
                    self.pipeline_data['active_projects'] = [{}]
            except Exception as e:
                self.log(pformat(e))

    def get_episodes_for_projects(self):
        projects = self.pipeline_data.get('active_projects', list())
        for project in projects:
            project_id = project.get('id', 'unknown_id')
            all_episodes_for_project = self.gazu.shot.all_episodes_for_project(project, client = self.gazu_client)
            self.pipeline_data['episodes_by_project_id'][project_id] = list(all_episodes_for_project)

    def resolve_storage_root(self):
        storage_root = self.prefs.get('storage_root')
        return storage_root
