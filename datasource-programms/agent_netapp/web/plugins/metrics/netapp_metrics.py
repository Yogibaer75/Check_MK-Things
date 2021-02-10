from cmk.gui.plugins.metrics.check_mk import ( df_translation, df_netapp_perfvarnames)

metric_info["snapshot_reserve"] = {
    "title" : _("Snapshot reserved space"),
    "unit"  : "bytes",
    "color" : "#ff8000",
}

metric_info["snapshot_size"] = {
    "title" : _("Snapshot size"),
    "unit"  : "bytes",
    "color" : "#ff4000",
}

check_metrics["check_mk-netapp_api_volumes"] = {
    "~(?!%s).*$" % "|".join(df_netapp_perfvarnames) : { "name"  : "fs_used", "scale" : MB },
    "fs_size" : { "scale" : MB },
    "growth"  : { "name"  : "fs_growth", "scale" : MB / 86400.0 },
    "trend"   : { "name"  : "fs_trend", "scale" : MB / 86400.0 },
    "snapshot_reserve" : { "scale" : MB },
    "snapshot_size"    : { "scale" : MB },
    "nfs_read_latency"      : { "scale" : m },
    "nfs_write_latency"     : { "scale" : m },
    "cifs_read_latency"     : { "scale" : m },
    "cifs_write_latency"    : { "scale" : m },
    "san_read_latency"      : { "scale" : m },
    "san_write_latency"     : { "scale" : m },
    "fcp_read_latency"      : { "scale" : m },
    "fcp_write_latency"     : { "scale" : m },
    "iscsi_read_latency"    : { "scale" : m },
    "iscsi_write_latency"   : { "scale" : m },
}

graph_info["snapshot_reserve"] = {
    "metrics" : [
        ( "snapshot_size", "area", _("Snapshot Size") ),
        ( "snapshot_reserve,snapshot_size,-#e3fff9", "stack", _("Free space") ),
        ( "snapshot_reserve", "line" ),
    ],
    "scalars" : [
        "snapshot_reserve:warn",
        "snapshot_reserve:crit",
        "snapshot_reserve:max",
    ],
    "range" : (0, "snapshot_size:max"),
}

