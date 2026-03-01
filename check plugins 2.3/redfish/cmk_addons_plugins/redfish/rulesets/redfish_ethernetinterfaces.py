#!/usr/bin/env python3
"""rule for discovery of ethernet interfaces"""
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.rulesets.v1 import form_specs, Help, rule_specs, Title


def _form_discovery_redfish_ethernetinterfaces() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        title=Title("Redfish physical port discovery"),
        elements={
            "state": form_specs.DictElement(
                parameter_form=form_specs.SingleChoice(
                    title=Title("Discovery settings for physical ports"),
                    help_text=Help("Specify if port state UP, DOWN or booth should be discovered"),
                    elements=[
                        form_specs.SingleChoiceElement(name="up", title=Title("Up only")),
                        form_specs.SingleChoiceElement(name="down", title=Title("Down only")),
                        form_specs.SingleChoiceElement(name="updown", title=Title("Up & Down")),
                    ],
                ),
            ),
        },
    )


rule_spec_discovery_redfish_ethernetinterfaces = rule_specs.DiscoveryParameters(
    title=Title("Redfish Ethernet Interface discovery"),
    topic=rule_specs.Topic.SERVER_HARDWARE,
    name="discovery_redfish_ethernetinterfaces",
    parameter_form=_form_discovery_redfish_ethernetinterfaces,
)


def _form_redfish_ethernetinterfaces() -> form_specs.Dictionary:
    return form_specs.Dictionary(
        elements={
            "state_if_link_status_changed": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("Monitoring state if Link Status changed"),
                    help_text=Help("Specify the monitoring state if link status changed"),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.CRIT),
                )
            ),
            "state_if_link_speed_changed": form_specs.DictElement(
                parameter_form=form_specs.ServiceState(
                    title=Title("Monitoring state if Link Speed changed"),
                    help_text=Help("Specify the monitoring state if link speed changed"),
                    prefill=form_specs.DefaultValue(form_specs.ServiceState.WARN),
                )
            ),
        },
        ignored_elements=(
            "discover_speed",
            "discover_link_status",
        ),
    )


rule_spec_redfish_ethernetinterfaces = rule_specs.CheckParameters(
    name="check_redfish_ethernetinterfaces",
    topic=rule_specs.Topic.SERVER_HARDWARE,
    parameter_form=_form_redfish_ethernetinterfaces,
    title=Title("Redfish Ethernet Interface"),
    condition=rule_specs.HostAndItemCondition(item_title=Title("Physical port")),
)
