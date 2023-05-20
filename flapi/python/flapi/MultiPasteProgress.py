from . import Library
import json

# MultiPasteProgress
#
# Progress information from Multi-Paste operation
#

class MultiPasteProgress:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Status = obj.get("Status")
            self.Summary = obj.get("Summary")
            self.ShotID = obj.get("ShotID")
            self.Frame = obj.get("Frame")
        else:
            self.Status = None
            self.Summary = None
            self.ShotID = None
            self.Frame = None

    @staticmethod
    def from_dict(o):
        return MultiPasteProgress(o)

    def json(self):
        return {
            "_type": "MultiPasteProgress",
            "Status": self.Status,
            "Summary": self.Summary,
            "ShotID": self.ShotID,
            "Frame": self.Frame,
        }

    def __repr__(self):
        return "flapi.MultiPasteProgress(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "MultiPasteProgress", MultiPasteProgress.from_dict );

