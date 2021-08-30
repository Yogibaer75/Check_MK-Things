metric_info["perc"] = {
    "color" : "#60f020",
    "unit"  : "%",
    "title" : _("Percent"),
    "help"  : _("Generic Percent usage"),
}

perfometer_info.append({
    "type"     : "linear",
    "metric"   : "perc",
    "segments" : ["perc"],
    "total"    : 100.0,
})