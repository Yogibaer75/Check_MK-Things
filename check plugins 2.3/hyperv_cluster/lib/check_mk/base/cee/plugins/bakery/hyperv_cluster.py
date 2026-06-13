#!/usr/bin/env python3

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from pathlib import Path
from typing import Any

from cmk.base.cee.plugins.bakery.bakery_api.v1 import (  # type: ignore[import]
    FileGenerator,
    OS,
    Plugin,
    register,
)


def get_hyperv_files(conf: dict[str, Any]) -> FileGenerator:
    """generate agent bakery plugins"""
    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_cluster.ps1"))
    if conf.get("deploy_csv"):
        yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_host_csv_io.ps1"))


register.bakery_plugin(
    name="hyperv_cluster",
    files_function=get_hyperv_files,
)
