#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Float,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersEnvironment,
)


def _parameter_valuespec_bacs_battery():
    return Dictionary(
        title=_("Voltage Sensor"),
        optional_keys=True,
        elements=[
            ("voltage",
             Tuple(
                 title=_("Upper Levels for Voltage"),
                 elements=[
                     Float(title=_("Warning over"), default_value=14.00, unit="V"),
                     Float(title=_("Critical over"), default_value=15.00, unit="V"),
                 ],
             )),
             ("voltage_lower",
             Tuple(
                 title=_("Lower Levels for Voltage"),
                 elements=[
                     Float(title=_("Warning below"), default_value=10.00, unit="V"),
                     Float(title=_("Critical below"), default_value=9.00, unit="V"),
                 ],
             )),
             ("temp",
             Tuple(
                 title=_("Upper Levels for Temperature"),
                 elements=[
                     Float(title=_("Warning below"), default_value=40.00, unit=u"°C"),
                     Float(title=_("Critical below"), default_value=50.00, unit=u"°C"),
                 ],
             )),
             ("temp_lower",
             Tuple(
                 title=_("Lower Levels for Temperature"),
                 elements=[
                     Float(title=_("Warning below"), default_value=10.00, unit=u"°C"),
                     Float(title=_("Critical below"), default_value=5.00, unit=u"°C"),
                 ],
             )),
             ("resistance",
             Tuple(
                 title=_("Levels for inside Resistance"),
                 elements=[
                     Float(title=_("Warning over"), default_value=15.00, unit="Ohm"),
                     Float(title=_("Critical over"), default_value=18.00, unit="Ohm"),
                 ],
             )),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="bacs",
        group=RulespecGroupCheckParametersEnvironment,
        item_spec=lambda: TextAscii(title=_("Battery Index"),),
        parameter_valuespec=_parameter_valuespec_bacs_battery,
        title=lambda: _("BACS Battery"),
    ))

