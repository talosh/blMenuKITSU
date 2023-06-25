from . import Library
import json

# ShotIndexRange
#
# shot index range
#

class ShotIndexRange:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.FirstIndex = obj.get("FirstIndex")
            self.LastIndex = obj.get("LastIndex")
        else:
            self.FirstIndex = None
            self.LastIndex = None

    @staticmethod
    def from_dict(o):
        return ShotIndexRange(o)

    def json(self):
        return {
            "_type": "ShotIndexRange",
            "FirstIndex": self.FirstIndex,
            "LastIndex": self.LastIndex,
        }

    def __repr__(self):
        return "flapi.ShotIndexRange(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ShotIndexRange", ShotIndexRange.from_dict );

