#!/usr/bin/env python3
"""Bakery plugin for Windows firewall check deployment"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

from typing import Any, Dict
from pathlib import Path

from cmk.base.cee.plugins.bakery.bakery_api.v1 import (
    FileGenerator,
    OS,
    Plugin,
    register,
)


def get_win_firewall_status_files(_conf: Dict[str, Any]) -> FileGenerator:
    """select and integrate plugin into agent"""
    yield Plugin(base_os=OS.WINDOWS, source=Path("win_firewall_status.ps1"))


register.bakery_plugin(
    name="win_firewall_status",
    files_function=get_win_firewall_status_files,
)
