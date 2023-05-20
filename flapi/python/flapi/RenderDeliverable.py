from . import Library
import json

# RenderDeliverable
#
# This type is used to specify the render settings for an individual deliverable defined within a RenderSetup
#

class RenderDeliverable:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Name = obj.get("Name")
            self.Disabled = obj.get("Disabled")
            self.IsMovie = obj.get("IsMovie")
            self.FileType = obj.get("FileType")
            self.MovieCodec = obj.get("MovieCodec")
            self.AudioCodec = obj.get("AudioCodec")
            self.ImageOptions = obj.get("ImageOptions")
            self.FastStart = obj.get("FastStart")
            self.AudioSampleRate = obj.get("AudioSampleRate")
            self.AudioNumChannels = obj.get("AudioNumChannels")
            self.Container = obj.get("Container")
            self.OutputDirectory = obj.get("OutputDirectory")
            self.FileNamePrefix = obj.get("FileNamePrefix")
            self.FileNamePostfix = obj.get("FileNamePostfix")
            self.FileNameNumDigits = obj.get("FileNameNumDigits")
            self.FileNameNumber = obj.get("FileNameNumber")
            self.FileNameExtension = obj.get("FileNameExtension")
            self.ColourSpaceTag = obj.get("ColourSpaceTag")
            self.RenderFormat = obj.get("RenderFormat")
            self.RenderResolution = obj.get("RenderResolution")
            self.RenderFrameRate = obj.get("RenderFrameRate")
            self.RenderFieldOrder = obj.get("RenderFieldOrder")
            self.RenderDecodeQuality = obj.get("RenderDecodeQuality")
            self.RenderColourSpace = obj.get("RenderColourSpace")
            self.RenderVideoLUT = obj.get("RenderVideoLUT")
            self.RenderLayer = obj.get("RenderLayer")
            self.RenderTrack = obj.get("RenderTrack")
            self.RenderMask = obj.get("RenderMask")
            self.RenderMaskMode = obj.get("RenderMaskMode")
            self.RenderBurnin = obj.get("RenderBurnin")
            self.RenderFlashBurnin = obj.get("RenderFlashBurnin")
            self.RenderDisableCache = obj.get("RenderDisableCache")
            self.HandleIncompleteStacks = obj.get("HandleIncompleteStacks")
            self.HandleEmptyFrames = obj.get("HandleEmptyFrames")
            self.HandleError = obj.get("HandleError")
            self.EmbedTimecode = obj.get("EmbedTimecode")
            self.EmbedTape = obj.get("EmbedTape")
            self.EmbedClip = obj.get("EmbedClip")
        else:
            self.Name = None
            self.Disabled = 0
            self.IsMovie = 0
            self.FileType = None
            self.MovieCodec = None
            self.AudioCodec = None
            self.ImageOptions = None
            self.FastStart = 0
            self.AudioSampleRate = 48000
            self.AudioNumChannels = 0
            self.Container = None
            self.OutputDirectory = None
            self.FileNamePrefix = ""
            self.FileNamePostfix = ""
            self.FileNameNumDigits = 7
            self.FileNameNumber = "F"
            self.FileNameExtension = None
            self.ColourSpaceTag = 1
            self.RenderFormat = None
            self.RenderResolution = "GMPR_HIGH"
            self.RenderFrameRate = None
            self.RenderFieldOrder = "None"
            self.RenderDecodeQuality = "GMDQ_OPTIMISED_UNLESS_HIGH"
            self.RenderColourSpace = None
            self.RenderVideoLUT = "none"
            self.RenderLayer = -1
            self.RenderTrack = 0
            self.RenderMask = "None"
            self.RenderMaskMode = 0
            self.RenderBurnin = None
            self.RenderFlashBurnin = 0
            self.RenderDisableCache = 0
            self.HandleIncompleteStacks = "GMREB_FAIL"
            self.HandleEmptyFrames = "GMREB_BLACK"
            self.HandleError = "ABORT"
            self.EmbedTimecode = 1
            self.EmbedTape = 1
            self.EmbedClip = 1

    @staticmethod
    def from_dict(o):
        return RenderDeliverable(o)

    def json(self):
        return {
            "_type": "RenderDeliverable",
            "Name": self.Name,
            "Disabled": self.Disabled,
            "IsMovie": self.IsMovie,
            "FileType": self.FileType,
            "MovieCodec": self.MovieCodec,
            "AudioCodec": self.AudioCodec,
            "ImageOptions": self.ImageOptions,
            "FastStart": self.FastStart,
            "AudioSampleRate": self.AudioSampleRate,
            "AudioNumChannels": self.AudioNumChannels,
            "Container": self.Container,
            "OutputDirectory": self.OutputDirectory,
            "FileNamePrefix": self.FileNamePrefix,
            "FileNamePostfix": self.FileNamePostfix,
            "FileNameNumDigits": self.FileNameNumDigits,
            "FileNameNumber": self.FileNameNumber,
            "FileNameExtension": self.FileNameExtension,
            "ColourSpaceTag": self.ColourSpaceTag,
            "RenderFormat": self.RenderFormat,
            "RenderResolution": self.RenderResolution,
            "RenderFrameRate": self.RenderFrameRate,
            "RenderFieldOrder": self.RenderFieldOrder,
            "RenderDecodeQuality": self.RenderDecodeQuality,
            "RenderColourSpace": self.RenderColourSpace,
            "RenderVideoLUT": self.RenderVideoLUT,
            "RenderLayer": self.RenderLayer,
            "RenderTrack": self.RenderTrack,
            "RenderMask": self.RenderMask,
            "RenderMaskMode": self.RenderMaskMode,
            "RenderBurnin": self.RenderBurnin,
            "RenderFlashBurnin": self.RenderFlashBurnin,
            "RenderDisableCache": self.RenderDisableCache,
            "HandleIncompleteStacks": self.HandleIncompleteStacks,
            "HandleEmptyFrames": self.HandleEmptyFrames,
            "HandleError": self.HandleError,
            "EmbedTimecode": self.EmbedTimecode,
            "EmbedTape": self.EmbedTape,
            "EmbedClip": self.EmbedClip,
        }

    def __repr__(self):
        return "flapi.RenderDeliverable(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "RenderDeliverable", RenderDeliverable.from_dict );

