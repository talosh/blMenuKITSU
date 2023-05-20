from . import Library
import json

# LicenceItem
#
# Description of a installed licence option
#

class LicenceItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Product = obj.get("Product")
            self.Version = obj.get("Version")
            self.Options = obj.get("Options")
            self.Permanent = obj.get("Permanent")
            self.Start = obj.get("Start")
            self.Duration = obj.get("Duration")
            self.DaysLeft = obj.get("DaysLeft")
        else:
            self.Product = None
            self.Version = None
            self.Options = None
            self.Permanent = None
            self.Start = None
            self.Duration = None
            self.DaysLeft = None

    @staticmethod
    def from_dict(o):
        return LicenceItem(o)

    def json(self):
        return {
            "_type": "LicenceItem",
            "Product": self.Product,
            "Version": self.Version,
            "Options": self.Options,
            "Permanent": self.Permanent,
            "Start": self.Start,
            "Duration": self.Duration,
            "DaysLeft": self.DaysLeft,
        }

    def __repr__(self):
        return "flapi.LicenceItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "LicenceItem", LicenceItem.from_dict );

