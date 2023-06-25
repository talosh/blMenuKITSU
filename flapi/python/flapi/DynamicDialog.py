from . import Library, Interface, FLAPIException
import json

# DynamicDialog
#
# This class can be used to show a complex dialog box to the user
#

class DynamicDialog(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a Dialog object
    #
    # Arguments:
    #    'title' (string): Title of dialog
    #    'defns' (list): Array of items to show in dialog
    #        '<n>' (DialogItem): Definition for an individual item in the DynamicDialog
    #    'settings' (dict): Dictionary of initial settings for dialog items
    #
    # Returns:
    #    (DynamicDialog): 
    #
    def create(self, title, defns, settings):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of DynamicDialog" )
        return self.conn.call(
            None,
            "DynamicDialog.create",
            {
                'title': title,
                'defns': defns,
                'settings': settings,
            }
        )

    # modal
    #
    # Display a Dialog object and return the settings
    #
    # Arguments:
    #    'title' (string): Title of dialog
    #    'defns' (list): Array of items to show in dialog
    #        '<n>' (DialogItem): 
    #    'settings' (dict): Dictionary of initial settings for dialog items
    #    'width' (int): Desired width of dialog box [Optional]
    #    'height' (int): Desired height of dialog box [Optional]
    #
    # Returns:
    #    (dict): Settings chosen by user, or NULL if dialog was cancelled
    #
    def modal(self, title, defns, settings, width = None, height = None):
        if self.target != None:
            raise FLAPIException( "Static method modal called on instance of DynamicDialog" )
        return self.conn.call(
            None,
            "DynamicDialog.modal",
            {
                'title': title,
                'defns': defns,
                'settings': settings,
                'width': width,
                'height': height,
            }
        )

    # show_modal
    #
    # Show dialog to user
    #
    # Arguments:
    #    'width' (int): Desired width of dialog box [Optional]
    #    'height' (int): Desired height of dialog box [Optional]
    #
    # Returns:
    #    (dict): Settings chosen by user, or NULL if dialog was cancelled
    #
    def show_modal(self, width = None, height = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "DynamicDialog.show_modal",
            {
                'width': width,
                'height': height,
            }
        )

    # get_settings
    #
    # Return current dialog settings
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): 
    #
    def get_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "DynamicDialog.get_settings",
            {}
        )

    # set_settings
    #
    # Set current dialog settings
    #
    # Arguments:
    #    'settings' (dict): 
    #
    # Returns:
    #    (none)
    #
    def set_settings(self, settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "DynamicDialog.set_settings",
            {
                'settings': settings,
            }
        )

    # set_timer_callback
    #
    # Set time until callback signal TimerCallback will be sent
    #
    # Arguments:
    #    'delay' (int): Time until signal in milliseconds
    #    'repeat' (int): Flag indicating signal should repeat until cancel_timer_callback is called [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_timer_callback(self, delay, repeat = 1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "DynamicDialog.set_timer_callback",
            {
                'delay': delay,
                'repeat': repeat,
            }
        )

    # cancel_timer_callback
    #
    # Cancel any pending timer callback
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def cancel_timer_callback(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "DynamicDialog.cancel_timer_callback",
            {}
        )

Library.register_class( 'DynamicDialog', DynamicDialog )

