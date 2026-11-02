#!/usr/bin/env python3
# Copyright (C) 2023 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.
from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    InputHint,
    Integer,
    Password,
    ServiceState,
    String,
    TimeMagnitude,
    TimeSpan,
    migrate_to_password,
)
from cmk.rulesets.v1.form_specs.validators import LengthInRange, NetworkPort
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic

# mypy: disable-error-code="type-arg"


def _logwatch_levels() -> Dictionary:
    return Dictionary(
        title=Title("State mapping for alerts"),
        help_text=Help(
            "Every new alert is written as one logwatch message. Here you can set "
            "the logwatch state of the message depending on the alert severity."
        ),
        elements={
            "state_info": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'INFO' alerts"),
                    prefill=DefaultValue(ServiceState.OK),
                ),
            ),
            "state_warning": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'WARNING' alerts"),
                    prefill=DefaultValue(ServiceState.WARN),
                ),
            ),
            "state_critical": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for 'CRITICAL' alerts"),
                    prefill=DefaultValue(ServiceState.CRIT),
                ),
            ),
            "state_fallback": DictElement(
                parameter_form=ServiceState(
                    title=Title("State for alerts with any other severity"),
                    prefill=DefaultValue(ServiceState.UNKNOWN),
                ),
            ),
        },
    )


def _alert_output() -> CascadingSingleChoice:
    return CascadingSingleChoice(
        title=Title("Output of the alerts"),
        help_text=Help(
            "By default all unresolved alerts are shown in one service on the "
            "monitored host. Alternatively the alerts can be written as logwatch "
            "logfile 'Nutanix Prism Alerts'. Then only the alerts created since the "
            "last agent run are sent, so they can be handled by logwatch or forwarded "
            "to the Event Console."
        ),
        elements=(
            CascadingSingleChoiceElement(
                name="service",
                title=Title("Single alert service (default)"),
                parameter_form=FixedValue(value=None),
            ),
            CascadingSingleChoiceElement(
                name="logwatch",
                title=Title("Logwatch logfile"),
                parameter_form=_logwatch_levels(),
            ),
            CascadingSingleChoiceElement(
                name="both",
                title=Title("Single alert service and logwatch logfile"),
                parameter_form=_logwatch_levels(),
            ),
        ),
        prefill=DefaultValue("service"),
    )


def _form_spec() -> Dictionary:
    def _pre_24_to_formspec_migration(values: object) -> dict:
        assert isinstance(values, dict)
        if "no_cert_check" not in values:
            values["no_cert_check"] = False
        return values

    return Dictionary(
        help_text=Help(
            "Note: Simultaneous monitoring of both Nutanix Prism Element "
            "and Nutanix Prism Central is not supported. "
            "Doing so may cause conflicting piggyback data."
        ),
        migrate=_pre_24_to_formspec_migration,
        elements={
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("TCP port for connection"),
                    custom_validate=(NetworkPort(),),
                    prefill=DefaultValue(9440),
                ),
                required=False,
            ),
            "username": DictElement(
                parameter_form=String(title=Title("User ID for web login")),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password of the user"),
                    custom_validate=(LengthInRange(min_value=1),),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
            "no_cert_check": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Skip TLS certificate verification"),
                    prefill=DefaultValue(False),
                ),
                required=True,
            ),
            "timeout": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Connection timeout"),
                    displayed_magnitudes=(TimeMagnitude.SECOND,),
                    prefill=InputHint(10.0),
                ),
            ),
            "alert_output": DictElement(
                parameter_form=_alert_output(),
            ),
        },
    )


rule_spec_special_agent_prism_v4 = SpecialAgent(
    topic=Topic.OPERATING_SYSTEM,
    name="prism_v4",
    title=Title("Nutanix Prism Central"),
    parameter_form=_form_spec,
)
