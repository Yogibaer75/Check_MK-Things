#!/usr/bin/env python3
'''ruleset for macmon special agent'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.watolib.rulespecs import (
    HostRulespec,
    rulespec_registry,
)

from cmk.gui.valuespec import (
    Integer,
    TextAscii,
    Password,
    Dictionary,
)

from cmk.gui.wato import (
    RulespecGroupDatasourceProgramsApps
)


def _valuespec_special_agents_macmon():
    return Dictionary(
        title=_("Macmon"),
        elements=[
            ("port",
             Integer(title=_("TCP port for connection"),
                     default_value=443,
                     minvalue=1,
                     maxvalue=65535)),
            ("username", TextAscii(title=_("User ID for web login"),)),
            ("password", Password(title=_("Password for this user"))),
        ],
        optional_keys=["port"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsApps,
        name="special_agents:macmon",
        valuespec=_valuespec_special_agents_macmon,
    ))
