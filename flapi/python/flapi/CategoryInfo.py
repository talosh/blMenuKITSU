from . import Library
import json

# CategoryInfo
#
# Definition of a Category used to annotate marks, shots or strips
#

class CategoryInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
            self.ReadOnly = obj.get("ReadOnly")
            self.Colour = obj.get("Colour")
        else:
            self.Key = None
            self.Name = None
            self.ReadOnly = None
            self.Colour = None

    @staticmethod
    def from_dict(o):
        return CategoryInfo(o)

    def json(self):
        return {
            "_type": "CategoryInfo",
            "Key": self.Key,
            "Name": self.Name,
            "ReadOnly": self.ReadOnly,
            "Colour": self.Colour,
        }

    def __repr__(self):
        return "flapi.CategoryInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "CategoryInfo", CategoryInfo.from_dict );

