#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def inventory_eseries_power(parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        yield name, {}


def check_eseries_power(item, _no_params, parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        if name == item:
            data = parsed[element]
            fru_type = data['fru_type']
            serial_number = data['serial_number']
            status = data['status']

            message = "PSU %s with serial %s and type %s has status %s" % (item, serial_number, fru_type, status)
            if status != "optimal":
                message += "(!)"
                return 1, message
            else:
                return 0, message


check_info["eseries_power"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_power,
    "inventory_function"     : inventory_eseries_power,
    "service_description"    : "PSU %s",
    "includes"               : ["eseries.include"],
}
