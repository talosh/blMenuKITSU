from . import Library
import json

# RenderOpInfo
#
# This type is returned to return information about render operations queued via QueueManager
#

class RenderOpInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ID = obj.get("ID")
            self.Warning = obj.get("Warning")
        else:
            self.ID = None
            self.Warning = None

    @staticmethod
    def from_dict(o):
        return RenderOpInfo(o)

    def json(self):
        return {
            "_type": "RenderOpInfo",
            "ID": self.ID,
            "Warning": self.Warning,
        }

    def __repr__(self):
        return "flapi.RenderOpInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderOpInfo", RenderOpInfo.from_dict );

