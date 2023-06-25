from . import Library, Interface, FLAPIException
import json

# CurrentGrade
#
#

class CurrentGrade(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get
    #
    # Get (singleton) current grade interface for the connected client
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (CurrentGrade): CurrentGrade object
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of CurrentGrade" )
        return self.conn.call(
            None,
            "CurrentGrade.get",
            {}
        )

    # request_update_current_shot_signal
    #
    # Explicitly request an 'UpdateCurrentShot' signal. This can be useful, for example, when first connecting to the current grade module for initialising a client's internal state.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    None
    #
    def request_update_current_shot_signal(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "CurrentGrade.request_update_current_shot_signal",
            {}
        )

    # get_current_cursor
    #
    # Get an interface to the cursor currently in use by Baselight for grading.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Cursor): Current cursor interface
    #
    def get_current_cursor(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "CurrentGrade.get_current_cursor",
            {}
        )

    # is_enabled
    #
    # Is this interface currently enabled. Note: The current grade interface may be arbitrarily enabled/disabled from the host application itself.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag indicating whether the interface is currently enabled
    #
    def is_enabled(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "CurrentGrade.is_enabled",
            {}
        )

Library.register_class( 'CurrentGrade', CurrentGrade )

