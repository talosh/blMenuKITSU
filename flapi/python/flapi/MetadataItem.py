from . import Library
import json

# MetadataItem
#
# Definition of a Metadata field that exists across all shots in a Scene
#

class MetadataItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
            self.Type = obj.get("Type")
            self.NumElements = obj.get("NumElements")
            self.IsReadOnly = obj.get("IsReadOnly")
            self.IsUserDefined = obj.get("IsUserDefined")
            self.Properties = obj.get("Properties")
        else:
            self.Key = None
            self.Name = None
            self.Type = None
            self.NumElements = None
            self.IsReadOnly = None
            self.IsUserDefined = None
            self.Properties = None

    @staticmethod
    def from_dict(o):
        return MetadataItem(o)

    def json(self):
        return {
            "_type": "MetadataItem",
            "Key": self.Key,
            "Name": self.Name,
            "Type": self.Type,
            "NumElements": self.NumElements,
            "IsReadOnly": self.IsReadOnly,
            "IsUserDefined": self.IsUserDefined,
            "Properties": self.Properties,
        }

    def __repr__(self):
        return "flapi.MetadataItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "MetadataItem", MetadataItem.from_dict );

