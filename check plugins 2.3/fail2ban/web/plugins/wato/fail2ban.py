# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# (c) Jens Kühnel <fail2ban-checkmk@jens.kuehnel.org> 2021
#
# Information about fail2ban check_mk module see:
# https://github.com/JensKuehnel/fail2ban-check-mk
#
# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.i18n import _

from cmk.gui.valuespec import (
    Dictionary,
    Integer,
    TextAscii,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersOperatingSystem,
)


def _item_valuespec_fail2ban():
    return TextAscii(title=_("Jail name"))


def _parameter_valuespec_fail2ban():
    return Dictionary(elements=[
         ("banned",
             Tuple(
                 title=_("Number of banned IPs"),
                 help=_("This number of IPs have failed multiple times and "
                        "are banned of a configure amount of times."),
                 elements=[
                     Integer(title=_("Warning at")),
                     Integer(title=_("Critical at")),
                 ],
             )),
         ("failed",
             Tuple(
                 title=_("Number of failed IPs"),
                 help=_("This number of IPs have failed logins. "
                        "If this happens multiple times they will be banned."),
                 elements=[
                     Integer(title=_("Warning at")),
                     Integer(title=_("Critical at")),
                 ],
             )),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="fail2ban",
        group=RulespecGroupCheckParametersOperatingSystem,
        match_type="dict",
        item_spec=_item_valuespec_fail2ban,
        parameter_valuespec=_parameter_valuespec_fail2ban,
        title=lambda: _("Number of fail2ban Banned/Failed IPs"),
    ))

