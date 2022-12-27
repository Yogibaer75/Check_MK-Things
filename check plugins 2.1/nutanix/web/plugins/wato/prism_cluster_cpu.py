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


def _parameter_valuespec_prism_cluster_cpu() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "util",
                Tuple(
                    elements=[
                        Percentage(title=_("Warning at a utilization of"), default_value=90.0),
                        Percentage(title=_("Critical at a utilization of"), default_value=95.0),
                    ],
                    title=_("Alert on excessive CPU utilization"),
                    help=_(
                        "This rule configures levels for the CPU utilization (not load) for "
                        "Nutanix cluster systems. "
                        "The utilization percentage is shown for the whole cluster."
                    ),
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="prism_cluster_cpu",
        group=RulespecGroupCheckParametersVirtualization,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_prism_cluster_cpu,
        title=lambda: _("Nutanix Cluster CPU utilization"),
    )
)