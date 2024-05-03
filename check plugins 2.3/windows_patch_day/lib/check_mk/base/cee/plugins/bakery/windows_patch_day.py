#!/usr/bin/env python3
"""Windows last update bakery plugin"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from pathlib import Path
from typing import Any, Dict
from cmk.base.plugins.bakery.bakery_api.v1 import FileGenerator, OS, Plugin, PluginConfig, register


def get_windows_patch_day_files(conf: Dict[str, Any]) -> FileGenerator:
    """generate cfg and insert ps1 script into agent"""

    if not conf.get("deploy"):
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("windows_patch_day.ps1"))

    updatecount = conf.get("updatecount", 30)
    filterstrings = conf.get("filterstring", ["XXXXXX"])
    filterstring = "|".join(filterstrings)
    cfg_lines = [f"updatecount={updatecount}", f"filterstring={filterstring}"]

    yield PluginConfig(
        base_os=OS.WINDOWS,
        lines=cfg_lines,
        target=Path("windows_patch_day.cfg"),
    )


register.bakery_plugin(
    name="windows_patch_day",
    files_function=get_windows_patch_day_files,
)
