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

def parse_dell_powervault_me4(string_table):
    items = {
        "controllers": "durable-id",
        "pools": "name",
        "volumes": "durable-id",
        "fan": "durable-id",
        "enclosure-fru": "fru-location",
        "power-supplies": "durable-id",
        "sensors": "durable-id",
        "system": "system-name",
        "drives": "durable-id",
        "controller-statistics": "durable-id",
        "volume-statistics": "volume-name",
        "port": "durable-id",
    }
    parsed = {}
    import ast
    data = ast.literal_eval(string_table[0][0])

    for key in items:
        if data.get(key, False):
            elements = data.get(key)
            for element in elements:
                item = element.get(items[key])
                parsed.setdefault(item, element)

    return parsed
