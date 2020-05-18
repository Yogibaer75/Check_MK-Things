#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Sample agent output
#<<<udp_backup:sep(124)>>>
#hostname1|13.09.2019 12:00:02|13|1|1
#hostname2|12.09.2019 22:00:02|14|1|1

factory_settings["udp_job_default_levels"] = {
    "levels" : (48, 72),
}

def inventory_udp_jobs(info):
    for line in info:
        yield line[1] + "_" + line[0], {}

def check_udp_jobs(item, params, info):

    udp_job_method = {
        "-1": ("Unknown"),
        "0" : ("Full backup job"),
        "1" : ("Incremental backup job"),
        "2" : ("Verify backup job"),
        "3" : ("All"),
        "4" : ("File Copy backup job"),
        "5" : ("Copy Recovery Point backup job"),
    }

    udp_job_status = {
        "-1" : (0, "All"),
        "0" : (0, "Active"),
        "1" : (0, "Finished"),
        "2" : (1, "Canceled"),
        "3" : (2, "Failed"),
        "4" : (1, "Incomplete"),
        "5" : (0, "Idle"),
        "6" : (0, "Waiting"),
        "7" : (2, "Crash"),
        "9" : (1, "License Failed"),
        "10" : (2, "Backupjob_PROC_EXIT"),
        "11" : (1, "Skipped"),
        "12" : (0, "Stop"),
        "10000" : (1, "Missed"),
    }

    if type(params) == tuple:
        params = { "levels" : params}
    warn, crit = params["levels"]

    for line in info:
        if line[1] + "_" + line[0] == item:
            status = 0
            msgtext = ""
            hostid, hostname, last_backup, job_status, size, job_method = line

            if last_backup == "":
                yield 0, "No UDP job until now"
            else:
                msgtext += "Last job %s," % last_backup
                last_backup = time.mktime(time.strptime(last_backup, "%d.%m.%Y %H:%M:%S"))
                backup_age = time.time() - last_backup
                state, name = udp_job_status[job_status]
                msgtext += " with state %s" % (name)
                method = udp_job_method[job_method]
                yield state, msgtext

                if backup_age >= crit * 3600:
                    msgtext = "last job to old"
                    yield 2, msgtext

                elif backup_age >= warn * 3600:
                    msgtext = "last job to old"
                    yield 1, msgtext

                msgtext = "backup size %s and backup method %s" % (get_bytes_human_readable(int(size)), method)
                yield 0, msgtext


check_info["udp_jobs"] = {
    "check_function"         : check_udp_jobs,
    "inventory_function"     : inventory_udp_jobs,
    "service_description"    : "UDP job status %s",
    "default_levels_variable": "udp_job_default_levels",
    "group"                  : "udp_d2d",
}

