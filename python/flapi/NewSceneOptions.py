from . import Library
import json

# NewSceneOptions
#
# Options for create a new database or temporary scene
#

class NewSceneOptions:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.format = obj.get("format")
            self.colourspace = obj.get("colourspace")
            self.frame_rate = obj.get("frame_rate")
            self.field_order = obj.get("field_order")
            self.template = obj.get("template")
            self.blg_template = obj.get("blg_template")
        else:
            self.format = None
            self.colourspace = None
            self.frame_rate = None
            self.field_order = "None"
            self.template = None
            self.blg_template = None

    @staticmethod
    def from_dict(o):
        return NewSceneOptions(o)

    def json(self):
        return {
            "_type": "NewSceneOptions",
            "format": self.format,
            "colourspace": self.colourspace,
            "frame_rate": self.frame_rate,
            "field_order": self.field_order,
            "template": self.template,
            "blg_template": self.blg_template,
        }

    def __repr__(self):
        return "flapi.NewSceneOptions(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "NewSceneOptions", NewSceneOptions.from_dict );

