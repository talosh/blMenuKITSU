from . import Library
import json

# VolumeInfo
#
# Definition of a volume attached to, or accessible from, a FilmLight system
#

class VolumeInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
            self.Label = obj.get("Label")
            self.Zone = obj.get("Zone")
            self.Path = obj.get("Path")
        else:
            self.Key = None
            self.Name = None
            self.Label = None
            self.Zone = None
            self.Path = None

    @staticmethod
    def from_dict(o):
        return VolumeInfo(o)

    def json(self):
        return {
            "_type": "VolumeInfo",
            "Key": self.Key,
            "Name": self.Name,
            "Label": self.Label,
            "Zone": self.Zone,
            "Path": self.Path,
        }

    def __repr__(self):
        return "flapi.VolumeInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "VolumeInfo", VolumeInfo.from_dict );

