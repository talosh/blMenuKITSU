from . import Library, Interface, FLAPIException
import json

# MultiPaste
#
# Multi-Paste operation
#

class MultiPaste(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new Multi-Paste operation object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (MultiPaste): MultiPaste object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of MultiPaste" )
        return self.conn.call(
            None,
            "MultiPaste.create",
            {}
        )

    # multi_paste
    #
    # Perform multi-paste operation using the given Multi-Paste settings
    #
    # Arguments:
    #    'scene' (Scene): Target scene to MultiPaste into
    #    'settings' (MultiPasteSettings): 
    #    'shot_ids' (list): Array of Shot IDs to apply multi-paste operation to [Optional]
    #        '<n>' (int): Shot ID
    #
    # Returns:
    #    (int): Number of shots updated by Multi-Paste operation
    #
    def multi_paste(self, scene, settings, shot_ids = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MultiPaste.multi_paste",
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
    #    (list): Array of multi-paste progress information
    #        '<n>' (MultiPasteProgress): 
    #
    def get_log(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MultiPaste.get_log",
            {}
        )

Library.register_class( 'MultiPaste', MultiPaste )

