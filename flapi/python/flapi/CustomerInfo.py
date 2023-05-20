from . import Library
import json

# CustomerInfo
#
# Dictionary containing customer related settings/preferences.
#

class CustomerInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.LogoURI = obj.get("LogoURI")
            self.WebsiteURL = obj.get("WebsiteURL")
        else:
            self.Name = None
            self.LogoURI = None
            self.WebsiteURL = None

    @staticmethod
    def from_dict(o):
        return CustomerInfo(o)

    def json(self):
        return {
            "_type": "CustomerInfo",
            "Name": self.Name,
            "LogoURI": self.LogoURI,
            "WebsiteURL": self.WebsiteURL,
        }

    def __repr__(self):
        return "flapi.CustomerInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "CustomerInfo", CustomerInfo.from_dict );

