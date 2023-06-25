from . import Library
import json

# RenderCodecInfo
#
# Definition of a Codec that is supported for an image or movie file type
#

class RenderCodecInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Text = obj.get("Text")
            self.Params = obj.get("Params")
        else:
            self.Key = None
            self.Text = None
            self.Params = None

    @staticmethod
    def from_dict(o):
        return RenderCodecInfo(o)

    def json(self):
        return {
            "_type": "RenderCodecInfo",
            "Key": self.Key,
            "Text": self.Text,
            "Params": self.Params,
        }

    def __repr__(self):
        return "flapi.RenderCodecInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderCodecInfo", RenderCodecInfo.from_dict );

