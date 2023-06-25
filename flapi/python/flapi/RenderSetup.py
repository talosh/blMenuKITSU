from . import Library, Interface, FLAPIException
import json

# RenderSetup
#
# Setup Baselight/Daylight scene for rendering
#

class RenderSetup(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_image_types
    #
    # Return array of supported image types for rendering
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (RenderFileTypeInfo): 
    #
    def get_image_types(self):
        if self.target != None:
            raise FLAPIException( "Static method get_image_types called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.get_image_types",
            {}
        )

    # get_movie_types
    #
    # Return array of movie types for rendering
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (RenderFileTypeInfo): 
    #
    def get_movie_types(self):
        if self.target != None:
            raise FLAPIException( "Static method get_movie_types called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.get_movie_types",
            {}
        )

    # get_movie_codecs
    #
    # Return array of video codecs available for the given movie type
    #
    # Arguments:
    #    'movieType' (string): Movie type key
    #
    # Returns:
    #    (list): 
    #        '<n>' (RenderCodecInfo): 
    #
    def get_movie_codecs(self, movieType):
        if self.target != None:
            raise FLAPIException( "Static method get_movie_codecs called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.get_movie_codecs",
            {
                'movieType': movieType,
            }
        )

    # get_movie_audio_codecs
    #
    # Return array of audio codecs available for the given movie type
    #
    # Arguments:
    #    'movieType' (string): Movie type key
    #
    # Returns:
    #    (list): 
    #        '<n>' (RenderCodecInfo): 
    #
    def get_movie_audio_codecs(self, movieType):
        if self.target != None:
            raise FLAPIException( "Static method get_movie_audio_codecs called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.get_movie_audio_codecs",
            {
                'movieType': movieType,
            }
        )

    # create
    #
    # Create a new RenderSetup instance
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (RenderSetup): New RenderSetup object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.create",
            {}
        )

    # create_from_scene
    #
    # Create a new RenderSetup instance configured to render the given Scene using its default deliverables
    #
    # Arguments:
    #    'scene' (Scene): Scene to render and take deliverable configuration from
    #
    # Returns:
    #    (RenderSetup): 
    #
    def create_from_scene(self, scene):
        if self.target != None:
            raise FLAPIException( "Static method create_from_scene called on instance of RenderSetup" )
        return self.conn.call(
            None,
            "RenderSetup.create_from_scene",
            {
                'scene': scene,
            }
        )

    # get_scene
    #
    # Return Scene object for RenderSetup
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Scene): 
    #
    def get_scene(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_scene",
            {}
        )

    # set_scene
    #
    # Set Scene to Render
    #
    # Arguments:
    #    'scene' (Scene): Scene object
    #
    # Returns:
    #    (none)
    #
    def set_scene(self, scene):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_scene",
            {
                'scene': scene,
            }
        )

    # save_into_scene
    #
    # Save the deliverables from this RenderSetup into the Scene. If a delta is not in progress on the Scene, a new delta will be created for the save operation.
    #
    # Arguments:
    #    'scene' (Scene): Scene to save deliverables into. If not specified, the deliverables will be saved into the scene currently associated with the RenderSetup. [Optional]
    #
    # Returns:
    #    (none)
    #
    def save_into_scene(self, scene = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.save_into_scene",
            {
                'scene': scene,
            }
        )

    # set_deliverables_from_scene
    #
    # Load Deliverables from Scene object assigned to this RenderSetup object
    #
    # Arguments:
    #    'scene' (Scene): If specified, load deliverables from the specified Scene instead of scene associated with RenderSetup [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_deliverables_from_scene(self, scene):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_deliverables_from_scene",
            {
                'scene': scene,
            }
        )

    # get_num_deliverables
    #
    # Render number of deliverables defined for this Scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of deliverables
    #
    def get_num_deliverables(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_num_deliverables",
            {}
        )

    # get_deliverable_names
    #
    # Return array of deliverable names
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of deliverable names
    #        '<n>' (string): Deliverable name
    #
    def get_deliverable_names(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_deliverable_names",
            {}
        )

    # get_deliverable
    #
    # Return the RenderDeliverable definition at the given index
    #
    # Arguments:
    #    'index' (int): Index of RenderDeliverable
    #
    # Returns:
    #    (RenderDeliverable): 
    #
    def get_deliverable(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_deliverable",
            {
                'index': index,
            }
        )

    # set_deliverable
    #
    # Set the settings for the deliverable at the given index
    #
    # Arguments:
    #    'index' (int): Index  of deliverable to  update
    #    'deliverable' (RenderDeliverable): Settings to use for this deliverable
    #
    # Returns:
    #    (none)
    #
    def set_deliverable(self, index, deliverable):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_deliverable",
            {
                'index': index,
                'deliverable': deliverable,
            }
        )

    # get_deliverable_by_name
    #
    # Get the settings for the RenderDeliverable definition with the given name.
    # Returns NULL if not matching deliverable can be found.
    #
    # Arguments:
    #    'name' (string): Name of RenderDeliverable
    #
    # Returns:
    #    (RenderDeliverable): 
    #
    def get_deliverable_by_name(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_deliverable_by_name",
            {
                'name': name,
            }
        )

    # set_deliverable_by_name
    #
    # Set the settings for the RenderDeliverable definition with the given name
    #
    # Arguments:
    #    'name' (string): Name of RenderDeliverable to update
    #    'deliverable' (RenderDeliverable): Settings to use for this deliverable
    #
    # Returns:
    #    (none)
    #
    def set_deliverable_by_name(self, name, deliverable):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_deliverable_by_name",
            {
                'name': name,
                'deliverable': deliverable,
            }
        )

    # add_deliverable
    #
    # Add a new deliverable to be generated as part of this render operation
    #
    # Arguments:
    #    'deliverable' (RenderDeliverable): Settings for render deliverable
    #
    # Returns:
    #    (none)
    #
    def add_deliverable(self, deliverable):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.add_deliverable",
            {
                'deliverable': deliverable,
            }
        )

    # delete_deliverable
    #
    # Delete the deliverable at the given index
    #
    # Arguments:
    #    'index' (int): Index of deliverable to delete
    #
    # Returns:
    #    (none)
    #
    def delete_deliverable(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.delete_deliverable",
            {
                'index': index,
            }
        )

    # delete_all_deliverables
    #
    # Delete all deliverables defined in the RenderSetup
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def delete_all_deliverables(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.delete_all_deliverables",
            {}
        )

    # get_deliverable_enabled
    #
    # Get enabled state of deliverable at given index
    #
    # Arguments:
    #    'index' (int): Index of deliverable
    #
    # Returns:
    #    (none)
    #
    def get_deliverable_enabled(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_deliverable_enabled",
            {
                'index': index,
            }
        )

    # set_deliverable_enabled
    #
    # Set enabled state of deliverable at given index
    #
    # Arguments:
    #    'index' (int): Index of deliverable
    #    'enabled' (int): Flag indicating whether deliverable is enabled for rendering
    #
    # Returns:
    #    (none)
    #
    def set_deliverable_enabled(self, index, enabled):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_deliverable_enabled",
            {
                'index': index,
                'enabled': enabled,
            }
        )

    # get_output_filename_for_deliverable
    #
    # Return the full filename for the given frame number of a deliverable
    #
    # Arguments:
    #    'index' (int): Index of deliverable
    #    'leave_container' (int): Leave %C container variable in returned path [Optional]
    #    'frame' (int): Frame number to generate filename for.
    #                   Default is -1 to indicate the first frame of the render operation. [Optional]
    #
    # Returns:
    #    (string): Full filename for rendered file/frame
    #
    def get_output_filename_for_deliverable(self, index, leave_container = 0, frame = -1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_output_filename_for_deliverable",
            {
                'index': index,
                'leave_container': leave_container,
                'frame': frame,
            }
        )

    # set_container
    #
    # Set the output container directory for all deliverables
    #
    # Arguments:
    #    'container' (string): Container path
    #
    # Returns:
    #    (none)
    #
    def set_container(self, container):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_container",
            {
                'container': container,
            }
        )

    # get_frames
    #
    # Get list of frame ranges to render
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): List of frame ranges
    #        '<n>' (FrameRange): 
    #
    def get_frames(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.get_frames",
            {}
        )

    # set_frames
    #
    # Set list of frame ranges to render
    #
    # Arguments:
    #    'frames' (list): List of frame ranges
    #        '<n>' (FrameRange): 
    #
    # Returns:
    #    (none)
    #
    def set_frames(self, frames):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.set_frames",
            {
                'frames': frames,
            }
        )

    # select_all
    #
    # Select all frames in Scene to render
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def select_all(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_all",
            {}
        )

    # select_shots
    #
    # Select the given Shots for rendering
    #
    # Arguments:
    #    'shots' (list): Array of Shot objects to select
    #        '<n>' (Shot): 
    #
    # Returns:
    #    (none)
    #
    def select_shots(self, shots):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_shots",
            {
                'shots': shots,
            }
        )

    # select_shot_ids
    #
    # Select the given Shots identified by their ID for rendering
    #
    # Arguments:
    #    'shotids' (list): Array of Shot IDs to select
    #        '<n>' (int): Shot ID
    #
    # Returns:
    #    (none)
    #
    def select_shot_ids(self, shotids):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_shot_ids",
            {
                'shotids': shotids,
            }
        )

    # select_graded_shots
    #
    # Select all graded shots to render
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def select_graded_shots(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_graded_shots",
            {}
        )

    # select_timeline_marks
    #
    # Select timeline marks matching the categories in the given category set
    #
    # Arguments:
    #    'categories' (set): Set of categories to match against [Optional]
    #
    # Returns:
    #    (none)
    #
    def select_timeline_marks(self, categories = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_timeline_marks",
            {
                'categories': categories,
            }
        )

    # select_shot_marks
    #
    # Select shot marks matching the categories in the given category set
    #
    # Arguments:
    #    'categories' (set): Set of categories to match against
    #
    # Returns:
    #    (none)
    #
    def select_shot_marks(self, categories):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_shot_marks",
            {
                'categories': categories,
            }
        )

    # select_poster_frames
    #
    # Select all shot poster frames to render
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def select_poster_frames(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_poster_frames",
            {}
        )

    # select_shots_of_category
    #
    # Select shots marked with one of the categories in the given category set
    #
    # Arguments:
    #    'categories' (set): Set of categories to match against
    #
    # Returns:
    #    (none)
    #
    def select_shots_of_category(self, categories):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.select_shots_of_category",
            {
                'categories': categories,
            }
        )

    # submit_to_queue
    #
    # Submit the current Render operation to a Queue for processing
    #
    # Arguments:
    #    'queue' (QueueManager): QueueManager object for machine running render queue
    #    'opname' (string): Operation name to use for queue job
    #
    # Returns:
    #    (RenderOpInfo): Operation info for job added to render queue
    #
    def submit_to_queue(self, queue, opname):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "RenderSetup.submit_to_queue",
            {
                'queue': queue,
                'opname': opname,
            }
        )

Library.register_class( 'RenderSetup', RenderSetup )

