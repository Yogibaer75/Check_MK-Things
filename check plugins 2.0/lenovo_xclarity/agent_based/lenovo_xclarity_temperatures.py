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

from .agent_based_api.v1.type_defs import (
    CheckResult, )

from .agent_based_api.v1 import (register, Result, State, Metric)

from .utils.lenovo_xclarity import (parse_lenovo_xclarity,
                                    discovery_lenovo_xclarity_multiple)

register.agent_section(
    name="lenovo_xclarity_temperatures",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_temperatures(item: str, section) -> CheckResult:
    data = section.get(item)
    state = data.get("Status", {"State": "Unknown"}).get("State", "Unknown")
    reading = data.get("ReadingCelsius", 0)
    crit_up = data.get("UpperThresholdCritical", 0)
    crit_lo = data.get("LowerThresholdCritical", 0)
    warn_up = data.get("UpperThresholdNonCritical", 0)
    warn_lo = data.get("LowerThresholdNonCritical", 0)

    reading = float(0 if reading is None else reading)
    crit_up = float(0 if crit_up is None else crit_up)
    crit_lo = float(0 if crit_lo is None else crit_lo)
    warn_up = float(0 if warn_up is None else warn_up)
    warn_lo = float(0 if warn_lo is None else warn_lo)

    message = "reading is %s C and has status %s" % (reading, state)

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
        message += " - Temperature critical (!!)"
    elif (reading >= warn_up and warn_up != 0) or (reading <= warn_lo and warn_lo != 0):
        status = 1
        message += " - Temperature warning (!)"

    yield Metric("temp", reading, levels=(warn_up, crit_up))
    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="lenovo_xclarity_temperatures",
    service_name="Temp %s",
    sections=["lenovo_xclarity_temperatures"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_temperatures,
)
