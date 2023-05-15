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
    Integer,
    TextAscii,
)

from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)

from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware


def _valuespec_special_agents_dell_idrac():
    return Dictionary(
        title=_("Dell iDRAC Management Controller"),
        help=_(
            "This rule selects the Agent Dell iDRAC instead of the normal Check_MK Agent "
            "which collects the data through the Redfish REST API"),
        elements=[
            ('user', TextAscii(
                title=_('Username'),
                allow_empty=False,
            )),
            ('password', IndividualOrStoredPassword(
                title=_("Password"),
                allow_empty=False,
            )),
            ("port", Integer(
                title = _("Advanced - TCP Port number"),
                help = _("Port number for connection to the Rest API. Usually 8443 (TLS)"),
                default_value = 443,
                minvalue = 1,
                maxvalue = 65535,
            )),
            ("proto", DropdownChoice(
                title = _("Advanced - Protocol"),
                default_value = 'https',
                help = _("Protocol for the connection to the Rest API. https is highly recommended!!!"),
                choices = [
                    ('http', _("http")),
                    ('https', _("https")),
                ],
            )),
            ("retries", Integer(
                title = _("Advanced - Number of retries"),
                help = _("Number of retry attempts made by the special agent."),
                default_value = 3,
                minvalue = 1,
                maxvalue = 20,
            )),
            ("timeout", Integer(
                title = _("Advanced - Timeout for connection"),
                help = _("Number of seconds for a single connection attempt before timeout occurs."),
                default_value = 5,
                minvalue = 1,
                maxvalue = 20,
            )),
        ],
        optional_keys=["port", "proto", "retries", "timeout"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:dell_idrac",
        valuespec=_valuespec_special_agents_dell_idrac,
    ))
