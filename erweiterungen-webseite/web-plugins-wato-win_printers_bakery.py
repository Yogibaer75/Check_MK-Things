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
    "agent_config:win_printers",
    DropdownChoice(
        title = _("Printer Status (Windows)"),
        help = _("Printer Status Plugin"),
        choices = [
            ( True, _("Deploy Printer Status Plugin") ),
            ( None, _("Do not deploy Printer Status Plugin") ),
        ]
    )
)
