#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# (c) Jens Kühnel <fail2ban-checkmk@jens.kuehnel.org> 2021
#
# Information about fail2ban check_mk module see:
# https://github.com/JensKuehnel/fail2ban-check-mk
#
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


# Example for output from agent
# ---------------------------------------------------------
# <<<fail2ban>>>
# Detected jails: 	postfix-sasl  sshd
# Status for the jail: postfix-sasl
# |- Filter
# |  |- Currently failed:	7
# |  |- Total failed:	1839
# |  `- Journal matches:	_SYSTEMD_UNIT=postfix.service
# `- Actions
#    |- Currently banned:	1
#    |- Total banned:	76
#    `- Banned IP list:	212.70.149.71
# Status for the jail: sshd
# |- Filter
# |  |- Currently failed:	6
# |  |- Total failed:	1066
# |  `- Journal matches:	_SYSTEMD_UNIT=sshd.service + _COMM=sshd
# `- Actions
#    |- Currently banned:	5
#    |- Total banned:	50
#    `- Banned IP list:	112.122.54.162 144.135.85.184 103.200.21.89 1.14.61.204

from .agent_based_api.v1 import *


def discovery_fail2ban(section):
    firstline = section[0]
    if firstline[:2] == ['Detected', 'jails:']:
        for jail in firstline[2:]:
            yield Service(item=jail)


def check_fail2ban(item, params, section):
    currentjail = ""
    currentfailedcrit = params["failed"][1]
    currentfailedwarn = params["failed"][0]
    currentbannedcrit = params["banned"][1]
    currentbannedwarn = params["banned"][0]

    # set variable to check for jails that are not there anymore
    currentfailed = None
    currentbanned = None
    totalfailed = None
    totalbanned = None

    for entry in section:
        if (entry[:3]) == ['Status', 'for', 'the']:
            currentjail = entry[4]
        elif currentjail != item:
            # skip lines when this item is requested at the moment
            continue
        elif (entry[:4]) == ['|', '|-', 'Currently', 'failed:', ]:
            currentfailed = int(entry[4])
        elif (entry[:4]) == ['|', '|-', 'Total', 'failed:', ]:
            totalfailed = int(entry[4])
        elif (entry[:3]) == ['|-', 'Currently', 'banned:', ]:
            currentbanned = int(entry[3])
        elif (entry[:3]) == ['|-', 'Total', 'banned:', ]:
            totalbanned = int(entry[3])

    # removed jails should not create a crash,
    # so we dont yield anything and simply return without anything
    if (currentfailed is None) or \
            (totalfailed is None) or \
            (currentbanned is None) or \
            (totalbanned is None):
        return
    elif currentfailedcrit <= currentfailed or \
            currentbannedcrit <= currentbanned:
        s = State.CRIT
        status = "Crit"
    elif currentfailedwarn <= currentfailed or \
            currentbannedwarn <= currentbanned:
        s = State.WARN
        status = "Warn"
    else:
        s = State.OK
        status = "OK"

    yield Metric(
            name="current_failed",
            value=currentfailed,
            levels=(currentfailedwarn, currentfailedcrit)
            )
    yield Metric(
            name="total_failed",
            value=totalfailed,
            )
    yield Metric(
            name="current_banned",
            value=currentbanned,
            levels=(currentbannedwarn, currentbannedcrit)
            )
    yield Metric(
            name="total_banned",
            value=totalbanned,
            )

    yield Result(
            state=s,
            summary=f"{status} - {item} active - {currentfailed} failed ({totalfailed} total), {currentbanned} banned ({totalbanned} total)"
            )
    return


register.check_plugin(
        name="fail2ban",
        service_name="Jail %s",
        discovery_function=discovery_fail2ban,
        check_function=check_fail2ban,
        check_default_parameters={'banned': (10, 20), 'failed': (30, 40)},
        check_ruleset_name="fail2ban",
        )

