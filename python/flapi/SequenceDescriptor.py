from . import Library, Interface, FLAPIException
import json

# SequenceDescriptor
#
# A SequenceDescriptor represents a movie file (e.g. `/vol/bl000-images/myjob/media/A001_C001_00000A_001.R3D`) or a sequence of image files (e.g. `/vol/bl000-images/myjob/renders/day1_%.7F.exr`) on disk.
# It has a frame range (which does not have to cover the full length of the media on disk) and associated metadata.
# Audio-only media (e.g. OpAtom MXF audio, or .wav files) is also described using a SequenceDescriptor.
#

class SequenceDescriptor(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # get_for_template
    #
    # Search the filesystem and return zero or more SequenceDescriptors which match the given filename template (e.g. "/vol/images/A001B002.mov" or "/vol/san/folder/%.6F.dpx", and optionally intersecting the given start and end frame numbers.
    #
    # Arguments:
    #    'template' (string): Path to the file, using FilmLight %.#F syntax for frame numbering
    #    'start' (int): Start frame number [Optional]
    #    'end' (int): End frame number (inclusive) [Optional]
    #
    # Returns:
    #    (list): Array of SequenceDescriptor objects
    #        '<n>' (SequenceDescriptor): 
    #
    def get_for_template(self, template, start = None, end = None):
        if self.target != None:
            raise FLAPIException( "Static method get_for_template called on instance of SequenceDescriptor" )
        return self.conn.call(
            None,
            "SequenceDescriptor.get_for_template",
            {
                'template': template,
                'start': start,
                'end': end,
            }
        )

    # get_for_template_with_timecode
    #
    # Search the filesystem and return zero or more SequenceDescriptors which match the given filename template (e.g. "/vol/images/A001B002.mov" or "/vol/san/folder/%.6F.dpx", and optionally intersecting the given start and end timecodes.
    #
    # Arguments:
    #    'template' (string): Path to the file, using FilmLight %.#F syntax for frame numbering
    #    'startTC' (timecode): Start timecode [Optional]
    #    'endTC' (timecode): End timecode (inclusive) [Optional]
    #
    # Returns:
    #    (list): Array of SequenceDescriptor objects
    #        '<n>' (SequenceDescriptor): 
    #
    def get_for_template_with_timecode(self, template, startTC = None, endTC = None):
        if self.target != None:
            raise FLAPIException( "Static method get_for_template_with_timecode called on instance of SequenceDescriptor" )
        return self.conn.call(
            None,
            "SequenceDescriptor.get_for_template_with_timecode",
            {
                'template': template,
                'startTC': startTC,
                'endTC': endTC,
            }
        )

    # get_for_file
    #
    # Create a SequenceDescriptor for a single file
    #
    # Arguments:
    #    'filepath' (string): Path to file
    #
    # Returns:
    #    (SequenceDescriptor): SequenceDescriptor for given path
    #
    def get_for_file(self, filepath):
        if self.target != None:
            raise FLAPIException( "Static method get_for_file called on instance of SequenceDescriptor" )
        return self.conn.call(
            None,
            "SequenceDescriptor.get_for_file",
            {
                'filepath': filepath,
            }
        )

    # get_start_frame
    #
    # Return the first frame number, which does not necessarily correspond with the first frame of the files on disk.
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
            "SequenceDescriptor.get_start_frame",
            {}
        )

    # get_end_frame
    #
    # Return the last frame number, which does not necessarily correspond with the last frame of the files on disk.
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
            "SequenceDescriptor.get_end_frame",
            {}
        )

    # get_start_timecode
    #
    # Return the timecode at the first frame of the sequence. Some media can support two timecode tracks, so you must specify which one you want (0 or 1).
    #
    # Arguments:
    #    'index' (int): Index of timecode track
    #
    # Returns:
    #    (timecode): Start timecode
    #
    def get_start_timecode(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_start_timecode",
            {
                'index': index,
            }
        )

    # get_end_timecode
    #
    # Return the timecode at the last frame of the sequence. Some media can support two timecode tracks, so you must specify which one you want (0 or 1).
    #
    # Arguments:
    #    'index' (int): Index of timecode track
    #
    # Returns:
    #    (timecode): End timecode
    #
    def get_end_timecode(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_end_timecode",
            {
                'index': index,
            }
        )

    # get_start_keycode
    #
    # Return the keycode at the first frame of the sequence.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (keycode): Start keycode
    #
    def get_start_keycode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_start_keycode",
            {}
        )

    # get_end_keycode
    #
    # Return the keycode at the last frame of the sequence.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (keycode): End keycode
    #
    def get_end_keycode(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_end_keycode",
            {}
        )

    # get_start_handle
    #
    # Return the first frame number on disk (0 for movie files).
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_start_handle(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_start_handle",
            {}
        )

    # get_end_handle
    #
    # Return the last frame number on disk (inclusive).
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Frame number
    #
    def get_end_handle(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_end_handle",
            {}
        )

    # get_width
    #
    # Return the width (in pixels) of the images in this sequence. Returns 0 for audio-only media.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Width
    #
    def get_width(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_width",
            {}
        )

    # get_height
    #
    # Return the height (in pixels) of the images in this sequence. Returns 0 for audio-only media.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Height
    #
    def get_height(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_height",
            {}
        )

    # get_pixel_aspect_ratio
    #
    # Return the pixel aspect ratio (width/height) of the images in this sequence. Returns 1.0 if unknown.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (float): Aspect ratio
    #
    def get_pixel_aspect_ratio(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_pixel_aspect_ratio",
            {}
        )

    # get_path
    #
    # Return the path to the folder containing this sequence.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Folder path
    #
    def get_path(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_path",
            {}
        )

    # get_name
    #
    # Return the filename (for a movie) or the filename template (for an image sequence, using FilmLight %.#F syntax for frame numbering), excluding the folder path.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Name of sequence
    #
    def get_name(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_name",
            {}
        )

    # get_ext
    #
    # Return the filename extension (including the leading '.') for this sequence.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Extension
    #
    def get_ext(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_ext",
            {}
        )

    # get_prefix
    #
    # Return filename prefix before numeric component
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Prefix
    #
    def get_prefix(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_prefix",
            {}
        )

    # get_postfix
    #
    # Return filename postfix after numeric component
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Postfix
    #
    def get_postfix(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_postfix",
            {}
        )

    # get_format_len
    #
    # Return number of digits in numerical component of filename
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of digits
    #
    def get_format_len(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_format_len",
            {}
        )

    # get_base_filename_with_F
    #
    # Return filename (without path) using FilmLight %.#F syntax for the frame number pattern
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Filename template
    #
    def get_base_filename_with_F(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_base_filename_with_F",
            {}
        )

    # get_base_filename_with_d
    #
    # Return filename (without path) using printf %0#d syntax for the frame number pattern
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Filename template
    #
    def get_base_filename_with_d(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_base_filename_with_d",
            {}
        )

    # get_full_filename_with_F
    #
    # Return filename (with path) using FilmLight %.#F syntax for the frame number pattern
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Filename
    #
    def get_full_filename_with_F(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_full_filename_with_F",
            {}
        )

    # get_full_filename_with_d
    #
    # Return filename (with path) using printf %0#d syntax for the frame number pattern
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (string): Filename
    #
    def get_full_filename_with_d(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_full_filename_with_d",
            {}
        )

    # get_base_filename
    #
    # Return filename (without path) for the given frame number
    #
    # Arguments:
    #    'frame' (int): Frame number
    #
    # Returns:
    #    (string): Filename
    #
    def get_base_filename(self, frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_base_filename",
            {
                'frame': frame,
            }
        )

    # get_filename_for_frame
    #
    # Return filename (with path) for the given frame number
    #
    # Arguments:
    #    'frame' (int): Frame number
    #
    # Returns:
    #    (string): Filename
    #
    def get_filename_for_frame(self, frame):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_filename_for_frame",
            {
                'frame': frame,
            }
        )

    # get_tape
    #
    # Return the tape name. Some media can support two tracks, so you must specify which one you want (0 or 1).
    #
    # Arguments:
    #    'index' (int): Index of timecode track
    #
    # Returns:
    #    (string): Tape name
    #
    def get_tape(self, index):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_tape",
            {
                'index': index,
            }
        )

    # get_metadata
    #
    # Return the metadata read when the sequence was scanned on disk, in human-readable form.
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (dict): Metadata
    #
    def get_metadata(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_metadata",
            {}
        )

    # is_movie
    #
    # Return whether sequence is a movie file
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag
    #
    def is_movie(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.is_movie",
            {}
        )

    # has_blg
    #
    # Return whether sequence has BLG (Baselight Linked Grade) information
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag
    #
    def has_blg(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.has_blg",
            {}
        )

    # is_blg
    #
    # Return whether sequence is a BLG (Baselight Linked Grade)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag
    #
    def is_blg(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.is_blg",
            {}
        )

    # has_audio
    #
    # Return whether movie file has audio
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Flag
    #
    def has_audio(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.has_audio",
            {}
        )

    # get_audio_channels
    #
    # Return number of audio channels in movie
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Number of channels
    #
    def get_audio_channels(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_audio_channels",
            {}
        )

    # get_audio_sample_rate
    #
    # Return audio sample rate (in Hz)
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Sample rate
    #
    def get_audio_sample_rate(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_audio_sample_rate",
            {}
        )

    # get_audio_length_in_samples
    #
    # Return total number of audio samples in file
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Length
    #
    def get_audio_length_in_samples(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.get_audio_length_in_samples",
            {}
        )

    # trim_movie
    #
    # Create (if possible) a trimmed copy of the movie specified by this descriptor
    #
    # Arguments:
    #    'output' (string): Output movie file name
    #    'start' (int): Start frame of output movie
    #    'length' (int): Number of frames to write to output movie
    #
    # Returns:
    #    None
    #
    def trim_movie(self, output, start, length):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "SequenceDescriptor.trim_movie",
            {
                'output': output,
                'start': start,
                'length': length,
            }
        )

Library.register_class( 'SequenceDescriptor', SequenceDescriptor )

