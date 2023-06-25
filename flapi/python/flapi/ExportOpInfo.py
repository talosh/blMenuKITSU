from . import Library
import json

# ExportOpInfo
#
# This type is returned to return information about export operations queued via QueueManager
#

class ExportOpInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ID = obj.get("ID")
            self.Log = obj.get("Log")
        else:
            self.ID = None
            self.Log = None

    @staticmethod
    def from_dict(o):
        return ExportOpInfo(o)

    def json(self):
        return {
            "_type": "ExportOpInfo",
            "ID": self.ID,
            "Log": self.Log,
        }

    def __repr__(self):
        return "flapi.ExportOpInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ExportOpInfo", ExportOpInfo.from_dict );

