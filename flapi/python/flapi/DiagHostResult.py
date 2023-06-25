from . import Library
import json

# DiagHostResult
#
# Result information for diagnostic tests run on a specific host
#

class DiagHostResult:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Host = obj.get("Host")
            self.Messages = obj.get("Messages")
            self.Status = obj.get("Status")
        else:
            self.Host = None
            self.Messages = None
            self.Status = None

    @staticmethod
    def from_dict(o):
        return DiagHostResult(o)

    def json(self):
        return {
            "_type": "DiagHostResult",
            "Host": self.Host,
            "Messages": self.Messages,
            "Status": self.Status,
        }

    def __repr__(self):
        return "flapi.DiagHostResult(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DiagHostResult", DiagHostResult.from_dict );

