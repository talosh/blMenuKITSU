from . import Library
import json

# AudioSyncSettings
#
# Settings to use for AudioSync operation
#

class AudioSyncSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Criteria = obj.get("Criteria")
            self.Timecode = obj.get("Timecode")
            self.Scene = obj.get("Scene")
            self.Take = obj.get("Take")
            self.Directory = obj.get("Directory")
            self.SubSearch = obj.get("SubSearch")
            self.Subdirs = obj.get("Subdirs")
            self.FPS = obj.get("FPS")
            self.Offset = obj.get("Offset")
            self.Metadata = obj.get("Metadata")
            self.ClapDetect = obj.get("ClapDetect")
            self.ClapDetectThreshold = obj.get("ClapDetectThreshold")
            self.Ratio = obj.get("Ratio")
            self.ReadLTC = obj.get("ReadLTC")
            self.LTCIndex = obj.get("LTCIndex")
            self.LTCColumn = obj.get("LTCColumn")
            self.AutoSync = obj.get("AutoSync")
        else:
            self.Criteria = None
            self.Timecode = None
            self.Scene = None
            self.Take = None
            self.Directory = None
            self.SubSearch = None
            self.Subdirs = None
            self.FPS = None
            self.Offset = None
            self.Metadata = None
            self.ClapDetect = None
            self.ClapDetectThreshold = None
            self.Ratio = None
            self.ReadLTC = None
            self.LTCIndex = None
            self.LTCColumn = None
            self.AutoSync = None

    @staticmethod
    def from_dict(o):
        return AudioSyncSettings(o)

    def json(self):
        return {
            "_type": "AudioSyncSettings",
            "Criteria": self.Criteria,
            "Timecode": self.Timecode,
            "Scene": self.Scene,
            "Take": self.Take,
            "Directory": self.Directory,
            "SubSearch": self.SubSearch,
            "Subdirs": self.Subdirs,
            "FPS": self.FPS,
            "Offset": self.Offset,
            "Metadata": self.Metadata,
            "ClapDetect": self.ClapDetect,
            "ClapDetectThreshold": self.ClapDetectThreshold,
            "Ratio": self.Ratio,
            "ReadLTC": self.ReadLTC,
            "LTCIndex": self.LTCIndex,
            "LTCColumn": self.LTCColumn,
            "AutoSync": self.AutoSync,
        }

    def __repr__(self):
        return "flapi.AudioSyncSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "AudioSyncSettings", AudioSyncSettings.from_dict );

