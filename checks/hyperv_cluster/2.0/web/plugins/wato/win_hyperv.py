#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    RulespecSubGroup,
    rulespec_registry,
    rulespec_group_registry,
)
from cmk.gui.plugins.wato.check_mk_configuration import (
    RulespecGroupMonitoringAgents,)
from cmk.gui.valuespec import (
    Alternative,
    Dictionary,
    FixedValue,
    TextAscii,
)


@rulespec_group_registry.register
class RulespecGroupMonitoringAgentsOwnAgentPlugins(RulespecSubGroup):
    @property
    def main_group(self):
        return RulespecGroupMonitoringAgents

    @property
    def sub_group_name(self):
        return "own_agent_plugins"

    @property
    def title(self):
        return _("Own Agent Plugins")


def _valuespec_agent_config_win_hyperv():
    return Alternative(
        title=_("HyperV Cluster (Windows)"),
        help=_("This plugin monitors HyperV Clusters"),
        elements=[
            Dictionary(
                title=_("Deploy HyperV Cluster plugin"),
                elements=[
                    ("clustername",
                     TextAscii(
                         title=_("HyperV Cluster to connect to"),
                         help=_("Put the name of the cluster here, e.g. cluster1"),
                         allow_empty=False,
                         regex=r"^[A-Za-z0-9_\\]+$",
                         regex_error=_("You have used an invalid character"),
                     )),
                ],
                optional_keys=False,
            ),
            FixedValue(None, title=_("Do not deploy the HyperV Cluster plugin"), totext=_("(disabled)")),
        ],
        default_value={"clustername": r"cluster1"},
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsOwnAgentPlugins,
        name="agent_config:win_hyperv",
        valuespec=_valuespec_agent_config_win_hyperv,
    ))

