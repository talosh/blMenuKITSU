from . import Library
import json

# QueueLogItem
#
# Log Item from Queue Operation
#

class QueueLogItem:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Time = obj.get("Time")
            self.Type = obj.get("Type")
            self.Task = obj.get("Task")
            self.Frame = obj.get("Frame")
            self.Message = obj.get("Message")
            self.Detail = obj.get("Detail")
        else:
            self.Time = None
            self.Type = None
            self.Task = None
            self.Frame = None
            self.Message = None
            self.Detail = None

    @staticmethod
    def from_dict(o):
        return QueueLogItem(o)

    def json(self):
        return {
            "_type": "QueueLogItem",
            "Time": self.Time,
            "Type": self.Type,
            "Task": self.Task,
            "Frame": self.Frame,
            "Message": self.Message,
            "Detail": self.Detail,
        }

    def __repr__(self):
        return "flapi.QueueLogItem(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "QueueLogItem", QueueLogItem.from_dict );

