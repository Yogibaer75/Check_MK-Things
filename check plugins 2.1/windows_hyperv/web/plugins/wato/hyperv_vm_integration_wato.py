#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

subgroup_applications = _("Applications, Processes & Services")
group = "checkparams"

register_check_parameters(
    subgroup_applications,
    "hyperv_vm_integration",
    "HyperV Integration Services Status",
    Dictionary(
        help = _("This defines the status of the integration services"),
        elements = [
            ( "default_status", DropdownChoice(
                    choices=[
                        ("active", _("active")),
                        ("inactive", _("inactive")),
                    ],
                title=_("Default State"),),
            ),
            ( "match_services",
                ListOf(
                    Tuple(
                        elements = [
                            TextAscii(title=_("Service name")),
                            DropdownChoice(
                                choices=[
                                    ("active", _("active")),
                                    ("inactive", _("inactive")),
                                ],
                            title=_("State"),),
                        ]),
                title=_("Special States"),),
            ),
        ]
    ),
    None,
    "dict"
)
