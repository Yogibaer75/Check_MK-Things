#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.graphing.v1 import Color, Localizable, metrics, Unit

metric_input_power = metrics.Metric(
    name="input_power",
    title=Localizable("Electrical input power"),
    unit=Unit.WATT,
    color=Color.BROWN,
)

metric_output_power = metrics.Metric(
    name="output_power",
    title=Localizable("Electrical output power"),
    unit=Unit.WATT,
    color=Color.BLUE,
)

metric_input_voltage = metrics.Metric(
    name="input_voltage",
    title=Localizable("Electrical input voltage"),
    unit=Unit.VOLT,
    color=Color.GREEN,
)
