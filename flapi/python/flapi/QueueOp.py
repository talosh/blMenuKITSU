from . import Library
import json

# QueueOp
#
# Description of an Operation in a Queue
#

class QueueOp:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.ID = obj.get("ID")
            self.Description = obj.get("Description")
            self.SubmitUser = obj.get("SubmitUser")
            self.SubmitHost = obj.get("SubmitHost")
        else:
            self.ID = None
            self.Description = None
            self.SubmitUser = None
            self.SubmitHost = None

    @staticmethod
    def from_dict(o):
        return QueueOp(o)

    def json(self):
        return {
            "_type": "QueueOp",
            "ID": self.ID,
            "Description": self.Description,
            "SubmitUser": self.SubmitUser,
            "SubmitHost": self.SubmitHost,
        }

    def __repr__(self):
        return "flapi.QueueOp(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "QueueOp", QueueOp.from_dict );

