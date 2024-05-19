#!/usr/bin/env python3
"""HPE 3Par special agent command line"""

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
    user: str | None = None
    accept_any_hostkey: bool | None = None
    infos: list | None = None


def _agent_3par_ssh_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    """build command line arguments"""

    command_arguments: list[str | Secret] = []
    if params.user is not None:
        command_arguments += ["-u", params.user]
    if params.accept_any_hostkey is not None:
        command_arguments += ["--accept-any-hostkey"]
    if params.infos is not None:
        command_arguments += ["-i", ",".join(params.infos)]
    command_arguments.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_threepar_ssh = SpecialAgentConfig(
    name="threepar_ssh",
    parameter_parser=Params.model_validate,
    commands_function=_agent_3par_ssh_arguments,
)
