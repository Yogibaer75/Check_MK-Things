#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

subgroup_environment =  _("Temperature, Humidity, Electrical Parameters, etc.")

register_check_parameters(
    subgroup_environment,
    "hw_fans_rpm",
    _("FAN speed of Hardware devices"),
    Dictionary(
        elements = [
            ("levels_lower",
            Tuple(
                help = _("Lower levels for the fan speed of a hardware device"),
                title = _("Lower Fan levels"),
                elements = [
                    Integer(title = _("warning if below"), unit = u"rpm"),
                    Integer(title = _("critical if below"), unit = u"rpm"),
                ]),
            ),
            ( "levels",
            Tuple(
                help = _("Upper levels for the fan speed of a hardware device"),
                title = _("Upper Fan levels"),
                elements = [
                    Integer(title = _("warning at"), unit = u"rpm", default_value = 20000),
                    Integer(title = _("critical at"), unit = u"rpm", default_value = 25000),
                ]),
            ),
            ( "device_levels_handling",
              DropdownChoice(
                  title = _("Interpretation of the device's own temperature status"),
                  choices = [
                      ( "usr", _("Ignore device's own levels") ),
                      ( "dev", _("Only use device's levels, ignore yours" ) ),
                      ( "best", _("Use least critical of your and device's levels") ),
                      ( "worst", _("Use most critical of your and device's levels") ),
                      ( "devdefault", _("Use device's levels if present, otherwise yours") ),
                      ( "usrdefault", _("Use your own levels if present, otherwise the device's") ),
                  ],
                  default_value = "usrdefault",
            )),
        ],
        optional_keys = ["levels", "device_levels_handling"],
    ),
    TextAscii(
        title = _("Fan Name"),
        help = _("The identificator of the fan.")),
    match_type = "dict",
)
