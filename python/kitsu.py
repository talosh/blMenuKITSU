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
                
                self.gazu.set_host(host)
                self.gazu.log_in(self.kitsu_user, self.kitsu_pass)

                self.gazu_client = self.gazu.client.create_client(host)
                if not self.gazu.client.host_is_up(client = self.gazu_client):
                    raise KitsuConnectionError(f'Host {host} is unreachable')
                result = self.gazu.log_in(self.kitsu_user, self.kitsu_pass, client = self.gazu_client)
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

    def get_kitsu_sequence(self, current_project, current_episode, bl_path):
        def all_sequences_for_project():
            all_sequences_for_project = []
            try:
                all_sequences_for_project = self.gazu.shot.all_sequences_for_project(current_project, client=self.gazu_client)
                # self.pipeline_data['all_sequences_for_project'] = list(all_sequences_for_project)
                # for entity in all_sequences_for_project:
                #     self.pipeline_data['entitiy_keys'].add((entity.get('type'), entity.get('id')))
                #     self.pipeline_data['entity_by_id'][entity.get('id')] = entity
            except Exception as e:
                self.log(pformat(e))
            return all_sequences_for_project
        # pprint (current_project)
        # pprint (current_episode)

        all_sequences = all_sequences_for_project()

        current_episode_id = current_episode.get('id')
        current_episode_sequences = []
        for sequence in all_sequences:
            if sequence.get('parent_id') == current_episode_id:
                current_episode_sequences.append(sequence)

        for sequence in current_episode_sequences:
            data = sequence.get('data')
            if data is None:
                continue
            if not isinstance(data, dict):
                continue
            if data.get('blpath') == bl_path:
                return sequence
        
        bl_scene_name = 'DefaultScene'
        try:
            bl_scene_name = bl_path.split(':')[-1]
        except Exception as e:
            self.log(f'Unable to get scene name: {pformat(e)}')

        for sequence in current_episode_sequences:
            if sequence.get('name') == bl_scene_name:
                return sequence
            
        return None

    def create_kitsu_sequence(self, current_project, current_episode, bl_path):
        bl_scene_name = 'DefaultScene'
        try:
            bl_scene_name = bl_path.split(':')[-1]
        except Exception as e:
            self.log(f'Unable to get scene name: {pformat(e)}')

        # try to create new sequence
        new_sequence = {}
        try:
            new_sequence = self.gazu.shot.new_sequence(
                current_project,
                bl_scene_name,
                episode=current_episode,
                client=self.gazu_client
            )
        except Exception as e:
            self.log(f'Unable to create sequence: {pformat(e)}')

        return new_sequence

    def get_shots_for_sequence(self, current_sequence):
        kitsu_shots = []
        try:
            kitsu_shots = gazu.shot.all_shots_for_sequence(current_sequence, client=self.gazu_client)
        except Exception as e:
            self.log(f'Unable to get shots from kitsu sequence: {pformat(e)}')
        return kitsu_shots
    
    def get_shots_for_episode(self, episode):
        shots = self.gazu.shot.all_shots_for_episode(episode, client=self.gazu_client)
        return shots

    def shots_without_previews(self, kitsu_shots):
        shots_without_preview = []
        for kitsu_shot in kitsu_shots:
            shot = self.gazu.shot.get_shot(
                kitsu_shot.get('id'),
                client = self.gazu_client)
            if shot:
                preview_files = self.gazu.shot.all_previews_for_shot(
                    shot,
                    client = self.gazu_client)
                if preview_files:
                    continue
                shots_without_preview.append(shot)
        
        return shots_without_preview

    def get_metadata_descriptors(self):
        # currently hardcoded
        return [
            {
                "name": "00.Shot-ID",
                "kitsu_key": "00_shot_id",
                "bl_metadata_key": "event",
                "padding": 4,
                "entity_type": "Shot"
            },
            {
                "name": "01.Locator",
                "kitsu_key": "01_locator",
                "bl_metadata_name": "01.Locator",
                "entity_type": "Shot"
            },
            {
                "name": "02.Prod-Opt-Notes",
                "kitsu_key": "02_prod_otp_notes",
                "bl_metadata_name": "02.Prod-Opt-Notes",
                "entity_type": "Shot"
            },
            {
                "name": "03.Conform-Notes",
                "entity_type": "Shot"
            },
            {
                "name": "04.Opt-Done",
                "entity_type": "Shot"
            },
            {
                "name": "05.Has Speed Change",
                "entity_type": "Shot"
            },
            {
                "name": "06.DL-Time-Est",
                "kitsu_key": "06_dl_time_est",
                "bl_metadata_name": "06.DL-Time-Est",
                "entity_type": "Shot"
            },
            {
                "name": "07.DL-Needs-Prod-Atn",
                "entity_type": "Shot"
            },
            {
                "name": "08.DL-Producer-Notes",
                "entity_type": "Shot"
            },
            {
                "name": "09.EDL-event",
                "entity_type": "Shot"
            },
            {
                "name": "10.Tape",
                "kitsu_key": "10_tape",
                "bl_metadata_key": "tape",
                "entity_type": "Shot"
            },
            {
                "name": "11.Source TC Start",
                "kitsu_key": "11_source_tc_start",
                "bl_metadata_key": "srctc.0",
                "entity_type": "Shot"
            },
            {
                "name": "12.Source TC End",
                "kitsu_key": "12_source_tc_end",
                "bl_metadata_key": "srctc.1",
                "entity_type": "Shot"
            },
            {
                "name": "13.Record TC Start",
                "kitsu_key": "13_record_tc_start",
                "bl_metadata_key": "rectc.0",
                "entity_type": "Shot"
            },
            {
                "name": "14.Record TC End",
                "kitsu_key": "14_record_tc_end",
                "bl_metadata_key": "rectc.1",
                "entity_type": "Shot"
            },
            {
                "name": "15.Vers-in-Baselight",
                "entity_type": "Shot"
            },
            {
                "name": "16.Vers-Prod-Final",
                "entity_type": "Shot"
            },
            {
                "name": "17.Vendor",
                "entity_type": "Shot"
            },
            {
                "name": "18.DL-Import-Date",
                "entity_type": "Shot"
            },
            {
                "name": "19.EDL-Comment",
                "entity_type": "Shot"
            },
            {
                "name": "21.Turnover-Package",
                "entity_type": "Shot"
            },
            {
                "name": "22.Prod TC In",
                "entity_type": "Shot"
            },
            {
                "name": "23.Prod TC Out",
                "entity_type": "Shot"
            },
            {
                "name": "25.Rec-Frame",
                "entity_type": "Shot"
            },
            {
                "name": "26.BL-Shot-Filename",
                "entity_type": "Shot"
            },
            {
                "name": "27.VFX-Latest-Pub",
                "entity_type": "Shot"
            },
            {
                "name": "28.DL-VFX-cost-est",
                "kitsu_key": "28_dl_vfx_cost_est",
                "bl_metadata_name": "28.DL-VFX-cost-est",
                "entity_type": "Shot"
            },
            {
                "name": "29.DL-VFX-hours-est",
                "kitsu_key": "29_dl_vfx_hours_est",
                "bl_metadata_name": "29.DL-VFX-hours-est",
                "entity_type": "Shot"
            },
            {
                "name": "30.DL-VFX-ID",
                "kitsu_key": "30_dl_vfx_id",
                "bl_metadata_name": "vfx-id",
                "entity_type": "Shot"
            }
        ]

    def build_kitsu_shot_data(self, baselight_shot):
        data = {}
        md_descriptors = self.get_metadata_descriptors()
        md_descriptors_by_bl_key = {}
        for md_desc in md_descriptors:
            bl_key = md_desc.get('bl_metadata_key')
            if not bl_key:
                bl_name = md_desc.get('bl_metadata_name')
                if not bl_name:
                    continue
                else:
                    mddefns = baselight_shot.get('mddefns')
                    for md_def in mddefns:
                        name = md_def.Name
                        if name == bl_name:
                            bl_key = md_def.Key
                            md_descriptors_by_bl_key[bl_key] = md_desc
                    continue
            md_descriptors_by_bl_key[bl_key] = md_desc
        shot_md = baselight_shot.get('shot_md')
        for bl_key in md_descriptors_by_bl_key.keys():
            kitsu_key = md_descriptors_by_bl_key[bl_key].get('kitsu_key')
            value = str(shot_md.get(bl_key))
            if 'padding' in md_descriptors_by_bl_key[bl_key].keys():
                padding = md_descriptors_by_bl_key[bl_key].get('padding', 0)
                value = value.zfill(padding)
            data[kitsu_key] = value
        return data

    def update_and_get_new_shots(self, baselight_linked_sequence):
        log = self.log
        log_debug = self.log_debug
        gazu = self.gazu
        
        log ('---')
        log ('--- Populating Kitsu from baselight sequence ---')
        log (baselight_linked_sequence.get('blpath'))

        # shot = gazu.shot.get_shot('412aa6b2-5d30-49c1-84b8-631b8c15fd3c')
        # pprint (shot)

        blpath = baselight_linked_sequence.get('blpath')

        kitsu_uid_metadata_obj = baselight_linked_sequence.get('kitsu_uid_metadata_obj')
    
        if not kitsu_uid_metadata_obj:
            return None

        baselight_shots = baselight_linked_sequence.get('baselight_shots')
        project_dict = gazu.project.get_project(baselight_linked_sequence.get('project_id'), client=self.gazu_client)
        kitsu_shots = baselight_linked_sequence.get('kitsu_shots')

        kitsu_shot_uids = set()
        for kitsu_shot in kitsu_shots:
            kitsu_shot_uids.add(kitsu_shot.get('id'))

        new_shots = []
        
        log('Looking for metadata updates...')
        for shot_ix, baselight_shot in enumerate(baselight_shots):        
            log( "Checking KITSU metadata against Baselight for shot %d of %s" % (shot_ix + 1, len(baselight_shots)))
            shot_md = baselight_shot.get('shot_md')
            if not shot_md:
                continue

            bl_kitsu_uid = shot_md.get(kitsu_uid_metadata_obj.Key)
            if bl_kitsu_uid in kitsu_shot_uids:

                new_data = {}
                bl_shot_data = self.build_kitsu_shot_data(baselight_shot)
                kitsu_shot = gazu.shot.get_shot(bl_kitsu_uid, client=self.gazu_client)
                kitsu_shot_data = kitsu_shot.get('data', dict())

                for data_key in bl_shot_data.keys():
                    if kitsu_shot_data.get(data_key):
                        continue
                    else:
                        if bl_shot_data.get(data_key):
                            new_data[data_key] = bl_shot_data.get(data_key)

                if not new_data:
                    continue
                
                for new_data_key in new_data.keys():
                    kitsu_shot_data[new_data_key] = new_data.get(new_data_key)
                kitsu_shot['data'] = kitsu_shot_data
                log.info('updating shot: %s' % kitsu_shot.get('name'))
                gazu.shot.update_shot(kitsu_shot, client=self.gazu_client)
                pprint (new_data)
                continue

            else:
                new_shots.append(baselight_shot)

        return new_shots

    def create_kitsu_shot_name(self, baselight_shot):
        import uuid
        shot_md = baselight_shot.get('shot_md')
        if not shot_md:
            return ((str(uuid.uuid1()).replace('-', '')).upper())[:4]
        rectc_in = shot_md.get('rectc.0')
        if not rectc_in:
            return ((str(uuid.uuid1()).replace('-', '')).upper())[:4]
        return str(rectc_in)

    def build_kitsu_shot_data(self, baselight_shot):
        data = {}
        md_descriptors = self.get_metadata_descriptors()
        md_descriptors_by_bl_key = {}
        for md_desc in md_descriptors:
            bl_key = md_desc.get('bl_metadata_key')
            if not bl_key:
                bl_name = md_desc.get('bl_metadata_name')
                if not bl_name:
                    continue
                else:
                    mddefns = baselight_shot.get('mddefns')
                    for md_def in mddefns:
                        name = md_def.Name
                        if name == bl_name:
                            bl_key = md_def.Key
                            md_descriptors_by_bl_key[bl_key] = md_desc
                    continue
            md_descriptors_by_bl_key[bl_key] = md_desc
        shot_md = baselight_shot.get('shot_md')
        for bl_key in md_descriptors_by_bl_key.keys():
            kitsu_key = md_descriptors_by_bl_key[bl_key].get('kitsu_key')
            value = str(shot_md.get(bl_key))
            if 'padding' in md_descriptors_by_bl_key[bl_key].keys():
                padding = md_descriptors_by_bl_key[bl_key].get('padding', 0)
                value = value.zfill(padding)
            data[kitsu_key] = value
        return data

    def create_metadata_fields(self, project):
        log = self.log
        log_debug = self.log_debug
        project_descriptor_data = self.gazu.project.all_metadata_descriptors(project, client=self.gazu_client)
        # descriptors_api_path = '/data/projects/' + project.get('id') + '/metadata-descriptors'
        # project_descriptor_data = self.gazu.client.get(descriptors_api_path, client = self.gazu_client)
        project_descriptor_names = [x['name'] for x in project_descriptor_data]
        
        for metadata_descriptor in self.get_metadata_descriptors():
            metadata_descriptor_name = metadata_descriptor.get('name')
            if not metadata_descriptor_name:
                continue
            if metadata_descriptor_name not in project_descriptor_names:
                if metadata_descriptor_name.lower() in project_descriptor_names:
                    continue
                
                data = {
                    'choices': [],
                    'for_client': False,
                    'entity_type': 'Shot',
                    'departments': []
                }

                for key in metadata_descriptor.keys():
                    data[key] = metadata_descriptor[key]

                log ('creating %s in %s' % (metadata_descriptor_name, project.get('name')))
                self.gazu.project.add_metadata_descriptor(
                    project,
                    metadata_descriptor_name,
                    'Shot',
                    client = self.gazu_client
                )

                # self.gazu.client.post(descriptors_api_path, data, client = self.gazu_client)

    def create_new_shot(self, project_dict, kitsu_sequence, shot_name, shot_data):
        new_shot = None
        try:
            new_shot = self.gazu.shot.new_shot(
                project_dict, 
                kitsu_sequence, 
                shot_name,
                data = shot_data,
                client=self.gazu_client
                # data = {'00_shot_id': baselight_shot.get('shot_id')}
            )
        except Exception as e:
            self.log(pformat(e))

        return new_shot
    
    def upload_thumbnail(self, kitsu_uid, file_path):
        log = self.log
        online_task_name = 'Online'

        new_shot = self.gazu.entity.get_entity(kitsu_uid, client=self.gazu_client)

        task_types = self.gazu.task.all_task_types(client=self.gazu_client)
        shot_task_types = [t for t in task_types if t['for_entity'] == 'Shot']
        shot_task_types = sorted(shot_task_types, key=lambda d: d['priority'])

        task = {}
        shot_tasks = self.gazu.task.all_tasks_for_shot(new_shot)
        for shot_task in shot_tasks:
            if shot_task.get('name') == online_task_name:
                task = shot_task
                break

        if not task:
            task = self.gazu.task.new_task(
                new_shot, 
                shot_task_types[0],
                name = online_task_name,
                client = self.gazu_client
                )

        todo = self.gazu.task.get_task_status_by_short_name("todo", client=self.gazu_client)
        comment = self.gazu.task.add_comment(task, todo, "Add thumbnail", client=self.gazu_client)

        log('Adding preview on task "%s"' % shot_task_types[0].get('name'))
        preview_file = self.gazu.task.add_preview(
            task,
            comment,
            file_path,
            client=self.gazu_client
        )

        log('Uploading thumbnail for shot: "%s"' % new_shot.get('name'))
        self.gazu.task.set_main_preview(preview_file, client=self.gazu_client)


        '''

        # try to open baselight scene and fill the shots back in with kitsu-related metadata
        flapi = import_flapi(config)
        flapi_host = resolve_flapi_host(config, blpath)

        conn = fl_connect(config, flapi, flapi_host)
        if not conn:
            return None
        scene_path = fl_get_scene_path(config, flapi, conn, blpath)
        if not scene_path:
            return None

        log.verbose( "Opening QueueManager connection" )

        try:
            log.verbose('Trying to open scene: %s in read-write mode' % scene_path.Host + ':' + scene_path.Job + ':' + scene_path.Scene)
            scene = conn.Scene.open_scene( scene_path, {  flapi.OPENFLAG_DISCARD  })
        except flapi.FLAPIException as ex:
            log.error( "Error opening scene: %s" % ex )
            return None


        for baselight_shot in new_shots:
            shot_name = create_kitsu_shot_name(config, baselight_shot)
            shot_data = build_kitsu_shot_data(config, baselight_shot)

            new_shot = gazu.shot.new_shot(
                project_dict, 
                baselight_linked_sequence, 
                shot_name,
                data = shot_data
                # data = {'00_shot_id': baselight_shot.get('shot_id')}
            )

            pprint (shot_data)

            shot_id = baselight_shot.get('shot_id')
            shot = scene.get_shot(shot_id)

            try:
                qm = conn.QueueManager.create_local()
            except flapi.FLAPIException as ex:
                log.error( "Can not create queue manager: %s" % ex )
                continue
            try:
                ex = conn.Export.create()
                ex.select_shot(shot)
                exSettings = flapi.StillExportSettings()
                exSettings.ColourSpace = "sRGB"
                exSettings.Format = "HD 1920x1080"
                exSettings.Overwrite = flapi.EXPORT_OVERWRITE_REPLACE
                exSettings.Directory = config.get('remote_temp_folder', '/var/tmp')
                exSettings.Frames = flapi.EXPORT_FRAMES_FIRST 
                # exSettings.Filename = "%{Job}/%{Clip}_%{TimelineFrame}"
                exSettings.Filename = str(shot_id)
                exSettings.Source = flapi.EXPORT_SOURCE_SELECTEDSHOTS

                print ('')
                # print ('Baselight sequence: %s' % blpath)
                print ('Generating thumbnail for: "%s" Shot name: "%s"' % (blpath, shot_name))
                log.verbose( "Submitting to queue" )
                exportInfo = ex.do_export_still( qm, scene, exSettings)
                waitForExportToComplete(qm, exportInfo)
                del ex
                print( "Closing QueueManager\n" )
                qm.release()
            except Exception as ex:
                log.error( "Can not export thumbnail: %s" % ex )

            file_list = remote_listdir(
                config.get('remote_temp_folder', '/var/tmp'),
                flapi_host.get('flapi_user'),
                flapi_host.get('flapi_hostname')
                )

            thumbnail_file_name = str(shot_id) + '.jpg'
            thumbnail_local_path = ''
            if thumbnail_file_name in file_list:
                # get it over here to upload thumbnail
                thumbnail_remote_path = os.path.join(
                    config.get('remote_temp_folder', '/var/tmp'),
                    thumbnail_file_name
                )
                thumbnail_local_path = config.get('temp_folder', '/var/tmp')
                if not thumbnail_local_path.endswith(os.path.sep):
                    thumbnail_local_path = thumbnail_local_path + os.path.sep
                rsync(
                    flapi_host.get('flapi_user'),
                    flapi_host.get('flapi_hostname'),
                    thumbnail_remote_path,
                    thumbnail_local_path
                )
                remote_rm(
                    thumbnail_remote_path,
                    flapi_host.get('flapi_user'),
                    flapi_host.get('flapi_hostname')    
                )
            
            if not thumbnail_local_path:
                log.verbose('Unable generate thumbnail for %s' % shot_name)
                continue

            task_types = gazu.task.all_task_types()
            shot_task_types = [t for t in task_types if t['for_entity'] == 'Shot']
            shot_task_types = sorted(shot_task_types, key=lambda d: d['priority'])
            task = gazu.task.new_task(new_shot, shot_task_types[0])
            todo = gazu.task.get_task_status_by_short_name("todo")
            comment = gazu.task.add_comment(task, todo, "Add thumbnail")

            log.verbose('Adding preview on task "%s"' % shot_task_types[0].get('name'))
            preview_file = gazu.task.add_preview(
                task,
                comment,
                os.path.join(
                    thumbnail_local_path,
                    thumbnail_file_name
                )
            )

            log.verbose('Uploading thumbnail for shot: "%s"' % shot_name)
            gazu.task.set_main_preview(preview_file)
            # gazu.task.remove_task(task)

            try:
                os.remove(thumbnail_local_path)
            except:
                pass

            scene.start_delta('Add kitsu metadata to shot %s' % shot_name)
            new_md_values = {
                kitsu_uid_metadata_obj.Key: new_shot.get('id')
            }

            shot.set_metadata( new_md_values )

            shot.release()

            scene.end_delta()
            scene.save_scene()
            # shot = scene.get_shot(shot_inf.ShotId)


        scene.save_scene()
        scene.close_scene()
        scene.release()
        '''