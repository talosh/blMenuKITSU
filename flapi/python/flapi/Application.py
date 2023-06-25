from . import Library, Interface, FLAPIException
import json

# Application
#
# Access information about the target application
#

class Application(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_application_info
    #
    # Information describing the application exposed via the FilmLight API
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Application Info
    #        'Build' (string): Build number i.e. 10000
    #        'Major' (string): Major version number, i.e. 5
    #        'Minor' (string): Minor version number, i.e. 0
    #        'Name' (string): Application Name, i.e. 'flapi'
    #        'Path' (string): Path to the application
    #        'Product' (string): Product Name, i.e. 'Baselight'
    #
    def get_application_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_application_info called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_application_info",
            {}
        )

    # get_sdk_versions
    #
    # Get SDK version information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of SDKVersion objects
    #        '<n>' (SDKVersion): 
    #
    def get_sdk_versions(self):
        if self.target != None:
            raise FLAPIException( "Static method get_sdk_versions called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_sdk_versions",
            {}
        )

    # get_connections_info
    #
    # Get array of current connections. Each entry in the array will be a ConnectionInfo object describing that connection.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of connection info objects
    #        '<n>' (ConnectionInfo): 
    #
    def get_connections_info(self):
        if self.target != None:
            raise FLAPIException( "Static method get_connections_info called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_connections_info",
            {}
        )

    # get_video_streaming_supported
    #
    # Is video streaming supported (hardware, setup & licensed)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if streaming supported, 0 if not
    #
    def get_video_streaming_supported(self):
        if self.target != None:
            raise FLAPIException( "Static method get_video_streaming_supported called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_video_streaming_supported",
            {}
        )

    # get_video_streaming_enabled
    #
    # Is video streaming currently enabled
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if streaming enabled, 0 if not
    #
    def get_video_streaming_enabled(self):
        if self.target != None:
            raise FLAPIException( "Static method get_video_streaming_enabled called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_video_streaming_enabled",
            {}
        )

    # get_video_stream_address
    #
    # Return address for video stream
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Address for video stream access. Used by Client View.
    #
    def get_video_stream_address(self):
        if self.target != None:
            raise FLAPIException( "Static method get_video_stream_address called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get_video_stream_address",
            {}
        )

    # is_playing
    #
    # Is playback currently in progress
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if playback in progress, 0 if not
    #
    def is_playing(self):
        if self.target != None:
            raise FLAPIException( "Static method is_playing called on instance of Application" )
        return self.conn.call(
            None,
            "Application.is_playing",
            {}
        )

    # get
    #
    # Return instance of the Application object (typically for signal connection)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Application): Returns Application object
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of Application" )
        return self.conn.call(
            None,
            "Application.get",
            {}
        )

    # get_current_scene
    #
    # Return the currently active Scene within the application
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Scene): Current Scene
    #
    def get_current_scene(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_current_scene",
            {}
        )

    # get_current_scene_name
    #
    # Return the name of the currently active Scene within the application
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Current Scene name
    #
    def get_current_scene_name(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_current_scene_name",
            {}
        )

    # get_open_scene_names
    #
    # Return array of names of scenes currently open in the application.
    # You can get the Scene object for a given name by calling get_scene_by_name().
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of Scene Names
    #        '<n>' (string): Scene Name
    #
    def get_open_scene_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_open_scene_names",
            {}
        )

    # get_scene_by_name
    #
    # Return the Scene object for the scene with the given name.
    # If no matching scene can be found, NULL is returned.
    #
    # Arguments:
    #    'name' (string): Name of Scene
    #
    # Returns:
    #    (Scene): Scene object for given scene name
    #
    def get_scene_by_name(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_scene_by_name",
            {
                'name': name,
            }
        )

    # get_current_cursor
    #
    # Return the currently active Cursor within the application
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Cursor): Current Cursor
    #
    def get_current_cursor(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_current_cursor",
            {}
        )

    # get_cursors
    #
    # Return active Cursor objects within the application
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of Cursor objects
    #        '<n>' (Cursor): Cursor object representing active cursor in application
    #
    def get_cursors(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_cursors",
            {}
        )

    # log
    #
    # Log message in application Log view
    #
    # Arguments:
    #    'category' (string): Category of message
    #    'severity' (string): Severity of message, Hard, Soft or Transient
    #    'message' (string): Message to log
    #
    # Returns:
    #    (none)
    #
    def log(self, category, severity, message):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.log",
            {
                'category': category,
                'severity': severity,
                'message': message,
            }
        )

    # message_dialog
    #
    # Present a message box in the Application for the user to interact with
    #
    # Arguments:
    #    'title' (string): Title of message box
    #    'message' (string): Contents of message box
    #    'buttons' (list): Array of buttons to show in dialog box
    #        '<n>' (string): Button label
    #
    # Returns:
    #    (string): Label of button selected by user
    #
    def message_dialog(self, title, message, buttons):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.message_dialog",
            {
                'title': title,
                'message': message,
                'buttons': buttons,
            }
        )

    # list_dialog
    #
    # Present a dialog to the user containing a list of items that the user can select from
    #
    # Arguments:
    #    'title' (string): Title of list dialog
    #    'message' (string): Message to show in list dialog
    #    'items' (list): Array of items to show in list
    #        '<n>' (KeyTextItem): 
    #
    # Returns:
    #    (any): Key of selected object, or NULL if no selection
    #
    def list_dialog(self, title, message, items):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.list_dialog",
            {
                'title': title,
                'message': message,
                'items': items,
            }
        )

    # set_custom_data
    #
    # Set a custom data value in the application with the supplied (string) key. Existing custom
    # data values can be deleted from the application by supplying NULL/None/null as the data value
    # (for an existing key).
    #
    # Arguments:
    #    'data_key' (string): Custom data value key
    #    'data_value' (any): New data value for the given key (or NULL/None/null to delete) [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_custom_data(self, data_key, data_value):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.set_custom_data",
            {
                'data_key': data_key,
                'data_value': data_value,
            }
        )

    # get_custom_data
    #
    # Get a custom data value from the application previously set using set_custom_data.
    #
    # Arguments:
    #    'data_key' (string): Custom data value key
    #
    # Returns:
    #    (any): Custom data value found
    #
    def get_custom_data(self, data_key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_custom_data",
            {
                'data_key': data_key,
            }
        )

    # get_custom_data_keys
    #
    # Return sorted array of (string) keys that can be used to fetch application
    # custom data values via get_custom_data.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (string): Key string
    #
    def get_custom_data_keys(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Application.get_custom_data_keys",
            {}
        )

Library.register_class( 'Application', Application )

