from . import Library
import json

# SceneInfo
#
# Return general information about the state of a scene
#

class SceneInfo:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.CreatedDate = obj.get("CreatedDate")
            self.CreatedBy = obj.get("CreatedBy")
            self.CreatedVersion = obj.get("CreatedVersion")
            self.OpenedDate = obj.get("OpenedDate")
            self.OpenedBy = obj.get("OpenedBy")
            self.OpenedVersion = obj.get("OpenedVersion")
            self.ModifiedDate = obj.get("ModifiedDate")
            self.ModifiedBy = obj.get("ModifiedBy")
            self.ModifiedVersion = obj.get("ModifiedVersion")
            self.WorkingFormat = obj.get("WorkingFormat")
            self.Notes = obj.get("Notes")
            self.LastEDL = obj.get("LastEDL")
        else:
            self.CreatedDate = None
            self.CreatedBy = None
            self.CreatedVersion = None
            self.OpenedDate = None
            self.OpenedBy = None
            self.OpenedVersion = None
            self.ModifiedDate = None
            self.ModifiedBy = None
            self.ModifiedVersion = None
            self.WorkingFormat = None
            self.Notes = None
            self.LastEDL = None

    @staticmethod
    def from_dict(o):
        return SceneInfo(o)

    def json(self):
        return {
            "_type": "SceneInfo",
            "CreatedDate": self.CreatedDate,
            "CreatedBy": self.CreatedBy,
            "CreatedVersion": self.CreatedVersion,
            "OpenedDate": self.OpenedDate,
            "OpenedBy": self.OpenedBy,
            "OpenedVersion": self.OpenedVersion,
            "ModifiedDate": self.ModifiedDate,
            "ModifiedBy": self.ModifiedBy,
            "ModifiedVersion": self.ModifiedVersion,
            "WorkingFormat": self.WorkingFormat,
            "Notes": self.Notes,
            "LastEDL": self.LastEDL,
        }

    def __repr__(self):
        return "flapi.SceneInfo(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "SceneInfo", SceneInfo.from_dict );

