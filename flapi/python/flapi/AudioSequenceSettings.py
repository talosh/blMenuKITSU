from . import Library
import json

# AudioSequenceSettings
#
# Settings defining the behaviour of an Audio Sequence
#

class AudioSequenceSettings:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Type = obj.get("Type")
            self.Filename = obj.get("Filename")
            self.Stems = obj.get("Stems")
            self.Offset = obj.get("Offset")
            self.Ratio = obj.get("Ratio")
        else:
            self.Type = None
            self.Filename = None
            self.Stems = None
            self.Offset = None
            self.Ratio = None

    @staticmethod
    def from_dict(o):
        return AudioSequenceSettings(o)

    def json(self):
        return {
            "_type": "AudioSequenceSettings",
            "Type": self.Type,
            "Filename": self.Filename,
            "Stems": self.Stems,
            "Offset": self.Offset,
            "Ratio": self.Ratio,
        }

    def __repr__(self):
        return "flapi.AudioSequenceSettings(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "AudioSequenceSettings", AudioSequenceSettings.from_dict );

