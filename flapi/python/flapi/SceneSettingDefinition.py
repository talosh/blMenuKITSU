from . import Library
import json

# SceneSettingDefinition
#
# Type information for an SceneSettings parameter
#

class SceneSettingDefinition:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Type = obj.get("Type")
            self.Desc = obj.get("Desc")
            self.Values = obj.get("Values")
        else:
            self.Type = None
            self.Desc = None
            self.Values = None

    @staticmethod
    def from_dict(o):
        return SceneSettingDefinition(o)

    def json(self):
        return {
            "_type": "SceneSettingDefinition",
            "Type": self.Type,
            "Desc": self.Desc,
            "Values": self.Values,
        }

    def __repr__(self):
        return "flapi.SceneSettingDefinition(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "SceneSettingDefinition", SceneSettingDefinition.from_dict );

