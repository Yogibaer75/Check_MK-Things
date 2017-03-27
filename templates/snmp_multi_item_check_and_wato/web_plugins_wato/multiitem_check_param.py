#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

register_check_parameters(
    subgroup_<environment/networking/storage/and so on>,
    "<wato_group>",
    _("WATO Group"),
    Dictionary(
        elements = [
            ( "levels",
              Tuple(
                  title = _("Levels of checked value"),
                  help = _("This rule sets the levels of the checked value."),
                  elements = [
                      Integer(title = _("Warning at"), default_value = 26),
                      Integer(title = _("Critical at"), default_value = 30),
                  ],
            )),
        ]
    ),
    TextAscii(
        title = _("Item name"),
        help = _("The identifier of the item.")),
    "dict",
)