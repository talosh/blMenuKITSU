from . import Library, Interface, FLAPIException
import json

# FormatSet
#
# The FormatSet interface allows enumeration of available resources on the FilmLight system such as formats, colour spaces, display render transforms, LUTs, etc.
#

class FormatSet(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # factory_formats
    #
    # Return factory FormatSet object for factory (built-in) formats
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (FormatSet): 
    #
    def factory_formats(self):
        if self.target != None:
            raise FLAPIException( "Static method factory_formats called on instance of FormatSet" )
        return self.conn.call(
            None,
            "FormatSet.factory_formats",
            {}
        )

    # global_formats
    #
    # Return global FormatSet object for formats defined in formats database
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (FormatSet): 
    #
    def global_formats(self):
        if self.target != None:
            raise FLAPIException( "Static method global_formats called on instance of FormatSet" )
        return self.conn.call(
            None,
            "FormatSet.global_formats",
            {}
        )

    # job_formats
    #
    # Return FormatSet object for formats defined in the given Job database
    #
    # Arguments:
    #    'hostname' (string): Database host
    #    'jobname' (string): Job name
    #
    # Returns:
    #    (FormatSet): 
    #
    def job_formats(self, hostname, jobname):
        if self.target != None:
            raise FLAPIException( "Static method job_formats called on instance of FormatSet" )
        return self.conn.call(
            None,
            "FormatSet.job_formats",
            {
                'hostname': hostname,
                'jobname': jobname,
            }
        )

    # get_drt_names
    #
    # Return array of Display Rendering Transform names
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of DRT names
    #        '<n>' (string): DRT Name
    #
    def get_drt_names(self):
        if self.target != None:
            raise FLAPIException( "Static method get_drt_names called on instance of FormatSet" )
        return self.conn.call(
            None,
            "FormatSet.get_drt_names",
            {}
        )

    # get_drt_info
    #
    # Return information for the given Display Rendering Transform name
    #
    # Arguments:
    #    'name' (string): Name of Display Rendering Transform
    #
    # Returns:
    #    (DRTInfo): 
    #
    def get_drt_info(self, name):
        if self.target != None:
            raise FLAPIException( "Static method get_drt_info called on instance of FormatSet" )
        return self.conn.call(
            None,
            "FormatSet.get_drt_info",
            {
                'name': name,
            }
        )

    # get_scope
    #
    # Return scope this is FormatSet represents
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string)
    #
    def get_scope(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_scope",
            {}
        )

    # get_scope_path
    #
    # Return the path for FormatSets representing a job/scene scope
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Scope path
    #
    def get_scope_path(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_scope_path",
            {}
        )

    # get_format_names
    #
    # Return array of format names
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Format names
    #        '<n>' (string): 
    #
    def get_format_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_format_names",
            {}
        )

    # get_basic_format_name
    #
    # Return name for a basic (auto-generated) format
    #
    # Arguments:
    #    'width' (int): Width of format
    #    'height' (int): Height of format
    #    'pixelAspectRatio' (float): Pixel aspect ratio [Optional]
    #
    # Returns:
    #    (string): Format name
    #
    def get_basic_format_name(self, width, height, pixelAspectRatio = 1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_basic_format_name",
            {
                'width': width,
                'height': height,
                'pixelAspectRatio': pixelAspectRatio,
            }
        )

    # get_format
    #
    # Return Format object for the named format
    #
    # Arguments:
    #    'name' (string): Format name
    #
    # Returns:
    #    (Format): 
    #
    def get_format(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_format",
            {
                'name': name,
            }
        )

    # get_colour_space_names
    #
    # Return array of colour space names
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of colour space names
    #        '<n>' (string): Colour space name
    #
    def get_colour_space_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_colour_space_names",
            {}
        )

    # get_colour_space_info
    #
    # Return information on the given colour space
    #
    # Arguments:
    #    'name' (string): Name of colour space
    #
    # Returns:
    #    (ColourSpaceInfo): 
    #
    def get_colour_space_info(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.get_colour_space_info",
            {
                'name': name,
            }
        )

    # add_format
    #
    # Add a new format to this FormatSet
    #
    # Arguments:
    #    'name' (string): Name of format
    #    'description' (string): Description of format
    #    'width' (int): Width of format in pixels
    #    'height' (int): Height of format in pixels
    #    'pixelAspectRatio' (float): Pixel aspect ratio [Optional]
    #
    # Returns:
    #    (Format): Object representing the newly created format
    #
    def add_format(self, name, description, width, height, pixelAspectRatio = 1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.add_format",
            {
                'name': name,
                'description': description,
                'width': width,
                'height': height,
                'pixelAspectRatio': pixelAspectRatio,
            }
        )

    # delete_format
    #
    # Delete a format from the FormatSet
    #
    # Arguments:
    #    'name' (string): Name of format to delete
    #
    # Returns:
    #    (none)
    #
    def delete_format(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "FormatSet.delete_format",
            {
                'name': name,
            }
        )

Library.register_class( 'FormatSet', FormatSet )

