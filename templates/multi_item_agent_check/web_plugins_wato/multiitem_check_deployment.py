#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offst: 4 -*-

# deployment without any options only select to deploy or not

group = "agents/" + _("Agent Plugins")

register_rule(
    group, "agent_config:win_CHECKNAME",
    DropdownChoice(title=_("CHECKNAME description (Windows)"),
                   help=_('This plugin checks the status of CHECKNAME description windows'),
                   choices=[
                       (True, _("Deploy plugin for CHECKNAME")),
                       (None, _("Do not deploy plugin for CHECKNAME")),
                   ]))
