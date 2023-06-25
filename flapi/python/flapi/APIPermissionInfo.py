from . import Library
import json

# APIPermissionInfo
#
# Definition of an API permission
#

class APIPermissionInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Label = obj.get("Label")
            self.Desc = obj.get("Desc")
        else:
            self.Key = None
            self.Label = None
            self.Desc = None

    @staticmethod
    def from_dict(o):
        return APIPermissionInfo(o)

    def json(self):
        return {
            "_type": "APIPermissionInfo",
            "Key": self.Key,
            "Label": self.Label,
            "Desc": self.Desc,
        }

    def __repr__(self):
        return "flapi.APIPermissionInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "APIPermissionInfo", APIPermissionInfo.from_dict );

