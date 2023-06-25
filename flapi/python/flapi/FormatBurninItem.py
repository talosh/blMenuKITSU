from . import Library
import json

# FormatBurninItem
#
# Definition of a text element within a FormatBurnin
#

class FormatBurninItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Type = obj.get("Type")
            self.X = obj.get("X")
            self.Y = obj.get("Y")
            self.XAlign = obj.get("XAlign")
            self.YAlign = obj.get("YAlign")
            self.Box = obj.get("Box")
            self.Height = obj.get("Height")
            self.Text = obj.get("Text")
            self.XScale = obj.get("XScale")
            self.YScale = obj.get("YScale")
            self.ResX = obj.get("ResX")
            self.ResY = obj.get("ResY")
            self.Opacity = obj.get("Opacity")
            self.File = obj.get("File")
        else:
            self.Type = None
            self.X = None
            self.Y = None
            self.XAlign = None
            self.YAlign = None
            self.Box = None
            self.Height = None
            self.Text = None
            self.XScale = None
            self.YScale = None
            self.ResX = None
            self.ResY = None
            self.Opacity = None
            self.File = None

    @staticmethod
    def from_dict(o):
        return FormatBurninItem(o)

    def json(self):
        return {
            "_type": "FormatBurninItem",
            "Type": self.Type,
            "X": self.X,
            "Y": self.Y,
            "XAlign": self.XAlign,
            "YAlign": self.YAlign,
            "Box": self.Box,
            "Height": self.Height,
            "Text": self.Text,
            "XScale": self.XScale,
            "YScale": self.YScale,
            "ResX": self.ResX,
            "ResY": self.ResY,
            "Opacity": self.Opacity,
            "File": self.File,
        }

    def __repr__(self):
        return "flapi.FormatBurninItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "FormatBurninItem", FormatBurninItem.from_dict );

