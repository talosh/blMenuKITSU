from . import Library
import json

# DiagProgress
#
# Overall process of diagnostic test operation
#

class DiagProgress:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Running = obj.get("Running")
            self.Total = obj.get("Total")
            self.NumComplete = obj.get("NumComplete")
            self.NumInProgress = obj.get("NumInProgress")
            self.NumWaiting = obj.get("NumWaiting")
            self.NumSkipped = obj.get("NumSkipped")
        else:
            self.Running = None
            self.Total = None
            self.NumComplete = None
            self.NumInProgress = None
            self.NumWaiting = None
            self.NumSkipped = None

    @staticmethod
    def from_dict(o):
        return DiagProgress(o)

    def json(self):
        return {
            "_type": "DiagProgress",
            "Running": self.Running,
            "Total": self.Total,
            "NumComplete": self.NumComplete,
            "NumInProgress": self.NumInProgress,
            "NumWaiting": self.NumWaiting,
            "NumSkipped": self.NumSkipped,
        }

    def __repr__(self):
        return "flapi.DiagProgress(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DiagProgress", DiagProgress.from_dict );

