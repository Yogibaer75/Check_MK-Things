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
    DropdownChoice,
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


def _valuespec_agent_config_win_hyperv_cluster():
    return DropdownChoice(
        title=_("Hyper-V Cluster (Windows)"),
        help=_("This plugin monitors HyperV Clusters"),
        choices=[
            (True, _("Deploy plugin for Hyper-V Clusters")),
            (None, _("Do not deploy plugin for Hyper-V Clusters")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsOwnAgentPlugins,
        name="agent_config:win_hyperv_cluster",
        valuespec=_valuespec_agent_config_win_hyperv_cluster,
    ))


def _valuespec_agent_config_win_hyperv_host():
    return DropdownChoice(
        title=_("Hyper-V Hosts (Windows)"),
        help=_("This plugin monitors HyperV Hosts"),
        choices=[
            (True, _("Deploy plugin for Hyper-V Hosts")),
            (None, _("Do not deploy plugin for Hyper-V Hosts")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsOwnAgentPlugins,
        name="agent_config:win_hyperv_host",
        valuespec=_valuespec_agent_config_win_hyperv_host,
    ))


def _valuespec_agent_config_win_hyperv_csv_io():
    return DropdownChoice(
        title=_("Hyper-V CSV I/O (Windows)"),
        help=_("This plugin monitors HyperV CSV I/O"),
        choices=[
            (True, _("Deploy plugin for Hyper-V CSV I/O")),
            (None, _("Do not deploy plugin for Hyper-V CSV I/O")),
        ],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsOwnAgentPlugins,
        name="agent_config:win_hyperv_csv_io",
        valuespec=_valuespec_agent_config_win_hyperv_csv_io,
    ))

