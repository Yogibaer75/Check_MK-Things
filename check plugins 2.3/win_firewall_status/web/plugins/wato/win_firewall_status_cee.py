#!/usr/bin/env python3
"""Ruleset definition for Windows firewall plugin deployment"""

# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

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
            "This will deploy the agent plugin <tt>win_firewall_status.ps1</tt> "
            "to check the Windows firewall state."
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
