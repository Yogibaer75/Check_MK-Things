#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import (
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

metric_info["input_voltage"] = {
    "title": _("Electical input voltage"),
    "unit": "v",
    "color": "24/a",
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
