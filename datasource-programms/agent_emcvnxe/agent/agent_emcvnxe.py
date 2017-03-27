#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# commands to be issued
#uemcli.sh -silent -d 10.1.36.13 -user XXXX -password XXXX show </env/ssd> -output csv
#uemcli.sh -silent -d 10.1.36.13 -user XXXX -password XXXX show </env/ps> -output csv
#uemcli.sh -silent -d 10.1.36.13 -user XXXX -password XXXX show </env/dae> -output csv
#uemcli.sh -silent -d 10.1.36.13 -user XXXX -password XXXX show </env/disk> -output csv
# without user and password
#uemcli.sh -silent -d 10.1.36.13 show </env/disk> -output csv

import sys, os, getopt, re, subprocess

import inspect, pprint # FOR DEBUGGING

#############################################################################
def usage():
#############################################################################
    sys.stderr.write("""Check_MK EMC VNXe Agent

USAGE: agent_emcvnxe [OPTIONS] HOST
       agent_emcvnxe -h

ARGUMENTS:
  HOST                          Host name or IP address of the target SP

OPTIONS:
  -h, --help                    Show this help message and exit
  -u USER, --user USER          Username for EMC VNXe login
  -p PASSWORD, --password PASSWORD  Password for EMC VNXe login

                                If you do not give USER and PASSWORD:
                                We try to use uemcli with security files.
                                These need to be created in advance by running as
                                the instance user:
                                uemcli.sh -d HOST -u USER -p PASSWORD -saveUser

  --debug                       Debug mode: write some debug messages,
                                let Python exceptions come through

  --profile                     Enable performance profiling in Python source code

  -i MODULES, --modules MODULES Modules to query. This is a comma separated list of
                                which may contain the keywords "ssd", "ps", "iomodule",
                                "dae", "lcc" or "all" to define which information
                                should be queried from the SP. You can define to use only
                                view of them to optimize performance. The default is "all".

""")

#############################################################################
# command line options
#############################################################################
short_options = 'hu:p:t:m:'
long_options  = [ 'help', 'user=', 'password=', 'debug', 'timeout=', 'modules=' ]

try:
    opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
except getopt.GetoptError, err:
    sys.stderr.write("%s\n" % err)
    sys.exit(1)

opt_debug      = False
opt_timeout    = 60

host_address   = None
user           = None
password       = None
mortypes       = [ 'all' ]
fetch_agent_info = False

naviseccli_options = {
    "ssd"      : {"cmd_option" : "/env/ssd",     "active" : False, "sep" : 44},
    "ps"       : {"cmd_option" : "/env/ps",      "active" : False, "sep" : 44},
    "iomodule" : {"cmd_option" : "/env/iomodule","active" : False, "sep" : 44},
    "dae"      : {"cmd_option" : "/env/dae",     "active" : False, "sep" : 44},
    "lcc"      : {"cmd_option" : "/env/lcc",     "active" : False, "sep" : 44},
    "sp"       : {"cmd_option" : "/env/sp",      "active" : False, "sep" : 44},
    "dpe"      : {"cmd_option" : "/env/dpe",     "active" : False, "sep" : 44},
    "disk"     : {"cmd_option" : "/env/disk",    "active" : False, "sep" : 44},
    "mm"       : {"cmd_option" : "/env/mm",      "active" : False, "sep" : 44},
    "ccard"    : {"cmd_option" : "/env/ccard",   "active" : False, "sep" : 44},
    "bat"      : {"cmd_option" : "/env/bat",     "active" : False, "sep" : 44},
}

for o,a in opts:
    if o in [ '--debug' ]:
        opt_debug = True
    elif o in [ '-u', '--user' ]:
        user = a
    elif o in [ '-p', '--password' ]:
        password = a
    elif o in [ '-m', '--modules' ]:
        mortypes = a.split(',')
    elif o in [ '-t', '--timeout' ]:
        opt_timeout = int(a)
    elif o in [ '-h', '--help' ]:
        usage()
        sys.exit(0)

if len(args) == 1:
    host_address = args[0]
elif not args:
    sys.stderr.write("ERROR: No host given.\n")
    sys.exit(1)
else:
    sys.stderr.write("ERROR: Please specify exactly one host.\n")
    sys.exit(1)

for module in naviseccli_options.keys():

    try:
        if mortypes.index("all") >= 0:
            naviseccli_options[module]["active"] = True
            fetch_agent_info = True
    except ValueError:
        pass

    try:
        if mortypes.index(module) >= 0:
            naviseccli_options[module]["active"] = True
    except ValueError:
        pass

try:
    if mortypes.index("agent") >= 0:
        fetch_agent_info = True
except ValueError:
    pass

#############################################################################
# fetch information by calling uemcli
#############################################################################

if (user == None or user == '') and (password == None or password == ''):
    # try using security files
    basecmd = "/opt/emc/uemcli/bin/uemcli.sh -silent -d %s " % host_address
else:
    basecmd = "/opt/emc/uemcli/bin/uemcli.sh -silent -d %s -user %s -password '%s' " % (host_address, user, password)

#
# check_mk section of agent output
#

cmd = basecmd + "/sys/general show -output csv"
if opt_debug:
    sys.stderr.write("executing external command: %s\n" % cmd)

# Now read the whole output of the command
cmdout = [ l.strip() for l in os.popen(cmd + " 2>&1").readlines() ]

if cmdout:
    if "uemcli.sh: not found" in cmdout[0]:
        sys.stderr.write("The command \"uemcli.sh\" could not be found. Terminating.\n")
        sys.exit(1)

    elif cmdout[0].startswith("You do not have access"):
        sys.stderr.write("Could not find security file. Please provide valid user "
                         "credentials if you don't have a security file.\n")
        sys.exit(1)

# Try to gather the version of the agent
emcvnxe_version = None
for line in cmdout:
    tokens = re.split(",", line)
    if tokens[2] == "\"EMC Storage System\"":
        emcvnxe_version = "_".join(tokens[1:3])
        emcvnxe_version = emcvnxe_version.replace(" ","_").replace("\"","")

print "<<<check_mk>>>"
print "Version: %s" % emcvnxe_version

# maybe we could fill AgentOS: by reading "Model:" line of naviseccli output
# in section "Agent/Host Information", but need a call of naviseccli with an
# other commandline argument
#print "AgentOS: %s " % emcvnx_model

print "<<<emcvnxe_info:sep(44)>>>"
for line in cmdout:
    print line

for module in naviseccli_options.keys():
    if naviseccli_options[module]["active"] == True:
        separator = naviseccli_options[module]["sep"]
        if separator:
            print "<<<emcvnxe_%s:sep(%s)>>>" % (module, separator)
        else:
            print "<<<emcvnxe_%s>>>" % module
        cmd=basecmd + naviseccli_options[module]["cmd_option"] + " show -output csv"
        if opt_debug:
            sys.stderr.write("executing external command: %s\n" % cmd)
        for line in os.popen(cmd).readlines():
            print line,

