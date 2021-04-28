#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offst: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:hyperv_vms_guestinfos",
    DropdownChoice(
        title = _("HyperV VMs GuestInfos (Windows)"),
        help = _('This plugin checks the status of HyperV VMs guestinfos'),
        choices = [
            ( True, _("Deploy plugin for HyperV VMs guestinfos") ),
            ( None, _("Do not deploy plugin for HyperV VMs guestinfos") ),
        ]
    )
)
