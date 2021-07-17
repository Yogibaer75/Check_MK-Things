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


def check_prism_vms(item: str, params, section) -> CheckResult:
    data = section.get(item)
    state = 0
    state_text = data["powerState"]
    vm_desc = data["description"]

    if "template" in str(vm_desc):
        vm_desc = "Template"
    prot_domain = data["protectionDomainName"]
    host_name = data["hostName"]
    memory = render.bytes(data["memoryCapacityInBytes"])
    if state_text != "on" and vm_desc != "Template":
        state = 1
    message = f"with status {state_text} - on Host {host_name} - Memory {memory} - Description {vm_desc} - Protetion Domain {prot_domain}"

    yield Result(state=State(state), summary=message)


register.check_plugin(
    name="prism_vms",
    service_name="NTNX VM %s",
    sections=["prism_vms"],
    check_default_parameters={
        'system_state': 0,
    },
    discovery_function=discovery_prism_vms,
    check_function=check_prism_vms,
    check_ruleset_name="prism_vms",
)
