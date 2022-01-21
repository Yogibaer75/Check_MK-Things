#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offst: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:win_cert",
    Alternative(
        title = _("System Certificate Age (Windows)"),
        help = _("This plugin dill deploy the win_cert.ps1 on Windows"),
        style = "dropdown",
        elements = [
            Dictionary(
                title = _("Deploy the win_cert.ps1 plugin"),
                elements = [
                    ("days", TextAscii(
                        title = _("Days to the future for certificate display"),
                        default_value = "90",
                    )),
                    ("issuer", TextAscii(
                        title = _("Search string for the issuer"),
                        default_value = ".*",
                    )),
                ],
            ),
            FixedValue(None, title = _("Do not deploy the win_cert.ps1 plugin."), totext = _("(disabled)") ),
        ]
    )
)

