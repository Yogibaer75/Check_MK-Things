#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

group = "agents/" + _("Agent Plugins")

register_rule(group,
    "agent_config:mssql_jobs",
    DropdownChoice(
        title = _("Microsoft SQL Server Job Plugin (Windows)"),
        help = _("This plugin will deploy the mssql_jobs.vbs on Windows"),
        style = "dropdown",
        choices = [
            ( True,   _("Deploy mssql_jobs plugin") ),
            ( False, _("Do not deploy mssql_jobs plugin") ),
        ]
    )
)

