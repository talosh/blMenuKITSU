from . import Library, Interface, FLAPIException
import json

# Format
#
# Format defines an image resolution and pixel aspect ratio with associated masks and burnins
#

class Format(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_description
    #
    # Return description of format
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Description
    #
    def get_description(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_description",
            {}
        )

    # get_resolution
    #
    # Return FormatInfo for given resolution of Format
    #
    # Arguments:
    #    'res' (string): Constant identify which resolution to fetch [Optional]
    #
    # Returns:
    #    (FormatInfo): 
    #
    def get_resolution(self, res = 'GMPR_HIGH'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_resolution",
            {
                'res': res,
            }
        )

    # get_mapping_names
    #
    # Return names of mapping from this format to other formats
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of names of format mapping
    #        '<n>' (string): Format name
    #
    def get_mapping_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_mapping_names",
            {}
        )

    # get_mapping
    #
    # Return definition of mapping from this format to named format
    #
    # Arguments:
    #    'name' (string): Name of target format
    #
    # Returns:
    #    (FormatMapping): 
    #
    def get_mapping(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_mapping",
            {
                'name': name,
            }
        )

    # get_masks
    #
    # Return array of FormatMasks defined for this format
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of masks
    #        '<n>' (FormatMask): 
    #
    def get_masks(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_masks",
            {}
        )

    # get_burnin_names
    #
    # Return array of names of burnins defined for this format
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of burnin names
    #        '<n>' (string): Burnin name
    #
    def get_burnin_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_burnin_names",
            {}
        )

    # add_burnin
    #
    # Create a new burnin with the given name, and return a FormatBurnin object for it
    #
    # Arguments:
    #    'name' (string): Burnin name
    #
    # Returns:
    #    (FormatBurnin): 
    #
    def add_burnin(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.add_burnin",
            {
                'name': name,
            }
        )

    # get_burnin
    #
    # Return FormatBurnin object for the named burnin
    #
    # Arguments:
    #    'name' (string): Burnin name
    #
    # Returns:
    #    (FormatBurnin): 
    #
    def get_burnin(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.get_burnin",
            {
                'name': name,
            }
        )

    # delete_burnin
    #
    # Delete the burnin with the given name
    #
    # Arguments:
    #    'name' (string): Burnin name
    #
    # Returns:
    #    (none)
    #
    def delete_burnin(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Format.delete_burnin",
            {
                'name': name,
            }
        )

Library.register_class( 'Format', Format )

