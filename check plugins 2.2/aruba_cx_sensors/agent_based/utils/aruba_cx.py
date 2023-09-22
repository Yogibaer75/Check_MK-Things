#!/usr/bin/env python3
'''Detect function for Aruba CX switches'''

from cmk.base.plugins.agent_based.agent_based_api.v1 import startswith, any_of

DETECT_ARUBA_CX = any_of(
    startswith(".1.3.6.1.2.1.1.2.0", ".1.3.6.1.4.1.47196.4.1.1.1"),
)
