#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersVirtualization,
)
from cmk.gui.valuespec import Dictionary, Percentage, Tuple


def _parameter_valuespec_prism_vm_cpu():
    return Dictionary(
        elements=[
            (
                "levels",
                Tuple(
                    title=_("Specify levels in percentage of CPU usage"),
                    elements=[
                        Percentage(title=_("Warning at"), unit=_("%")),
                        Percentage(title=_("Critical at"), unit=_("%")),
                    ],
                ),
            ),
            (
                "levels_rdy",
                Tuple(
                    title=_("Specify levels if percentage of CPU ready state"),
                    elements=[
                        Percentage(title=_("Warning at"), unit=_("%")),
                        Percentage(title=_("Critical at"), unit=_("%")),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="prism_vm_cpu",
        group=RulespecGroupCheckParametersVirtualization,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_prism_vm_cpu,
        title=lambda: _("Nutanix VM CPU utilization"),
    )
)
