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
    """Parameters for the special agent"""

    user: str
    password: Secret
    verify_cert: bool = False


def _agent_dellpowervault_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    """build command line arguments"""
    command_arguments = []
    if params.user is not None:
        command_arguments += ["-u", params.user]
    if params.password is not None:
        command_arguments += ["-p", params.password]
    if params.verify_cert:
        command_arguments += ["--verify-cert"]
    command_arguments += [host_config.primary_ip_config.address]

    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_dellpowervault = SpecialAgentConfig(
    name="dellpowervault",
    parameter_parser=Params.model_validate,
    commands_function=_agent_dellpowervault_arguments,
)
