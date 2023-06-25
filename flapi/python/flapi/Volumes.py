from . import Library, Interface, FLAPIException
import json

# Volumes
#
# Query and configure storage for this system
#

class Volumes(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_volume_keys
    #
    # Return keys for volumes accessible from this system
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of volume keys
    #        '<n>' (string): Key
    #
    def get_volume_keys(self):
        if self.target != None:
            raise FLAPIException( "Static method get_volume_keys called on instance of Volumes" )
        return self.conn.call(
            None,
            "Volumes.get_volume_keys",
            {}
        )

    # get_local_volume_keys
    #
    # Return volumes defined locally on this system
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of volume keys
    #        '<n>' (string): Key
    #
    def get_local_volume_keys(self):
        if self.target != None:
            raise FLAPIException( "Static method get_local_volume_keys called on instance of Volumes" )
        return self.conn.call(
            None,
            "Volumes.get_local_volume_keys",
            {}
        )

    # get_volume_info
    #
    # Return VolumeInfo describing the volume with the given key
    #
    # Arguments:
    #    'keys' (list): Array of volume keys
    #        '<n>' (string): Key identifying volume
    #
    # Returns:
    #    (VolumeInfo): 
    #
    def get_volume_info(self, keys):
        if self.target != None:
            raise FLAPIException( "Static method get_volume_info called on instance of Volumes" )
        return self.conn.call(
            None,
            "Volumes.get_volume_info",
            {
                'keys': keys,
            }
        )

Library.register_class( 'Volumes', Volumes )

