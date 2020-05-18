#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Sample agent output
#<<<udp_recpoints:sep(124)>>>
#1|hostname1|13.09.2019 12:00:02|13|1|1
#2|hostname2|12.09.2019 22:00:02|14|1|1

factory_settings["udp_recpoints_default_levels"] = {
    "levels" : (20, 30),
}

def inventory_udp_recpoints(info):
    for line in info:
        yield line[1] + "_" + line[0], {}

def check_udp_recpoints(item, params, info):

    udp_recpoints_status = {
        "0" : (3,"Unknown"),
        "1" : (0,"Finished"),
        "2" : (2,"Failed"),
        "3" : (0,"Active"),
        "4" : (1,"Canceled"),
        "5" : (2,"Crashed"),
    }

    udp_recpoint_status = {
        "0" : (3, "Unknown", "(!!!)"),
        "1" : (0, "OK", ""),
        "2" : (1, "Warning", "(!)"),
        "3" : (2, "Error", "(!!)"),
    }

    if type(params) == tuple:
        params = { "levels" : params}
    warn, crit = params["levels"]

    for line in info:
        if line[1] + "_" + line[0] == item:
            status = 0
            msgtext = ""
            hostid, hostname, last_backup, recpoints, rec_status, bck_status = line

            if last_backup == "":
                yield 0, "No 2D2 Backup until now"
            else:
                msgtext += "Last backup %s," % last_backup
                state, name, state_str = udp_recpoint_status[rec_status]
                #status = max(status, state)
                msgtext += " %s restore points with state %s%s," % (recpoints, name, state_str)
                state, name = udp_recpoints_status[bck_status]
                status = max(status, state)
                msgtext += " last backup state %s" % name
                yield status, msgtext


check_info["udp_recpoints"] = {
    "check_function"         : check_udp_recpoints,
    "inventory_function"     : inventory_udp_recpoints,
    "service_description"    : "UDP recpoint status %s",
    "default_levels_variable": "udp_recpoints_default_levels",
    "group"                  : "udp_d2d",
}
