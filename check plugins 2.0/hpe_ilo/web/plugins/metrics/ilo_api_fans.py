#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

metric_info["perc"] = {
    "color": "#60f020",
    "unit": "%",
    "title": _("Percent"),
    "help": _("Generic Percent usage"),
}

perfometer_info.append({
    "type": "linear",
    "metric": "perc",
    "segments": ["perc"],
    "total": 100.0,
})