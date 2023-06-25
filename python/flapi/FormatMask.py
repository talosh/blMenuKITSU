from . import Library
import json

# FormatMask
#
# Specifies the area of Mark defined with a Format
#

class FormatMask:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.XMin = obj.get("XMin")
            self.XMax = obj.get("XMax")
            self.YMin = obj.get("YMin")
            self.YMax = obj.get("YMax")
        else:
            self.Name = None
            self.XMin = None
            self.XMax = None
            self.YMin = None
            self.YMax = None

    @staticmethod
    def from_dict(o):
        return FormatMask(o)

    def json(self):
        return {
            "_type": "FormatMask",
            "Name": self.Name,
            "XMin": self.XMin,
            "XMax": self.XMax,
            "YMin": self.YMin,
            "YMax": self.YMax,
        }

    def __repr__(self):
        return "flapi.FormatMask(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FormatMask", FormatMask.from_dict );

