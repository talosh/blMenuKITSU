from . import Library
import json

# DialogItem
#
# Definition of an item to be shown in a DynamicDialog
#

class DialogItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Label = obj.get("Label")
            self.Type = obj.get("Type")
            self.Help = obj.get("Help")
            self.Default = obj.get("Default")
            self.Options = obj.get("Options")
            self.RegExp = obj.get("RegExp")
            self.Password = obj.get("Password")
            self.IntMin = obj.get("IntMin")
            self.IntMax = obj.get("IntMax")
            self.FloatMin = obj.get("FloatMin")
            self.FloatMax = obj.get("FloatMax")
            self.FloatSnap = obj.get("FloatSnap")
            self.Style = obj.get("Style")
            self.Height = obj.get("Height")
        else:
            self.Key = None
            self.Label = None
            self.Type = None
            self.Help = None
            self.Default = None
            self.Options = None
            self.RegExp = None
            self.Password = None
            self.IntMin = None
            self.IntMax = None
            self.FloatMin = None
            self.FloatMax = None
            self.FloatSnap = None
            self.Style = None
            self.Height = 0

    @staticmethod
    def from_dict(o):
        return DialogItem(o)

    def json(self):
        return {
            "_type": "DialogItem",
            "Key": self.Key,
            "Label": self.Label,
            "Type": self.Type,
            "Help": self.Help,
            "Default": self.Default,
            "Options": self.Options,
            "RegExp": self.RegExp,
            "Password": self.Password,
            "IntMin": self.IntMin,
            "IntMax": self.IntMax,
            "FloatMin": self.FloatMin,
            "FloatMax": self.FloatMax,
            "FloatSnap": self.FloatSnap,
            "Style": self.Style,
            "Height": self.Height,
        }

    def __repr__(self):
        return "flapi.DialogItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "DialogItem", DialogItem.from_dict );

