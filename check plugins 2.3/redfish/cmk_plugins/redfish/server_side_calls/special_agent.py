#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
'''server side component to create the special agent call'''
# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from collections.abc import Iterator, Mapping

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    # parse_secret,
    HostConfig,
    HTTPProxy,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    '''as a missing password form_spec is missing i need to transfer the password as clear text at the moment'''
    user: str | None = None
#    password: tuple[Literal["store", "password"], str] | None = None
    password: str | None = None
    port: int | None = None
    proto: str | None = None
    sections: list | None = None
    timeout: int | None = None
    retries: int | None = None


def _agent_redfish_arguments(
    params: Params,
    host_config: HostConfig,
    _proxy_config: Mapping[str, HTTPProxy]
) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = []
    if params.user is not None:
        command_arguments += ["-u", params.user]
    if params.password is not None:
        command_arguments += ["-s", params.password]  # only needed without password from_spec
#        command_arguments += ["-s", parse_secret(params.password[0], params.password[1])]
    if params.port is not None:
        command_arguments += ["-p", str(params.port)]
    if params.proto is not None:
        command_arguments += ["-P", str(params.proto)]
    if params.sections is not None:
        command_arguments += ["-m", ','.join(params.sections)]
    if params.timeout is not None:
        command_arguments += ["--timeout", params.timeout]
    if params.retries is not None:
        command_arguments += ["--retries", params.retries]
    command_arguments.append(host_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_redfish = SpecialAgentConfig(
    name="redfish",
    parameter_parser=Params.model_validate,
    commands_function=_agent_redfish_arguments,
)
