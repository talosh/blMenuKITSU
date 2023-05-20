from . import Library
import json

# CubeExportSettings
#
# Settings to use for Cube exports
#

class CubeExportSettings:
    
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
            self.NumLUTs = obj.get("NumLUTs")
            self.LUT1Options = obj.get("LUT1Options")
            self.LUT1Path = obj.get("LUT1Path")
            self.LUT1Name = obj.get("LUT1Name")
            self.LUT2Options = obj.get("LUT2Options")
            self.LUT2Path = obj.get("LUT2Path")
            self.LUT2Name = obj.get("LUT2Name")
            self.LUT3Options = obj.get("LUT3Options")
            self.LUT3Path = obj.get("LUT3Path")
            self.LUT3Name = obj.get("LUT3Name")
            self.InputColourSpace = obj.get("InputColourSpace")
            self.InputDRT = obj.get("InputDRT")
            self.LUTFormat = obj.get("LUTFormat")
            self.ExtendedRanges = obj.get("ExtendedRanges")
            self.InputMin = obj.get("InputMin")
            self.InputMaxLog = obj.get("InputMaxLog")
            self.InputMaxLin = obj.get("InputMaxLin")
            self.InputLogOffset = obj.get("InputLogOffset")
            self.OutputColourSpace = obj.get("OutputColourSpace")
            self.CubeResolution = obj.get("CubeResolution")
            self.LUTResolution = obj.get("LUTResolution")
            self.GradeReplace = obj.get("GradeReplace")
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
            self.NumLUTs = None
            self.LUT1Options = None
            self.LUT1Path = None
            self.LUT1Name = None
            self.LUT2Options = None
            self.LUT2Path = None
            self.LUT2Name = None
            self.LUT3Options = None
            self.LUT3Path = None
            self.LUT3Name = None
            self.InputColourSpace = None
            self.InputDRT = None
            self.LUTFormat = None
            self.ExtendedRanges = None
            self.InputMin = None
            self.InputMaxLog = None
            self.InputMaxLin = None
            self.InputLogOffset = None
            self.OutputColourSpace = None
            self.CubeResolution = None
            self.LUTResolution = None
            self.GradeReplace = None

    @staticmethod
    def from_dict(o):
        return CubeExportSettings(o)

    def json(self):
        return {
            "_type": "CubeExportSettings",
            "Source": self.Source,
            "Filter": self.Filter,
            "Category": self.Category,
            "CategoryMatch": self.CategoryMatch,
            "Frames": self.Frames,
            "MarkCategory": self.MarkCategory,
            "Stereo": self.Stereo,
            "Directory": self.Directory,
            "Overwrite": self.Overwrite,
            "NumLUTs": self.NumLUTs,
            "LUT1Options": self.LUT1Options,
            "LUT1Path": self.LUT1Path,
            "LUT1Name": self.LUT1Name,
            "LUT2Options": self.LUT2Options,
            "LUT2Path": self.LUT2Path,
            "LUT2Name": self.LUT2Name,
            "LUT3Options": self.LUT3Options,
            "LUT3Path": self.LUT3Path,
            "LUT3Name": self.LUT3Name,
            "InputColourSpace": self.InputColourSpace,
            "InputDRT": self.InputDRT,
            "LUTFormat": self.LUTFormat,
            "ExtendedRanges": self.ExtendedRanges,
            "InputMin": self.InputMin,
            "InputMaxLog": self.InputMaxLog,
            "InputMaxLin": self.InputMaxLin,
            "InputLogOffset": self.InputLogOffset,
            "OutputColourSpace": self.OutputColourSpace,
            "CubeResolution": self.CubeResolution,
            "LUTResolution": self.LUTResolution,
            "GradeReplace": self.GradeReplace,
        }

    def __repr__(self):
        return "flapi.CubeExportSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "CubeExportSettings", CubeExportSettings.from_dict );

