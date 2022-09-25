#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    render,
)


def parse_prism_vms(string_table):
    import ast
    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data.get("entities"):
        parsed.setdefault(element.get("vmName", "unknown"), element)
    return parsed


register.agent_section(
    name="prism_vms",
    parse_function=parse_prism_vms,
)


def discovery_prism_vms(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


_POWER_STATES = {
    "on": 0,
    "unknown": 3,
    "off": 1,
    "powering_on": 0,
    "shutting_down": 1,
    "powering_off": 1,
    "pausing": 1,
    "paused": 1,
    "suspending": 1,
    "suspended": 1,
    "resuming": 0,
    "resetting": 1,
    "migrating": 0,
}


def check_prism_vms(item: str, params, section) -> CheckResult:
    wanted_state = params.get("system_state", "on")
    data = section.get(item)
    state_text = data["powerState"]
    state_value = _POWER_STATES.get(state_text.lower(), 3)
    vm_desc = data["description"]
    if vm_desc:
        vm_desc = vm_desc.replace("\n", r"\n")

    if "template" in str(vm_desc):
        vm_desc = "Template"
        state = 0
    prot_domain = data["protectionDomainName"]
    host_name = data["hostName"]
    memory = render.bytes(data["memoryCapacityInBytes"])
    if wanted_state == state_text.lower():
        state = 0
    else:
        state = state_value

    message = f"with status {state_text} - on Host {host_name}"
    yield Result(state=State(state), summary=message)

    yield Result(state=State(0), notice=f"Memory {memory},"
                                        f"\nDescription {vm_desc},"
                                        f"\nProtetion Domain {prot_domain}")


register.check_plugin(
    name="prism_vms",
    service_name="NTNX VM %s",
    sections=["prism_vms"],
    check_default_parameters={
        'system_state': "on",
    },
    discovery_function=discovery_prism_vms,
    check_function=check_prism_vms,
    check_ruleset_name="prism_vms",
)
