#!/usr/bin/env python3
"""rule for discovery of ethernet interfaces"""
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    ServiceState,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    DiscoveryParameters,
    HostAndItemCondition,
    Topic,
)


def _form_discovery_redfish_ethernetinterfaces() -> Dictionary:
    return Dictionary(
        title=Title("Redfish physical port discovery"),
        elements={
            "state": DictElement(
                parameter_form=SingleChoice(
                    title=Title("Discovery settings for physical ports"),
                    help_text=Help("Specify if port state UP, DOWN or booth should be discovered"),
                    elements=[
                        SingleChoiceElement(name="up", title=Title("Up only")),
                        SingleChoiceElement(name="down", title=Title("Down only")),
                        SingleChoiceElement(name="updown", title=Title("Up & Down")),
                    ],
                ),
            ),
        },
    )


rule_spec_discovery_redfish_ethernetinterfaces = DiscoveryParameters(
    title=Title("Redfish Ethernet Interface discovery"),
    topic=Topic.SERVER_HARDWARE,
    name="discovery_redfish_ethernetinterfaces",
    parameter_form=_form_discovery_redfish_ethernetinterfaces,
)


def _form_redfish_ethernetinterfaces() -> Dictionary:
    return Dictionary(
        elements={
            "state_if_link_status_changed": DictElement(
                parameter_form=ServiceState(
                    title=Title("Discover Link Status"),
                    help_text=Help("Specify the link status to discover"),
                    prefill=DefaultValue(ServiceState.CRIT),
                )
            ),
            "state_if_link_speed_changed": DictElement(
                parameter_form=ServiceState(
                    title=Title("State if Link Speed Changed"),
                    help_text=Help("Specify the state if link speed changed"),
                    prefill=DefaultValue(ServiceState.WARN),
                )
            ),
            "discover_speed": DictElement(
                render_only=True,
                parameter_form=Integer(
                    title=Title("Discover Link Speed"),
                    help_text=Help("Specify the link speed to discover in Mbps"),
                ),
            ),
            "discover_link_status": DictElement(
                render_only=True,
                parameter_form=String(
                    title=Title("Discover Link Status"),
                    help_text=Help("Specify the link status to discover"),
                ),
            ),
        }
    )


rule_spec_redfish_ethernetinterfaces = CheckParameters(
    name="check_redfish_ethernetinterfaces",
    topic=Topic.SERVER_HARDWARE,
    parameter_form=_form_redfish_ethernetinterfaces,
    title=Title("Redfish Ethernet Interface"),
    condition=HostAndItemCondition(item_title=Title("Physical port")),
)
