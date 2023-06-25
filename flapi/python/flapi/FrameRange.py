from . import Library
import json

# FrameRange
#
# Defines a range of frames
#

class FrameRange:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Start = obj.get("Start")
            self.End = obj.get("End")
        else:
            self.Start = None
            self.End = None

    @staticmethod
    def from_dict(o):
        return FrameRange(o)

    def json(self):
        return {
            "_type": "FrameRange",
            "Start": self.Start,
            "End": self.End,
        }

    def __repr__(self):
        return "flapi.FrameRange(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FrameRange", FrameRange.from_dict );

