#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.valuespec import Dictionary, FixedValue, Alternative, MonitoringState, TextAscii, DropdownChoice, ListOf, Tuple

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)


def _parameter_valuespec_hyperv_vm_integration():
    return Dictionary(
        title=_("HyperV Integration Services Status"),
        elements = [
            ( "default_status", DropdownChoice(
                    choices=[
                        ("active", _("active")),
                        ("inactive", _("inactive")),
                    ],
                title=_("Default State"),),
            ),
            ( "match_services",
                ListOf(
                    Tuple(
                        elements = [
                            TextAscii(title=_("Service name")),
                            DropdownChoice(
                                choices=[
                                    ("active", _("active")),
                                    ("inactive", _("inactive")),
                                ],
                            title=_("State"),),
                        ]),
                title=_("Special States"),),
            ),
        ],
        help=_('This defines the status of the integration services'),
        optional_keys=[],
    )


def _item_spec_hyperv_vm_integration():
    return TextAscii(
        title=_("Name of the VM"),
        help=_("Specify the name of the VM, for example z4065012."),
        allow_empty=False,
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="hyperv_vm_integration",
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_hyperv_vm_integration,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_hyperv_vm_integration,
        title=lambda: _("HyperV Integration Services Status"),
    ))

