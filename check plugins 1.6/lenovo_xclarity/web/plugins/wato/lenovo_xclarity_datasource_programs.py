#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
group = "datasource_programs"

register_rule(
    group,
    "special_agents:lenovo_xclarity",
    Dictionary(
        elements=[
            (
                "user",
                TextAscii(
                    title=_("Username"),
                    allow_empty=False,
                ),
            ),
            (
                "password",
                Password(
                    title=_("Password"),
                    allow_empty=False,
                ),
            ),
        ],
        optional_keys=False,
    ),
    title=_("Lenovo XClarity Management Controller"),
    help=_(
        "This rule selects the Agent Lenovo XClarity instead of the normal Check_MK Agent "
        "which collects the data through the Redfish REST API"
    ),
    match="first",
)
