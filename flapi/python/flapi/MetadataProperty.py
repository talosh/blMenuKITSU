from . import Library
import json

# MetadataProperty
#
# Definition of a Property that can specified for each MetadataItem defined in a Scene
#

class MetadataProperty:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Name = obj.get("Name")
        else:
            self.Key = None
            self.Name = None

    @staticmethod
    def from_dict(o):
        return MetadataProperty(o)

    def json(self):
        return {
            "_type": "MetadataProperty",
            "Key": self.Key,
            "Name": self.Name,
        }

    def __repr__(self):
        return "flapi.MetadataProperty(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "MetadataProperty", MetadataProperty.from_dict );

