#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Dict

from cmk.utils.type_defs import AgentConfig

from cmk.base.cee.bakery.api import FileFromSite, PluginContainer
from cmk.base.cee.bakery.constants import OS
from cmk.base.cee.bakery.plugins import CoreFileContainerGenerator, register_core_bakelet


def get_win_hyperv_cluster_files(agconf: AgentConfig) -> CoreFileContainerGenerator:
    yield PluginContainer(agconf=agconf,
                          content=FileFromSite(base_os=OS.WINDOWS, source=Path("hyperv_cluster_status.ps1")))


def get_win_hyperv_host_files(agconf: AgentConfig) -> CoreFileContainerGenerator:
    yield PluginContainer(agconf=agconf,
                          content=FileFromSite(base_os=OS.WINDOWS, source=Path("hyperv_host_vms.ps1")))


def get_win_hyperv_csv_io_files(agconf: AgentConfig) -> CoreFileContainerGenerator:
    yield PluginContainer(agconf=agconf,
                          content=FileFromSite(base_os=OS.WINDOWS, source=Path("hyperv_host_csv_io.ps1")))


register_core_bakelet(
    name="win_hyperv_cluster",
    files_function=get_win_hyperv_cluster_files,
)


register_core_bakelet(
    name="win_hyperv_host",
    files_function=get_win_hyperv_host_files,
)


register_core_bakelet(
    name="win_hyperv_csv_io",
    files_function=get_win_hyperv_csv_io_files,
)

