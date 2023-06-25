from . import Library
import json

# RenderCodecParameterValue
#
# Definition of a valid value for a codec parameter
#

class RenderCodecParameterValue:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Text = obj.get("Text")
        else:
            self.Key = None
            self.Text = None

    @staticmethod
    def from_dict(o):
        return RenderCodecParameterValue(o)

    def json(self):
        return {
            "_type": "RenderCodecParameterValue",
            "Key": self.Key,
            "Text": self.Text,
        }

    def __repr__(self):
        return "flapi.RenderCodecParameterValue(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderCodecParameterValue", RenderCodecParameterValue.from_dict );

