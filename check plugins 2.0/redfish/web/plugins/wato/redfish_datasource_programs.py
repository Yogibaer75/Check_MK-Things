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
    TextAscii,
    Password,
    ListChoice,
    Integer,
    DropdownChoice,
)

from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)

from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsHardware


def _valuespec_special_agents_redfish():
    return Dictionary(
        title=_("Redfish Compatible Management Controller"),
        help=_(
            "This rule selects the Agent Redfish instead of the normal Check_MK Agent "
            "which collects the data through the Redfish REST API"),
        elements=[
            ('user', TextAscii(
                title=_('Username'),
                allow_empty=False,
            )),
            ('password', Password(
                title=_("Password"),
                allow_empty=False,
            )),
            ("sections", ListChoice(
                title = _("Retrieve information about..."),
                choices = [
                    ("Memory", _("Memory Modules")),
                    ("Power", _("Powers Supply")),
                    ("Processors", _("CPUs")),
                    ("Thermal", _("Fan and Temperatures")),
                    ("FirmwareInventory", _("Firmware Versions")),
                    ("NetworkAdapters", _("Network Cards")),
                    ("NetworkInterfaces", _("Network Interfaces 1")),
                    ("EthernetInterfaces", _("Network Interfaces 2")),
                    ("Storage", _("Storage")),
                    ("ArrayControllers", _("Array Controllers")),
                    ("SmartStorage", _("HPE Storagesubsystem")),
                    ("HostBusAdapters", _("Hostbustadapters")),
                    ("PhysicalDrives", _("Physical Drives")),
                    ("LogicalDrives", _("Logical Drives")),
                ],
                default_value = [
                    "Memory",
                    "Power",
                    "Processors",
                    "Thermal",
                    "FirmwareInventory",
                    "NetworkAdapters",
                    "NetworkInterfaces",
                    "EthernetInterfaces",
                    "Storage",
                    "ArrayControllers",
                    "SmartStorage",
                    "HostBusAdapters",
                    "PhysicalDrives",
                    "LogicalDrives",
                ],
                allow_empty = False,
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
        ],
        optional_keys=["port", "proto", "sections"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:redfish",
        valuespec=_valuespec_special_agents_redfish,
    ))
