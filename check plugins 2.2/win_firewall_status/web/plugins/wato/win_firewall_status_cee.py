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
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import (
    RulespecGroupMonitoringAgentsWindowsAgent,
)
from cmk.gui.valuespec import (
    DropdownChoice,
)


def _valuespec_agent_config_win_firewall_status():
    return DropdownChoice(
        title=_("Windows Firewall Status (Windows)"),
        help=_(
            "This will deploy the agent plugin <tt>win_firewall_status.ps1</tt> to check the Windows firewall state."
        ),
        choices=[
            (True, _("Deploy plugin for Windows firewall")),
            (None, _("Do not deploy plugin for Windows firewall")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsWindowsAgent,
        name="agent_config:win_firewall_status",
        valuespec=_valuespec_agent_config_win_firewall_status,
    )
)
