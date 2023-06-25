from . import Library
import json

# BLGExportSettings
#
# Settings to use for BLG exports
#

class BLGExportSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Source = obj.get("Source")
            self.Filter = obj.get("Filter")
            self.Category = obj.get("Category")
            self.CategoryMatch = obj.get("CategoryMatch")
            self.Frames = obj.get("Frames")
            self.MarkCategory = obj.get("MarkCategory")
            self.Stereo = obj.get("Stereo")
            self.Directory = obj.get("Directory")
            self.Overwrite = obj.get("Overwrite")
            self.Path = obj.get("Path")
            self.Template = obj.get("Template")
            self.Scale = obj.get("Scale")
            self.AllowMultiInput = obj.get("AllowMultiInput")
            self.GenerateNukeScripts = obj.get("GenerateNukeScripts")
            self.GenerateWriteNode = obj.get("GenerateWriteNode")
            self.Keyframes = obj.get("Keyframes")
            self.LockGrade = obj.get("LockGrade")
            self.ViewingColourSpace = obj.get("ViewingColourSpace")
            self.ViewingFormat = obj.get("ViewingFormat")
        else:
            self.Source = None
            self.Filter = None
            self.Category = None
            self.CategoryMatch = None
            self.Frames = None
            self.MarkCategory = None
            self.Stereo = None
            self.Directory = None
            self.Overwrite = None
            self.Path = None
            self.Template = None
            self.Scale = None
            self.AllowMultiInput = None
            self.GenerateNukeScripts = None
            self.GenerateWriteNode = None
            self.Keyframes = None
            self.LockGrade = None
            self.ViewingColourSpace = None
            self.ViewingFormat = None

    @staticmethod
    def from_dict(o):
        return BLGExportSettings(o)

    def json(self):
        return {
            "_type": "BLGExportSettings",
            "Source": self.Source,
            "Filter": self.Filter,
            "Category": self.Category,
            "CategoryMatch": self.CategoryMatch,
            "Frames": self.Frames,
            "MarkCategory": self.MarkCategory,
            "Stereo": self.Stereo,
            "Directory": self.Directory,
            "Overwrite": self.Overwrite,
            "Path": self.Path,
            "Template": self.Template,
            "Scale": self.Scale,
            "AllowMultiInput": self.AllowMultiInput,
            "GenerateNukeScripts": self.GenerateNukeScripts,
            "GenerateWriteNode": self.GenerateWriteNode,
            "Keyframes": self.Keyframes,
            "LockGrade": self.LockGrade,
            "ViewingColourSpace": self.ViewingColourSpace,
            "ViewingFormat": self.ViewingFormat,
        }

    def __repr__(self):
        return "flapi.BLGExportSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "BLGExportSettings", BLGExportSettings.from_dict );

