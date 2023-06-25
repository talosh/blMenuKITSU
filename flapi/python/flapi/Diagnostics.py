from . import Library, Interface, FLAPIException
import json

# Diagnostics
#
# Run diagnostics and query results
#

class Diagnostics(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get
    #
    # Create an instance of the Diagnostics module
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Diagnostics): 
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of Diagnostics" )
        return self.conn.call(
            None,
            "Diagnostics.get",
            {}
        )

    # get_hosts
    #
    # Return list of hosts that diags will be run on
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of hostnames
    #        '<n>' (string): Hostname
    #
    def get_hosts(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.get_hosts",
            {}
        )

    # get_groups
    #
    # Return list of diagnostic test groups
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of group names
    #        '<n>' (string): Group name
    #
    def get_groups(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.get_groups",
            {}
        )

    # get_tests
    #
    # Return list of diagnostic test information
    #
    # Arguments:
    #    'group' (string): Optional group name. Only return tests matching this group. [Optional]
    #
    # Returns:
    #    (list): Array of diagnostics
    #        '<n>' (DiagInfo): 
    #
    def get_tests(self, group):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.get_tests",
            {
                'group': group,
            }
        )

    # can_start
    #
    # Check to see if it is possible to start diagnostic tests
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag indicating whether it is possible to start diagnostics tests
    #
    def can_start(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.can_start",
            {}
        )

    # start
    #
    # Start diagnostic tests
    #
    # Arguments:
    #    'weight' (string): Weight of tests to run [Optional]
    #
    # Returns:
    #    (none)
    #
    def start(self, weight = 'DIAGWEIGHT_MEDIUM'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.start",
            {
                'weight': weight,
            }
        )

    # start_specific
    #
    # Start a specific diagnostic test and any of its pre-requisites
    #
    # Arguments:
    #    'test' (string): Name of diagnostic test
    #
    # Returns:
    #    (none)
    #
    def start_specific(self, test):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.start_specific",
            {
                'test': test,
            }
        )

    # cancel
    #
    # Cancel diagnostic test in progress
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def cancel(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.cancel",
            {}
        )

    # get_progress
    #
    # Return overall progress of diagnostic operation
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (DiagProgress): 
    #
    def get_progress(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.get_progress",
            {}
        )

    # get_results
    #
    # Return results for all tests
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (DiagResult): 
    #
    def get_results(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Diagnostics.get_results",
            {}
        )

Library.register_class( 'Diagnostics', Diagnostics )

