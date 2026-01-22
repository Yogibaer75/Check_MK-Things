#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checkmk NPT Special Connections Agent-Based Plugin."""
import time
from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import AgentSection, CheckPlugin, Result, Service, State
from cmk.plugins.lib import interfaces, uptime

Section = Dict[str, int]


def parse_npt_special_conn(string_table):
    """Parses NPT special connection data from the agent output."""
    data = {}
    new_data = {}
    for line in string_table:
        name, data = " ".join(line).split(":")
        name = name.strip()
        data = data.strip()
        new_data[name] = data

    return new_data


agent_section_npt_special = AgentSection(
    name="npt_special",
    parse_function=parse_npt_special_conn,
    parsed_section_name="npt_special_conn",
)


def discover_npt_special_conn(section):
    """Interface discovery for NPT special connections."""
    for name in section:
        if "Interface" in name:
            yield Service(item=name.replace("Interface ", ""))


def check_npt_special_conn(
    item: str,
    params: Mapping[str, Any],
    section: Section,
):
    """Interface check for NPT special connections."""

    data = section

    item = "Interface " + str(item)
    for name in data:
        if item in name:
            ifidx, in_octets, out_octets, in_error, in_ucast = data[name].split("---")
            if_table = []
            if_table.append(
                interfaces.InterfaceWithCounters(
                    interfaces.Attributes(
                        index=str(ifidx),
                        descr=str(name),
                        alias=str(name),
                        type="6",
                        speed=0,
                        oper_status="1",
                        out_qlen=0,
                        phys_address="0",
                    ),
                    interfaces.Counters(
                        in_octets=interfaces.saveint(in_octets),
                        in_ucast=interfaces.saveint(in_ucast),
                        in_mcast=0,
                        in_bcast=0,
                        in_disc=0,
                        in_err=interfaces.saveint(in_error),
                        out_octets=interfaces.saveint(out_octets),
                        out_ucast=0,
                        out_mcast=0,
                        out_bcast=0,
                        out_disc=0,
                        out_err=0,
                    ),
                    timestamp=time.time(),
                )
            )
            yield from interfaces.check_multiple_interfaces(
                item,
                params,
                if_table,
            )


check_plugin_npt_special_conn = CheckPlugin(
    name="npt_special_conn",
    service_name="Interface %s",
    check_ruleset_name="interfaces",
    check_default_parameters=interfaces.CHECK_DEFAULT_PARAMETERS,
    discovery_function=discover_npt_special_conn,
    check_function=check_npt_special_conn,
)


def discover_npt_special_uptime(section):
    """Uptime discovery for NPT special connections."""
    for name in section:
        if "Uptime" in name:
            yield Service()


def check_npt_special_uptime(params: Mapping[str, Any], section: Section):
    """Uptime check for NPT special connections."""
    uptime_data = uptime.Section(float(str(section["Uptime"])) / 100, None)
    yield from uptime.check(params, uptime_data)


check_plugin_npt_special_uptime = CheckPlugin(
    name="npt_special_uptime",
    service_name="Uptime",
    sections=["npt_special_conn"],
    check_ruleset_name="uptime",
    check_default_parameters={},
    discovery_function=discover_npt_special_uptime,
    check_function=check_npt_special_uptime,
)


def discover_npt_special_info(section):
    """Info discovery for NPT special connections."""
    for name in section:
        if "Type" in name:
            yield Service()


def check_npt_special_info(section: Section):
    """Info check for NPT special connections."""
    dev_typ = section["Type"]
    yield Result(state=State(0), summary=f"Device Type {dev_typ}")


check_plugin_npt_special_info = CheckPlugin(
    name="npt_special_info",
    service_name="SNMP Info",
    sections=["npt_special_conn"],
    discovery_function=discover_npt_special_info,
    check_function=check_npt_special_info,
)
