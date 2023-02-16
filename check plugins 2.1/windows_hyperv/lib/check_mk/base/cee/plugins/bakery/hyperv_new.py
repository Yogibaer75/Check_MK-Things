#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from pathlib import Path
from typing import Any, Dict

from .bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register

def get_hyperv_new_files(conf: Dict[str, Any]) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_cluster.ps1"))
    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_host_csv_io.ps1"))


register.bakery_plugin(
        name="hyperv_new",
        files_function=get_hyperv_new_files,
        )
