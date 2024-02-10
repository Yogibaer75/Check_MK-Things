#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""rule for assinging the special agent to host objects"""
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Localizable, validators
from cmk.rulesets.v1.form_specs import DefaultValue
from cmk.rulesets.v1.form_specs.basic import (
    FixedValue,
    Integer,
    Text,
)
from cmk.rulesets.v1.form_specs.composed import (
    Dictionary,
    DictElement,
    MultipleChoice,
    MultipleChoiceElement,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
)
from cmk.rulesets.v1.form_specs.preconfigured import Password
from cmk.rulesets.v1.rule_specs import EvalType, Topic, SpecialAgent


def _valuespec_special_agents_redfish() -> Dictionary:
    return Dictionary(
        title=Localizable("Redfish Compatible Management Controller"),
        elements={
            "user": DictElement(
                parameter_form=Text(
                    title=Localizable("Username"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Localizable("Password"),
                ),
                required=True,
            ),
            "sections": DictElement(
                parameter_form=MultipleChoice(
                    title=Localizable("Retrieve information about..."),
                    elements=[
                        MultipleChoiceElement(
                            name="Memory", title=Localizable("Memory Modules")
                        ),
                        MultipleChoiceElement(
                            name="Power", title=Localizable("Powers Supply")
                        ),
                        MultipleChoiceElement(
                            name="Processors", title=Localizable("CPUs")
                        ),
                        MultipleChoiceElement(
                            name="Thermal", title=Localizable("Fan and Temperatures")
                        ),
                        MultipleChoiceElement(
                            name="FirmwareInventory",
                            title=Localizable("Firmware Versions"),
                        ),
                        MultipleChoiceElement(
                            name="NetworkAdapters", title=Localizable("Network Cards")
                        ),
                        MultipleChoiceElement(
                            name="NetworkInterfaces",
                            title=Localizable("Network Interfaces 1"),
                        ),
                        MultipleChoiceElement(
                            name="EthernetInterfaces",
                            title=Localizable("Network Interfaces 2"),
                        ),
                        MultipleChoiceElement(
                            name="Storage", title=Localizable("Storage")
                        ),
                        MultipleChoiceElement(
                            name="ArrayControllers",
                            title=Localizable("Array Controllers"),
                        ),
                        MultipleChoiceElement(
                            name="SmartStorage",
                            title=Localizable("HPE Storagesubsystem"),
                        ),
                        MultipleChoiceElement(
                            name="HostBusAdapters",
                            title=Localizable("Hostbustadapters"),
                        ),
                        MultipleChoiceElement(
                            name="PhysicalDrives", title=Localizable("Physical Drives")
                        ),
                        MultipleChoiceElement(
                            name="LogicalDrives", title=Localizable("Logical Drives")
                        ),
                    ],
                    prefill=DefaultValue([
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
                    ]),
                    show_toggle_all=True,
                ),
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - TCP Port number"),
                    help_text=Localizable(
                        "Port number for connection to the Rest API. Usually 8443 (TLS)"
                    ),
                    prefill=DefaultValue(443),
                    custom_validate=validators.InRange(min_value=1, max_value=65535),
                ),
            ),
            "proto": DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Localizable("Advanced - Protocol"),
                    prefill=DefaultValue("https"),
                    help_text=Localizable(
                        "Protocol for the connection to the Rest API."
                        "https is highly recommended!!!"
                    ),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="http",
                            title=Localizable("http"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="https",
                            title=Localizable("https"),
                            parameter_form=FixedValue(value=None),
                        ),
                    ],
                ),
            ),
            "retries": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - Number of retries"),
                    help_text=Localizable(
                        "Number of retry attempts made by the special agent."
                    ),
                    prefill=DefaultValue(10),
                    custom_validate=validators.InRange(min_value=1, max_value=20),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Localizable("Advanced - Timeout for connection"),
                    help_text=Localizable(
                        "Number of seconds for a single connection attempt before timeout occurs."
                    ),
                    prefill=DefaultValue(10),
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
