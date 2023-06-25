from . import Library
import json

# DiagResult
#
# Result information for an individual diagnostic test across all hosts running this test
#

class DiagResult:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.Hosts = obj.get("Hosts")
        else:
            self.Name = None
            self.Hosts = None

    @staticmethod
    def from_dict(o):
        return DiagResult(o)

    def json(self):
        return {
            "_type": "DiagResult",
            "Name": self.Name,
            "Hosts": self.Hosts,
        }

    def __repr__(self):
        return "flapi.DiagResult(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DiagResult", DiagResult.from_dict );

