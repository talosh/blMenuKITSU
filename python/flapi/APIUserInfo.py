from . import Library
import json

# APIUserInfo
#
# Settings for an API user
#

class APIUserInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Login = obj.get("Login")
            self.Name = obj.get("Name")
            self.Permissions = obj.get("Permissions")
            self.Enabled = obj.get("Enabled")
        else:
            self.Login = None
            self.Name = None
            self.Permissions = None
            self.Enabled = None

    @staticmethod
    def from_dict(o):
        return APIUserInfo(o)

    def json(self):
        return {
            "_type": "APIUserInfo",
            "Login": self.Login,
            "Name": self.Name,
            "Permissions": self.Permissions,
            "Enabled": self.Enabled,
        }

    def __repr__(self):
        return "flapi.APIUserInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "APIUserInfo", APIUserInfo.from_dict );

