#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.special_agents.common import (
    RulespecGroupDatasourceProgramsHardware,
)
from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import Dictionary, DropdownChoice, Integer, ListChoice, TextAscii


def _valuespec_special_agents_redfish():
    return Dictionary(
        title=_("Redfish Compatible Management Controller"),
        help=_(
            "This rule selects the Agent Redfish instead of the normal Check_MK Agent "
            "which collects the data through the Redfish REST API"
        ),
        elements=[
            (
                "user",
                TextAscii(
                    title=_("Username"),
                    allow_empty=False,
                ),
            ),
            (
                "password",
                IndividualOrStoredPassword(
                    title=_("Password"),
                    allow_empty=False,
                ),
            ),
            (
                "sections",
                ListChoice(
                    title=_("Retrieve information about..."),
                    choices=[
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
                        ("SmartStorage", _("HPE - Storagesubsystem")),
                        ("HostBusAdapters", _("Hostbustadapters")),
                        ("PhysicalDrives", _("iLO5 - Physical Drives")),
                        ("LogicalDrives", _("iLO5 - Logical Drives")),
                        ("Drives", _("Drives")),
                        ("Volumes", _("Volumes")),
                        ("SimpleStorage", _("Simple Storage Collection (tbd)")),
                    ],
                    default_value=[
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
                        "Drives",
                        "Volumes",
                        "SimpleStorage",
                    ],
                    allow_empty=False,
                ),
            ),
            (
                "port",
                Integer(
                    title=_("Advanced - TCP Port number"),
                    help=_(
                        "Port number for connection to the Rest API. Usually 8443 (TLS)"
                    ),
                    default_value=443,
                    minvalue=1,
                    maxvalue=65535,
                ),
            ),
            (
                "proto",
                DropdownChoice(
                    title=_("Advanced - Protocol"),
                    default_value="https",
                    help=_(
                        "Protocol for the connection to the Rest API. https is highly recommended!!!"
                    ),
                    choices=[
                        ("http", _("http")),
                        ("https", _("https")),
                    ],
                ),
            ),
            (
                "retries",
                Integer(
                    title=_("Advanced - Number of retries"),
                    help=_("Number of retry attempts made by the special agent."),
                    default_value=10,
                    minvalue=1,
                    maxvalue=20,
                ),
            ),
            (
                "timeout",
                Integer(
                    title=_("Advanced - Timeout for connection"),
                    help=_(
                        "Number of seconds for a single connection attempt before timeout occurs."
                    ),
                    default_value=10,
                    minvalue=1,
                    maxvalue=20,
                ),
            ),
        ],
        optional_keys=["port", "proto", "sections", "retries", "timeout"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:redfish",
        valuespec=_valuespec_special_agents_redfish,
    )
)
