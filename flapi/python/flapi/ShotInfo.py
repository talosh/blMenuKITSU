from . import Library
import json

# ShotInfo
#
# Shot info object
#

class ShotInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ShotId = obj.get("ShotId")
            self.StartFrame = obj.get("StartFrame")
            self.EndFrame = obj.get("EndFrame")
            self.PosterFrame = obj.get("PosterFrame")
        else:
            self.ShotId = None
            self.StartFrame = None
            self.EndFrame = None
            self.PosterFrame = None

    @staticmethod
    def from_dict(o):
        return ShotInfo(o)

    def json(self):
        return {
            "_type": "ShotInfo",
            "ShotId": self.ShotId,
            "StartFrame": self.StartFrame,
            "EndFrame": self.EndFrame,
            "PosterFrame": self.PosterFrame,
        }

    def __repr__(self):
        return "flapi.ShotInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ShotInfo", ShotInfo.from_dict );

