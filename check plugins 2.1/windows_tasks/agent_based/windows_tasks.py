#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.
from typing import Any, Container, Dict, TypedDict
from .agent_based_api.v1 import register, Result, Service, State
from .agent_based_api.v1.type_defs import CheckResult, DiscoveryResult, StringTable

Section = Dict[Any, Any]


def parse_windows_tasks(string_table: StringTable) -> Section:
    parsed = {}
    if string_table[0][1] == "LastRunTime":
        keys = string_table[0]
        data = string_table[1:]
        parsed = {entry[0]: dict(zip(keys, entry)) for entry in data}
    else:
        last_task = False
        for line in string_table:
            name = line[0].strip()
            value = ":".join(line[1:]).strip()
            if value and last_task and name != "TaskName":
                parsed[last_task][name] = value

            elif name == "TaskName":
                last_task = value
                parsed[last_task] = {}

            elif not value and not parsed[last_task]:
                parsed.pop(last_task)
                last_task += " " + name
                parsed[last_task] = {}
    return parsed


register.agent_section(
    name="windows_tasks",
    parse_function=parse_windows_tasks,
)


_MAP_EXIT_CODES = {
    "0x00000000": (0, "The task exited successfully"),
    "0x00041300": (0, "The task is ready to run at its next scheduled time."),
    "0x00041301": (0, "The task is currently running."),
    "0x00041302": (
        0,
        "The task will not run at the scheduled times because it has been disabled.",
    ),
    "0x00041303": (0, "The task has not yet run."),
    "0x00041304": (0, "There are no more runs scheduled for this task."),
    "0x00041305": (
        1,
        "One or more of the properties that are needed to run this task on a schedule have not been set.",
    ),
    "0x00041306": (0, "The last run of the task was terminated by the user."),
    "0x00041307": (
        1,
        "Either the task has no triggers or the existing triggers are disabled or not set.",
    ),
    "0x00041308": (1, "Event triggers do not have set run times."),
    "0x80041309": (1, "A task's trigger is not found."),
    "0x8004130a": (
        1,
        "One or more of the properties required to run this task have not been set.",
    ),
    "0x8004130b": (0, "There is no running instance of the task."),
    "0x8004130c": (2, "The Task Scheduler service is not installed on this computer."),
    "0x8004130d": (1, "The task object could not be opened."),
    "0x8004130e": (
        1,
        "The object is either an invalid task object or is not a task object.",
    ),
    "0x8004130f": (
        1,
        "No account information could be found in the Task Scheduler security database for the task indicated.",
    ),
    "0x80041310": (1, "Unable to establish existence of the account specified."),
    "0x80041311": (
        2,
        "Corruption was detected in the Task Scheduler security database; the database has been reset.",
    ),
    "0x80041312": (
        1,
        "Task Scheduler security services are available only on Windows NT.",
    ),
    "0x80041313": (1, "The task object version is either unsupported or invalid."),
    "0x80041314": (
        1,
        "The task has been configured with an unsupported combination of account settings and run time options.",
    ),
    "0x80041315": (1, "The Task Scheduler Service is not running."),
    "0x80041316": (1, "The task XML contains an unexpected node."),
    "0x80041317": (
        1,
        "The task XML contains an element or attribute from an unexpected namespace.",
    ),
    "0x80041318": (
        1,
        "The task XML contains a value which is incorrectly formatted or out of range.",
    ),
    "0x80041319": (1, "The task XML is missing a required element or attribute."),
    "0x8004131a": (1, "The task XML is malformed."),
    "0x0004131b": (
        1,
        "The task is registered, but not all specified triggers will start the task.",
    ),
    "0x0004131c": (
        1,
        "The task is registered, but may fail to start. Batch logon privilege needs to be enabled for the task principal.",
    ),
    "0x8004131d": (1, "The task XML contains too many nodes of the same type."),
    "0x8004131e": (1, "The task cannot be started after the trigger end boundary."),
    "0x8004131f": (0, "An instance of this task is already running."),
    "0x80041320": (1, "The task will not run because the user is not logged on."),
    "0x80041321": (1, "The task image is corrupt or has been tampered with."),
    "0x80041322": (1, "The Task Scheduler service is not available."),
    "0x80041323": (
        1,
        "The Task Scheduler service is too busy to handle your request. Please try again later.",
    ),
    "0x80041324": (
        1,
        "The Task Scheduler service attempted to run the task, but the task did not run due to one of the constraints in the task definition.",
    ),
    "0x00041325": (0, "The Task Scheduler service has asked the task to run."),
    "0x80041326": (0, "The task is disabled."),
    "0x80041327": (
        1,
        "The task has properties that are not compatible with earlier versions of Windows.",
    ),
    "0x80041328": (1, "The task settings do not allow the task to start on demand."),
}


