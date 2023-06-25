from . import Library, Interface, FLAPIException
import json

# Timer
#
# A Timer allows your script to be triggered periodically to perform processing
#

class Timer(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new Timer object
    #
    # Arguments:
    #    'interval' (int): Number of milliseconds between timer ticks firing
    #    'repeat' (int): Flag indicating whether timer should repeat after interval elapses [Optional]
    #
    # Returns:
    #    (Timer): 
    #
    def create(self, interval, repeat = 1):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of Timer" )
        return self.conn.call(
            None,
            "Timer.create",
            {
                'interval': interval,
                'repeat': repeat,
            }
        )

    # start
    #
    # Start timer running
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def start(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Timer.start",
            {}
        )

    # is_started
    #
    # Inquire if timer is started
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag indicating whether timer is started
    #
    def is_started(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Timer.is_started",
            {}
        )

    # stop
    #
    # Stop timer firing
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def stop(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Timer.stop",
            {}
        )

    # get_interval
    #
    # Return interval between timer ticks firing
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Interval in milliseconds
    #
    def get_interval(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Timer.get_interval",
            {}
        )

    # set_interval
    #
    # Set interval between timer ticks firing
    #
    # Arguments:
    #    'interval' (int): Interval in milliseconds
    #
    # Returns:
    #    (none)
    #
    def set_interval(self, interval):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Timer.set_interval",
            {
                'interval': interval,
            }
        )

Library.register_class( 'Timer', Timer )

