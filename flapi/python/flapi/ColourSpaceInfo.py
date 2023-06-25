from . import Library
import json

# ColourSpaceInfo
#
# Description of a Truelight Colour Space
#

class ColourSpaceInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.DisplayName = obj.get("DisplayName")
            self.Type = obj.get("Type")
        else:
            self.Name = None
            self.DisplayName = None
            self.Type = None

    @staticmethod
    def from_dict(o):
        return ColourSpaceInfo(o)

    def json(self):
        return {
            "_type": "ColourSpaceInfo",
            "Name": self.Name,
            "DisplayName": self.DisplayName,
            "Type": self.Type,
        }

    def __repr__(self):
        return "flapi.ColourSpaceInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ColourSpaceInfo", ColourSpaceInfo.from_dict );

