from . import Library, Interface, FLAPIException
import json

# FormatBurnin
#
# Definition of a burn-in for a Format
#

class FormatBurnin(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_opacity
    #
    # Get burnin opacity
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Opacity
    #
    def get_opacity(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.get_opacity",
            {}
        )

    # set_opacity
    #
    # Set burnin opacity
    #
    # Arguments:
    #    'opacity' (float): Opacity
    #
    # Returns:
    #    (none)
    #
    def set_opacity(self, opacity):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.set_opacity",
            {
                'opacity': opacity,
            }
        )

    # get_box_colour
    #
    # Set colour of box around text items
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): RGBA box colour
    #        '<n>' (float): 
    #
    def get_box_colour(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.get_box_colour",
            {}
        )

    # set_box_colour
    #
    # Set colour of box around text items
    #
    # Arguments:
    #    'colour' (list): RGBA box colour
    #        '<n>' (float): 
    #
    # Returns:
    #    (none)
    #
    def set_box_colour(self, colour):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.set_box_colour",
            {
                'colour': colour,
            }
        )

    # get_font
    #
    # Get font name for this burnin
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Font name
    #
    def get_font(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.get_font",
            {}
        )

    # set_font
    #
    # Get font name for this burnin
    #
    # Arguments:
    #    'name' (string): Font name
    #
    # Returns:
    #    (none)
    #
    def set_font(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.set_font",
            {
                'name': name,
            }
        )

    # add_item
    #
    # Add new item to the burnin
    #
    # Arguments:
    #    'item' (FormatBurninItem): 
    #
    # Returns:
    #    (none)
    #
    def add_item(self, item):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.add_item",
            {
                'item': item,
            }
        )

    # get_num_items
    #
    # Return number of items defined within this burnin
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of burnin items
    #
    def get_num_items(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.get_num_items",
            {}
        )

    # get_item
    #
    # Return definition for the burnin item at the given index
    #
    # Arguments:
    #    'index' (int): Index of burnin item
    #
    # Returns:
    #    (FormatBurninItem): 
    #
    def get_item(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.get_item",
            {
                'index': index,
            }
        )

    # set_item
    #
    # Return definition for the burnin item at the given index
    #
    # Arguments:
    #    'index' (int): Index of burnin item
    #    'item' (FormatBurninItem): 
    #
    # Returns:
    #    (none)
    #
    def set_item(self, index, item):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.set_item",
            {
                'index': index,
                'item': item,
            }
        )

    # delete_item
    #
    # Delete the burnin item at the given index
    #
    # Arguments:
    #    'index' (int): Index of burnin item
    #
    # Returns:
    #    (none)
    #
    def delete_item(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatBurnin.delete_item",
            {
                'index': index,
            }
        )

Library.register_class( 'FormatBurnin', FormatBurnin )

