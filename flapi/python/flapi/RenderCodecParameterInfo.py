from . import Library
import json

# RenderCodecParameterInfo
#
# Definition of a parameter to an image or movie codec
#

class RenderCodecParameterInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Text = obj.get("Text")
            self.Type = obj.get("Type")
            self.Choices = obj.get("Choices")
        else:
            self.Key = None
            self.Text = None
            self.Type = None
            self.Choices = None

    @staticmethod
    def from_dict(o):
        return RenderCodecParameterInfo(o)

    def json(self):
        return {
            "_type": "RenderCodecParameterInfo",
            "Key": self.Key,
            "Text": self.Text,
            "Type": self.Type,
            "Choices": self.Choices,
        }

    def __repr__(self):
        return "flapi.RenderCodecParameterInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderCodecParameterInfo", RenderCodecParameterInfo.from_dict );

