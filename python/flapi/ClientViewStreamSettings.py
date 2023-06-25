from . import Library
import json

# ClientViewStreamSettings
#
# Settings for a Client View stream
#

class ClientViewStreamSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Resolution = obj.get("Resolution")
            self.Bitrate = obj.get("Bitrate")
            self.ColourSpace = obj.get("ColourSpace")
        else:
            self.Resolution = None
            self.Bitrate = None
            self.ColourSpace = None

    @staticmethod
    def from_dict(o):
        return ClientViewStreamSettings(o)

    def json(self):
        return {
            "_type": "ClientViewStreamSettings",
            "Resolution": self.Resolution,
            "Bitrate": self.Bitrate,
            "ColourSpace": self.ColourSpace,
        }

    def __repr__(self):
        return "flapi.ClientViewStreamSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ClientViewStreamSettings", ClientViewStreamSettings.from_dict );

