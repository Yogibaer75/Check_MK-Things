#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

group = "agents/" + _("Agent Plugins")

mssql_ha_authentication_choices = [
    ("system", _("System Authentication")),
    ("db", _("Database User Credentials"), Tuple(
        elements = [
            TextAscii(
                title = _("User ID"),
                default_value = "monitoring",
            ),
            Password(
                title = _("Password")
            ),
        ]
    )),
]

register_rule(group,
    "agent_config:mssql_ha",
    Transform(
        Alternative(
            title = _("Microsoft SQL Server HA (Windows)"),
            help = _('This plugin can be used to collect information of all running MSSQL servers '
                     'on the local system. Only usable if they are configured as HA group. '
                     'The current implementation of the check uses the "trusted authentication" '
                     'where no user/password needs to be created in the MSSQL server instance by '
                     'default. Using this method, you needed to grant the user as which the Check_MK '
                     'windows agent service is running access to the MSSQL database. Otherwise you '
                     'can configure the credentials of a database user which has the permission to '
                     'read the needed information from the server instance.'),
            style = "dropdown",
            elements = [
                Dictionary(
                    title = _("Deploy MSSQL Server plugin"),
                    elements = [
                        ("auth_default", CascadingDropdown(
                            title = _("Authentication (defaults)"),
                            choices = mssql_ha_authentication_choices,
                        )),
                        ("auth_instances", ListOf(
                            Tuple(
                                elements = [
                                    TextAscii(
                                        title = _("Instance ID"),
                                    ),
                                    CascadingDropdown(
                                        title = _("Authentication (defaults)"),
                                        choices = mssql_ha_authentication_choices,
                                    ),
                                ],
                            ),
                            allow_empty = False,
                            title = _("Authentication (instance specific)"),
                        )),
                    ],
                    optional_keys = ["auth_instances"],
                ),
                FixedValue(None, title = _("Do not deploy plugin for Microsoft SQL Server"), totext = _("(disabled)")),
            ],
            default_value = {
                "auth_default": "system",
            }
        ),
        forth = lambda x: x == True and {"auth_default":"system"} or x,
    )
)

