#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Tuple,
    Float,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    RulespecGroupCheckParametersEnvironment,
    CheckParameterRulespecWithoutItem,
)


def _parameter_valuespec_apc_pdu():
    return Dictionary(elements=[
        ("level_watts",
             Tuple(
                 title=_("Upper Levels for Power in Watts"),
                 elements=[
                     Float(title=_("Warning at"), default_value=3000.00, unit="Watt"),
                     Float(title=_("Critical at"), default_value=3700.00, unit="Watt"),
                 ],            
         )),
        ("level_va",
             Tuple(
                 title=_("Upper Levels for Power in VA"),
                 elements=[
                     Float(title=_("Warning at"), default_value=3000.00, unit="VA"),
                     Float(title=_("Critical at"), default_value=3700.00, unit="VA"),
                 ],
         )),
         ],)


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="apc_pdu",
        group=RulespecGroupCheckParametersEnvironment,
        parameter_valuespec=_parameter_valuespec_apc_pdu,
        title=lambda: _("APC PDU Power levels"),
    ))
