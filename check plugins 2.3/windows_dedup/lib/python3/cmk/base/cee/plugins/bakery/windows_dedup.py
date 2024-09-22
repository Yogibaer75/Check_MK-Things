#!/usr/bin/env python3
"""Windows dedup status plugin"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from pathlib import Path
from typing import Any, Dict
from cmk.base.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, register


def get_windows_dedup_files(conf: Dict[str, Any]) -> FileGenerator:
    """insert ps1 script into agent"""

    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("windows_dedup.ps1"))


register.bakery_plugin(
    name="windows_dedup",
    files_function=get_windows_dedup_files,
)