class DiscoveryParams(TypedDict):
    state: Container[str]


def discovery_windows_tasks(
    params: DiscoveryParams, section: Section
) -> DiscoveryResult:
    print(params)
    for element in section.keys():
        if (
            section[element].get("State")
            or section[element].get("Scheduled Task State")
        ) in params.get("state"):
            continue
        yield Service(item=element)


def check_windows_tasks(
    item: str, params: Dict[str, Any], section: Section
) -> CheckResult:
    if item not in section:
        yield Result(
            state=State.UNKNOWN,
            summary="Task not found in agent output",
        )
        return

    state_not_enabled = params.get("state_not_enabled", 1)

    custom_map_exit_codes = {
        exit_code: (
            user_defined_mapping["monitoring_state"],
            user_defined_mapping.get(
                "info_text",
                # in case info_text was not specified, we use the default one if available
                _MAP_EXIT_CODES.get(exit_code, (None, None))[1],
            ),
        )
        for user_defined_mapping in params.get("exit_code_to_state", [])
        for exit_code in [user_defined_mapping["exit_code"]]
    }
    map_exit_codes = {
        **_MAP_EXIT_CODES,
        **custom_map_exit_codes,
    }

    data = section[item]
    if "LastTaskResult" in data:
        last_result = data["LastTaskResult"]
    else:
        last_result = data["Last Result"]

    # schtasks.exe (used by the check plugin) returns a signed integer
    # e.g. -2147024629. However, error codes are unsigned integers.
    # To make it easier for the user to lookup the error code (e.g. on
    # MSDN) we convert the negative numbers to the hexadecimal
    # representation.
    last_result_unsigned = int(last_result) & 0xFFFFFFFF
    last_result_hex = f"{last_result_unsigned:#010x}"  # padding with zeros

    state, state_txt = map_exit_codes.get(
        last_result_hex,
        (2, None),
    )
    yield Result(
        state=State(state),
        summary=f"{state_txt} ({last_result_hex})"
        if state_txt
        else f"Got exit code {last_result_hex}",
    )

    if "Scheduled Task State" in data:
        if data["Scheduled Task State"] != "Enabled":
            yield state_not_enabled, "Task not enabled"
    else:
        if data["State"] != "Ready":
            yield state_not_enabled, f"Task {data['State']}"

    additional_infos = []
    for key, title in [
        ("LastRunTime", "Last run time"),
        ("NextRunTime", "Next run time"),
        ("Last Run Time", "Last run time"),
        ("Next Run Time", "Next run time"),
    ]:
        if key in data:
            additional_infos.append("%s: %s" % (title, data[key]))

    if additional_infos:
        yield Result(state=State.OK, summary=", ".join(additional_infos))


register.check_plugin(
    name="windows_tasks",
    service_name="Task %s",
    sections=["windows_tasks"],
    discovery_ruleset_name="discovery_windows_tasks_rules",
    discovery_default_parameters={"state": ["Disabled", "Deaktiviert"]},
    discovery_function=discovery_windows_tasks,
    check_function=check_windows_tasks,
    check_ruleset_name="windows_tasks",
    check_default_parameters={},
)
