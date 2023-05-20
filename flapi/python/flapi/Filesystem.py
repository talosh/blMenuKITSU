from . import Library, Interface, FLAPIException
import json

# Filesystem
#
# Access host filesystem
#

class Filesystem(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_items
    #
    # Return array of items in given directory
    #
    # Arguments:
    #    'dir' (string): Path to directory
    #    'filter' (set):  [Optional]
    #
    # Returns:
    #    (list): 
    #        '<n>' (dict): name
    #            'type' (string): Type of item
    #
    def get_items(self, dir, filter):
        if self.target != None:
            raise FLAPIException( "Static method get_items called on instance of Filesystem" )
        return self.conn.call(
            None,
            "Filesystem.get_items",
            {
                'dir': dir,
                'filter': filter,
            }
        )

Library.register_class( 'Filesystem', Filesystem )

