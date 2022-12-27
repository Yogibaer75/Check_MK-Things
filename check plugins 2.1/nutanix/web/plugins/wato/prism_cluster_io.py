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
from cmk.gui.valuespec import Dictionary, Float, Integer, Tuple


def _parameter_valuespec_prism_cluster_io() -> Dictionary:
    return Dictionary(
        elements=[
            (
                "io",
                Tuple(
                    elements=[
                        Float(title=_("Warning at"), unit=_("MB/s"), default_value=500.0),
                        Float(title=_("Critical at"), unit=_("MB/s"), default_value=1000.0),
                    ],
                    title=_("Levels for IO traffic per second."),
                ),
            ),
            (
                "iops",
                Tuple(
                    elements=[
                        Integer(title=_("Warning at"), unit=_("iops"), default_value=10000),
                        Integer(title=_("Critical at"), unit=_("iops"), default_value=20000),
                    ],
                    title=_("Levels for IO operations per second."),
                ),
            ),
            (
                "iolat",
                Tuple(
                    elements=[
                        Float(title=_("Warning at"), unit=_("ms"), default_value=500.0),
                        Float(title=_("Critical at"), unit=_("ms"), default_value=1000.0),
                    ],
                    title=_("Levels for IO latency."),
                ),
            ),
        ]
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="prism_cluster_io",
        group=RulespecGroupCheckParametersVirtualization,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_prism_cluster_io,
        title=lambda: _("Nutanix Cluster IO utilization"),
    )
)