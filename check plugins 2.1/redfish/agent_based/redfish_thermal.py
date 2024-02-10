#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.base.plugins.agent_based.agent_based_api.v1 import register
from .utils.redfish import parse_redfish_multiple

register.agent_section(
    name="redfish_thermal",
    parse_function=parse_redfish_multiple,
)
