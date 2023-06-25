from . import Library
import json

# ClientViewClientSettings
#
# Settings for a connected Client View
#

class ClientViewClientSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.StreamIndex = obj.get("StreamIndex")
            self.StreamConfigsAge = obj.get("StreamConfigsAge")
            self.NotesEnabled = obj.get("NotesEnabled")
            self.LaserEnabled = obj.get("LaserEnabled")
            self.Debug = obj.get("Debug")
        else:
            self.StreamIndex = None
            self.StreamConfigsAge = None
            self.NotesEnabled = None
            self.LaserEnabled = None
            self.Debug = None

    @staticmethod
    def from_dict(o):
        return ClientViewClientSettings(o)

    def json(self):
        return {
            "_type": "ClientViewClientSettings",
            "StreamIndex": self.StreamIndex,
            "StreamConfigsAge": self.StreamConfigsAge,
            "NotesEnabled": self.NotesEnabled,
            "LaserEnabled": self.LaserEnabled,
            "Debug": self.Debug,
        }

    def __repr__(self):
        return "flapi.ClientViewClientSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ClientViewClientSettings", ClientViewClientSettings.from_dict );

