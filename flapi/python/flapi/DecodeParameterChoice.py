from . import Library
import json

# DecodeParameterChoice
#
#

class DecodeParameterChoice:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Value = obj.get("Value")
            self.Label = obj.get("Label")
        else:
            self.Value = None
            self.Label = None

    @staticmethod
    def from_dict(o):
        return DecodeParameterChoice(o)

    def json(self):
        return {
            "_type": "DecodeParameterChoice",
            "Value": self.Value,
            "Label": self.Label,
        }

    def __repr__(self):
        return "flapi.DecodeParameterChoice(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DecodeParameterChoice", DecodeParameterChoice.from_dict );

