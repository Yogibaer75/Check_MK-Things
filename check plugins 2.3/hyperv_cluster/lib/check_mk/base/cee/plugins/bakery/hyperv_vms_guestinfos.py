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


def get_hyperv_vms_guestinfos_files(conf: dict[str, Any]) -> FileGenerator:
    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("hyperv_host.ps1"))


register.bakery_plugin(
    name="hyperv_vm_info",
    files_function=get_hyperv_vms_guestinfos_files,
)
