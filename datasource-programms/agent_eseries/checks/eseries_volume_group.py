#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

def inventory_eseries_volume_group(parsed):
    for element in parsed:
        yield parsed[element]['name'], {}


def check_eseries_volume_group(item, params, parsed):
    for element in parsed:
        if parsed[element]['name'] == item:
            data = parsed[element]

            size_total_bytes = int(data['total_raided_space'])
            size_free_bytes = int(data['free_space'])
            size_used_bytes = int(data['used_space'])

            size = get_bytes_human_readable(size_total_bytes)
            raid = data['raid_level']
            status = data['state']

            message = "VolumeGroup %s with raid level %s has status %s" % (item, raid, status)
            if status != "complete":
                message += "(!)"
                yield 1, message
            else:
                yield 0, message

            yield df_check_filesystem_single(
                  item,
                  size_total_bytes / 1024.0 / 1024.0,
                  size_free_bytes / 1024.0 / 1024.0,
                  0,
                  None,
                  None,
                  params,
                  )


check_info["eseries_volume_group"] = {
    "parse_function"         : parse_eseries,
    "check_function"         : check_eseries_volume_group,
    "inventory_function"     : inventory_eseries_volume_group,
    "service_description"    : "VolumeGroup %s",
    "group"                  : "filesystem",
    "includes"               : ["eseries.include","size_trend.include", "df.include"],
}
