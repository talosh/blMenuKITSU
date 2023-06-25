from . import Library
import json

# KeyTextItem
#
# A mapping for a key object to a user-readable string describing that key
#

class KeyTextItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Key = obj.get("Key")
            self.Text = obj.get("Text")
        else:
            self.Key = None
            self.Text = None

    @staticmethod
    def from_dict(o):
        return KeyTextItem(o)

    def json(self):
        return {
            "_type": "KeyTextItem",
            "Key": self.Key,
            "Text": self.Text,
        }

    def __repr__(self):
        return "flapi.KeyTextItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "KeyTextItem", KeyTextItem.from_dict );

