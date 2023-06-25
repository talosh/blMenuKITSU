from . import Library
import json

# ConnectionInfo
#
# Dictionary describing a single connection.
#

class ConnectionInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ConnectionID = obj.get("ConnectionID")
            self.UserName = obj.get("UserName")
            self.UsageType = obj.get("UsageType")
        else:
            self.ConnectionID = None
            self.UserName = None
            self.UsageType = None

    @staticmethod
    def from_dict(o):
        return ConnectionInfo(o)

    def json(self):
        return {
            "_type": "ConnectionInfo",
            "ConnectionID": self.ConnectionID,
            "UserName": self.UserName,
            "UsageType": self.UsageType,
        }

    def __repr__(self):
        return "flapi.ConnectionInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ConnectionInfo", ConnectionInfo.from_dict );

