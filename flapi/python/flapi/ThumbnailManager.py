from . import Library, Interface, FLAPIException
import json

# ThumbnailManager
#
# Interface used to generate shot thumbnails
#

class ThumbnailManager(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_poster_uri
    #
    # Get a poster (or specific) frame thumbnail URI for a shot
    #
    # Arguments:
    #    'shot_if' (Shot): Shot interface object
    #    'options' (dict): Stucture containing optional settings used to control the type of thumbnail image rendered.
    #        'DCSpace' (string): Display colourspace (sRGB or P3) [Optional]
    #        'Graded' (int): Graded/ungraded flag [Optional]
    #        'HiRes' (string): Flag indicating hi-res image preferable [Optional]
    #        'ShotFrame' (int): Optional timeline frame number (constrained to shot range) [Optional]
    #
    # Returns:
    #    (string): Thumbnail URI
    #
    def get_poster_uri(self, shot_if, options):
        if self.target != None:
            raise FLAPIException( "Static method get_poster_uri called on instance of ThumbnailManager" )
        return self.conn.call(
            None,
            "ThumbnailManager.get_poster_uri",
            {
                'shot_if': shot_if,
                'options': options,
            }
        )

    # get_scrub_uri_template
    #
    # Get a scrub image URI template (prefix & suffix strings). This can be used while scrubbing to generate image URIs without additional roundtrips/calls to the server.
    #
    # Arguments:
    #    'scene_if' (Scene): Scene interface object
    #    'shot_id' (Shot): ID of shot in scene
    #    'options' (dict): Stucture containing optional settings used to control the type of scrub image rendered.
    #        'DCSpace' (string): Display colourspace (sRGB or P3) [Optional]
    #        'Graded' (int): Graded/ungraded flag [Optional]
    #        'HiRes' (string): Flag indicating hi-res image preferable [Optional]
    #
    # Returns:
    #    (list): Template array containing 2 strings; a URI prefix & suffix. To form a completeURI, the scrub frame number required should be inserted between these 2 strings.
    #        '<n>' (string): 
    #
    def get_scrub_uri_template(self, scene_if, shot_id, options):
        if self.target != None:
            raise FLAPIException( "Static method get_scrub_uri_template called on instance of ThumbnailManager" )
        return self.conn.call(
            None,
            "ThumbnailManager.get_scrub_uri_template",
            {
                'scene_if': scene_if,
                'shot_id': shot_id,
                'options': options,
            }
        )

Library.register_class( 'ThumbnailManager', ThumbnailManager )

