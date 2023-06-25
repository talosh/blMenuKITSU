from . import Library
import json

# StillExportSettings
#
# Settings to use for Still exports
#

class StillExportSettings:
    
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
            self.FileType = obj.get("FileType")
            self.ImageOptions = obj.get("ImageOptions")
            self.Path = obj.get("Path")
            self.Filename = obj.get("Filename")
            self.ColourSpace = obj.get("ColourSpace")
            self.Format = obj.get("Format")
            self.Resolution = obj.get("Resolution")
            self.DecodeQuality = obj.get("DecodeQuality")
            self.Mask = obj.get("Mask")
            self.MaskMode = obj.get("MaskMode")
            self.Burnin = obj.get("Burnin")
            self.Truelight = obj.get("Truelight")
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
            self.FileType = None
            self.ImageOptions = None
            self.Path = None
            self.Filename = None
            self.ColourSpace = None
            self.Format = None
            self.Resolution = None
            self.DecodeQuality = None
            self.Mask = None
            self.MaskMode = None
            self.Burnin = None
            self.Truelight = None

    @staticmethod
    def from_dict(o):
        return StillExportSettings(o)

    def json(self):
        return {
            "_type": "StillExportSettings",
            "Source": self.Source,
            "Filter": self.Filter,
            "Category": self.Category,
            "CategoryMatch": self.CategoryMatch,
            "Frames": self.Frames,
            "MarkCategory": self.MarkCategory,
            "Stereo": self.Stereo,
            "Directory": self.Directory,
            "Overwrite": self.Overwrite,
            "FileType": self.FileType,
            "ImageOptions": self.ImageOptions,
            "Path": self.Path,
            "Filename": self.Filename,
            "ColourSpace": self.ColourSpace,
            "Format": self.Format,
            "Resolution": self.Resolution,
            "DecodeQuality": self.DecodeQuality,
            "Mask": self.Mask,
            "MaskMode": self.MaskMode,
            "Burnin": self.Burnin,
            "Truelight": self.Truelight,
        }

    def __repr__(self):
        return "flapi.StillExportSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "StillExportSettings", StillExportSettings.from_dict );

