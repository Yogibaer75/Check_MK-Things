#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

register_check_parameters(
    subgroup_networking,
    "fortigate_update",
    _("Fortigate Update"),
    Dictionary(
        elements=[
            (
                "levels",
                Tuple(
                    title=_("Days since last update"),
                    help=_("This rule sets the levels of the checked value."),
                    elements=[
                        Integer(title=_("Warning at"), default_value=30),
                        Integer(title=_("Critical at"), default_value=90),
                    ],
                ),
            ),
            (
                "no_levels",
                Checkbox(
                    title=_("Do not impose levels"),
                    label=_("no levels"),
                    default_value=False,
                ),
            ),
        ]
    ),
    TextAscii(title=_("Item name"), help=_("The identifier of the item.")),
    "dict",
)
