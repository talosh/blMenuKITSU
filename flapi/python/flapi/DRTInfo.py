from . import Library
import json

# DRTInfo
#
# Description of a Truelight Display Rendering Transform
#

class DRTInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.InputSpace = obj.get("InputSpace")
            self.OutputSpace = obj.get("OutputSpace")
            self.ViewingConditions = obj.get("ViewingConditions")
        else:
            self.Name = None
            self.InputSpace = None
            self.OutputSpace = None
            self.ViewingConditions = None

    @staticmethod
    def from_dict(o):
        return DRTInfo(o)

    def json(self):
        return {
            "_type": "DRTInfo",
            "Name": self.Name,
            "InputSpace": self.InputSpace,
            "OutputSpace": self.OutputSpace,
            "ViewingConditions": self.ViewingConditions,
        }

    def __repr__(self):
        return "flapi.DRTInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DRTInfo", DRTInfo.from_dict );

