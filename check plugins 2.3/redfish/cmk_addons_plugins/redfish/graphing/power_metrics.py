#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.graphing.v1 import graphs, metrics, perfometers, Title

metric_averageconsumedwatts_0 = metrics.Metric(
    name="averageconsumedwatts_0",
    title=Title("Average Consumed Watts System 0"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.BLUE,
)

metric_minconsumedwatts_0 = metrics.Metric(
    name="minconsumedwatts_0",
    title=Title("Minimum Consumed Watts System 0"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.LIGHT_BLUE,
)

metric_maxconsumedwatts_0 = metrics.Metric(
    name="maxconsumedwatts_0",
    title=Title("Maximum Consumed Watts System 0"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.DARK_BLUE,
)

perfometer_averageconsumedwatts_0 = perfometers.Perfometer(
    name="averageconsumedwatts_0",
    focus_range=perfometers.FocusRange(
        perfometers.Closed(0),
        perfometers.Open(
            metrics.MaximumOf("averageconsumedwatts_0", color=metrics.Color.BLUE)
        ),
    ),
    segments=[
        "averageconsumedwatts_0",
    ],
)

graph_power_metrics_system_0 = graphs.Graph(
    name="redfish_power_metrics_system_0",
    title=Title("Redfish Power Metrics System 0"),
    simple_lines=[
        "averageconsumedwatts_0",
        "minconsumedwatts_0",
        "maxconsumedwatts_0",
    ],
)

metric_averageconsumedwatts_2 = metrics.Metric(
    name="averageconsumedwatts_2",
    title=Title("Average Consumed Watts System 2"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.BLUE,
)

metric_minconsumedwatts_2 = metrics.Metric(
    name="minconsumedwatts_2",
    title=Title("Minimum Consumed Watts System 2"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.LIGHT_BLUE,
)

metric_maxconsumedwatts_2 = metrics.Metric(
    name="maxconsumedwatts_2",
    title=Title("Maximum Consumed Watts System 2"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.DARK_BLUE,
)

metric_averageconsumedwatts_1 = metrics.Metric(
    name="averageconsumedwatts_1",
    title=Title("Average Consumed Watts System 1"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.BLUE,
)

metric_minconsumedwatts_1 = metrics.Metric(
    name="minconsumedwatts_1",
    title=Title("Minimum Consumed Watts System 1"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.LIGHT_BLUE,
)

metric_maxconsumedwatts_1 = metrics.Metric(
    name="maxconsumedwatts_1",
    title=Title("Maximum Consumed Watts System 1"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.DARK_BLUE,
)

metric_averageconsumedwatts_3 = metrics.Metric(
    name="averageconsumedwatts_3",
    title=Title("Average Consumed Watts System 3"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.BLUE,
)

metric_minconsumedwatts_3 = metrics.Metric(
    name="minconsumedwatts_3",
    title=Title("Minimum Consumed Watts System 3"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.LIGHT_BLUE,
)

metric_maxconsumedwatts_3 = metrics.Metric(
    name="maxconsumedwatts_3",
    title=Title("Maximum Consumed Watts System 3"),
    unit=metrics.Unit(metrics.DecimalNotation("W")),
    color=metrics.Color.DARK_BLUE,
)

graph_power_metrics_system_1 = graphs.Graph(
    name="redfish_power_metrics_system_1",
    title=Title("Redfish Power Metrics System 1"),
    simple_lines=[
        "averageconsumedwatts_1",
        "minconsumedwatts_1",
        "maxconsumedwatts_1",
    ],
)

graph_power_metrics_system_2 = graphs.Graph(
    name="redfish_power_metrics_system_2",
    title=Title("Redfish Power Metrics System 2"),
    simple_lines=[
        "averageconsumedwatts_2",
        "minconsumedwatts_2",
        "maxconsumedwatts_2",
    ],
)

graph_power_metrics_system_3 = graphs.Graph(
    name="redfish_power_metrics_system_3",
    title=Title("Redfish Power Metrics System 3"),
    simple_lines=[
        "averageconsumedwatts_3",
        "minconsumedwatts_3",
        "maxconsumedwatts_3",
    ],
)
