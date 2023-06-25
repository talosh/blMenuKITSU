from . import Library
import json

# QueueOpStatus
#
# Status of an Operation in a Queue
#

class QueueOpStatus:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ID = obj.get("ID")
            self.Status = obj.get("Status")
            self.Progress = obj.get("Progress")
            self.ProgressText = obj.get("ProgressText")
            self.TimeElapsed = obj.get("TimeElapsed")
            self.TimeRemaining = obj.get("TimeRemaining")
            self.Warnings = obj.get("Warnings")
            self.Errors = obj.get("Errors")
        else:
            self.ID = None
            self.Status = None
            self.Progress = None
            self.ProgressText = None
            self.TimeElapsed = None
            self.TimeRemaining = None
            self.Warnings = None
            self.Errors = None

    @staticmethod
    def from_dict(o):
        return QueueOpStatus(o)

    def json(self):
        return {
            "_type": "QueueOpStatus",
            "ID": self.ID,
            "Status": self.Status,
            "Progress": self.Progress,
            "ProgressText": self.ProgressText,
            "TimeElapsed": self.TimeElapsed,
            "TimeRemaining": self.TimeRemaining,
            "Warnings": self.Warnings,
            "Errors": self.Errors,
        }

    def __repr__(self):
        return "flapi.QueueOpStatus(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "QueueOpStatus", QueueOpStatus.from_dict );

