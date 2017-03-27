#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offst: 4 -*-

# deployment without any options only select to deploy or not

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:win_<checkname>",
    DropdownChoice(
        title = _("<checkname> description (Windows)"),
        help = _('This plugin checks the status of <checkname> description windows'),
        choices = [
            ( True, _("Deploy plugin for <checkname>") ),
            ( None, _("Do not deploy plugin for <checkname>") ),
        ]
    )
)
