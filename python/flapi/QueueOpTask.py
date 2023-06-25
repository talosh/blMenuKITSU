from . import Library
import json

# QueueOpTask
#
# Task information for FLAPI queue operation
#

class QueueOpTask:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ID = obj.get("ID")
            self.Seq = obj.get("Seq")
            self.Type = obj.get("Type")
            self.Desc = obj.get("Desc")
            self.Skip = obj.get("Skip")
            self.Params = obj.get("Params")
            self.Weight = obj.get("Weight")
        else:
            self.ID = None
            self.Seq = None
            self.Type = None
            self.Desc = None
            self.Skip = 0
            self.Params = None
            self.Weight = 1.000000

    @staticmethod
    def from_dict(o):
        return QueueOpTask(o)

    def json(self):
        return {
            "_type": "QueueOpTask",
            "ID": self.ID,
            "Seq": self.Seq,
            "Type": self.Type,
            "Desc": self.Desc,
            "Skip": self.Skip,
            "Params": self.Params,
            "Weight": self.Weight,
        }

    def __repr__(self):
        return "flapi.QueueOpTask(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "QueueOpTask", QueueOpTask.from_dict );

