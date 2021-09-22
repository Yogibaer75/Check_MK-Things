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
    Tuple,
    Integer,
)

from cmk.gui.plugins.wato import (
    rulespec_registry,
    CheckParameterRulespecWithoutItem,
    RulespecGroupCheckParametersOperatingSystem,
)


def _parameter_valuespec_windows_patch_day():
    return Dictionary(
        title=_('Time since last install of updates.'),
        elements=[
            ('levels',
             Tuple(
                 title=_('Days since update'),
                 elements=[
                     Integer(title=_("Warning at"),
                             unit=u"days",
                             default_value=30),
                     Integer(title=_("Critical at"),
                             unit=u"days",
                             default_value=15),
                 ],
             )),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="windows_patch_day",
        group=RulespecGroupCheckParametersOperatingSystem,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_windows_patch_day,
        title=lambda: _("Windows Patch Day"),
    ))
