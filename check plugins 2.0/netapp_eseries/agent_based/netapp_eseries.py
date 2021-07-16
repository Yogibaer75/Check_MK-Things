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
from .agent_based_api.v1.type_defs import (
    DiscoveryResult, )

from .agent_based_api.v1 import (
    Service, )


def discovery_netapp_eseries_multiple(section) -> DiscoveryResult:
    for item in section:
        yield Service(item=item)


def parse_netapp_eseries(string_table):

    typ_items = {
        "batteries": "location",
        "controllers": "location",
        "drawers": "location",
        "drives": "serialNumber",
        "esms": "location",
        "fans": "location",
        "interfaces": "interfaceRef",
        "pools": "name",
        "power_supplies": "location",
        "system": "name",
        "trays": "location",
        "volumes": "name",
        "sensors": "location",
    }

    import ast
    parsed = {}
    data = ast.literal_eval(string_table[0][0])
    # dev_id = None
    for element in data:
        device = data[element]
        dev_name = None
        name_find = next(v for k, v in typ_items.items()
                         if element.startswith(k))
        if name_find == "location":
            dev_name = name_netapp_eseries(device)
        else:
            dev_name = device.get(name_find)
        parsed.setdefault(dev_name, device)

    return parsed


def name_netapp_eseries(element):
    name = ""
    location = element['physicalLocation']
    name = "%s-%s" % (location['locationPosition'], location['slot'])
    if location['label'] != '':
        name += " %s" % location['label']
    return name
