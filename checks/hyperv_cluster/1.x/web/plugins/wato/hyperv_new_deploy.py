#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offst: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:hyperv_new",
    DropdownChoice(
        title = _("HyperV Cluster Plugins (Windows)"),
        help = _('This plugin checks the status of HyperV Cluster'),
        choices = [
            ( True, _("Deploy plugin for HyperV Cluster plugin") ),
            ( None, _("Do not deploy plugin for HyperV Cluster plugin") ),
        ]
    )
)

