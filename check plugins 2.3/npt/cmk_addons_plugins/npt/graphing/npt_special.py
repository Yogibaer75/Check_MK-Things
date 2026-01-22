#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.graphing.v1 import translations, metrics, graphs, Title

translation_npt_ehtif = translations.Translation(
    name="npt_ehtif",
    check_commands=[
        translations.PassiveCheck("npt_ehtif"),
    ],
    translations={
        "in": translations.RenameToAndScaleBy(
            "if_in_bps",
            8,
        ),
        "out": translations.RenameToAndScaleBy(
            "if_out_bps",
            8,
        ),
    },
)

metric_in_avg_15 = metrics.Metric(
    name="in_avg_15",
    title=Title("Input bandwidth average"),
    unit=metrics.Unit(metrics.DecimalNotation("bytes/s")),
    color=metrics.Color.GREEN,
)

metric_out_avg_15 = metrics.Metric(
    name="out_avg_15",
    title=Title("Output bandwidth average"),
    unit=metrics.Unit(metrics.DecimalNotation("bytes/s")),
    color=metrics.Color.CYAN,
)

graph_bandwidth_cummulative = graphs.Bidirectional(
    name="bandwidth_average",
    title=Title("Bandwidth average"),
    lower=graphs.Graph(
        name="lower",
        title=Title("Outgoing traffic"),
        compound_lines=["out_avg_15"],
    ),
    upper=graphs.Graph(
        name="upper",
        title=Title("Incoming traffic"),
        compound_lines=["in_avg_15"],
    ),
)

#
# graph Metrics muessen noch mit 8 multipliziert werden fuer bits pro sekunde
#
