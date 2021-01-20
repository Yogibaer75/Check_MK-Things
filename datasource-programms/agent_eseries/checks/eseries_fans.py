#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def inventory_eseries_fans(parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        yield name, {}


def check_eseries_fans(item, _no_params, parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        if name == item:
            data = parsed[element]
            status = data['status']

            message = "FAN %s has status %s" % (item, status)
            if status != "optimal":
                message += "(!)"
                return 1, message
            else:
                return 0, message


check_info["eseries_fans"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_fans,
    "inventory_function"     : inventory_eseries_fans,
    "service_description"    : "FAN %s",
    "includes"               : ["eseries.include"],
}
