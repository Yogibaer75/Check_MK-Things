#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""Server-side call configuration for the ECI NPT special SNMP agent."""
from collections.abc import Iterator
from pydantic import BaseModel
from cmk.server_side_calls.v1 import (
    HostConfig,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    """Parameters for the NPT special SNMP agent."""

    timeout: int | None = None


def _agent_npt_special_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    """Generate command line arguments for the NPT special SNMP agent."""
    command_arguments: list[str] = []
    if params.timeout is not None:
        command_arguments += ["--timeout", str(params.timeout)]
    command_arguments.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_npt_special = SpecialAgentConfig(
    name="npt_special",
    parameter_parser=Params.model_validate,
    commands_function=_agent_npt_special_arguments,
)
