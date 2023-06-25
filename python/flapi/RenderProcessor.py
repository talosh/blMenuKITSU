from . import Library, Interface, FLAPIException
import json

# RenderProcessor
#
# A RenderProcessor will execute a RenderSetup and produce deliverable data
#

class RenderProcessor(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get
    #
    # Get RenderProcessor instance
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (RenderProcessor): 
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of RenderProcessor" )
        return self.conn.call(
            None,
            "RenderProcessor.get",
            {}
        )

    # start
    #
    # Start render operation for the given RenderSetup
    #
    # Arguments:
    #    'renderSetup' (RenderSetup): 
    #
    # Returns:
    #    (none)
    #
    def start(self, renderSetup):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderProcessor.start",
            {
                'renderSetup': renderSetup,
            }
        )

    # get_progress
    #
    # Returns current render progress
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (RenderStatus): 
    #
    def get_progress(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderProcessor.get_progress",
            {}
        )

    # get_log
    #
    # Get log of operation progress
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of log entries from this render operation
    #        '<n>' (RenderProcessorLogItem): 
    #
    def get_log(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderProcessor.get_log",
            {}
        )

    # shutdown
    #
    # Shutdown the RenderProcessor instance. This releases any resources in use by the RenderProcessor.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def shutdown(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderProcessor.shutdown",
            {}
        )

Library.register_class( 'RenderProcessor', RenderProcessor )

