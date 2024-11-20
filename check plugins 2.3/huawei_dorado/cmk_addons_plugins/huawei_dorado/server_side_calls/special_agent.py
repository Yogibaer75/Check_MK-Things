#!/usr/bin/env python3
"""build special agent command line"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Iterator
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    """params validator"""

    api_port: int | None = None
    api_user: str | None = None
    api_password: Secret | None = None


def _agent_huawei_dorado(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = []
    if params.api_user is not None:
        command_arguments += ["--api_user", params.api_user]
    if params.api_port is not None:
        command_arguments += ["--api_port", str(params.api_port)]
    if params.api_password is not None:
        command_arguments += ["--api_password", params.api_password]
    command_arguments += ["--api_ip", host_config.primary_ip_config.address]

    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_huawei_dorado = SpecialAgentConfig(
    name="huawei_dorado",
    parameter_parser=Params.model_validate,
    commands_function=_agent_huawei_dorado,
)
