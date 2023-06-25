from . import Library, Interface, FLAPIException
import json

# MenuItem
#
# A menu item in the application user interface, which can trigger actions
#

class MenuItem(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new MenuItem object
    #
    # Arguments:
    #    'title' (string): Title of MenuItem
    #    'key' (any): A value which can be used as a key to identify this menu item [Optional]
    #
    # Returns:
    #    (MenuItem): 
    #
    def create(self, title, key = None):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of MenuItem" )
        return self.conn.call(
            None,
            "MenuItem.create",
            {
                'title': title,
                'key': key,
            }
        )

    # register
    #
    # Register this menu item to insert it into the application's UI
    #
    # Arguments:
    #    'location' (string): Where to register menu item
    #
    # Returns:
    #    (none)
    #
    def register(self, location):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.register",
            {
                'location': location,
            }
        )

    # get_title
    #
    # Get menu item title
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Menu item title
    #
    def get_title(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.get_title",
            {}
        )

    # set_title
    #
    # Set menu item title
    #
    # Arguments:
    #    'title' (string): New menu item title
    #
    # Returns:
    #    (none)
    #
    def set_title(self, title):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.set_title",
            {
                'title': title,
            }
        )

    # get_enabled
    #
    # Get menu item enabled state
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Enabled state
    #
    def get_enabled(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.get_enabled",
            {}
        )

    # set_enabled
    #
    # Set menu item enabled state
    #
    # Arguments:
    #    'enabled' (int): Enabled state
    #
    # Returns:
    #    (none)
    #
    def set_enabled(self, enabled):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.set_enabled",
            {
                'enabled': enabled,
            }
        )

    # get_hidden
    #
    # Get menu item hidden state
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Hidden state
    #
    def get_hidden(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.get_hidden",
            {}
        )

    # set_hidden
    #
    # Set menu item hidden state
    #
    # Arguments:
    #    'hidden' (int): Hidden state
    #
    # Returns:
    #    (none)
    #
    def set_hidden(self, hidden):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.set_hidden",
            {
                'hidden': hidden,
            }
        )

    # get_sub_menu
    #
    # Get sub-menu for this menu item
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Menu): 
    #
    def get_sub_menu(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.get_sub_menu",
            {}
        )

    # set_sub_menu
    #
    # Set sub-menu for this menu item
    #
    # Arguments:
    #    'submenu' (Menu): Menu object containing sub-menu items
    #
    # Returns:
    #    (none)
    #
    def set_sub_menu(self, submenu):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "MenuItem.set_sub_menu",
            {
                'submenu': submenu,
            }
        )

Library.register_class( 'MenuItem', MenuItem )

