#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andreas Doehler <andreas.doehler@gmail.com>/<andreas.doehler@bechtle.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from pathlib import Path
from typing import Any
from .bakery_api.v0 import (register, OS, Plugin, FileGenerator)


def get_win_hyperv_cluster_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_cluster_status.ps1"))


def get_win_hyperv_host_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_host_vms.ps1"))


def get_win_hyperv_csv_io_files(conf: Any) -> FileGenerator:
    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_host_csv_io.ps1"))


register.bakery_plugin(
    name="win_hyperv_cluster",
    files_function=get_win_hyperv_cluster_files,
)


register.bakery_plugin(
    name="win_hyperv_host",
    files_function=get_win_hyperv_host_files,
)


register.bakery_plugin(
    name="win_hyperv_csv_io",
    files_function=get_win_hyperv_csv_io_files,
)
