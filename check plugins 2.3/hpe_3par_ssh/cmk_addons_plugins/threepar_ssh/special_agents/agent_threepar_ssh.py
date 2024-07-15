#!/usr/bin/env python3
"""Special agent for HPE 3Par"""

# (c) Andreas Doehler 'andreas.doehler@bechtle.com'
# License: GNU General Public License v2

# needs to issue a command like
# ssh USER@HOSTNAME 'showld'
#
# This agent uses the original special agent for IBM SVC only modified
# for HP 3par storage
#

import sys
import getopt
import subprocess


def usage():
    '''help text'''
    sys.stderr.write(
        """Check_MK 3par Agent

USAGE: agent_3par [OPTIONS] HOST
       agent_3par -h

ARGUMENTS:
  HOST                          Host name or IP address of the target device

OPTIONS:
  -h, --help                    Show this help message and exit
  -u USER, --user USER          Username for 3par Login

                                We try to use SSH key authentification.
                                Private key must be pre-created in ~/.ssh/

  -k, --accept-any-hostkey      Accept any SSH Host Key
                                Please note: This might be a security issue because
                                man-in-the-middle attacks are not recognized

  --debug                       Debug mode: write some debug messages,
                                let Python exceptions come through

  --profile                     Enable performance profiling in Python source code

  -i MODULES, --modules MODULES Modules to query. This is a comma separated list of
                                which may contain the keywords "showcage", "showpd",
                                "showld", "showvv", "showps", "shownode",
                                or "all" to define which information should be queried
                                from the device.
                                You can define to use only view of them to optimize
                                performance. The default is "all".

"""
    )


def main():
    '''special agent main function'''
    #############################################################################
    # command line options
    #############################################################################
    short_options = "hu:p:t:m:i:k"
    long_options = [
        "help",
        "user=",
        "debug",
        "timeout=",
        "profile",
        "modules=",
        "accept-any-hostkey",
    ]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_options, long_options)
    except getopt.GetoptError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(1)

    opt_debug = False
    opt_timeout = 10
    opt_any_hostkey = ""

    host_address = None
    user = None
    mortypes = ["all"]

    command_options = {
        "showcage": {"section_header": "3par_cage", "active": False, "command": "showcage"},
        "showpd": {"section_header": "3par_pd", "active": False, "command": "showpd"},
        "showld": {"section_header": "3par_ld", "active": False, "command": "showld"},
        "showvv": {"section_header": "3par_vv", "active": False, "command": "showvv"},
        "showps": {
            "section_header": "3par_ps",
            "active": False,
            "command": "shownode -ps -nohdtot",
        },
        "shownode": {
            "section_header": "3par_node",
            "active": False,
            "command": "shownode -nohdtot",
        },
    }

    for o, a in opts:
        if o in ["--debug"]:
            opt_debug = True
        elif o in ["-u", "--user"]:
            user = a
        elif o in ["-i", "--modules"]:
            mortypes = a.split(",")
        elif o in ["-t", "--timeout"]:
            opt_timeout = int(a)
        elif o in ["-k", "--accept-any-hostkey"]:
            opt_any_hostkey = "-o StrictHostKeyChecking=no"
        elif o in ["-h", "--help"]:
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

    if user is None:
        sys.stderr.write("ERROR: No user name given.\n")
        sys.exit(1)

    for module, data in command_options.items():
        try:
            if mortypes.index("all") >= 0:
                data["active"] = True
        except ValueError:
            pass

        try:
            if mortypes.index(module) >= 0:
                data["active"] = True
        except ValueError:
            pass

    cmd = ""
    cmdcore = (
        f"ssh -o ConnectTimeout={opt_timeout} {opt_any_hostkey} {user}@{host_address} '"
    )

    for module, data in command_options.items():
        if data["active"] is True:
            print(f"<<<{data['section_header']}>>>")
            cmd = cmdcore
            cmd += f"{data['command']}"
            cmd += "'"
            if opt_debug:
                sys.stderr.write(f"executing external command: {cmd}\n")
            result = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=None
            )
            stdout, stderr = result.communicate()
            exit_code = result.wait()
            lines = stdout.split(b"\n")
            for line in lines:
                print(line.decode("utf-8"))

    if exit_code not in [0, 1]:
        sys.stderr.write(f"Error connecting via ssh: {stderr}\n")
        sys.exit(2)
