#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# 

def inventory_eseries_volume(parsed):
    for element in parsed:
        yield parsed[element]['name'], {}


def check_eseries_volume(item, _no_params, parsed):
    for element in parsed:
        if parsed[element]['name'] == item:
            data = parsed[element]
            size_bytes = int(data['total_size_in_bytes'])
            size = get_bytes_human_readable(size_bytes)
            raid = data['raid_level']
            status = data['status']

            message = "Volume %s with size %s and raid level %s has status %s" % (item, size, raid, status)
            if status != "optimal":
                message += "(!)"
                return 1, message
            else:
                return 0, message


check_info["eseries_volume"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_volume,
    "inventory_function"     : inventory_eseries_volume,
    "service_description"    : "Volume %s",
    "group"                  : "eseries_volume",
    "includes"               : ["eseries.include"],
}
