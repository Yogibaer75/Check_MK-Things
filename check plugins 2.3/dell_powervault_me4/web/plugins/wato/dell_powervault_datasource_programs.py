#!/usr/bin/env python3
"""Dell ME4 datasource program settings"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
)

from cmk.gui.watolib.rulespecs import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.wato import (
    MigrateToIndividualOrStoredPassword,
    RulespecGroupDatasourceProgramsHardware,
)


def _valuespec_special_agents_dellpowervault():
    return Dictionary(
        title=_("Dell Powervault M4 storage system"),
        elements=[
            (
                "user",
                TextAscii(
                    title=_("Username"),
                    allow_empty=False,
                ),
            ),
            (
                "password",
                MigrateToIndividualOrStoredPassword(
                    title=_("Password"),
                    allow_empty=False,
                ),
            ),
        ],
        optional_keys=False,
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:dellpowervault",
        valuespec=_valuespec_special_agents_dellpowervault,
    )
)
