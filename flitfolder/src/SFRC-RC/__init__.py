"""
A library for determining the moment-curvature diagram 
and shear capacity of SFRC-RC rectangular beam cross-sections
without tirrups
"""

__version__ = "0.0.1"

from .eng_module.SFRC import (
    momentcurvatureSFRC, 
    shearcap)

from .eng_module.beams import (build_beam, extract_arrays_all_combos)