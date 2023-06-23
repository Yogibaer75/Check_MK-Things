#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

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
from cmk.gui.plugins.metrics.utils import (
    metric_info,
    perfometer_info,
)


metric_info["input_power"] = {
    "title": _("Electrical input power"),
    "unit": "w",
    "color": "22/a",
}

metric_info["output_power"] = {
    "title": _("Electrical output power"),
    "unit": "w",
    "color": "22/b",
}

perfometer_info.append({
    "type": "stacked",
    "perfometers": [
        {
            "type": "logarithmic",
            "metric": "input_power",
            "half_value": 1000,
            "exponent": 2,
        },
        {
            "type": "logarithmic",
            "metric": "output_power",
            "half_value": 1000,
            "exponent": 2,
        },
    ],
})
