from . import Library
import json

# Rational
#
# Holds a rational number.  Used in situations where exact ratios are required.
#

class Rational:
    
    # Constructor
    def __init__(self, obj=None, **kwargs):
        if obj is None:
            obj=kwargs
        if obj != None:
            self.Numerator = obj.get("Numerator")
            self.Denominator = obj.get("Denominator")
        else:
            self.Numerator = None
            self.Denominator = None

    @staticmethod
    def from_dict(o):
        return Rational(o)

    def json(self):
        return {
            "_type": "Rational",
            "Numerator": self.Numerator,
            "Denominator": self.Denominator,
        }

    def __repr__(self):
        return "flapi.Rational(%s)" % (vars(self))
    def __str__(self):
        return "%s" % vars(self)
Library.register_decoder( "Rational", Rational.from_dict );

