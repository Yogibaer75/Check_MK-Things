#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
import json
from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
    StringTable,
    HostLabelGenerator,
)

from .agent_based_api.v1 import (
    check_levels,
    register,
    render,
    Metric,
    Result,
    State,
    HostLabel,
    Service,
)


def parse_nextcloud(string_table):
    parsed = {
        "nextcloud": {},
        "server": {},
        "activeusers": {},
    }

    parsed = json.loads(string_table[0][0])
    nextcloud = parsed.get("ocs").get("data").get("nextcloud")
    parsed.setdefault("nextcloud", nextcloud)
    server = parsed.get("ocs").get("data").get("server")
    parsed.setdefault("server", server)
    activeusers = parsed.get("ocs").get("data").get("activeUsers")
    parsed.setdefault("activeusers", activeusers)

    return parsed


register.agent_section(
    name="nextcloud",
    parse_function=parse_nextcloud,
)


def discovery_nextcloud(section) -> DiscoveryResult:
    if section["nextcloud"].get("system"):
        yield Service(item="Status")


def discovery_nextcloud_software(section) -> DiscoveryResult:
    if section["server"].get("webserver"):
        yield Service(item="Status")


def discovery_nextcloud_apps(section) -> DiscoveryResult:
    if section["nextcloud"].get("system").get("apps"):
        yield Service(item="Status")


def discovery_nextcloud_users(section) -> DiscoveryResult:
    if "activeusers" in section:
        yield Service(item="Status")


def check_nextcloud(item, params, section) -> CheckResult:
    if section["nextcloud"].get("system"):
        data = section["nextcloud"].get("system")
        yield Result(state=State.OK, Summary="Version %s installed" % data["version"])
    else:
        yield Result(
            state=State.UNKNOWN,
            summary="System state not found: %s" % section["nextcloud"],
        )


def check_nextcloud_software(item, params, section) -> CheckResult:
    yield Result(state=State.OK, summary="All is fine")


def check_nextcloud_apps(item, params, section) -> CheckResult:
    yield Result(state=State.OK, summary="All is fine")


def check_nextcloud_users(item, params, section) -> CheckResult:
    yield Result(state=State.OK, summary="All is fine")


register.check_plugin(
    name="nextcloud",
    service_name="Nextcloud %s",
    sections=["nextcloud"],
    discovery_function=discovery_nextcloud,
    check_function=check_nextcloud,
)

register.check_plugin(
    name="nextcloud_software",
    service_name="Nextcloud Software %s",
    sections=["nextcloud"],
    discovery_function=discovery_nextcloud_software,
    check_function=check_nextcloud_software,
)

register.check_plugin(
    name="nextcloud_apps",
    service_name="Nextcloud Apps %s",
    sections=["nextcloud"],
    discovery_function=discovery_nextcloud_apps,
    check_function=check_nextcloud_apps,
)

register.check_plugin(
    name="nextcloud_server",
    service_name="Nextcloud Users %s",
    sections=["nextcloud"],
    discovery_function=discovery_nextcloud_users,
    check_function=check_nextcloud_users,
)
