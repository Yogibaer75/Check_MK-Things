#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:win_ps",
    Dictionary(
        title = _("Windows process monitoring with WMI"),
        elements = [
            ("use_wmi",
             DropdownChoice(
                 title = _("Use WMI to get process informations"),
                 choices = [
                     ( "no", _("no") ),
                     ( "yes", _("yes") ),
                 ],
                 default_value = "no",
             ),
            ),
            ("full_path",
             DropdownChoice(
                 title = _("Get full path and all arguments of processes - use_wmi must be set"),
                 choices = [
                     ( "no", _("no") ),
                     ( "yes", _("yes") ),
                 ],
                 default_value = "no",
             ),
            ),
        ],
        optional_keys = False,
    )
)