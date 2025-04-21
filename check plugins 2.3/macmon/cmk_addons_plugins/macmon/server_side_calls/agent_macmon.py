#!/usr/bin/env python3
"""Special agent command line configuration"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Iterator

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)
from pydantic import BaseModel


class Params(BaseModel):
    """Parameters for the special agent"""

    username: str
    password: Secret
    port: int | None = None


def _agent_macmon_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    """build special agent command line"""
    command_arguments = []
    if params.username is not None:
        command_arguments += ["--username", params.username]
    if params.password is not None:
        command_arguments += ["--password", params.password]
    if params.port is not None:
        command_arguments += ["--port", str(params.port)]
    command_arguments += ["--server", host_config.primary_ip_config.address]

    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_macmon = SpecialAgentConfig(
    name="macmon",
    parameter_parser=Params.model_validate,
    commands_function=_agent_macmon_arguments,
)
