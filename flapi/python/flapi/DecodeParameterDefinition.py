from . import Library
import json

# DecodeParameterDefinition
#
# This type is returned by get_decode_parameter_definitions to define the data type, label, ranges and values for each decode parameter that can be get or set for a Shot.
#

class DecodeParameterDefinition:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Parameter = obj.get("Parameter")
            self.Type = obj.get("Type")
            self.Default = obj.get("Default")
            self.Label = obj.get("Label")
            self.Min = obj.get("Min")
            self.Max = obj.get("Max")
            self.Choices = obj.get("Choices")
        else:
            self.Parameter = None
            self.Type = None
            self.Default = None
            self.Label = None
            self.Min = None
            self.Max = None
            self.Choices = None

    @staticmethod
    def from_dict(o):
        return DecodeParameterDefinition(o)

    def json(self):
        return {
            "_type": "DecodeParameterDefinition",
            "Parameter": self.Parameter,
            "Type": self.Type,
            "Default": self.Default,
            "Label": self.Label,
            "Min": self.Min,
            "Max": self.Max,
            "Choices": self.Choices,
        }

    def __repr__(self):
        return "flapi.DecodeParameterDefinition(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DecodeParameterDefinition", DecodeParameterDefinition.from_dict );

