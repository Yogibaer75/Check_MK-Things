#!/usr/bin/env python3
"""Netbackup job status bakery plugin"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from pathlib import Path
from typing import Any, Dict
from cmk.base.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_netbackup_files(conf: Dict[str, Any]) -> FileGenerator:
    """generate cfg and insert ps1 script into agent"""

    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("netbackup_jobs.ps1"))

    errorpath = conf.get("errorpath", "C:\\\\Program Files\\\\Veritas\\\\NetBackup\\\\bin\\\\admincmd\\\\")
    cfg_lines = [f"errorpath={errorpath}"]

    yield PluginConfig(
        base_os=OS.WINDOWS,
        lines=cfg_lines,
        target=Path("netbackup.cfg"),
    )


register.bakery_plugin(
    name="netbackup",
    files_function=get_netbackup_files,
)
