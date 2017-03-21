#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

register_check_parameters(
    subgroup_applications,
    "mein_check",
    _("Mein Check Wert"),
    Dictionary(
        title = _('Anzahl des Mein Check Wertes'),
        help = _('Groesse des Counters von Mein Check.'),
        elements = [
            ('anzahl', 
                Tuple(title = "Anzahl der Mein Check Werte",
                    elements = [
                        Integer(title = _("Warning at"), default_value = 100000)
                        Integer(title = _("Critical at"), default_value = 500000)
                    ])),
        ],
    ),
    TextAscii(title = _('Mein Check Wert')),
    match_type = "dict",
)
