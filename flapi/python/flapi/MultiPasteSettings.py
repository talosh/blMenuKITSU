from . import Library
import json

# MultiPasteSettings
#
# Settings to use for MultiPaste operation
#

class MultiPasteSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Source = obj.get("Source")
            self.SourceScenes = obj.get("SourceScenes")
            self.SourceDirectory = obj.get("SourceDirectory")
            self.SourceEDL = obj.get("SourceEDL")
            self.EDLApplyASCCDL = obj.get("EDLApplyASCCDL")
            self.ASCCDLLayerNumber = obj.get("ASCCDLLayerNumber")
            self.ASCCDLColour = obj.get("ASCCDLColour")
            self.ASCCDLCategories = obj.get("ASCCDLCategories")
            self.BLGResourceConflict = obj.get("BLGResourceConflict")
            self.DestSelection = obj.get("DestSelection")
            self.LUTDirectory = obj.get("LUTDirectory")
            self.LUTLayerNum = obj.get("LUTLayerNum")
            self.LUTLayerColour = obj.get("LUTLayerColour")
            self.LUTCategories = obj.get("LUTCategories")
            self.CDLDirectory = obj.get("CDLDirectory")
            self.CDLLayerNum = obj.get("CDLLayerNum")
            self.CDLLayerColour = obj.get("CDLLayerColour")
            self.CDLCategories = obj.get("CDLCategories")
            self.MatchBy = obj.get("MatchBy")
            self.MatchQuality = obj.get("MatchQuality")
            self.PasteGrades = obj.get("PasteGrades")
            self.LayerZeroBehaviour = obj.get("LayerZeroBehaviour")
            self.LayerZeroOverwrite = obj.get("LayerZeroOverwrite")
            self.LayerZeroAudio = obj.get("LayerZeroAudio")
            self.InputColourSpace = obj.get("InputColourSpace")
            self.SourceShots = obj.get("SourceShots")
            self.SourceShotCategories = obj.get("SourceShotCategories")
            self.DestShots = obj.get("DestShots")
            self.DestShotCategories = obj.get("DestShotCategories")
            self.DetectGradeChanges = obj.get("DetectGradeChanges")
            self.GradeChangedCategory = obj.get("GradeChangedCategory")
            self.ClearUnchangedGrades = obj.get("ClearUnchangedGrades")
            self.PasteLocation = obj.get("PasteLocation")
            self.LayerZeroCategories = obj.get("LayerZeroCategories")
            self.LayerZeroExcludeCategories = obj.get("LayerZeroExcludeCategories")
            self.PasteMetadata = obj.get("PasteMetadata")
            self.MetadataColumns = obj.get("MetadataColumns")
            self.AddExtraMetadata = obj.get("AddExtraMetadata")
            self.OverwriteMetadata = obj.get("OverwriteMetadata")
            self.PasteGroups = obj.get("PasteGroups")
            self.ShredComps = obj.get("ShredComps")
            self.ShredProtectCategories = obj.get("ShredProtectCategories")
            self.ShredExternalMattes = obj.get("ShredExternalMattes")
        else:
            self.Source = None
            self.SourceScenes = None
            self.SourceDirectory = None
            self.SourceEDL = None
            self.EDLApplyASCCDL = None
            self.ASCCDLLayerNumber = None
            self.ASCCDLColour = None
            self.ASCCDLCategories = None
            self.BLGResourceConflict = None
            self.DestSelection = None
            self.LUTDirectory = None
            self.LUTLayerNum = None
            self.LUTLayerColour = None
            self.LUTCategories = None
            self.CDLDirectory = None
            self.CDLLayerNum = None
            self.CDLLayerColour = None
            self.CDLCategories = None
            self.MatchBy = None
            self.MatchQuality = None
            self.PasteGrades = None
            self.LayerZeroBehaviour = None
            self.LayerZeroOverwrite = None
            self.LayerZeroAudio = None
            self.InputColourSpace = None
            self.SourceShots = None
            self.SourceShotCategories = None
            self.DestShots = None
            self.DestShotCategories = None
            self.DetectGradeChanges = None
            self.GradeChangedCategory = None
            self.ClearUnchangedGrades = None
            self.PasteLocation = None
            self.LayerZeroCategories = None
            self.LayerZeroExcludeCategories = None
            self.PasteMetadata = None
            self.MetadataColumns = None
            self.AddExtraMetadata = None
            self.OverwriteMetadata = None
            self.PasteGroups = None
            self.ShredComps = None
            self.ShredProtectCategories = None
            self.ShredExternalMattes = None

    @staticmethod
    def from_dict(o):
        return MultiPasteSettings(o)

    def json(self):
        return {
            "_type": "MultiPasteSettings",
            "Source": self.Source,
            "SourceScenes": self.SourceScenes,
            "SourceDirectory": self.SourceDirectory,
            "SourceEDL": self.SourceEDL,
            "EDLApplyASCCDL": self.EDLApplyASCCDL,
            "ASCCDLLayerNumber": self.ASCCDLLayerNumber,
            "ASCCDLColour": self.ASCCDLColour,
            "ASCCDLCategories": self.ASCCDLCategories,
            "BLGResourceConflict": self.BLGResourceConflict,
            "DestSelection": self.DestSelection,
            "LUTDirectory": self.LUTDirectory,
            "LUTLayerNum": self.LUTLayerNum,
            "LUTLayerColour": self.LUTLayerColour,
            "LUTCategories": self.LUTCategories,
            "CDLDirectory": self.CDLDirectory,
            "CDLLayerNum": self.CDLLayerNum,
            "CDLLayerColour": self.CDLLayerColour,
            "CDLCategories": self.CDLCategories,
            "MatchBy": self.MatchBy,
            "MatchQuality": self.MatchQuality,
            "PasteGrades": self.PasteGrades,
            "LayerZeroBehaviour": self.LayerZeroBehaviour,
            "LayerZeroOverwrite": self.LayerZeroOverwrite,
            "LayerZeroAudio": self.LayerZeroAudio,
            "InputColourSpace": self.InputColourSpace,
            "SourceShots": self.SourceShots,
            "SourceShotCategories": self.SourceShotCategories,
            "DestShots": self.DestShots,
            "DestShotCategories": self.DestShotCategories,
            "DetectGradeChanges": self.DetectGradeChanges,
            "GradeChangedCategory": self.GradeChangedCategory,
            "ClearUnchangedGrades": self.ClearUnchangedGrades,
            "PasteLocation": self.PasteLocation,
            "LayerZeroCategories": self.LayerZeroCategories,
            "LayerZeroExcludeCategories": self.LayerZeroExcludeCategories,
            "PasteMetadata": self.PasteMetadata,
            "MetadataColumns": self.MetadataColumns,
            "AddExtraMetadata": self.AddExtraMetadata,
            "OverwriteMetadata": self.OverwriteMetadata,
            "PasteGroups": self.PasteGroups,
            "ShredComps": self.ShredComps,
            "ShredProtectCategories": self.ShredProtectCategories,
            "ShredExternalMattes": self.ShredExternalMattes,
        }

    def __repr__(self):
        return "flapi.MultiPasteSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "MultiPasteSettings", MultiPasteSettings.from_dict );

