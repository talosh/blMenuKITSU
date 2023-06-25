from . import Library, Interface, FLAPIException
import json

# ImageSearcher
#
# Search for image sequences on disk
#

class ImageSearcher(Interface):

    # Constructor
    def __init__(self, conn, target):
        Interface.__init__(self, conn, target)

    # create
    #
    # Create a new Image Searcher object
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (ImageSearcher): New ImageSearcher object
    #
    def create(self):
        if self.target != None:
            raise FLAPIException( "Static method create called on instance of ImageSearcher" )
        return self.conn.call(
            None,
            "ImageSearcher.create",
            {}
        )

    # add_root_directory
    #
    # Add a root directory to search to the image searcher
    #
    # Arguments:
    #    'dir' (string): Path to directory
    #    'recurse' (int): Flag indicating whether to recursively search this directory
    #
    # Returns:
    #    (int): Returns 1 if directory as successfully added, or 0 if directory cannot be added.
    #
    def add_root_directory(self, dir, recurse):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.add_root_directory",
            {
                'dir': dir,
                'recurse': recurse,
            }
        )

    # scan
    #
    # Begin search for image sequences and movies.
    # The scan will run asynchronously.
    # You can check for scan completion by calling is_scan_in_progress().
    # Alternatively you can cancel the scan by calling cancel().
    # You can poll the ImageSearcher object for progress by calling get_num_images() or get_num_sequences().
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Returns 1 if scan is started successfully, or 0 if scan cannot be started.
    #
    def scan(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.scan",
            {}
        )

    # is_scan_in_progress
    #
    # Check whether scan is in progress
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Returns 1 if scan is in progress, 0 if scan is not in progress
    #
    def is_scan_in_progress(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.is_scan_in_progress",
            {}
        )

    # cancel
    #
    # Cancel scan in progress
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
            "ImageSearcher.cancel",
            {}
        )

    # is_cancelled
    #
    # Check if scan was cancelled
    #
    # Arguments:
    #    None
    #
    # Returns:
    #    (int): Returns 1 if scan was cancelled, 0 if scan was not cancelled.
    #
    def is_cancelled(self):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.is_cancelled",
            {}
        )

    # get_num_images
    #
    # Return number of image files found
    #
    # Arguments:
    #    'rootDir' (string): Directory to get statistics for
    #
    # Returns:
    #    (int): Number of image files found
    #
    def get_num_images(self, rootDir):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.get_num_images",
            {
                'rootDir': rootDir,
            }
        )

    # get_num_movies
    #
    # Return number of movie files found
    #
    # Arguments:
    #    'rootDir' (string): Directory to get statistics for
    #
    # Returns:
    #    (int): Number of image files found
    #
    def get_num_movies(self, rootDir):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.get_num_movies",
            {
                'rootDir': rootDir,
            }
        )

    # get_sequences
    #
    # Get array of sequences found by the ImageSearcher
    #
    # Arguments:
    #    'track' (string): Choose which metadata 'track' to use to separate sequences.
    #                      A range of files may be grouped into sequences based frame number, timecode (track 1 or 2), or keycode.
    #                      For example, a single sequence with contiguous frame numbers could result in multiple distinct
    #                      sub-sequences when separated by timecode or keycode.
    #    'limit' (int): Limit the number of sequences returned by this call
    #
    # Returns:
    #    (list): Array of SequenceDescriptor objects
    #        '<n>' (SequenceDescriptor): 
    #
    def get_sequences(self, track, limit):
        if self.target == None:
            raise FLAPIException( "Instance method called on object with no instance" )
        return self.conn.call(
            self.target,
            "ImageSearcher.get_sequences",
            {
                'track': track,
                'limit': limit,
            }
        )

Library.register_class( 'ImageSearcher', ImageSearcher )

