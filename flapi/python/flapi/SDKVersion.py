from . import Library
import json

# SDKVersion
#
# Version information for 3rd-party SDKs used in the application
#

class SDKVersion:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
            self.Description = obj.get("Description")
            self.Version = obj.get("Version")
        else:
            self.Key = None
            self.Name = None
            self.Description = None
            self.Version = None

    @staticmethod
    def from_dict(o):
        return SDKVersion(o)

    def json(self):
        return {
            "_type": "SDKVersion",
            "Key": self.Key,
            "Name": self.Name,
            "Description": self.Description,
            "Version": self.Version,
        }

    def __repr__(self):
        return "flapi.SDKVersion(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "SDKVersion", SDKVersion.from_dict );

