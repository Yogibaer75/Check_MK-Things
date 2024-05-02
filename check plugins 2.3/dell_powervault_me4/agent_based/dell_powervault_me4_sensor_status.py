#!/usr/bin/env python3
"""Dell ME4 sensor status check"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2


from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
    Metric,
)

from .utils.dell_powervault_me4 import parse_dell_powervault_me4

register.agent_section(
    name="dell_powervault_me4_sensor_status",
    parse_function=parse_dell_powervault_me4,
)


def discovery_dell_powervault_me4_sensor_status(section) -> DiscoveryResult:
    """for every sensor a service is discovered"""
    for item in section:
        yield Service(item=item)


def check_dell_powervault_me4_sensor_status(item: str, params, section) -> CheckResult:
    """check the state of the sensor"""
    data = section.get(item, {})
    if not data:
        return
    sensor_states = {
        0: ("Unsupported", 3),
        1: ("OK", 0),
        2: ("Critical", 2),
        3: ("Warning", 1),
        4: ("Unrecoverable", 2),
        5: ("Not Installed", 1),
        6: ("Unknown", 3),
        7: ("Unavailable", 3),
    }

    sensor_unit = {
        "Temperature": ("°C", "temp"),
        "Voltage": ("V", "voltage"),
        "Charge Capacity": ("%", "battery_capacity"),
        "Current": ("A", "current"),
        "Unknown": ("", ""),
    }
    value = data.get("value")
    value_number = "".join(c for c in value if (c.isdigit() or c == "."))
    status_unit, perf_unit = sensor_unit.get(
        data.get("sensor-type", "Unknown"), ("", "count")
    )
    state_text, status_num = sensor_states.get(
        data.get("status-numeric", 7), ("Unknown", 3)
    )
    message = f"Sensor state is {state_text}"
    if value_number != "":
        message += f" with reading {value_number}{status_unit}"
    yield Result(state=State(status_num), summary=message)

    if status_unit != "":
        yield Metric(perf_unit, float(value_number))


register.check_plugin(
    name="dell_powervault_me4_sensor_status",
    service_name="Sensor %s",
    sections=["dell_powervault_me4_sensor_status"],
    check_default_parameters={
        "sensor_state": 0,
    },
    discovery_function=discovery_dell_powervault_me4_sensor_status,
    check_function=check_dell_powervault_me4_sensor_status,
    check_ruleset_name="dell_powervault_me4_sensor_status",
)
