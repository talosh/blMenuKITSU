from . import Library
import json

# ClientViewHostUserSettings
#
# Settings for user hosting the Client View
#

class ClientViewHostUserSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.UserName = obj.get("UserName")
            self.LaserColour = obj.get("LaserColour")
        else:
            self.UserName = None
            self.LaserColour = None

    @staticmethod
    def from_dict(o):
        return ClientViewHostUserSettings(o)

    def json(self):
        return {
            "_type": "ClientViewHostUserSettings",
            "UserName": self.UserName,
            "LaserColour": self.LaserColour,
        }

    def __repr__(self):
        return "flapi.ClientViewHostUserSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ClientViewHostUserSettings", ClientViewHostUserSettings.from_dict );

