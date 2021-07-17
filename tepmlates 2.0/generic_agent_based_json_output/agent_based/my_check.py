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

# Example Output:
#
#

import time

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


def parse_my_check(string_table):
    import ast
    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    for element in data.get("something"):
        parsed.setdefault(element.get("name", "unknown"), element)
    return parsed


register.agent_section(
    name="my_check",
    parse_function=parse_my_check,
)


def discovery_my_check(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def check_my_check(item: str, params, section) -> CheckResult:
    data = section.get(item)
    state = 0
    state_text = data["state"]
    #TODO: check state
    #Here are some useful check should be inserted
    #
    message = "Some usefull message with status %s" % (state_text)
    if state_text != "something":
        state = 1
        message += "(!)"
    yield Result(state=State(state), summary=message)


register.check_plugin(
    name="my_check",
    service_name="My Check Item %s",
    sections=["my_check"],
    check_default_parameters={
        'state': 0,
    },
    discovery_function=discovery_my_check,
    check_function=check_my_check,
    check_ruleset_name="my_check",
)
