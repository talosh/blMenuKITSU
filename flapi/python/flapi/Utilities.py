from . import Library, Interface, FLAPIException
import json

# Utilities
#
# Utility functions
#

class Utilities(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # timecode_from_string
    #
    # Convert string to Timecode
    #
    # Arguments:
    #    'str' (string): Timecode in string form
    #    'fps' (int): FPS [Optional]
    #    'wraphour' (int): Hour at which timecode is considered to wrap around, defaults to 24. Set this to 0 to disable timecode wrapping. [Optional]
    #
    # Returns:
    #    (timecode): Timecode parsed from string
    #
    def timecode_from_string(self, str, fps = None, wraphour = 24):
        if self.target != None:
            raise FLAPIException( "Static method timecode_from_string called on instance of Utilities" )
        return self.conn.call(
            None,
            "Utilities.timecode_from_string",
            {
                'str': str,
                'fps': fps,
                'wraphour': wraphour,
            }
        )

    # get_allowed_enum_values
    #
    # Returns an array of EnumInfo objects representing the allowed
    # values for a given enumeration type.  Explictly, each returned entry
    # has two fields:
    # * Value - The (unique) internal value.
    # * Desc - The user-friendly description for the value
    # (so that you would typically present Desc to the user
    # and use Value in calls to FLAPI functions).
    #
    # Arguments:
    #    'enumType' (string): The name of the enumerated type.  e.g. CUBEEXPORT_LUTFORMAT
    #
    # Returns:
    #    (list): Array of EnumInfo objects
    #        '<n>' (EnumInfo): 
    #
    def get_allowed_enum_values(self, enumType):
        if self.target != None:
            raise FLAPIException( "Static method get_allowed_enum_values called on instance of Utilities" )
        return self.conn.call(
            None,
            "Utilities.get_allowed_enum_values",
            {
                'enumType': enumType,
            }
        )

Library.register_class( 'Utilities', Utilities )

