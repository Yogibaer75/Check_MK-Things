#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.plugins.wato import (
    IndividualOrStoredPassword,
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.plugins.wato.datasource_programs import (
    RulespecGroupDatasourcePrograms,
)
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    Transform,
)

def _valuespec_special_agents_ilo():
    return Transform(
        Dictionary(
            title=_("Agent HPE iLO Configuration"),
            elements=[
                ("user", TextAscii(
                    title=_("Username"),
                    allow_empty=False,
                )),
                ("password", IndividualOrStoredPassword(
                    title=_("Password"),
                    allow_empty=False,
                )),
            ],
        ),
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourcePrograms,
        name="special_agents:ilo",
        title=lambda: _("Agent HPE iLO Configuration"),
        valuespec=_valuespec_special_agents_ilo,
    ))

