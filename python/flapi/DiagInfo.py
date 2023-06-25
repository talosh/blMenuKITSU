from . import Library
import json

# DiagInfo
#
# Information about a particular diagnostic test
#

class DiagInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
            self.Group = obj.get("Group")
            self.Hosts = obj.get("Hosts")
            self.Weight = obj.get("Weight")
        else:
            self.Key = None
            self.Name = None
            self.Group = None
            self.Hosts = None
            self.Weight = None

    @staticmethod
    def from_dict(o):
        return DiagInfo(o)

    def json(self):
        return {
            "_type": "DiagInfo",
            "Key": self.Key,
            "Name": self.Name,
            "Group": self.Group,
            "Hosts": self.Hosts,
            "Weight": self.Weight,
        }

    def __repr__(self):
        return "flapi.DiagInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DiagInfo", DiagInfo.from_dict );

