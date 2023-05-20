from . import Library, Interface, FLAPIException
import json

# ProgressDialog
#
# Display a progress dialog within the application
#

class ProgressDialog(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new ProgressDialog
    #
    # Arguments:
    #    'title' (string): Title of progress dialog
    #    'msg' (string): Message to display in progress dialog
    #    'cancellable' (int): Flag indicating that progress dialog has cancel button [Optional]
    #
    # Returns:
    #    (ProgressDialog): 
    #
    def create(self, title, msg, cancellable = 0):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of ProgressDialog" )
        return self.conn.call(
            None,
            "ProgressDialog.create",
            {
                'title': title,
                'msg': msg,
                'cancellable': cancellable,
            }
        )

    # show
    #
    # Show the progress dialog
    #
    # Arguments:
    #    'delay' (float): Only show progress dialog after a delay, in seconds [Optional]
    #
    # Returns:
    #    (none)
    #
    def show(self, delay = 0):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ProgressDialog.show",
            {
                'delay': delay,
            }
        )

    # set_title
    #
    # Set the title of the progress dialog
    #
    # Arguments:
    #    'title' (string): New title for dialog
    #
    # Returns:
    #    (none)
    #
    def set_title(self, title):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ProgressDialog.set_title",
            {
                'title': title,
            }
        )

    # set_progress
    #
    # Update the progress & message displayed in dialog
    #
    # Arguments:
    #    'progress' (float): Progress value between 0.0 and 1.0
    #    'message' (string): Progress message to display
    #
    # Returns:
    #    (none)
    #
    def set_progress(self, progress, message):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ProgressDialog.set_progress",
            {
                'progress': progress,
                'message': message,
            }
        )

    # hide
    #
    # Hide the progress dialog
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def hide(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ProgressDialog.hide",
            {}
        )

Library.register_class( 'ProgressDialog', ProgressDialog )

