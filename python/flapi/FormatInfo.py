from . import Library
import json

# FormatInfo
#
# Specifies the width, height, pixel aspect ratio
#

class FormatInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Width = obj.get("Width")
            self.Height = obj.get("Height")
            self.PixelAspectRatio = obj.get("PixelAspectRatio")
        else:
            self.Width = None
            self.Height = None
            self.PixelAspectRatio = None

    @staticmethod
    def from_dict(o):
        return FormatInfo(o)

    def json(self):
        return {
            "_type": "FormatInfo",
            "Width": self.Width,
            "Height": self.Height,
            "PixelAspectRatio": self.PixelAspectRatio,
        }

    def __repr__(self):
        return "flapi.FormatInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FormatInfo", FormatInfo.from_dict );

