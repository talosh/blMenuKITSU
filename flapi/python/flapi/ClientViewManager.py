from . import Library, Interface, FLAPIException
import json

# ClientViewManager
#
# Manages settings for connected Client Views.
#

class ClientViewManager(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get
    #
    # Get reference to the (singleton) ClientViewManager object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (ClientViewManager): 
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of ClientViewManager" )
        return self.conn.call(
            None,
            "ClientViewManager.get",
            {}
        )

    # get_host_user_settings
    #
    # Get object containing Settings for the Client View's host user
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (ClientViewHostUserSettings): 
    #
    def get_host_user_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_host_user_settings",
            {}
        )

    # get_client_settings
    #
    # Get the connected Client View's config/settings object.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (ClientViewClientSettings): 
    #
    def get_client_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_client_settings",
            {}
        )

    # get_stream_settings
    #
    # Get array of stream settings objects.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (ClientViewStreamSettings): 
    #
    def get_stream_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_stream_settings",
            {}
        )

    # get_streaming_enabled
    #
    # Is streaming currently enabled.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if streaming enabled, otherwise 0
    #
    def get_streaming_enabled(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_streaming_enabled",
            {}
        )

    # get_session_name
    #
    # Get the current Client View session name.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Current session name
    #
    def get_session_name(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_session_name",
            {}
        )

    # get_session_clients
    #
    # Get array of current session clients. Each entry in the array will be a ConnectionInfo object describing that connection.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of current session clients
    #        '<n>' (ConnectionInfo): 
    #
    def get_session_clients(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.get_session_clients",
            {}
        )

    # log
    #
    # Private routine used to log client view messages for debugging
    #
    # Arguments:
    #    'category' (string): Category of message
    #    'message' (string): Message to log
    #    'severity' (string): Severity of message, Hard, Soft (warning) or Transient (info) [Optional]
    #
    # Returns:
    #    (none)
    #
    def log(self, category, message, severity = 'ERR_INFO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.log",
            {
                'category': category,
                'message': message,
                'severity': severity,
            }
        )

    # set_available_simad_actions
    #
    # Set debug actions availble to SimAd
    #
    # Arguments:
    #    'actions' (dict): 
    #
    # Returns:
    #    (none)
    #
    def set_available_simad_actions(self, actions):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ClientViewManager.set_available_simad_actions",
            {
                'actions': actions,
            }
        )

Library.register_class( 'ClientViewManager', ClientViewManager )

