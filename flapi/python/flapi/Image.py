from . import Library, Interface, FLAPIException
import json

# Image
#
#

class Image(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_raw_metadata
    #
    # Returns raw metadata for the image or movie at the supplied path
    #
    # Arguments:
    #    'filename' (string): Filename of image/movie to examine
    #
    # Returns:
    #    (dict): Dictionary of metadata
    #
    def get_raw_metadata(self, filename):
        if self.target != None:
            raise FLAPIException( "Static method get_raw_metadata called on instance of Image" )
        return self.conn.call(
            None,
            "Image.get_raw_metadata",
            {
                'filename': filename,
            }
        )

Library.register_class( 'Image', Image )

