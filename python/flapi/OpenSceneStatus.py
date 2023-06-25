from . import Library
import json

# OpenSceneStatus
#
# Status of scene opening or creation operation
#

class OpenSceneStatus:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Done = obj.get("Done")
            self.Error = obj.get("Error")
            self.Progress = obj.get("Progress")
            self.Message = obj.get("Message")
        else:
            self.Done = None
            self.Error = None
            self.Progress = None
            self.Message = None

    @staticmethod
    def from_dict(o):
        return OpenSceneStatus(o)

    def json(self):
        return {
            "_type": "OpenSceneStatus",
            "Done": self.Done,
            "Error": self.Error,
            "Progress": self.Progress,
            "Message": self.Message,
        }

    def __repr__(self):
        return "flapi.OpenSceneStatus(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "OpenSceneStatus", OpenSceneStatus.from_dict );

