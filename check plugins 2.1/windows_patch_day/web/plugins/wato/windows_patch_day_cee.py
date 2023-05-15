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
from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsWindowsAgent
from cmk.gui.valuespec import Alternative, Dictionary, FixedValue, Integer, ListOfStrings


def _valuespec_agent_config_windows_patch_day():
    return Alternative(
        title=_("Windows Patch Day (Windows)"),
        help=
        _("This will deploy the agent plugin <tt>windows_patch_day.ps1</tt> to check the Windows update installation time."
          "As option you can set the maximum amount of updates in history that should be transfered. It is also possible to"
          "filter unwanted update entries like the daily Windows Defender Pattern updates."
          ),
        elements=[
            Dictionary(
                title=_("Deploy plugin for Windows patch day"),
                elements=[
                    ("updatecount",
                     Integer(
                         title=_("Update history count"),
                         unit=_("Updates"),
                         default_value=40,
                     )),
                    ("filterstring",
                     ListOfStrings(
                         title=_("Unwanted updates (Regular Expressions)"),
                         help=
                         _('Regular expressions matching the begining of the installed update name.'
                           ),
                         orientation="horizontal",
                         default_value=[
                             "Security Intelligence-Update für Microsoft Defender Antivirus",
                             "Update für Microsoft Defender Antivirus-Antischadsoftwareplattform",
                             "Windows-Tool zum Entfernen bösartiger Software"
                         ],
                     )),
                ],
                optional_keys=False,
            ),
            FixedValue(None,
                       title=_("Do not deploy the Windows Patch day plugin"),
                       totext=_("(disabled)")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsWindowsAgent,
        name="agent_config:windows_patch_day",
        valuespec=_valuespec_agent_config_windows_patch_day,
    ))
