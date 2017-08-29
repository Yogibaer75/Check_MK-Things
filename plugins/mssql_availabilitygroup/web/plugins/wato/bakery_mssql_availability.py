#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:mssql_availability",
    Alternative(
        title = _("Microsoft SQL Server Databases Availability (Windows)"),
        help = _("This plugin will deploy the mssql_availability_status on Windows"),
        style = "dropdown",
        elements = [
            Dictionary(
                title = _("Deploy the mssql_availability_status.ps1 plugin"),
                elements = [
                    ("server", TextAscii(
                                title = _("Server name to connect to"),
                                default_value = "",
                    )),
                    ("instance", TextAscii(
                                title = _("Instance name to connect to"),
                                default_value = "",
                    )),
                    ("group", TextAscii(
                                title = _("Availability group name"),
                                default_value = "",
                    )),
                ],
            ),
            FixedValue(None, title = _("Do not deploy the mssql_availability_status.ps1"), totext = _("(disabled)") ),
        ]
    )
)

