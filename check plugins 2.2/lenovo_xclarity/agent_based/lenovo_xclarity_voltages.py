#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# (c) Andre Eckstein <andre.eckstein@bechtle.com>

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

from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
)

from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    Result,
    State,
    Metric,
)

from .utils.lenovo_xclarity import (
    parse_lenovo_xclarity,
    discovery_lenovo_xclarity_multiple,
)

register.agent_section(
    name="lenovo_xclarity_voltages",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_voltages(item: str, section) -> CheckResult:
    data = section.get(item)
    state = data.get("Status", {"State": "Unknown"}).get("State", "Unknown")
    crit_up = float(data.get("UpperThresholdCritical", 0))
    crit_lo = float(data.get("LowerThresholdCritical", 0))
    warn_up = float(data.get("UpperThresholdNonCritical", 0))
    warn_lo = float(data.get("LowerThresholdNonCritical", 0))

    reading = float(data.get("ReadingVolts", 0))
    message = "reading is %s Volts and has status %s" % (reading, state)
    status = 0
    if state != "Enabled":
        message += "(!)"
        status = 1

    if crit_up <= warn_up:
        crit_up = warn_up
    if crit_lo >= warn_lo:
        crit_lo = warn_lo

    if (reading >= crit_up and crit_up != 0) or (reading <= crit_lo and crit_lo != 0):
        status = 2
        message += " - Voltage critical (!!)"
    elif (reading >= warn_up and warn_up != 0) or (reading <= warn_lo and warn_lo != 0):
        status = 1
        message += " - Voltage warning (!)"

    yield Metric("voltage", reading)
    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="lenovo_xclarity_voltages",
    service_name="Voltage %s",
    sections=["lenovo_xclarity_voltages"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_voltages,
)
