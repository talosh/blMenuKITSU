from . import Library
import json

# RenderFileTypeInfo
#
# Definition of an image or movie type
#

class RenderFileTypeInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Text = obj.get("Text")
            self.Extensions = obj.get("Extensions")
            self.Params = obj.get("Params")
        else:
            self.Key = None
            self.Text = None
            self.Extensions = None
            self.Params = None

    @staticmethod
    def from_dict(o):
        return RenderFileTypeInfo(o)

    def json(self):
        return {
            "_type": "RenderFileTypeInfo",
            "Key": self.Key,
            "Text": self.Text,
            "Extensions": self.Extensions,
            "Params": self.Params,
        }

    def __repr__(self):
        return "flapi.RenderFileTypeInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderFileTypeInfo", RenderFileTypeInfo.from_dict );

