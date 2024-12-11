#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
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
                    help_text=Help(
                        "Specify if port state UP, DOWN or booth should be discovered"
                    ),
                    elements=[
                        form_specs.SingleChoiceElement(
                            name="up", title=Title("Up only")
                        ),
                        form_specs.SingleChoiceElement(
                            name="down", title=Title("Down only")
                        ),
                        form_specs.SingleChoiceElement(
                            name="updown", title=Title("Up & Down")
                        ),
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