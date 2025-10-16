#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any, Dict

from cmk.base.cee.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


def get_hyperv_files(conf: Dict[str, Any]) -> FileGenerator:
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
