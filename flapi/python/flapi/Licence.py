from . import Library, Interface, FLAPIException
import json

# Licence
#
# Licence management
#

class Licence(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_system_id
    #
    # Return the system ID used to identify this system for licensing
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): System ID string
    #
    def get_system_id(self):
        if self.target != None:
            raise FLAPIException( "Static method get_system_id called on instance of Licence" )
        return self.conn.call(
            None,
            "Licence.get_system_id",
            {}
        )

    # get_licence_info
    #
    # Return licence information
    #
    # Arguments:
    #    'include_expired' (int): Flag indicating whether to include expired licenses in the list [Optional]
    #
    # Returns:
    #    (list): Array of installed licence items
    #        '<n>' (LicenceItem): 
    #
    def get_licence_info(self, include_expired = 0):
        if self.target != None:
            raise FLAPIException( "Static method get_licence_info called on instance of Licence" )
        return self.conn.call(
            None,
            "Licence.get_licence_info",
            {
                'include_expired': include_expired,
            }
        )

    # install_licence
    #
    # Install the given licence data
    #
    # Arguments:
    #    'licenceData' (string): String containing Base-64 encoded licence data
    #
    # Returns:
    #    (none)
    #
    def install_licence(self, licenceData):
        if self.target != None:
            raise FLAPIException( "Static method install_licence called on instance of Licence" )
        return self.conn.call(
            None,
            "Licence.install_licence",
            {
                'licenceData': licenceData,
            }
        )

Library.register_class( 'Licence', Licence )

