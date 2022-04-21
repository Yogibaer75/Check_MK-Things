#!/usr/bin/env python3
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
from cmk.gui.valuespec import Dictionary, Tuple, Integer, TextAscii, DropdownChoice

from cmk.gui.plugins.wato import (
    rulespec_registry,
    CheckParameterRulespecWithItem,
    RulespecGroupCheckParametersApplications,
)


def _parameter_valuespec_arcserve_udp_jobs():
    return Dictionary(
        title=_("Arcserve UDP Job status."),
        elements=[
            (
                "levels",
                Tuple(
                    title=_("Backup age"),
                    elements=[
                        Integer(title=_("Warning at"), unit="hours", default_value=36),
                        Integer(title=_("Critical at"), unit="hours", default_value=72),
                    ],
                ),
            ),
            (
                "no_backup",
                DropdownChoice(
                    title=_("Interpretation of no existing backup"),
                    choices=[
                        (0, _("no existing backup is treated as OK")),
                        (1, _("no existing backup is treated as WARN")),
                        (2, _("no existing backup is treated as CRIT")),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="arcserve_udp_jobs",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        item_spec=lambda: TextAscii(
            title=_("Servername"),
            help=_("Name of the server object and database id combined"),
        ),
        parameter_valuespec=_parameter_valuespec_arcserve_udp_jobs,
        title=lambda: _("Arcserve UDP Jobs"),
    )
)


def _parameter_valuespec_arcserve_udp_backup():
    return Dictionary(
        title=_("Arcserve UDP host status."),
        elements=[
            (
                "levels",
                Tuple(
                    title=_("maximal amount of recovery points"),
                    elements=[
                        Integer(title=_("Warning at"), default_value=40),
                        Integer(title=_("Critical at"), default_value=60),
                    ],
                ),
            ),
            (
                "levels_lower",
                Tuple(
                    title=_("minimal amount of recovery points"),
                    elements=[
                        Integer(title=_("Warning below"), default_value=5),
                        Integer(title=_("Critical below"), default_value=1),
                    ],
                ),
            ),
            (
                "no_backup",
                DropdownChoice(
                    title=_("Interpretation of no existing backup"),
                    choices=[
                        (0, _("no existing backup is treated as OK")),
                        (1, _("no existing backup is treated as WARN")),
                        (2, _("no existing backup is treated as CRIT")),
                    ],
                ),
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="arcserve_udp_backup",
        group=RulespecGroupCheckParametersApplications,
        match_type="dict",
        item_spec=lambda: TextAscii(
            title=_("Servername"),
            help=_("Name of the server object and database id combined"),
        ),
        parameter_valuespec=_parameter_valuespec_arcserve_udp_backup,
        title=lambda: _("Arcserve UDP Backup"),
    )
)
