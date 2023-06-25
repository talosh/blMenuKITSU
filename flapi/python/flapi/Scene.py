from . import Library, Interface, FLAPIException
import json

# Scene
#
# Now in Scene.md
#

class Scene(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # parse_path
    #
    # Convert the given string into a ScenePath object contaning Host, Job, Scene components, or raise an error if the path is invalid
    #
    # Arguments:
    #    'str' (string): Path string containing host, job, folder and scene elements
    #
    # Returns:
    #    (ScenePath): A ScenePath object containing the elements of the path
    #
    def parse_path(self, str):
        if self.target != None:
            raise FLAPIException( "Static method parse_path called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.parse_path",
            {
                'str': str,
            }
        )

    # path_to_string
    #
    # Convert the given ScenePath object into a string
    #
    # Arguments:
    #    'scenepath' (ScenePath): ScenePath object containing Host, Job, Scene fields
    #
    # Returns:
    #    (string): String form of ScenePath
    #
    def path_to_string(self, scenepath):
        if self.target != None:
            raise FLAPIException( "Static method path_to_string called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.path_to_string",
            {
                'scenepath': scenepath,
            }
        )

    # create
    #
    # Create an empty Scene object, which can then be used to create a temporary scene, a new scene, or load an existing scene.
    # After creating an empty Scene object, you must call ::temporary_scene_nonblock::, ::new_scene_nonblock:: or ::open_scene_nonblock::.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Scene): Scene object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.create",
            {}
        )

    # new_scene
    #
    # Create a new scene stored in a database. This function will block until the new scene has been created in the database. If the new scene cannot be created, this function will raise an exception containing an error message.
    #
    # Arguments:
    #    'scenepath' (ScenePath): 
    #    'options' (NewSceneOptions): Options to use for new scene
    #
    # Returns:
    #    (Scene): 
    #
    def new_scene(self, scenepath, options):
        if self.target != None:
            raise FLAPIException( "Static method new_scene called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.new_scene",
            {
                'scenepath': scenepath,
                'options': options,
            }
        )

    # open_scene
    #
    # Open a scene. This function will block until the scene has been opened. If the scene cannot be opened, this function will raise an exception containing an error message.
    #
    # Arguments:
    #    'scenepath' (ScenePath): ScenePath identifying scene to open
    #    'flags' (set):  [Optional]
    #
    # Returns:
    #    (Scene): 
    #
    def open_scene(self, scenepath, flags = None):
        if self.target != None:
            raise FLAPIException( "Static method open_scene called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.open_scene",
            {
                'scenepath': scenepath,
                'flags': flags,
            }
        )

    # temporary_scene
    #
    # Create a temporary scene that is not stored in a database. This function will block until the temporary scene has been created. If the temporary scene cannot be created, this function will raise an exception containing an error message.
    #
    # Arguments:
    #    'options' (NewSceneOptions): Options to use for new scene
    #
    # Returns:
    #    (Scene): 
    #
    def temporary_scene(self, options):
        if self.target != None:
            raise FLAPIException( "Static method temporary_scene called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.temporary_scene",
            {
                'options': options,
            }
        )

    # new_scene_nonblock
    #
    # Create a new scene
    #
    # Arguments:
    #    'scenepath' (ScenePath): 
    #    'options' (NewSceneOptions): Options to use for new scene
    #
    # Returns:
    #    (none)
    #
    def new_scene_nonblock(self, scenepath, options):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.new_scene_nonblock",
            {
                'scenepath': scenepath,
                'options': options,
            }
        )

    # open_scene_nonblock
    #
    # Open a scene
    #
    # Arguments:
    #    'scenepath' (ScenePath): ScenePath identifying scene to open
    #    'flags' (set):  [Optional]
    #
    # Returns:
    #    (none)
    #
    def open_scene_nonblock(self, scenepath, flags):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.open_scene_nonblock",
            {
                'scenepath': scenepath,
                'flags': flags,
            }
        )

    # temporary_scene_nonblock
    #
    # Create a temporary scene that is not stored in a database
    #
    # Arguments:
    #    'options' (NewSceneOptions): Options to use for new scene
    #
    # Returns:
    #    (none)
    #
    def temporary_scene_nonblock(self, options):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.temporary_scene_nonblock",
            {
                'options': options,
            }
        )

    # save_scene
    #
    # Save changes to scene into database
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def save_scene(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.save_scene",
            {}
        )

    # get_open_status
    #
    # Fetch status of scene open operation
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (OpenSceneStatus): 
    #
    def get_open_status(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_open_status",
            {}
        )

    # wait_until_open
    #
    # Wait for any scene opening/creation operations to complete, and return the status
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (OpenSceneStatus): 
    #
    def wait_until_open(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.wait_until_open",
            {}
        )

    # close_scene
    #
    # Close scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 on success, 0 if no scene is open.
    #
    def close_scene(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.close_scene",
            {}
        )

    # get_scene_pathname
    #
    # Get current scene's 'pathname' string (typically 'host:job:scene')
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Scene's pathname string
    #
    def get_scene_pathname(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_scene_pathname",
            {}
        )

    # get_scene_container
    #
    # Get the current container for the scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Container path for the scene
    #
    def get_scene_container(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_scene_container",
            {}
        )

    # set_scene_container
    #
    # Set the current container for the scene
    #
    # Arguments:
    #    'container' (string): New container path for the scene
    #
    # Returns:
    #    (none)
    #
    def set_scene_container(self, container):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_scene_container",
            {
                'container': container,
            }
        )

    # start_delta
    #
    # Start a 'delta' on a scene that has been opened read/write. A delta is a set of modifcations/edits on a scene that together constitute a single, logical operation/transaction. Each start_delta call must have a matching end_delta call (with one or more editing operations in between). Every delta has a user visible name (eg. 'Change Film Grade Exposure'). Once a delta has been completed/ended it becomes an atomic, undoable operation.
    #
    # Arguments:
    #    'name' (string): Name of delta to start
    #
    # Returns:
    #    (none)
    #
    def start_delta(self, name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.start_delta",
            {
                'name': name,
            }
        )

    # cancel_delta
    #
    # Cancel a 'delta' (a set of scene modifications/edits) previously started via
    # the start_delta() method, reverting the Scene back to the state it was in before start_delta().
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def cancel_delta(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.cancel_delta",
            {}
        )

    # end_delta
    #
    # End a 'delta' (a set of scene modifications/edits) previously started via
    # the start_delta() method.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def end_delta(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.end_delta",
            {}
        )

    # is_read_only
    #
    # Has this scene interface been opened 'read only'. Interfaces opened read only cannot modify their scene using the standard start_delta, make changes, end_delta paradigm. At any given time, multiple interfaces may reference/open the same scene in read only mode. However, at most only a single interface may reference a scene in read/write mode 
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if the interface is read only, 0 if not (read/write)
    #
    def is_read_only(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.is_read_only",
            {}
        )

    # is_read_only_for_host
    #
    # Is the scene opened 'read only' for the host application. Note: This will be false if any interface has opened the scene in read/write mode (or the host has explicitly opened the scene read/write itself)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if the scene is read only for the host, 0 if not
    #
    def is_read_only_for_host(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.is_read_only_for_host",
            {}
        )

    # get_formats
    #
    # Return FormatSet for formats defined within this Scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (FormatSet): 
    #
    def get_formats(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_formats",
            {}
        )

    # get_scene_settings
    #
    # Return SceneSettings object for this Scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (SceneSettings): 
    #
    def get_scene_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_scene_settings",
            {}
        )

    # get_category
    #
    # Return category definition
    #
    # Arguments:
    #    'key' (string): Key used to identify category
    #
    # Returns:
    #    (CategoryInfo): 
    #
    def get_category(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_category",
            {
                'key': key,
            }
        )

    # set_category
    #
    # Overwrites an existing category in the scene, or adds a new category if a category of that name doesn't exist. Will fail if an attempt is made to overwrite an built-in, read-only category.
    #
    # Arguments:
    #    'name' (string): User-visible name for this category. This value will also act as the key identifying the category when adding categories to strips and marks.
    #    'colour' (list): Colour associated with this category
    #        '<n>' (float): RGBA components
    #
    # Returns:
    #    (none)
    #
    def set_category(self, name, colour):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_category",
            {
                'name': name,
                'colour': colour,
            }
        )

    # get_mark_categories
    #
    # Return array of mark category keys
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of mark category keys
    #        '<n>' (string): Category
    #
    def get_mark_categories(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_mark_categories",
            {}
        )

    # get_strip_categories
    #
    # Return array of strip category keys
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of strip category keys
    #        '<n>' (string): Category
    #
    def get_strip_categories(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_strip_categories",
            {}
        )

    # get_start_frame
    #
    # Get frame number of start of first shot in scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_start_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_start_frame",
            {}
        )

    # get_end_frame
    #
    # Get frame number of end of last shot in scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_end_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_end_frame",
            {}
        )

    # get_working_frame_rate
    #
    # Get the working frame rate of the current scene (in FPS)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): The scene's frame rate (in FPS).
    #
    def get_working_frame_rate(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_working_frame_rate",
            {}
        )

    # get_record_timecode_for_frame
    #
    # Get record timecode for a given (timeline) frame number
    #
    # Arguments:
    #    'frame_num' (int): Timeline frame number
    #
    # Returns:
    #    (timecode): Record timecode
    #
    def get_record_timecode_for_frame(self, frame_num):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_record_timecode_for_frame",
            {
                'frame_num': frame_num,
            }
        )

    # get_shot_index_range
    #
    # Get index range of shots intersecting the (end exclusive) timeline frame range supplied
    #
    # Arguments:
    #    'startFrame' (float): timeline frame range start
    #    'endFrame' (float): timeline frame range end
    #
    # Returns:
    #    (ShotIndexRange): shot index range
    #
    def get_shot_index_range(self, startFrame, endFrame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_shot_index_range",
            {
                'startFrame': startFrame,
                'endFrame': endFrame,
            }
        )

    # get_num_shots
    #
    # Get number of Shots within scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of Shots
    #
    def get_num_shots(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_num_shots",
            {}
        )

    # get_shot_id_at
    #
    # Return the ID of the shot at the timeline frame number supplied
    #
    # Arguments:
    #    'frame' (int): Timeline frame number
    #
    # Returns:
    #    (int): ID of shot at frame, or -1 if none found
    #
    def get_shot_id_at(self, frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_shot_id_at",
            {
                'frame': frame,
            }
        )

    # get_shot_id
    #
    # Return the ID for the shot at the given index within the Scene
    #
    # Arguments:
    #    'index' (int): Index of shot within scene (relative to get_num_shots)
    #
    # Returns:
    #    (int): Shot ID
    #
    def get_shot_id(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_shot_id",
            {
                'index': index,
            }
        )

    # get_shot_ids
    #
    # Get an array of shots in the supplied indexed range. Each array entry
    # is an object containing basic information for that shot. Explicitly,
    # each shot entry will contain the following keys:
    # * ShotId - A shot idenfifier (which can be used to obtain a Shot object via get_shot() if required).
    # * StartFrame - The shot's timeline start frame
    # * EndFrame - The shot's timeline end frame
    # * PosterFrame - The shot's timeline poster frame
    # Returns new array shot list on success, NULL on error.
    #
    # Arguments:
    #    'firstIndex' (int): Index of first shot [Optional]
    #    'lastIndex' (int): Index of last shot [Optional]
    #
    # Returns:
    #    (list): Array of shot info objects
    #        '<n>' (ShotInfo): 
    #
    def get_shot_ids(self, firstIndex = 0, lastIndex = -1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_shot_ids",
            {
                'firstIndex': firstIndex,
                'lastIndex': lastIndex,
            }
        )

    # get_shot
    #
    # Create a new Shot object for the given shot ID
    #
    # Arguments:
    #    'shot_id' (int): Identifier of shot
    #
    # Returns:
    #    (Shot): Shot object
    #
    def get_shot(self, shot_id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_shot",
            {
                'shot_id': shot_id,
            }
        )

    # delete_shot
    #
    # Delete the given shot and its associated layers from the Scene
    #
    # Arguments:
    #    'shot_id' (int): ID of Shot to be deleted. Note this is *not* an index
    #    'cleanup' (int): Flag indicating whether vertical space left by shot should be reclaimed
    #    'closeGap' (int): Flag indicating whether horizontal gap left by shot should be closed
    #
    # Returns:
    #    (none)
    #
    def delete_shot(self, shot_id, cleanup, closeGap):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.delete_shot",
            {
                'shot_id': shot_id,
                'cleanup': cleanup,
                'closeGap': closeGap,
            }
        )

    # insert_bars
    #
    # Insert a Bars strip into the Scene
    #
    # Arguments:
    #    'barType' (string): The type of Bars to insert.
    #    'duration' (float): Duration for strip in frames
    #    'where' (string): Where in the scene the sequence should be inserted.
    #    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    #    'barsColourSpace' (string): Name of desired Bars colour space, or NULL
    #                                to use the default Bars colour space for the barType [Optional]
    #    'stackColourSpace' (string): Name of desired Stack colour space, or NULL
    #                                 to use the default Stack colour space for the barType [Optional]
    #
    # Returns:
    #    (Shot): Shot created by inserting Blank into Scene
    #
    def insert_bars(self, barType, duration, where, relativeTo = None, barsColourSpace = None, stackColourSpace = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.insert_bars",
            {
                'barType': barType,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'barsColourSpace': barsColourSpace,
                'stackColourSpace': stackColourSpace,
            }
        )

    # insert_blank
    #
    # Insert a Blank strip into the Scene
    #
    # Arguments:
    #    'red' (string): Red component of colour for blank
    #    'green' (string): Green component of colour for blank
    #    'blue' (string): Blue component of colour for blank
    #    'duration' (float): Duration for strip in frames
    #    'where' (string): Where in the scene the sequence should be inserted.
    #    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    #    'colourSpace' (string): Name of desired output colour space, or NULL
    #                            to use the working colour space [Optional]
    #
    # Returns:
    #    (Shot): Shot created by inserting Blank into Scene
    #
    def insert_blank(self, red, green, blue, duration, where, relativeTo = None, colourSpace = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.insert_blank",
            {
                'red': red,
                'green': green,
                'blue': blue,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'colourSpace': colourSpace,
            }
        )

    # insert_sequence
    #
    # Insert an image/movie sequence into the Scene
    #
    # Arguments:
    #    'sequence' (SequenceDescriptor): SequenceDescriptor for sequence to insert
    #    'where' (string): Where in the scene the sequence should be inserted.
    #    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    #    'colourSpace' (string): Input Colour Space to use for sequence. Leave NULL to determine automatically [Optional]
    #    'format' (string): Input Format to use for sequence. Leave NULL to use basic format [Optional]
    #
    # Returns:
    #    (Shot): Shot created by inserting SequenceDescriptor into Scene
    #
    def insert_sequence(self, sequence, where, relativeTo = None, colourSpace = None, format = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.insert_sequence",
            {
                'sequence': sequence,
                'where': where,
                'relativeTo': relativeTo,
                'colourSpace': colourSpace,
                'format': format,
            }
        )

    # insert_text
    #
    # Insert a Text strip into the Scene
    #
    # Arguments:
    #    'text' (string): The text to rendered in the Rop.
    #    'duration' (float): Duration for strip in frames
    #    'where' (string): Where in the scene the sequence should be inserted
    #    'relativeTo' (Shot): Shot to insert sequence relative to when using INSERT_BEFORE, INSERT_AFTER, INSERT_ABOVE, or INSERT_BELOW [Optional]
    #    'alignment' (string): Alignment for the text [Optional]
    #
    # Returns:
    #    (Shot): Shot created by inserting Text into Scene
    #
    def insert_text(self, text, duration, where, relativeTo = None, alignment = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.insert_text",
            {
                'text': text,
                'duration': duration,
                'where': where,
                'relativeTo': relativeTo,
                'alignment': alignment,
            }
        )

    # get_num_marks
    #
    # Return number of Timeline Marks in Scene
    #
    # Arguments:
    #    'type' (string): If specified, return number of marks of this type [Optional]
    #
    # Returns:
    #    (int): Number of marks
    #
    def get_num_marks(self, type = ''):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_num_marks",
            {
                'type': type,
            }
        )

    # get_mark_ids
    #
    # Return array of mark ids
    #
    # Arguments:
    #    'offset' (int): Offset within list of marks to fetch from [Optional]
    #    'count' (int): Number of Mark objects to fetch, use -1 to fetch all marks [Optional]
    #    'type' (string): If specified, only return marks of this type [Optional]
    #
    # Returns:
    #    (list): Array of Mark IDs
    #        '<n>' (int): Mark ID
    #
    def get_mark_ids(self, offset = 0, count = -1, type = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_mark_ids",
            {
                'offset': offset,
                'count': count,
                'type': type,
            }
        )

    # get_mark_ids_in_range
    #
    # Return array of mark ids within the given frame range in the Scene
    #
    # Arguments:
    #    'startF' (int): Start frame in Scene timeline
    #    'endF' (int): End frame in Scene timeline (exclusive)
    #    'type' (string): Mark type/category [Optional]
    #
    # Returns:
    #    (list): Array of Mark IDs
    #        '<n>' (int): Mark ID
    #
    def get_mark_ids_in_range(self, startF, endF, type = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_mark_ids_in_range",
            {
                'startF': startF,
                'endF': endF,
                'type': type,
            }
        )

    # get_mark
    #
    # Return Mark object for the given mark ID
    #
    # Arguments:
    #    'id' (int): Mark ID
    #
    # Returns:
    #    (Mark): Mark object matching the given mark ID
    #
    def get_mark(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_mark",
            {
                'id': id,
            }
        )

    # add_mark
    #
    # Add new Mark to the Scene at the given frame number
    #
    # Arguments:
    #    'frame' (int): Frame number
    #    'category' (string): Key identifying Mark Category
    #    'note' (string): Note text for mark [Optional]
    #
    # Returns:
    #    (int): ID of new mark object
    #
    def add_mark(self, frame, category, note = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.add_mark",
            {
                'frame': frame,
                'category': category,
                'note': note,
            }
        )

    # delete_mark
    #
    # Remove Mark object with the given ID
    #
    # Arguments:
    #    'id' (int): Mark ID
    #
    # Returns:
    #    (none)
    #
    def delete_mark(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.delete_mark",
            {
                'id': id,
            }
        )

    # get_metadata_definitions
    #
    # Return array of metadata item definitions
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of MetadataItems define metadata types defined in scene
    #        '<n>' (MetadataItem): 
    #
    def get_metadata_definitions(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_metadata_definitions",
            {}
        )

    # add_metadata_defn
    #
    # Add a new Metadata Item field to the Scene
    #
    # Arguments:
    #    'name' (string): User-visible name for Metadata Item
    #    'type' (string): Data type for Metadata Item
    #
    # Returns:
    #    (MetadataItem): Definition of new Metadata Item, including internal Key created for it
    #
    def add_metadata_defn(self, name, type):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.add_metadata_defn",
            {
                'name': name,
                'type': type,
            }
        )

    # delete_metadata_defn
    #
    # Delete a Metadata Item field from the Scene
    #
    # Arguments:
    #    'key' (string): Key identifying metadata item to delete
    #
    # Returns:
    #    (none)
    #
    def delete_metadata_defn(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.delete_metadata_defn",
            {
                'key': key,
            }
        )

    # get_metadata_property_types
    #
    # Return list of properties that can be defined for each MetadataItem
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of MetadataProperty objects
    #        '<n>' (MetadataProperty): 
    #
    def get_metadata_property_types(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_metadata_property_types",
            {}
        )

    # get_metadata_defn_property
    #
    # Set the value for the given property for the given metadata item key
    #
    # Arguments:
    #    'key' (string): Key identifying metadata item to modify
    #    'property' (string): Key identifying which property of the metadata item to get
    #
    # Returns:
    #    (string): Current value for metadata item property
    #
    def get_metadata_defn_property(self, key, property):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_metadata_defn_property",
            {
                'key': key,
                'property': property,
            }
        )

    # set_metadata_defn_property
    #
    # Set the value for the given property for the given metadata item key
    #
    # Arguments:
    #    'key' (string): Key identifying metadata item to modify
    #    'property' (string): Key identifying which property of the metadata item to set
    #    'value' (string): New property value
    #
    # Returns:
    #    (none)
    #
    def set_metadata_defn_property(self, key, property, value):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_metadata_defn_property",
            {
                'key': key,
                'property': property,
                'value': value,
            }
        )

    # get_look_names
    #
    # Return names of available Looks
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of names of looks
    #        '<n>' (string): Look name
    #
    def get_look_names(self):
        if self.target != None:
            raise FLAPIException( "Static method get_look_names called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.get_look_names",
            {}
        )

    # get_look_infos
    #
    # Get an array of available Looks.  Each array entry
    # is a LookInfo object containing the Name and Group
    # for each Look. Explicitly, each entry will contain
    # the following keys:
    # * Name - The name of the look.   This is unique and used as an identifier
    # * Group - The look group for the look
    # Returns new array of LookInfo objects on success, NULL on error.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of shot info objects
    #        '<n>' (LookInfo): 
    #
    def get_look_infos(self):
        if self.target != None:
            raise FLAPIException( "Static method get_look_infos called on instance of Scene" )
        return self.conn.call(
            None,
            "Scene.get_look_infos",
            {}
        )

    # set_transient_write_lock_deltas
    #
    # Use to enable (or disable) creation of deltas in a scene where FLAPI does not have the write lock.  In particular, this is needed for FLAPI scripts running inside the main application that wish to modify the current scene.
    #  When you open such a delta, you are preventing anything else from being able to make normal scene modifications.  You should therefore ensure you hold it open for as short a time as possible. 
    # Note also that you should not disable transient deltas while a transient delta is in progress.
    #
    # Arguments:
    #    'enable' (int): If non-zero, creation of deltas when FLAPI does not have the write lock will be enabled
    #
    # Returns:
    #    (none)
    #
    def set_transient_write_lock_deltas(self, enable):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_transient_write_lock_deltas",
            {
                'enable': enable,
            }
        )

    # set_custom_data
    #
    # Set a custom data value in the scene with the supplied (string) key. Setting a
    # custom data value does not require a delta. Also custom data values are unaffected
    # by undo/redo. Existing custom data values can be deleted from a scene by supplying
    # NULL/None/null as the data value (for an existing key).
    #
    # Arguments:
    #    'data_key' (string): Custom data value key
    #    'data_value' (any): New data value for the given key (or NULL/None/null to delete) [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_custom_data(self, data_key, data_value):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_custom_data",
            {
                'data_key': data_key,
                'data_value': data_value,
            }
        )

    # get_custom_data
    #
    # Get a custom data value from the scene previously set using set_custom_data.
    #
    # Arguments:
    #    'data_key' (string): Custom data value key
    #
    # Returns:
    #    (any): Custom data value found
    #
    def get_custom_data(self, data_key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_custom_data",
            {
                'data_key': data_key,
            }
        )

    # get_custom_data_keys
    #
    # Return sorted array of (string) keys that can be used to fetch scene
    # custom data values via get_custom_data.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): 
    #        '<n>' (string): Key string
    #
    def get_custom_data_keys(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_custom_data_keys",
            {}
        )

    # get_groups
    #
    # Return list of groups in the scene
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of group keys
    #        '<n>' (string): Groups
    #
    def get_groups(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_groups",
            {}
        )

    # get_group
    #
    # Return array of shot IDs for shots in group, or NULL if the group doesn't exist
    #
    # Arguments:
    #    'key' (string): Key used to identify group
    #
    # Returns:
    #    (list): Set of shot IDs [Optional]
    #        '<n>' (int): ShotId
    #
    def get_group(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.get_group",
            {
                'key': key,
            }
        )

    # set_group
    #
    # Create or update a group of shot IDs
    #
    # Arguments:
    #    'key' (string): Key used to identify group
    #    'shotIDs' (list): Array of shot IDs [Optional]
    #        '<n>' (int): ShotId
    #
    # Returns:
    #    (none)
    #
    def set_group(self, key, shotIDs):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.set_group",
            {
                'key': key,
                'shotIDs': shotIDs,
            }
        )

    # delete_group
    #
    # Delete Group
    #
    # Arguments:
    #    'key' (string): Key used to identify group
    #
    # Returns:
    #    (none)
    #
    def delete_group(self, key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Scene.delete_group",
            {
                'key': key,
            }
        )

Library.register_class( 'Scene', Scene )

