from . import Library
import json

# CDLExportSettings
#
# Settings to use for CDL exports
#

class CDLExportSettings:
    
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
            self.Format = obj.get("Format")
            self.PathExample = obj.get("PathExample")
            self.Template = obj.get("Template")
            self.LookNameExample = obj.get("LookNameExample")
            self.LookName = obj.get("LookName")
            self.CDLLayer = obj.get("CDLLayer")
            self.CDLLayerCustom = obj.get("CDLLayerCustom")
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
            self.Format = None
            self.PathExample = None
            self.Template = None
            self.LookNameExample = None
            self.LookName = None
            self.CDLLayer = None
            self.CDLLayerCustom = None

    @staticmethod
    def from_dict(o):
        return CDLExportSettings(o)

    def json(self):
        return {
            "_type": "CDLExportSettings",
            "Source": self.Source,
            "Filter": self.Filter,
            "Category": self.Category,
            "CategoryMatch": self.CategoryMatch,
            "Frames": self.Frames,
            "MarkCategory": self.MarkCategory,
            "Stereo": self.Stereo,
            "Directory": self.Directory,
            "Overwrite": self.Overwrite,
            "Format": self.Format,
            "PathExample": self.PathExample,
            "Template": self.Template,
            "LookNameExample": self.LookNameExample,
            "LookName": self.LookName,
            "CDLLayer": self.CDLLayer,
            "CDLLayerCustom": self.CDLLayerCustom,
        }

    def __repr__(self):
        return "flapi.CDLExportSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "CDLExportSettings", CDLExportSettings.from_dict );

