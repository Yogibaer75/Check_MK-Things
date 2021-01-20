#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def inventory_eseries_battery(parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        yield name, {}


def check_eseries_battery(item, _no_params, parsed):
    for element in parsed:
        location = parsed[element]['physical_location']
        name = "%s-%s" % (location['location_position'], location['slot'])
        if name == item:
            data = parsed[element]
            status = data['status']
            serial_number = data['vendor_sn']

            last_test = data['learn_cycle_data']['last_battery_learn_cycle']
            next_test = data['learn_cycle_data']['next_battery_learn_cycle']
            
            message = "Batter %s with serial %s has status %s - last test was %s - next test is %s" % (item, serial_number, status, get_timestamp_human_readable(last_test), get_timestamp_human_readable(next_test))
            if status != "optimal":
                message += "(!)"
                return 1, message
            else:
                return 0, message


check_info["eseries_battery"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_battery,
    "inventory_function"     : inventory_eseries_battery,
    "service_description"    : "Battery %s",
    "includes"               : ["eseries.include"],
}
