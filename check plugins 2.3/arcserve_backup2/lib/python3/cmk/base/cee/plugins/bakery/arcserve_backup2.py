#!/usr/bin/env python3
"""Arcserve Backup2 bakery plugin"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from pathlib import Path
from typing import Any, Dict
from cmk.base.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


def get_arcserve_backup2_files(conf: Dict[str, Any]) -> FileGenerator:
    """insert ps1 script into agent"""

    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("arcserve_backup2.ps1"))


register.bakery_plugin(
    name="arcserve_backup2",
    files_function=get_arcserve_backup2_files,
)
