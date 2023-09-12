#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithoutItem,
    rulespec_registry,
    RulespecGroupCheckParametersVirtualization,
)
from cmk.gui.valuespec import Dictionary, DropdownChoice


def _parameter_valuespec_prism_vm_tools():
    return Dictionary(
        elements=[
            (
                "tools_install",
                DropdownChoice(
                    title=_("Tools install state"),
                    choices=[
                        ("installed", _("installed")),
                        ("not_installed", _("not installed")),
                        ("ignored", _("ignored")),
                    ],
                    default_value="installed",
                ),
            ),
            (
                "tools_enabled",
                DropdownChoice(
                    title=_("VMTools activation state"),
                    choices=[
                        ("enabled", _("enabled")),
                        ("disabled", _("disabled")),
                        ("irngored", _("ignored")),
                    ],
                    default_value="enabled",
                ),
            ),
        ],
        title=_("Wanted VM State for defined Nutanix VMs"),
    )


rulespec_registry.register(
    CheckParameterRulespecWithoutItem(
        check_group_name="prism_vm_tools",
        group=RulespecGroupCheckParametersVirtualization,
        match_type="dict",
        parameter_valuespec=_parameter_valuespec_prism_vm_tools,
        title=lambda: _("Nutanix Prism VM Tools"),
    )
)
