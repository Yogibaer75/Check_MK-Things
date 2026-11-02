#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterator, Mapping

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
    noop_parser,
)

# logwatch level for the configured service state of an alert severity
_LOGWATCH_LEVELS = {0: "O", 1: "W", 2: "C", 3: "u"}
# alert severity -> (ruleset key, default service state)
_SEVERITY_STATES = {
    "INFO": ("state_info", 0),
    "WARNING": ("state_warning", 1),
    "CRITICAL": ("state_critical", 2),
    "FALLBACK": ("state_fallback", 3),
}


def _alert_levels(states: Mapping[str, int]) -> str:
    return ",".join(
        f"{severity}={_LOGWATCH_LEVELS[states.get(key, default)]}"
        for severity, (key, default) in _SEVERITY_STATES.items()
    )


def generate_prism_command_v4(
    params: Mapping[str, object],
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    assert isinstance(secret := params["password"], Secret)

    args: list[str | Secret] = [
        "--server",
        host_config.primary_ip_config.address,
        "--username",
        str(params["username"]),
        "--password-id",
        secret,
    ]

    if "port" in params:
        args.extend(["--port", str(params["port"])])

    if params["no_cert_check"]:
        args.append("--no-cert-check")
    else:
        args.extend(["--cert-server-name", host_config.name])

    if "timeout" in params:
        args.extend(["--timeout", f"{params['timeout']:.0f}"])

    # ("service", None), ("logwatch", {...}) or ("both", {...}), missing means "service"
    match params.get("alert_output"):
        case (("logwatch" | "both") as alert_output, Mapping() as states):
            args.extend(["--alert-output", alert_output, "--alert-levels", _alert_levels(states)])

    yield SpecialAgentCommand(command_arguments=args)


special_agent_prism_v4 = SpecialAgentConfig(
    name="prism_v4",
    parameter_parser=noop_parser,
    commands_function=generate_prism_command_v4,
)
