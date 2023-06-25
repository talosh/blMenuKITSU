from . import Library
import json

# LookInfo
#
# Information for a Look
#

class LookInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.Group = obj.get("Group")
        else:
            self.Name = None
            self.Group = None

    @staticmethod
    def from_dict(o):
        return LookInfo(o)

    def json(self):
        return {
            "_type": "LookInfo",
            "Name": self.Name,
            "Group": self.Group,
        }

    def __repr__(self):
        return "flapi.LookInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "LookInfo", LookInfo.from_dict );

