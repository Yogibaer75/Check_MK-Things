#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    TextAscii,
    Checkbox,
    ListChoice,
    Transform,
)

from cmk.gui.plugins.wato.utils import (
    HostRulespec,
    rulespec_registry,
)

from cmk.gui.plugins.wato.special_agents.common import (
    RulespecGroupDatasourceProgramsHardware,
)


def _valuespec_special_agents_3par_ssh():
    return Dictionary(
        title=_("HPE 3par with SSH"),
        help=_(
            "This rule set selects the <tt>3par</tt> agent instead of the normal Check_MK Agent "
            "and allows monitoring of HPE 3par storage systems by calling "
            "show* commands there over SSH. "
            "Make sure you have SSH key authentication enabled for your monitoring user. "
            "That means: The user your monitoring is running under on the monitoring "
            "system must be able to ssh to the storage system as the user you gave below "
            "without password."
        ),
        elements=[
            (
                "user",
                TextAscii(
                    title=_("HPE 3par user name"),
                    allow_empty=True,
                    help=_(
                        "User name on the storage system. Read only permissions are sufficient."
                    ),
                ),
            ),
            (
                "accept-any-hostkey",
                Checkbox(
                    title=_("Accept any SSH Host Key"),
                    label=_("Accept any SSH Host Key"),
                    default_value=False,
                    help=_(
                        "Accepts any SSH Host Key presented by the storage device. "
                        "Please note: This might be a security issue because man-in-the-middle "
                        "attacks are not recognized! Better solution would be to add the "
                        "SSH Host Key of the monitored storage devices to the .ssh/known_hosts "
                        "file for the user your monitoring is running under (on OMD: the site user)"
                    ),
                ),
            ),
            (
                "infos",
                Transform(
                    ListChoice(
                        choices=[
                            ("showcage", _("Hosts Connected")),
                            ("showpd", _("Licensing Status")),
                            ("showld", _("MDisks")),
                            ("showvv", _("MDisksGrps")),
                            ("showps", _("IO Groups")),
                            ("shownode", _("Node Stats")),
                        ],
                        default_value=[
                            "showcage",
                            "showpd",
                            "showld",
                            "showvv",
                            "showps",
                            "shownode",
                        ],
                        allow_empty=False,
                    ),
                    title=_("Retrieve information about..."),
                ),
            ),
        ],
        optional_keys=["infos", "accept-any-hostkey"],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsHardware,
        name="special_agents:3par_ssh",
        valuespec=_valuespec_special_agents_3par_ssh,
    )
)
