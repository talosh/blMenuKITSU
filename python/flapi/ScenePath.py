from . import Library
import json

# ScenePath
#
# A ScenePath defines the host, job, folder and scene names required to create or open a FilmLight scene
#

class ScenePath:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Type = obj.get("Type")
            self.Host = obj.get("Host")
            self.Job = obj.get("Job")
            self.Scene = obj.get("Scene")
            self.Tag = obj.get("Tag")
            self.Filename = obj.get("Filename")
        else:
            self.Type = "psql"
            self.Host = None
            self.Job = None
            self.Scene = None
            self.Tag = "Main"
            self.Filename = ""

    @staticmethod
    def from_dict(o):
        return ScenePath(o)

    def json(self):
        return {
            "_type": "ScenePath",
            "Type": self.Type,
            "Host": self.Host,
            "Job": self.Job,
            "Scene": self.Scene,
            "Tag": self.Tag,
            "Filename": self.Filename,
        }

    def __repr__(self):
        return "flapi.ScenePath(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "ScenePath", ScenePath.from_dict );

