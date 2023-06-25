from . import Library, Interface, FLAPIException
import json

# SceneSettings
#
# This class provides an interface to get/set scene settings, which affect all Shots in a Scene.
#

class SceneSettings(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_setting_keys
    #
    # Return array of keys that can be used to get/set Scene Settings parameters
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (string): Key string
    #
    def get_setting_keys(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.get_setting_keys",
            {}
        )

    # get_setting_definition
    #
    # Return SceneSettings parameter type definition for the given key
    #
    # Arguments:
    #    'key' (string): Key for SceneSettings parameter
    #
    # Returns:
    #    (SceneSettingDefinition): 
    #
    def get_setting_definition(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.get_setting_definition",
            {
                'key': key,
            }
        )

    # get
    #
    # Return values for given SceneSettings keys
    #
    # Arguments:
    #    'keys' (list): Array of keys
    #        '<n>' (string): Key for parameter
    #
    # Returns:
    #    (dict): 
    #
    def get(self, keys):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.get",
            {
                'keys': keys,
            }
        )

    # get_single
    #
    # Return value for given SceneSettings key
    #
    # Arguments:
    #    'key' (string): SceneSettings Key for value wanted
    #
    # Returns:
    #    (any): 
    #
    def get_single(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.get_single",
            {
                'key': key,
            }
        )

    # set
    #
    # Set values for the given SceneSettings keys
    #
    # Arguments:
    #    'values' (dict): A dictionary containing new values for the given SceneSettings keys
    #
    # Returns:
    #    (none)
    #
    def set(self, values):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.set",
            {
                'values': values,
            }
        )

    # set_single
    #
    # Set value for the given SceneSettings key
    #
    # Arguments:
    #    'key' (string): SceneSettings key for value to set
    #    'value' (any): New value for the given SceneSettings key [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_single(self, key, value):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SceneSettings.set_single",
            {
                'key': key,
                'value': value,
            }
        )

Library.register_class( 'SceneSettings', SceneSettings )

