from . import Library, Interface, FLAPIException
import json

# Shot
#
# A shot in Baselight is a set of strips comprising a top strip (typically containing a Sequence operator referencing input media) and the strips lying directly underneath it. These strips apply image-processing and other operations to the top strip.
#

class Shot(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # is_valid
    #
    #  Called to determine if the shot object references a valid top strip an open scene. A shot object may become invalid in a couple of ways:
    #   * The scene which it is in is closed.
    #   * The shot's top strip is removed from the scene's timeline.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if this shot interface is valid, 0 if not.
    #
    def is_valid(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.is_valid",
            {}
        )

    # get_scene
    #
    # Get the scene object which this shot is a part of.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (Scene): The shot's scene.
    #
    def get_scene(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_scene",
            {}
        )

    # get_id
    #
    # Get the shot's identifier, an integer which uniquely identifies the shot within the timeline. The id is persistent, remaining constant even if the scene containing the shot is closed and reopened. 
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): The shot's unique identifier.
    #
    def get_id(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_id",
            {}
        )

    # get_start_frame
    #
    # Get the start frame of the shot within the scene which contains it. Because the time extent of a shot is actually defined by the shot's top strip, the start frame is actually the start frame of the top strip.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Start frame of the shot (inclusive).
    #
    def get_start_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_start_frame",
            {}
        )

    # get_end_frame
    #
    # Get the end frame of the shot within the scene which contains it. Because the time extent of a shot is defined by the shot's top strip, the end frame is actually the end frame of the top strip. In Baselight, shot extents are defined in floating-point frames and are start-inclusive and end-exclusive. This means that the shot goes all the way up to the beginning of the end frame, but doesn't include it. 
    # So a 5-frame shot  starting at frame 100.0 would have an end frame 105.0 and 104.75, 104.9 and 104.99999 would all lie within the shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): End frame of the shot (exclusive).
    #
    def get_end_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_end_frame",
            {}
        )

    # get_poster_frame
    #
    # Get the poster frame of the shot within the scene that contains it. 
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Poster frame number of the shot.
    #
    def get_poster_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_poster_frame",
            {}
        )

    # get_start_timecode
    #
    # Get the start record timecode of the shot
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (timecode): Start record timecode of the shot
    #
    def get_start_timecode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_start_timecode",
            {}
        )

    # get_end_timecode
    #
    # Get the end record timecode of the shot
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (timecode): End record timecode of the shot (exclusive)
    #
    def get_end_timecode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_end_timecode",
            {}
        )

    # get_timecode_at_frame
    #
    # Get the record timecode at the given frame within the shot
    #
    # Arguments:
    #    'frame' (int): Frame relative to start of shot
    #
    # Returns:
    #    (timecode): Record timecode for frame
    #
    def get_timecode_at_frame(self, frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_timecode_at_frame",
            {
                'frame': frame,
            }
        )

    # get_src_start_frame
    #
    # Return start frame number within source sequence/movie
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_src_start_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_start_frame",
            {}
        )

    # get_src_end_frame
    #
    # Return end frame number within source sequence/movie (exclusive)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_src_end_frame(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_end_frame",
            {}
        )

    # get_src_start_timecode
    #
    # Return start timecode within source sequence/movie
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (timecode): Start source timecode
    #
    def get_src_start_timecode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_start_timecode",
            {}
        )

    # get_src_end_timecode
    #
    # Return end timecode within source sequence/movie (exclusive)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (timecode): End source timecode
    #
    def get_src_end_timecode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_end_timecode",
            {}
        )

    # get_src_timecode_at_frame
    #
    # Return source timecode at the given frame within the shot
    #
    # Arguments:
    #    'frame' (int): Frame number relative to start of shot
    #
    # Returns:
    #    (timecode): Timecode for given frame
    #
    def get_src_timecode_at_frame(self, frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_timecode_at_frame",
            {
                'frame': frame,
            }
        )

    # get_src_start_keycode
    #
    # Return start keycode within source sequence/movie
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (keycode): Start source keycode
    #
    def get_src_start_keycode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_start_keycode",
            {}
        )

    # get_src_end_keycode
    #
    # Return end keycode within source sequence/movie (exclusive)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (keycode): End source keycode
    #
    def get_src_end_keycode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_src_end_keycode",
            {}
        )

    # get_input_colour_space
    #
    # Return the input colour space defined for this shot. Can be 'None', indicating no specific colour space defined. For RAW codecs, this may be 'auto' indicating that the input colour space will be determined by the SDK used to decode to the image data. In either case the actual input colour space can be determined by call get_actual_input_colour_space().
    #
    # Arguments:
    #    'eye' (string): Find input colour space for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (string): Colour space name, or 'auto'
    #
    def get_input_colour_space(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_input_colour_space",
            {
                'eye': eye,
            }
        )

    # set_input_colour_space
    #
    # Set the input colour space
    #
    # Arguments:
    #    'name' (string): Input colour space name, or 'Auto'
    #    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_input_colour_space(self, name, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_input_colour_space",
            {
                'name': name,
                'eye': eye,
            }
        )

    # get_actual_input_colour_space
    #
    # Return the input colour space for this shot.
    # If the input colour space is set to 'Auto', the actual colour space name will be returned.
    #
    # Arguments:
    #    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (string): Colour space name
    #
    def get_actual_input_colour_space(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_actual_input_colour_space",
            {
                'eye': eye,
            }
        )

    # get_input_format
    #
    # Return the input format name for this shot
    #
    # Arguments:
    #    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (string): Format name
    #
    def get_input_format(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_input_format",
            {
                'eye': eye,
            }
        )

    # set_input_format
    #
    # Set the input format name for this shot
    #
    # Arguments:
    #    'name' (string): Format name
    #    'eye' (string): Input colour space for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_input_format(self, name, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_input_format",
            {
                'name': name,
                'eye': eye,
            }
        )

    # get_input_video_lut
    #
    # Return the input video lut value for this shot
    #
    # Arguments:
    #    'eye' (string): Input video LUT for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (string): Input Video LUT (either VIDEOLUT_NONE or VIDEOLUT_UNSCALE) or NULL/None/null if an input video LUT is inappropriate for the shot's current media type and input colour space settings (indicated by the "Legal to Full Scale" button not being present in the Baselight Sequence operator UI.
    #
    def get_input_video_lut(self, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_input_video_lut",
            {
                'eye': eye,
            }
        )

    # set_input_video_lut
    #
    # Set the input video LUT for this shot
    #
    # Arguments:
    #    'video_lut' (string): Video LUT to be applied to the input sequence. The only permitted values for this method are VIDEOLUT_UNSCALE and VIDEOLUT_NONE.
    #    'eye' (string): Input video LUT for the given eye in a stereo sequence [Optional]
    #
    # Returns:
    #    (none)
    #
    def set_input_video_lut(self, video_lut, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_input_video_lut",
            {
                'video_lut': video_lut,
                'eye': eye,
            }
        )

    # get_metadata
    #
    # Get metadata values for the keys provided. The possible keys and the value type for each key are obtained using the Scene.get_metadata_definitions method.
    #
    # Arguments:
    #    'md_keys' (set): Set of metadata keys whose values are required.
    #
    # Returns:
    #    (dict): Key/value pairs containing the metadata obtained.
    #
    def get_metadata(self, md_keys):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_metadata",
            {
                'md_keys': md_keys,
            }
        )

    # get_metadata_strings
    #
    # Get metadata values expressed as strings for the keys provided. The possible keys are obtained using the Scene.get_metadata_definitions method.
    #
    # Arguments:
    #    'md_keys' (set): Set of metadata keys whose values are required.
    #
    # Returns:
    #    (dict): Key/value pairs containing the metadata obtained. All the values will have been converted to strings.
    #
    def get_metadata_strings(self, md_keys):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_metadata_strings",
            {
                'md_keys': md_keys,
            }
        )

    # set_metadata
    #
    # Set metadata values for the keys provided. The possible keys and the value type for each key are obtained using the Scene.get_metadata_definitions method.
    #
    # Arguments:
    #    'metadata' (dict): Key/value pairs of metadata to assign in the shot.
    #
    # Returns:
    #    (none)
    #
    def set_metadata(self, metadata):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_metadata",
            {
                'metadata': metadata,
            }
        )

    # get_sequence_descriptor
    #
    # Get a SequenceDescriptor object that represents the input media for this shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (SequenceDescriptor): Object containing information about the shot's input media.
    #
    def get_sequence_descriptor(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_sequence_descriptor",
            {}
        )

    # supports_client_event_data
    #
    # Does this shot support client event lists/data.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): 1 if the shot supports client event data, otherwise 0.
    #
    def supports_client_event_data(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.supports_client_event_data",
            {}
        )

    # get_client_event_list
    #
    # Get array of client events (notes/flags) for either an entire shot, or a specific frame of a shot. When querying the event list at a specific frame, NULL/None/null will be returned if no event list exists at that frame or the shot. The events array returned will be chronologically sorted (oldest first). Each event entry is itself a dictionary describing that event.
    #
    # Arguments:
    #    'list_frame' (int): Identifies which event list to return; either for the entire shot (if no list_frame supplied), or for a specific, shot start relative frame number [Optional]
    #
    # Returns:
    #    (list): Array of client events for the shot.
    #        '<n>' (dict): Client event entry.
    #            'ClientName' (string): The name of the client that added the entry.
    #            'EventId' (int): Identifier used to modify/delete this event.
    #            'EventType' (string): The event type. Currently either "Note" or "Flag".
    #            'NoteText' (string): Only valid when "EventType" value is "Note". The note text. [Optional]
    #            'RelativeTimeString' (string): Time the entry was created as a formatted as a user friendly string (eg. "Tuesday 17:25").
    #            'Source' (string): Source of the event. Either "FLAPI" if event was added from an external source, or "Application" if added from the Filmlight host application.
    #            'Time' (int): Time the entry was created (in seconds since 1/1/70 UTC).
    #
    def get_client_event_list(self, list_frame = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_client_event_list",
            {
                'list_frame': list_frame,
            }
        )

    # add_client_note
    #
    # Add a client note to either the client event list for an entire shot, or to the client event list at a specific frame number.
    #
    # Arguments:
    #    'client_name' (string): Name of client adding the note.
    #    'note_text' (string): Note text.
    #    'event_list_frame' (int): Client event list frame number, or NULL/None/null for the entire shot's client event list [Optional]
    #
    # Returns:
    #    (int): Event identifier which can be used to edit/delete the note later.
    #
    def add_client_note(self, client_name, note_text, event_list_frame = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.add_client_note",
            {
                'client_name': client_name,
                'note_text': note_text,
                'event_list_frame': event_list_frame,
            }
        )

    # add_client_flag
    #
    # Add a new client flag entry to either the client event list for an entire shot, or to the client event list at a specific frame number. A client event list only supports a single flag event for a given client name; If one already exists, a call to this method will replace it with a new one. 
    #
    # Arguments:
    #    'client_name' (string): Name of client flagging the shot.
    #    'event_list_frame' (int): Client event list frame number, or NULL/None/null for the entire shot's client event list [Optional]
    #
    # Returns:
    #    (int): Event identifier which can be used to remove the flag later.
    #
    def add_client_flag(self, client_name, event_list_frame = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.add_client_flag",
            {
                'client_name': client_name,
                'event_list_frame': event_list_frame,
            }
        )

    # delete_client_event
    #
    # Delete the (note or flag) event with the supplied id from the shot's client event list.
    #
    # Arguments:
    #    'event_id' (string): Event list identifier of event to delete.
    #
    # Returns:
    #    (int): 1 on success, 0 if no event found.
    #
    def delete_client_event(self, event_id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.delete_client_event",
            {
                'event_id': event_id,
            }
        )

    # set_client_event_metadata
    #
    # Set custom metadata key/value pairs for the client event with the supplied ID.
    #
    # Arguments:
    #    'client_event_id' (int): ID of client event
    #    'metadata' (dict): Key/value pairs containing the metadata for the client event.
    #
    # Returns:
    #    (none)
    #
    def set_client_event_metadata(self, client_event_id, metadata):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'metadata': metadata,
            }
        )

    # get_client_event_metadata
    #
    # Get custom metadata key/value pairs for the client event with the supplied ID.
    #
    # Arguments:
    #    'client_event_id' (int): ID of client event
    #    'md_keys' (set): Set of metadata keys whose values are required, or NULL/None/null for all metadata. [Optional]
    #
    # Returns:
    #    (dict): Key/value pairs containing the metadata for the client event.
    #
    def get_client_event_metadata(self, client_event_id, md_keys = None):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'md_keys': md_keys,
            }
        )

    # delete_client_event_metadata
    #
    # Delete a single metadata key/value item from the client event with the supplied ID.
    #
    # Arguments:
    #    'client_event_id' (int): ID of client event
    #    'metadata_key' (any): Key of metadata item to remove from client event.
    #
    # Returns:
    #    (none)
    #
    def delete_client_event_metadata(self, client_event_id, metadata_key):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.delete_client_event_metadata",
            {
                'client_event_id': client_event_id,
                'metadata_key': metadata_key,
            }
        )

    # get_client_event_list_frames
    #
    # Get array of (shot start relative) frame numbers of frames with client event lists
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of frames with client event lists
    #        '<n>' (int): frame number
    #
    def get_client_event_list_frames(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_client_event_list_frames",
            {}
        )

    # delete_frame_client_event_list
    #
    # Delete the entire client event list at the given shot frame (if any).
    #
    # Arguments:
    #    'list_frame' (int): Frame number of frame containing the event list
    #
    # Returns:
    #    (none)
    #
    def delete_frame_client_event_list(self, list_frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.delete_frame_client_event_list",
            {
                'list_frame': list_frame,
            }
        )

    # get_client_data_summary
    #
    # Get summary info on any client data associated with this shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Client summary info
    #        'Clients' (dict): Dictionary containing client name keys/entries for all clients who have added data to this shot. The value associated with each key is a set containing all the types of data that client has added ("Note" and/or "Flag").
    #
    def get_client_data_summary(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_client_data_summary",
            {}
        )

    # get_num_marks
    #
    # Get number of marks within shot.
    # If type is supplied, only return number of marks of the given type
    #
    # Arguments:
    #    'type' (string): Mark type
    #
    # Returns:
    #    (int): Number of marks
    #
    def get_num_marks(self, type):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_num_marks",
            {
                'type': type,
            }
        )

    # get_mark_ids
    #
    # Get shot mark ids within the shot.
    # Shot marks are marks which are attached to the shot's top strip.
    # If type is specified, only return marks of matching type.
    #
    # Arguments:
    #    'offset' (int): Offset into array of marks [Optional]
    #    'count' (int): Number of marks to fetch, pass -1 to fetch all [Optional]
    #    'type' (string): Mark type, which is a category name. Only shot marks of this type will be returned. If not provided, all marks within the shot will be returned. Possible categories for marks can be obtained using the Scene.get_mark_categories method. [Optional]
    #    'eye' (string): Which eye to get marks for stereo sequence [Optional]
    #
    # Returns:
    #    (list): Array of Mark IDs
    #        '<n>' (int): Mark ID
    #
    def get_mark_ids(self, offset = 0, count = -1, type = None, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_mark_ids",
            {
                'offset': offset,
                'count': count,
                'type': type,
                'eye': eye,
            }
        )

    # get_mark
    #
    # Get Mark object for given ID
    #
    # Arguments:
    #    'id' (int): Mark ID
    #
    # Returns:
    #    (Mark): Mark object
    #
    def get_mark(self, id):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_mark",
            {
                'id': id,
            }
        )

    # add_mark
    #
    # Add new Mark to the shot at the given source frame
    #
    # Arguments:
    #    'frame' (int): Source frame number
    #    'category' (string): Mark category
    #    'note' (string): Mark note text [Optional]
    #    'eye' (string): Which eye to add mark for in stereo sequence [Optional]
    #
    # Returns:
    #    (int): Mark ID
    #
    def add_mark(self, frame, category, note = None, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.add_mark",
            {
                'frame': frame,
                'category': category,
                'note': note,
                'eye': eye,
            }
        )

    # delete_mark
    #
    # Delete the Mark object with the given mark ID
    #
    # Arguments:
    #    'id' (int): Mark ID
    #    'eye' (string): Which eye to delete mark for in stereo sequence [Optional]
    #
    # Returns:
    #    (none)
    #
    def delete_mark(self, id, eye = 'GMSE_MONO'):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.delete_mark",
            {
                'id': id,
                'eye': eye,
            }
        )

    # get_categories
    #
    # Get the set of categories assigned to this shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (set): Set of category keys. The Scene.get_category method can be used to obtain information (such as the UI colour and user-readable name) about a given category key.
    #
    def get_categories(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_categories",
            {}
        )

    # set_categories
    #
    # Set the categories assigned to this shot
    #
    # Arguments:
    #    'categories' (set): Set of category keys to be assigned to the shot.
    #
    # Returns:
    #    (none)
    #
    def set_categories(self, categories):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_categories",
            {
                'categories': categories,
            }
        )

    # insert_blg_stack
    #
    # Insert a BLG stack at the bottom of the shot.
    #
    # Arguments:
    #    'blg_path' (string): Path to the BLG to be applied to the shot.
    #
    # Returns:
    #    (none)
    #
    def insert_blg_stack(self, blg_path):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_blg_stack",
            {
                'blg_path': blg_path,
            }
        )

    # get_blg_payload
    #
    # Returns the BLG payload for this shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): String containing the payload.
    #
    def get_blg_payload(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_blg_payload",
            {}
        )

    # apply_blg_payload
    #
    # Insert a BLG stack at the bottom of the shot.
    #
    # Arguments:
    #    'blg_payload' (string): A BLG payload as returned by get_blg_payload().
    #    'blg_resources' (string): BLG resources as returned by get_blg_resources().
    #
    # Returns:
    #    (none)
    #
    def apply_blg_payload(self, blg_payload, blg_resources):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.apply_blg_payload",
            {
                'blg_payload': blg_payload,
                'blg_resources': blg_resources,
            }
        )

    # get_blg_resources
    #
    # Returns the BLG resources for this shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): String containing the resources.
    #
    def get_blg_resources(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_blg_resources",
            {}
        )

    # insert_basegrade_layer
    #
    # Insert a BaseGrade layer at the bottom of the stack.
    #
    # Arguments:
    #    'values' (dict): A dictionary containing new values for the given 
    #                     BaseGrade parameters.  Valid keys are 
    #                     BalanceExposure, BalanceA, BalanceB, 
    #                     Flare, 
    #                     Saturation, 
    #                     Contrast, 
    #                     LightExposure, LightA, LightB, 
    #                     DimExposure, DimA, DimB, 
    #                     BrightExposure, BrightA, BrightB, 
    #                     DarkExposure, DarkA, DarkB, 
    #                     ContrastPivot, 
    #                     LightPivot, LightFalloff, 
    #                     DimPivot, DimFalloff, 
    #                     BrightPivot, BrightFalloff, 
    #                     DarkPivot, DarkFalloff, 
    #                     LightSaturation, 
    #                     DimSaturation, 
    #                     BrightSaturation, 
    #                     DarkSaturation
    #
    # Returns:
    #    (none)
    #
    def insert_basegrade_layer(self, values):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_basegrade_layer",
            {
                'values': values,
            }
        )

    # insert_cdl_layer
    #
    # Insert a CDLGrade layer at the bottom of the shot.
    #
    # Arguments:
    #    'cdl_values' (list): CDL values (Slope R, Slope G, Slope B, Offset R, Offset G, Offset B, Power R, Power G, Power B, Saturation).
    #        '<n>' (float): 
    #
    # Returns:
    #    (none)
    #
    def insert_cdl_layer(self, cdl_values):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_cdl_layer",
            {
                'cdl_values': cdl_values,
            }
        )

    # insert_cdl_layer_above
    #
    # Insert a CDLGrade layer at the top of the shot.
    #
    # Arguments:
    #    'cdl_values' (list): CDL values (Slope R, Slope G, Slope B, Offset R, Offset G, Offset B, Power R, Power G, Power B, Saturation).
    #        '<n>' (float): 
    #
    # Returns:
    #    (none)
    #
    def insert_cdl_layer_above(self, cdl_values):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_cdl_layer_above",
            {
                'cdl_values': cdl_values,
            }
        )

    # insert_look_layer
    #
    # Insert a Look kayer at the bottom of the shot.
    #
    # Arguments:
    #    'look_name' (string): Name of the Look to be inserted.
    #
    # Returns:
    #    (none)
    #
    def insert_look_layer(self, look_name):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_look_layer",
            {
                'look_name': look_name,
            }
        )

    # insert_truelight_layer
    #
    # Insert a Truelight layer at the bottom of the shot. The Truelight operator is used for applying 1D and 3D LUTs to an image.
    #
    # Arguments:
    #    'lut_path' (string): Path to the LUT file to be set in the newly created Truelight operator.
    #
    # Returns:
    #    (none)
    #
    def insert_truelight_layer(self, lut_path):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_truelight_layer",
            {
                'lut_path': lut_path,
            }
        )

    # insert_shape_layer_from_svg
    #
    # Insert a layer with a shape strip populated from an SVG file at the bottom of the shot.
    #
    # Arguments:
    #    'svg_path' (string): Path to the SVG file used to populate the layer's shape strip.
    #    'fit_mode' (string): Controls how an SVG is transformed/fitted into the shape strip.
    #    'mask_format' (string): Fit to this format and mask (supplied in 'mask_name' parameter). If set, the SVG will be transformed/fitted to this format's mask area mapped to the working format area. If none supplied, the SVG will be transformed/fitted to the entire working format area. [Optional]
    #    'mask_name' (string): Mask name (from the 'mask_format'). This may be used to further constrain fitting of the SVG to the working format area (see above). [Optional]
    #
    # Returns:
    #    (none)
    #
    def insert_shape_layer_from_svg(self, svg_path, fit_mode, mask_format = '', mask_name = ''):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_shape_layer_from_svg",
            {
                'svg_path': svg_path,
                'fit_mode': fit_mode,
                'mask_format': mask_format,
                'mask_name': mask_name,
            }
        )

    # insert_colour_space_layer
    #
    # Insert a ColourSpace operator at the bottom of the stack for this shot
    #
    # Arguments:
    #    'toColourSpace' (string): Name of Output Colour Space
    #    'drt' (string): Name of DRT to use when converting between scene-referred and display-referred colour spaces.
    #                    Default is 'scene' which uses Scene's current Display Render Transform. [Optional]
    #    'identify' (int): Set to 1 to indicate the Colour Space operator is being used to tag/identify the colour space at this point in the stack, without any colour conversions.
    #                      This would be applicable when using the Colour Space operator after a Truelight operator. [Optional]
    #
    # Returns:
    #    (none)
    #
    def insert_colour_space_layer(self, toColourSpace, drt = 'scene', identify = 0):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_colour_space_layer",
            {
                'toColourSpace': toColourSpace,
                'drt': drt,
                'identify': identify,
            }
        )

    # insert_lut_layer
    #
    # Insert a LUT operator at the bottom of the stack for this shot
    #
    # Arguments:
    #    'location' (string): Specify where LUT data is stored.
    #    'file' (string): Path to LUT file. You can use %C/ to use a path relative to the Scene's container. [Optional]
    #    'inputColourSpace' (string): Name of Input Colour Space for this LUT.
    #    'outputColourSpace' (string): Name of Output Colour Space for this LUT
    #    'inputLegalRange' (int): Flag indicating that input to LUT is expected to be video-legal range. Defautls to 0 to indicate full-range. [Optional]
    #    'outputLegalRange' (int): Flag indicating that output of LUT is video-legal range. Defaults to 0 to indicate full-range. [Optional]
    #    'tetrahedral' (int): Flag indicating that high-quality tetrahedral interpolation should be used. [Optional]
    #
    # Returns:
    #    (none)
    #
    def insert_lut_layer(self, location, file, inputColourSpace, outputColourSpace, inputLegalRange = 0, outputLegalRange = 0, tetrahedral = 1):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.insert_lut_layer",
            {
                'location': location,
                'file': file,
                'inputColourSpace': inputColourSpace,
                'outputColourSpace': outputColourSpace,
                'inputLegalRange': inputLegalRange,
                'outputLegalRange': outputLegalRange,
                'tetrahedral': tetrahedral,
            }
        )

    # delete_all_layers
    #
    # Remove all layers from the shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (none)
    #
    def delete_all_layers(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.delete_all_layers",
            {}
        )

    # get_codec
    #
    # Method to obtain the codec of the input media of the shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): A short string containing the codec name, or NULL if the codec couldn't be determined.
    #
    def get_codec(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_codec",
            {}
        )

    # get_decode_parameter_types
    #
    # Return list of supported decode parameter codec keys
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (list): Array of supported decode parameter codec keys
    #        '<n>' (string): Decode Parameter codec key
    #
    def get_decode_parameter_types(self):
        if self.target != None:
            raise FLAPIException( "Static method get_decode_parameter_types called on instance of Shot" )
        return self.conn.call(
            None,
            "Shot.get_decode_parameter_types",
            {}
        )

    # get_decode_parameter_type_for_codec
    #
    # Return the key identifying the decode parameters type to use for the given video codec
    #
    # Arguments:
    #    'codec' (string): Name of codec
    #
    # Returns:
    #    (string): Decode Parameter type key
    #
    def get_decode_parameter_type_for_codec(self, codec):
        if self.target != None:
            raise FLAPIException( "Static method get_decode_parameter_type_for_codec called on instance of Shot" )
        return self.conn.call(
            None,
            "Shot.get_decode_parameter_type_for_codec",
            {
                'codec': codec,
            }
        )

    # get_decode_parameter_definitions
    #
    # Static method called to obtain the image decode parameter definitions for a given codec. The decode parameters are used to control how an RGBA image is generated from RAW formats like ARRIRAW, R3D etc.
    #  This method returns an array of image decode parameter definitions for a given decode parameter type, one per parameter. Each parameter definition is a collection of key/value pairs, with different entries dependent on the type of parameter.
    #
    # Arguments:
    #    'decode_type' (string): Type of decode parameter definitions to be obtained
    #
    # Returns:
    #    (list): An array containing parameter definitions as defined above.
    #        '<n>' (DecodeParameterDefinition): 
    #
    def get_decode_parameter_definitions(self, decode_type):
        if self.target != None:
            raise FLAPIException( "Static method get_decode_parameter_definitions called on instance of Shot" )
        return self.conn.call(
            None,
            "Shot.get_decode_parameter_definitions",
            {
                'decode_type': decode_type,
            }
        )

    # get_decode_parameters
    #
    # This method returns the image decode parameters for the shot.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Key/value pairs containing the current decode parameters. The meaning of the various keys can be discovered using the Shot.get_decode_parameter_definitions static method.
    #
    def get_decode_parameters(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_decode_parameters",
            {}
        )

    # set_decode_parameters
    #
    # Set some or all of the image decode parameters for the shot.
    #
    # Arguments:
    #    'decode_params' (dict): Key/value pairs containing new decode parameter values. The allowable keys and valid values for those keys can be discovered using the get_decode_parameter_definitions static method. It is not necessary to specify all the parameters - any parameters not set will remain untouched.
    #
    # Returns:
    #    (none)
    #
    def set_decode_parameters(self, decode_params):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_decode_parameters",
            {
                'decode_params': decode_params,
            }
        )

    # get_audio_settings
    #
    # Return the audio settings defined for this shot. Returns NULL if the shot has no audio defined.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (AudioSequenceSettings): Audio settings for shot
    #
    def get_audio_settings(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.get_audio_settings",
            {}
        )

    # set_audio_settings
    #
    # Set the audio settings for this shot. 
    #
    # Arguments:
    #    'audio_settings' (AudioSequenceSettings): New audio settings for shot
    #
    # Returns:
    #    (none)
    #
    def set_audio_settings(self, audio_settings):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.set_audio_settings",
            {
                'audio_settings': audio_settings,
            }
        )

    # bypass_all_layers
    #
    # Bypass/unbypass all layers in the shot.
    #
    # Arguments:
    #    'bypass' (int): Whether to bypass or unbypass the shot's layers.
    #    'ignore_top_layer' (int): Whether to ignore the top-most layer, flag indicating true or false.
    #    'ignore_bottom_layer' (int): Whether to ignore the bottom-most layer, flag indicating true or false.
    #
    # Returns:
    #    (none)
    #
    def bypass_all_layers(self, bypass, ignore_top_layer, ignore_bottom_layer):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "Shot.bypass_all_layers",
            {
                'bypass': bypass,
                'ignore_top_layer': ignore_top_layer,
                'ignore_bottom_layer': ignore_bottom_layer,
            }
        )

Library.register_class( 'Shot', Shot )

