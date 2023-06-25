from . import Library, Interface, FLAPIException
import json

# APITest
#
# Test API fundamentals
#

class APITest(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create an instance of the APITest object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (APITest): APITest object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of APITest" )
        return self.conn.call(
            None,
            "APITest.create",
            {}
        )

    # get
    #
    # Return client-specific instance of APITest
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (APITest): APITest object
    #
    def get(self):
        if self.target != None:
            raise FLAPIException( "Static method get called on instance of APITest" )
        return self.conn.call(
            None,
            "APITest.get",
            {}
        )

    # send_test_signal
    #
    # Emit TestSignal
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    None
    #
    def send_test_signal(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "APITest.send_test_signal",
            {}
        )

    # defer_test_signal
    #
    # Emit TestSignal asynchronously after a delay
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    None
    #
    def defer_test_signal(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "APITest.defer_test_signal",
            {}
        )

    # promise_test
    #
    # This function will do something time-consuming by returning a promise, making it asynchronous
    #
    # Arguments:
    #    'value' (string): Value to return via promise
    #
    # Returns:
    #    (string): Result
    #
    def promise_test(self, value):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "APITest.promise_test",
            {
                'value': value,
            }
        )

    # fail
    #
    # This method is expected to fail with an error message 'FAIL'
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def fail(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "APITest.fail",
            {}
        )

Library.register_class( 'APITest', APITest )

