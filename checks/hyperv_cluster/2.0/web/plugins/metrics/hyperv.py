#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

df_basic_perfvarnames = [
    "inodes_used", "fs_size", "growth", "trend", "reserved", "fs_free", "fs_provisioning",
    "uncommitted", "overprovisioned"
]
df_translation = {
    "~(?!%s).*$" % "|".join(df_basic_perfvarnames): {
        "name": "fs_used",
        "scale": MB
    },
    "fs_used": {
        "scale": MB
    },
    "fs_size": {
        "scale": MB
    },
    "reserved": {
        "scale": MB
    },
    "fs_free": {
        "scale": MB
    },
    "growth": {
        "name": "fs_growth",
        "scale": MB / 86400.0
    },
    "trend": {
        "name": "fs_trend",
        "scale": MB / 86400.0
    },
    "trend_hoursleft": {
        "scale": 3600,
    },
    "uncommitted": {
        "scale": MB,
    },
    "overprovisioned": {
        "scale": MB,
    },
}

check_metrics["check_mk-hyperv_cluster_csv"] = df_translation
check_metrics["check_mk-hyperv_vm_vhd"] = df_translation
