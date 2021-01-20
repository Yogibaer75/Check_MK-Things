#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def inventory_eseries_drives(parsed):
    for element in parsed:
        yield parsed[element]['serial_number'], {}


def check_eseries_drives(item, params, parsed):
    for element in parsed:
        if parsed[element]['serial_number'] == item:
            data = parsed[element]
            size_bytes = int(data['usable_capacity'])
            size = get_bytes_human_readable(size_bytes)
            status = data['status']

            message = "Drive %s with size %s has status %s" % (item, size, status)
            if status != "optimal":
                message += "(!)"
                yield 1, message
            else:
                yield 0, message

            if data['drive_media_type'] == 'ssd':
                perfdata = []
                erase_count = int(data['ssd_wear_life']['average_erase_count_percent'])
                endurance_used = int(data['ssd_wear_life']['percent_endurance_used'])
                spare_blocks = int(data['ssd_wear_life']['spare_blocks_remaining_percent'])
                perfdata.append(("erase",erase_count, '', '', 0, 100))
                perfdata.append(("endurance",endurance_used, '', '', 0, 100))
                perfdata.append(("spare_blocks",spare_blocks, '', '', 0, 100))
                yield 0, "Disk type is SSD", perfdata

            yield check_temperature(data["drive_temperature"]["current_temp"], params, "eseries_temp_%s" % item)

check_info["eseries_drives"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_drives,
    "inventory_function"     : inventory_eseries_drives,
    "service_description"    : "Drive %s",
    "has_perfdata"           : True,
    "group"                  : "temperature",
    "includes"               : ["eseries.include","temperature.include"],
}
