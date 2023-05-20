from . import Library
import json

# EnumInfo
#
# Information about a defined enumerated value
#

class EnumInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Value = obj.get("Value")
            self.Desc = obj.get("Desc")
        else:
            self.Value = None
            self.Desc = None

    @staticmethod
    def from_dict(o):
        return EnumInfo(o)

    def json(self):
        return {
            "_type": "EnumInfo",
            "Value": self.Value,
            "Desc": self.Desc,
        }

    def __repr__(self):
        return "flapi.EnumInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "EnumInfo", EnumInfo.from_dict );

