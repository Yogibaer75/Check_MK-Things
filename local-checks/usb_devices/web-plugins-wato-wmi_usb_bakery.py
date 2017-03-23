#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

import agent_bakery
import urllib

try:
    from hashlib import md5
except ImportError:
    from md5 import md5 # deprecated with python 2.5

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:wmi_usb",
    DropdownChoice(
        title = _("USB Devices (Local Check)(Windows)"),
        help = _("USB Devices List (Local Check)"),
        choices = [
            ( True, _("Deploy WMI USB Local Check") ),
            ( None, _("Do not deploy WMI USB Local Check") ),
        ]
    )
)
