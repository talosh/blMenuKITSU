from . import Library, Interface, FLAPIException
import json

# Cursor
#
# Interface for accessing cursors within a scene.
#

class Cursor(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_time
    #
    # Get cursor's position in the timeline in seconds
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Timeline time
    #
    def get_time(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_time",
            {}
        )

    # get_frame
    #
    # Get cursor's position in the timeline as a frame number
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Timeline frame number
    #
    def get_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_frame",
            {}
        )

    # get_record_timecode
    #
    # Get cursor's position in the timeline as a timecode
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (timecode): Record timecode
    #
    def get_record_timecode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_record_timecode",
            {}
        )

    # get_viewing_format_name
    #
    # Get the name of the cursor's current viewing format.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Viewing format name
    #
    def get_viewing_format_name(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_viewing_format_name",
            {}
        )

    # get_viewing_format_dims
    #
    # Get basic geometry (width, height and aspect ratio) of the cursor's current viewing format
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Viewing format dimensions
    #        'AspectRatio' (float): Viewing format pixel aspect ratio (for anamorphic formats)
    #        'Height' (int): Viewing format height
    #        'Width' (int): Viewing format width
    #
    def get_viewing_format_dims(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_viewing_format_dims",
            {}
        )

    # get_viewing_format_mask_name
    #
    # Get current viewing format mask name
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (FormatMask):  [Optional]
    #
    def get_viewing_format_mask_name(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_viewing_format_mask_name",
            {}
        )

    # get_viewing_format_mask
    #
    # Get current viewing format mask rectangle
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (FormatMask):  [Optional]
    #
    def get_viewing_format_mask(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_viewing_format_mask",
            {}
        )

    # get_age
    #
    # Get the cursor's 'age'. The age is an integer, incremented whenever an attribute which could result in a visual change to the image display has been modfied.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Cursor age value
    #
    def get_age(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.get_age",
            {}
        )

    # is_using_truelight
    #
    # Is Truelight currently in use (ie. a profile has been selected & Truelight is enabled) in this cursor.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag indicating if Truelight is in use
    #
    def is_using_truelight(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Cursor.is_using_truelight",
            {}
        )

Library.register_class( 'Cursor', Cursor )

