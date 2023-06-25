from . import Library, Interface, FLAPIException
import json

# Mark
#
# Mark defined in a Shot or Scene
#

class Mark(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_id
    #
    # Return Mark object ID
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Mark ID
    #
    def get_id(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_id",
            {}
        )

    # get_type
    #
    # Return Mark type
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Value indicating type of mark
    #
    def get_type(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_type",
            {}
        )

    # get_position
    #
    # Return Mark position
    # For Shot marks, this value is a frame number relative to the start of the image sequence.
    # For Strip marks, this value is a time in seconds relative to the start of the strip.
    # For Timeline marks, this value is a time in seconds relative to the start of the timeline.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Position in seconds or frames
    #
    def get_position(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_position",
            {}
        )

    # get_time
    #
    # Return Mark position in seconds
    # For Shot and Strip marks, this returns the time relative to the start of the shot
    # For Timeline marks, this returns the time relative to the start of the timeline
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Position in seconds
    #
    def get_time(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_time",
            {}
        )

    # get_note_text
    #
    # Return Mark note text
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Note text
    #
    def get_note_text(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_note_text",
            {}
        )

    # get_colour
    #
    # Return Mark colour
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): RGBA colour
    #        '<n>' (float): 
    #
    def get_colour(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_colour",
            {}
        )

    # get_category
    #
    # Return Mark category
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Mark category
    #
    def get_category(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_category",
            {}
        )

    # get_source_frame
    #
    # Return the source image frame number for this mark
    # Only applicable for Shot/Strip marks. Will fail for Timeline marks
    #
    # Arguments:
    #    'eye' (string): Which eye for stereo sequences [Optional]
    #
    # Returns:
    #    (int): Source frame number
    #
    def get_source_frame(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_source_frame",
            {
                'eye': eye,
            }
        )

    # get_source_timecode
    #
    # Return the source image timecode for this mark
    # Only applicable for Shot/Strip marks. Will fail for Timeline marks
    #
    # Arguments:
    #    'eye' (string): Which eye for stereo sequences [Optional]
    #
    # Returns:
    #    (timecode): Source timecode
    #
    def get_source_timecode(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_source_timecode",
            {
                'eye': eye,
            }
        )

    # get_record_frame
    #
    # Return the source image frame number for this mark
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Record frame number
    #
    def get_record_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_record_frame",
            {}
        )

    # get_record_timecode
    #
    # Return the source image timecode for this mark
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
            "Mark.get_record_timecode",
            {}
        )

    # get_properties
    #
    # Return dictionary of properties for this Mark object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Dictionary containing property keys and values
    #
    def get_properties(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.get_properties",
            {}
        )

    # set_properties
    #
    # Set the property values for the given dictionary of keys & values.
    # Setting a value to NULL will remove it from the property set.
    #
    # Arguments:
    #    'props' (dict): Dictionary of property keys & values
    #
    # Returns:
    #    (none)
    #
    def set_properties(self, props):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Mark.set_properties",
            {
                'props': props,
            }
        )

Library.register_class( 'Mark', Mark )

