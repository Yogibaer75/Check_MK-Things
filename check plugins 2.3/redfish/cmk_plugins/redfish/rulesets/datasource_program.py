#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
'''rule for assinging the special agent to host objects'''
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Localizable, validators
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    List,
    TextInput,
    Integer,
    DropdownChoice,
    DropdownChoiceElement,
)
from cmk.rulesets.v1.rule_specs import EvalType, Topic, SpecialAgent


def _valuespec_special_agents_redfish():
    return Dictionary(
        elements={
            "user": DictElement(
                parameter_form=TextInput(
                    title=Localizable("Username"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=TextInput(
                    title=Localizable("Password"),
                ),
                required=True,
            ),
            "sections": DictElement(
                parameter_form=List(
                    parameter_form=DropdownChoice(
                        title=Localizable("Select subsystem"),
                        elements=[
                            DropdownChoiceElement(
                                name="Memory", title=Localizable("Memory Modules")
                            ),
                            DropdownChoiceElement(
                                name="Power", title=Localizable("Powers Supply")
                            ),
                            DropdownChoiceElement(
                                name="Processors", title=Localizable("CPUs")
                            ),
                            DropdownChoiceElement(
                                name="Thermal", title=Localizable("Fan and Temperatures")
                            ),
                            DropdownChoiceElement(
                                name="FirmwareInventory",
                                title=Localizable("Firmware Versions"),
                            ),
                            DropdownChoiceElement(
                                name="NetworkAdapters", title=Localizable("Network Cards")
                            ),
                            DropdownChoiceElement(
                                name="NetworkInterfaces",
                                title=Localizable("Network Interfaces 1"),
                            ),
                            DropdownChoiceElement(
                                name="EthernetInterfaces",
                                title=Localizable("Network Interfaces 2"),
                            ),
                            DropdownChoiceElement(
                                name="Storage", title=Localizable("Storage")
                            ),
                            DropdownChoiceElement(
                                name="ArrayControllers",
                                title=Localizable("Array Controllers"),
                            ),
                            DropdownChoiceElement(
                                name="SmartStorage",
                                title=Localizable("HPE Storagesubsystem"),
                            ),
                            DropdownChoiceElement(
                                name="HostBusAdapters",
                                title=Localizable("Hostbustadapters"),
                            ),
                            DropdownChoiceElement(
                                name="PhysicalDrives", title=Localizable("Physical Drives")
                            ),
                            DropdownChoiceElement(
                                name="LogicalDrives", title=Localizable("Logical Drives")
                            ),
                        ],
                    ),
                    title=Localizable("Retrieve information about..."),
                    prefill_value=[
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
                ),
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - TCP Port number"),
                    help_text=Localizable(
                        "Port number for connection to the Rest API. Usually 8443 (TLS)"
                    ),
                    prefill_value=443,
                    custom_validate=validators.InRange(min_value=1, max_value=65535),
                ),
            ),
            "proto": DictElement(
                parameter_form=DropdownChoice(
                    title=Localizable("Advanced - Protocol"),
                    prefill_selection="https",
                    help_text=Localizable(
                        "Protocol for the connection to the Rest API."
                        "https is highly recommended!!!"
                    ),
                    elements=[
                        DropdownChoiceElement("http", Localizable("http")),
                        DropdownChoiceElement("https", Localizable("https")),
                    ],
                ),
            ),
            "retries": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - Number of retries"),
                    help_text=Localizable(
                        "Number of retry attempts made by the special agent."
                    ),
                    prefill_value=10,
                    custom_validate=validators.InRange(min_value=1, max_value=20),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - Timeout for connection"),
                    help_text=Localizable(
                        "Number of seconds for a single connection attempt before timeout occurs."
                    ),
                    prefill_value=10,
                    custom_validate=validators.InRange(min_value=1, max_value=20),
                ),
            ),
        },
    )


rule_spec_redfish_datasource_programs = SpecialAgent(
    name="redfish",
    title=Localizable("Redfish Compatible Management Controller"),
    topic=Topic.SERVER_HARDWARE,
    parameter_form=_valuespec_special_agents_redfish,
    eval_type=EvalType.ALL,
    help_text=(
        "This rule selects the Agent Redfish instead of the normal Check_MK Agent "
        "which collects the data through the Redfish REST API"
    ),
)
