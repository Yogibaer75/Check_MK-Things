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
#naviseccli -h 10.1.36.13 -User XXXX -Password XXXX -Scope0 getall < -sp>
#naviseccli -h 10.1.36.13 -User XXXX -Password XXXX -Scope0 getall < -disk>
#naviseccli -h 10.1.36.13 -User XXXX -Password XXXX -Scope0 getall < -array>
#naviseccli -h 10.1.36.13 -User XXXX -Password XXXX -Scope0 getall < -lun>

# command generic (rest less important)
# naviseccli -h 10.1.36.13 -User XXXX -Password XXXX -Scope0 getall <-host>
# < -array><-hba ><-sp><-cache><-disk><-lun><-rg><-sg>
# <-mirrorview><-snapviews><-sancopy><-reserved> <-cloneview><-metalun>
# <-migration><-ioportconfig> <-fastcache><-backendbus>

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
                                which may contain the keywords "disks", "hba", "hwstatus",
                                "raidgroups", "agent" or "all" to define which information
                                should be queried from the SP. You can define to use only
                                view of them to optimize performance. The default is "all".

""")

#############################################################################
# command line options
#############################################################################
short_options = 'hu:p:t:m:i:'
long_options  = [ 'help', 'user=', 'password=', 'debug', 'timeout=', 'profile', 'modules=' ]

try:
    opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
except getopt.GetoptError, err:
    sys.stderr.write("%s\n" % err)
    sys.exit(1)

opt_debug      = False
opt_timeout    = 60

g_profile      = None
g_profile_path = "emcvnx_profile.out"

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
}

for o,a in opts:
    if o in [ '--debug' ]:
        opt_debug = True
    elif o in [ '--profile' ]:
        import cProfile
        g_profile = cProfile.Profile()
        g_profile.enable()
    elif o in [ '-u', '--user' ]:
        user = a
    elif o in [ '-p', '--password' ]:
        password = a
    elif o in [ '-i', '--modules' ]:
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

cmd = basecmd + "/env/general show -output csv"
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
    if tokens[2] == "EMC Storage System":
        emcvnxe_version = "_".join(tokens[1:2])
        emcvnxe_version = emcvnxe_version.replace(" ","_").replace("\"","")

print "<<<check_mk>>>"
print "Version: %s" % emcvnx_version

# maybe we could fill AgentOS: by reading "Model:" line of naviseccli output
# in section "Agent/Host Information", but need a call of naviseccli with an
# other commandline argument
#print "AgentOS: %s " % emcvnx_model

print "<<<emcvnxe_info>>>"
for line in cmdout:
    print line

# if module "agent" was requested, fetch additional information about the
# agent, e. g. Model and Revision
#if fetch_agent_info:
#    cmd=basecmd + "getagent"
#    if opt_debug:
#        sys.stderr.write("executing external command: %s\n" % cmd)
#
#    for line in os.popen(cmd).readlines():
#        print line,
#
#
# all other sections of agent output
#
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


#############################################################################
#def output_profile():
#############################################################################
#    g_profile.dump_stats(g_profile_path)
#    show_profile = os.path.join(os.path.dirname(g_profile_path), 'show_profile.py')
#    file(show_profile, "w")\
#        .write("#!/usr/bin/python\n"
#               "import pstats\n"
#               "stats = pstats.Stats('%s')\n"
#               "stats.sort_stats('time').print_stats()\n" % g_profile_path)
#    os.chmod(show_profile, 0755)
#
#    sys.stderr.write("Profile '%s' written. Please run %s.\n" % (g_profile_path, show_profile))
#
#if g_profile:
#    output_profile()
