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
    name="lenovo_xclarity_fans",
    parse_function=parse_lenovo_xclarity,
)


def check_lenovo_xclarity_fans(item: str, section) -> CheckResult:
    data = section.get(item)

    state = data.get("Status", {"State": "Unknown"}).get("State", "Unknown")
    reading = data.get("Reading", 0)
    min_range = data.get("MinReadingRange", 0)
    max_range = data.get("MaxReadingRange", 0)

    reading = float(0 if reading is None else reading)
    min_range = float(0 if min_range is None else min_range)
    max_range = float(0 if max_range is None else max_range)

    max_warn = max_range / 100 * 80
    if min_range == 0:
        min_warn = max_range / 100 * 20
    else:
        min_warn = (max_range - min_range) / 100 * 20 + min_range

    message = "reading is %s RPM and has status %s" % (reading, state)
    yield Metric("fan",
                 reading,
                 levels=(max_warn, None),
                 boundaries=(min_range, max_range))

    status = 0
    if state != "Enabled":
        message += "(!)"
        status = 1

    if reading >= max_warn or reading <= min_warn:
        status = 1
        message += " Speed problem (!)"

    yield Result(state=State(status), summary=message)


register.check_plugin(
    name="lenovo_xclarity_fans",
    service_name="%s",
    sections=["lenovo_xclarity_fans"],
    discovery_function=discovery_lenovo_xclarity_multiple,
    check_function=check_lenovo_xclarity_fans,
)
