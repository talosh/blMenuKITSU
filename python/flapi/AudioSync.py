from . import Library, Interface, FLAPIException
import json

# AudioSync
#
# audio sync operation
#

class AudioSync(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new audio sync operation object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (AudioSync): AudioSync object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of AudioSync" )
        return self.conn.call(
            None,
            "AudioSync.create",
            {}
        )

    # audio_sync
    #
    # Perform audio sync operation using the given audio sync settings
    #
    # Arguments:
    #    'scene' (Scene): Target scene to AudioSync into
    #    'settings' (AudioSyncSettings): 
    #    'shot_ids' (list): Array of Shot IDs to apply audio sync operation to [Optional]
    #        '<n>' (int): Shot ID
    #
    # Returns:
    #    (int): Number of shots updated by audio sync operation
    #
    def audio_sync(self, scene, settings, shot_ids = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "AudioSync.audio_sync",
            {
                'scene': scene,
                'settings': settings,
                'shot_ids': shot_ids,
            }
        )

    # get_log
    #
    # Return log of progress information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of audio sync progress information
    #        '<n>' (AudioSyncProgress): 
    #
    def get_log(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "AudioSync.get_log",
            {}
        )

Library.register_class( 'AudioSync', AudioSync )

