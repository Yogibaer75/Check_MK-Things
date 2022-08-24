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
from cmk.gui.plugins.wato import (
    IndividualOrStoredPassword,
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    Transform,
)


def _valuespec_special_agents_ilo():
    return Transform(
        Dictionary(
            title=_("Agent HPE iLO Configuration"),
            elements=[
                ("user", TextAscii(
                    title=_("Username"),
                    allow_empty=False,
                )),
                ("password",
                 IndividualOrStoredPassword(
                     title=_("Password"),
                     allow_empty=False,
                 )),
            ],
        ), )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:ilo",
        title=lambda: _("Agent HPE iLO Configuration"),
        valuespec=_valuespec_special_agents_ilo,
    ))
