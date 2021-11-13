#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

import agent_bakery

group = "agents/" + _("Agent Plugins")

register_rule(
    group, "agent_config:wmi_usb",
    DropdownChoice(title=_("USB Devices (Local Check)(Windows)"),
                   help=_("USB Devices List (Local Check)"),
                   choices=[
                       (True, _("Deploy WMI USB Local Check")),
                       (None, _("Do not deploy WMI USB Local Check")),
                   ]))
