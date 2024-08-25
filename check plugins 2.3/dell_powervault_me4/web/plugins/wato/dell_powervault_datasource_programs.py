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
from cmk.gui.plugins.wato.special_agents.common_tls_verification import (
    tls_verify_flag_default_no,
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
            tls_verify_flag_default_no(),
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
