from . import Library, Interface, FLAPIException
import json

# JobManager
#
# Query and manipulate the FilmLight job database
#

class JobManager(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_jobs
    #
    # Fetch list of jobs in job database
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #
    # Returns:
    #    (list): Array of job name strings
    #        '<n>' (string): Job name
    #
    def get_jobs(self, host):
        if self.target != None:
            raise FLAPIException( "Static method get_jobs called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.get_jobs",
            {
                'host': host,
            }
        )

    # get_folders
    #
    # Fetch list of folder names within job/folder in job database
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'job' (string): Job name within job database
    #    'folder' (string): Folder within job [Optional]
    #    'recursive' (int): Return all folders contained within the given job/folder [Optional]
    #
    # Returns:
    #    (list): Array of folder names
    #        '<n>' (string): Folder name
    #
    def get_folders(self, host, job, folder = None, recursive = 1):
        if self.target != None:
            raise FLAPIException( "Static method get_folders called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.get_folders",
            {
                'host': host,
                'job': job,
                'folder': folder,
                'recursive': recursive,
            }
        )

    # get_scenes
    #
    # Fetch list of scene names within job/folder in job database
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'job' (string): Job name within job database
    #    'folder' (string): Folder within job [Optional]
    #
    # Returns:
    #    (list): Array of scene names
    #        '<n>' (string): Scene name
    #
    def get_scenes(self, host, job, folder = None):
        if self.target != None:
            raise FLAPIException( "Static method get_scenes called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.get_scenes",
            {
                'host': host,
                'job': job,
                'folder': folder,
            }
        )

    # create_job
    #
    # Create a new job
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #
    # Returns:
    #    (none)
    #
    def create_job(self, host, jobname):
        if self.target != None:
            raise FLAPIException( "Static method create_job called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.create_job",
            {
                'host': host,
                'jobname': jobname,
            }
        )

    # rename_job
    #
    # Rename job
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'new_jobname' (string): New job name
    #
    # Returns:
    #    (none)
    #
    def rename_job(self, host, jobname, new_jobname):
        if self.target != None:
            raise FLAPIException( "Static method rename_job called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.rename_job",
            {
                'host': host,
                'jobname': jobname,
                'new_jobname': new_jobname,
            }
        )

    # delete_job
    #
    # Delete job
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'force' (int): Force deletion of job [Optional]
    #
    # Returns:
    #    (none)
    #
    def delete_job(self, host, jobname, force = 0):
        if self.target != None:
            raise FLAPIException( "Static method delete_job called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.delete_job",
            {
                'host': host,
                'jobname': jobname,
                'force': force,
            }
        )

    # job_exists
    #
    # Check if job exists
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #
    # Returns:
    #    (int): Flag indicating whether job exists
    #
    def job_exists(self, host, jobname):
        if self.target != None:
            raise FLAPIException( "Static method job_exists called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.job_exists",
            {
                'host': host,
                'jobname': jobname,
            }
        )

    # create_folder
    #
    # Create a folder within job
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'foldername' (string): Folder name within job
    #
    # Returns:
    #    (none)
    #
    def create_folder(self, host, jobname, foldername):
        if self.target != None:
            raise FLAPIException( "Static method create_folder called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.create_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
            }
        )

    # rename_folder
    #
    # Rename folder
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'foldername' (string): Folder name within job
    #    'new_foldername' (string): New folder name
    #
    # Returns:
    #    (none)
    #
    def rename_folder(self, host, jobname, foldername, new_foldername):
        if self.target != None:
            raise FLAPIException( "Static method rename_folder called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.rename_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
                'new_foldername': new_foldername,
            }
        )

    # delete_folder
    #
    # Delete folder
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'foldername' (string): Folder name within job
    #
    # Returns:
    #    (none)
    #
    def delete_folder(self, host, jobname, foldername):
        if self.target != None:
            raise FLAPIException( "Static method delete_folder called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.delete_folder",
            {
                'host': host,
                'jobname': jobname,
                'foldername': foldername,
            }
        )

    # get_scene_info
    #
    # Return information about scene
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'scenename' (string): Scene name
    #
    # Returns:
    #    (SceneInfo): An object containing properties of the Scene
    #
    def get_scene_info(self, host, jobname, scenename):
        if self.target != None:
            raise FLAPIException( "Static method get_scene_info called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.get_scene_info",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
            }
        )

    # scene_exists
    #
    # Check if scene exists
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'scenename' (string): Scene name
    #
    # Returns:
    #    (int): Flag indicating whether scene exists
    #
    def scene_exists(self, host, jobname, scenename):
        if self.target != None:
            raise FLAPIException( "Static method scene_exists called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.scene_exists",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
            }
        )

    # delete_scene
    #
    # Delete scene
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'scenename' (string): Scene name
    #    'ignoreLocks' (int): Flag indicating any existing locks on scene should be ignored [Optional]
    #
    # Returns:
    #    (none)
    #
    def delete_scene(self, host, jobname, scenename, ignoreLocks = 0):
        if self.target != None:
            raise FLAPIException( "Static method delete_scene called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.delete_scene",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
                'ignoreLocks': ignoreLocks,
            }
        )

    # rename_scene
    #
    # Rename scene
    #
    # Arguments:
    #    'host' (string): Hostname of job database
    #    'jobname' (string): Job name
    #    'scenename' (string): Scene name
    #    'newname' (string): New Scene name
    #
    # Returns:
    #    (none)
    #
    def rename_scene(self, host, jobname, scenename, newname):
        if self.target != None:
            raise FLAPIException( "Static method rename_scene called on instance of JobManager" )
        return self.conn.call(
            None,
            "JobManager.rename_scene",
            {
                'host': host,
                'jobname': jobname,
                'scenename': scenename,
                'newname': newname,
            }
        )

Library.register_class( 'JobManager', JobManager )

