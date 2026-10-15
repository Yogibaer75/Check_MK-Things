#!/usr/bin/env python3

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from pathlib import Path
from typing import Literal

from cmk.bakery.v2_unstable import OS, BakeryPlugin, FileGenerator, Plugin  # type: ignore[import]
from pydantic import BaseModel


class Config(BaseModel):
    deploy: Literal[True, False]


def get_arcserve_udp_files(conf: Config) -> FileGenerator:
    """insert ps1 script into agent"""
    if not conf.deploy:
        return

    yield Plugin(base_os=OS.WINDOWS, source=Path("arcserve_udp.ps1"))


bakery_plugin_arcserve_udp = BakeryPlugin(
    name="arcserve_udp",
    parameter_parser=Config.model_validate,
    default_parameters=None,
    files_function=get_arcserve_udp_files,
)
