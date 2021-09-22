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
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsWindowsAgent
from cmk.gui.valuespec import Alternative, Dictionary, FixedValue, Integer, TextAscii


def _valuespec_agent_config_win_cert():
    return Alternative(
        title=_("Windows System Certificates (Windows)"),
        help=
        _("This will deploy the agent plugin <tt>win_cert.ps1</tt> to check the Windows system certificates."
          "As option you can set the minimum age a certificate needs to be included in the output and"
          "you can filter the certificate authority."),
        elements=[
            Dictionary(
                title=_("Deploy plugin for system certificates"),
                elements=[
                    ("valid",
                     Integer(
                         title=_("Minimum certificate validity"),
                         unit=_("Days"),
                         default_value=30,
                     )),
                    ("auth",
                     TextAscii(
                         title=_("Certificate Authority to filter for"),
                         allow_empty=False,
                         default_value=".*",
                     )),
                ],
                optional_keys=False,
            ),
            FixedValue(None,
                       title=_("Do not deploy the plugin system certificates"),
                       totext=_("(disabled)")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsWindowsAgent,
        name="agent_config:win_cert",
        valuespec=_valuespec_agent_config_win_cert,
    ))
