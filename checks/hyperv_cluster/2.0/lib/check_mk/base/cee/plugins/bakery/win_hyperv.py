#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict

from cmk.utils.type_defs import AgentConfig

from cmk.base.cee.bakery.api import FileFromSite, PluginContainer
from cmk.base.cee.bakery.constants import OS
from cmk.base.cee.bakery.plugins import CoreFileContainerGenerator, register_core_bakelet


def get_win_hyperv_files(agconf: AgentConfig) -> CoreFileContainerGenerator:
    yield PluginContainer(agconf=agconf,
                          content=FileFromSite(base_os=OS.WINDOWS, source=Path("hyperv_cluster_status.ps1")))


register_core_bakelet(
    name="win_hyperv",
    files_function=get_win_hyperv_files,
)

