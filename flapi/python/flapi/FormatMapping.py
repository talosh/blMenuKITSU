from . import Library
import json

# FormatMapping
#
# Defines the mapping from one Format to another Format
#

class FormatMapping:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.sx = obj.get("sx")
            self.sy = obj.get("sy")
            self.tx = obj.get("tx")
            self.ty = obj.get("ty")
            self.inside = obj.get("inside")
            self.src_mask = obj.get("src_mask")
            self.dst_mask = obj.get("dst_mask")
        else:
            self.sx = None
            self.sy = None
            self.tx = None
            self.ty = None
            self.inside = None
            self.src_mask = None
            self.dst_mask = None

    @staticmethod
    def from_dict(o):
        return FormatMapping(o)

    def json(self):
        return {
            "_type": "FormatMapping",
            "sx": self.sx,
            "sy": self.sy,
            "tx": self.tx,
            "ty": self.ty,
            "inside": self.inside,
            "src_mask": self.src_mask,
            "dst_mask": self.dst_mask,
        }

    def __repr__(self):
        return "flapi.FormatMapping(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FormatMapping", FormatMapping.from_dict );

