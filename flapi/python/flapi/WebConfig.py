from . import Library, Interface, FLAPIException
import json

# WebConfig
#
# WebConfig interface used by Web Management UI to configure users/passwords for web interface access
#

class WebConfig(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_permissions
    #
    # Return list of available permissions
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of permission definitions
    #        '<n>' (APIPermissionInfo): 
    #
    def get_permissions(self):
        if self.target != None:
            raise FLAPIException( "Static method get_permissions called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.get_permissions",
            {}
        )

    # get_users
    #
    # Return list of web users
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of users
    #        '<n>' (APIUserInfo): 
    #
    def get_users(self):
        if self.target != None:
            raise FLAPIException( "Static method get_users called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.get_users",
            {}
        )

    # add_user
    #
    # Add new user
    #
    # Arguments:
    #    'info' (APIUserInfo): 
    #
    # Returns:
    #    (none)
    #
    def add_user(self, info):
        if self.target != None:
            raise FLAPIException( "Static method add_user called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.add_user",
            {
                'info': info,
            }
        )

    # update_user
    #
    # Update user config
    #
    # Arguments:
    #    'name' (string): User login name
    #    'info' (APIUserInfo): 
    #
    # Returns:
    #    (none)
    #
    def update_user(self, name, info):
        if self.target != None:
            raise FLAPIException( "Static method update_user called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.update_user",
            {
                'name': name,
                'info': info,
            }
        )

    # delete_user
    #
    # Delete user
    #
    # Arguments:
    #    'name' (string): User login name
    #
    # Returns:
    #    (none)
    #
    def delete_user(self, name):
        if self.target != None:
            raise FLAPIException( "Static method delete_user called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.delete_user",
            {
                'name': name,
            }
        )

    # set_password
    #
    # Set user password
    #
    # Arguments:
    #    'name' (string): User login name
    #    'password' (string): New password
    #
    # Returns:
    #    (none)
    #
    def set_password(self, name, password):
        if self.target != None:
            raise FLAPIException( "Static method set_password called on instance of WebConfig" )
        return self.conn.call(
            None,
            "WebConfig.set_password",
            {
                'name': name,
                'password': password,
            }
        )

Library.register_class( 'WebConfig', WebConfig )

