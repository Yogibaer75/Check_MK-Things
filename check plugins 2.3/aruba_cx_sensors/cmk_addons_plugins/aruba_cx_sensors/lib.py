#!/usr/bin/env python3
"""Detect function for Aruba CX switches"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    any_of,
    startswith,
)

DETECT_ARUBA_CX = any_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.47196.4.1.1.1"),
)
