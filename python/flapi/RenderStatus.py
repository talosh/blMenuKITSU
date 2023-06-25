from . import Library
import json

# RenderStatus
#
# Status of render operation
#

class RenderStatus:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Status = obj.get("Status")
            self.Error = obj.get("Error")
            self.Total = obj.get("Total")
            self.Complete = obj.get("Complete")
            self.Remaining = obj.get("Remaining")
            self.Failed = obj.get("Failed")
            self.Progress = obj.get("Progress")
            self.ProgressMessage = obj.get("ProgressMessage")
        else:
            self.Status = None
            self.Error = None
            self.Total = None
            self.Complete = None
            self.Remaining = None
            self.Failed = None
            self.Progress = None
            self.ProgressMessage = None

    @staticmethod
    def from_dict(o):
        return RenderStatus(o)

    def json(self):
        return {
            "_type": "RenderStatus",
            "Status": self.Status,
            "Error": self.Error,
            "Total": self.Total,
            "Complete": self.Complete,
            "Remaining": self.Remaining,
            "Failed": self.Failed,
            "Progress": self.Progress,
            "ProgressMessage": self.ProgressMessage,
        }

    def __repr__(self):
        return "flapi.RenderStatus(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderStatus", RenderStatus.from_dict );

