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
from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    ListOf,
    Tuple,
    TextAscii,
)

from cmk.gui.plugins.wato.utils import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersOperatingSystem,
)


def _parameter_valuespec_win_firewall_status():
    return Dictionary(
        title=_('Time left for installed certificates before renew.'),
        elements=[
            ("profiles",
             ListOf(
                 Tuple(elements=[
                     TextAscii(
                         title=_("Profile name"),
                         help=_("Name of the firewall profile."),
                     ),
                     DropdownChoice(
                         title=_("State"),
                         help=_("Profile state active or inaktive"),
                         choices=[
                             ("True", _("Enabled")),
                             ("False", _("Disabled")),
                         ],
                     ),
                     DropdownChoice(
                         title=_("Incomming Action"),
                         help=_("Default behaviour for incomming traffic."),
                         choices=[
                             ("Block", _("Block")),
                             ("Allow", _("Allow")),
                         ],
                     ),
                     DropdownChoice(
                         title=_("Outgoing Action"),
                         help=_("Default behaviour for outgoing traffic."),
                         choices=[
                             ("Block", _("Block")),
                             ("Allow", _("Allow")),
                         ],
                     ),
                 ], ),
                 title=_("Firewall Profile configuration"),
                 help=_("Please select the abropriate profile configuration."),
                 allow_empty=False,
                 default_value=[
                     ("Domain", "True", "Block", "Allow"),
                     ("Private", "True", "Block", "Allow"),
                     ("Public", "True", "Block", "Allow"),
                 ],
             )),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="win_firewall_status",
        group=RulespecGroupCheckParametersOperatingSystem,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_win_firewall_status,
        title=lambda: _("Windows Firewall Status"),
    ))
