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

from cmk.gui.plugins.metrics import (
    metric_info,
    graph_info,
)

metric_info["current_failed"] = {
    "title": _("current failed"),
    "unit": "count",
    "color": "16/a",
}

metric_info["current_banned"] = {
    "title": _("current banned "),
    "unit": "count",
    "color": "24/a",
}

metric_info["total_failed"] = {
    "title": _("toal failed"),
    "unit": "count",
    "color": "16/b",
}

metric_info["total_banned"] = {
    "title": _("total banned "),
    "unit": "count",
    "color": "24/b",
}

graph_info["current"] = {
    "metrics": [
        ("current_failed", "line"),
        ("current_banned", "line"),
    ],
}

graph_info["total"] = {
    "metrics": [
        ("total_failed", "line"),
        ("total_banned", "line"),
    ],
}

