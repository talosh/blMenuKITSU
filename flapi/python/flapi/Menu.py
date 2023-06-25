from . import Library, Interface, FLAPIException
import json

# Menu
#
# A menu in the application user interface, which contains MenuItems
#

class Menu(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create new Menu object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Menu): Menu object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of Menu" )
        return self.conn.call(
            None,
            "Menu.create",
            {}
        )

    # add_item
    #
    # Add MenuItem to menu
    #
    # Arguments:
    #    'item' (MenuItem): Item to add to menu
    #    'index' (int): Index to insert item at. Use 0 to append to front. Use -1 to append to end. [Optional]
    #
    # Returns:
    #    (none)
    #
    def add_item(self, item, index = -1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.add_item",
            {
                'item': item,
                'index': index,
            }
        )

    # get_num_items
    #
    # Get number of items in menu
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of items in menu
    #
    def get_num_items(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.get_num_items",
            {}
        )

    # get_item_at
    #
    # Get MenuItem at given index within menu
    #
    # Arguments:
    #    'index' (int): Index of menu item
    #
    # Returns:
    #    (MenuItem): 
    #
    def get_item_at(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.get_item_at",
            {
                'index': index,
            }
        )

    # get_index_of_item
    #
    # Return the index of the given MenuItem within this Menu
    #
    # Arguments:
    #    'item' (MenuItem): Item to find index for
    #
    # Returns:
    #    (int): Index of MenuItem, -1 if not found
    #
    def get_index_of_item(self, item):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.get_index_of_item",
            {
                'item': item,
            }
        )

    # remove_item_at
    #
    # Remove menu item at the given index
    #
    # Arguments:
    #    'index' (int): Index of menu item
    #
    # Returns:
    #    (none)
    #
    def remove_item_at(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.remove_item_at",
            {
                'index': index,
            }
        )

    # remove_item
    #
    # Remove menu item from menu
    #
    # Arguments:
    #    'item' (MenuItem): MenuItem to remove
    #
    # Returns:
    #    (none)
    #
    def remove_item(self, item):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.remove_item",
            {
                'item': item,
            }
        )

    # remove_all_items
    #
    # Remove all menu items from menu
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def remove_all_items(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Menu.remove_all_items",
            {}
        )

Library.register_class( 'Menu', Menu )

