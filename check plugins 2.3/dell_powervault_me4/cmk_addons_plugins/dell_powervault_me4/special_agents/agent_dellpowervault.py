#!/usr/bin/env python3
"""Dell ME4 special agent"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>
# License: GNU General Public License v2

import argparse
import hashlib
import sys
from pathlib import Path

import requests
import urllib3
from cmk.special_agents.v0_unstable.agent_common import SectionWriter
from cmk.utils import password_store

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

password_store.replace_passwords()

commands = (
    "controllers",
    "disks",
    "system",
    "sensor-status",
    "power-supplies",
    "frus",
    "fans",
    "volumes",
    "pools",
    "controller-statistics",
    "volume-statistics",
    "ports",
)


def parse_arguments(argv):
    """argument parser"""
    parser = argparse.ArgumentParser(description=__doc__)

    # flags
    parser.add_argument(
        "-v", "--verbose", action="count", help="""Increase verbosity"""
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="""Debug mode: let Python exceptions come through""",
    )

    parser.add_argument("hostaddress", help="DELL EMC PowerVault host name")
    parser.add_argument("-u", "--username", required=True, help="DELL EMC user name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-p", "--password", help="DELL EMC user password from CMK password store"
    )
    group.add_argument(
        "-s",
        "--secret",
        help="DELL EMC user password manually entered",
    )
    parser.add_argument(
        "--verify-cert",
        action="store_true",
        help="Should TLS Certificate been verified",
    )

    args = parser.parse_args(argv)
    return args


def fetch_url(session, url, verify, timeout):
    """Fetch data from url"""
    return session.get(url, verify=verify, timeout=timeout)


def main(argv=None):
    """parse arguments and retrieve data from the device"""
    args = parse_arguments(argv or sys.argv[1:])

    if args.password:
        pw_id, pw_path = args.password.split(":")
        password = password_store.lookup(Path(pw_path), pw_id)
    else:
        password = args.secret

    url = "https://" + args.hostaddress
    auth_string = hashlib.sha256(
        f"{args.username}_{password}".encode("utf-8")
    ).hexdigest()

    verify = False
    if args.verify_cert:
        verify = True

    timeout = 5
    s = requests.session()
    s.headers.update({"datatype": "json"})
    r = fetch_url(s, url + "/api/login/" + auth_string, verify, timeout)
    sessionkey = r.json()["status"][0]["response"]
    s.headers.update({"sessionKey": sessionkey})

    for element in commands:
        response = fetch_url(s, url + "/api/show/" + element, verify, timeout)
        with SectionWriter(f"dell_powervault_me4_{element.replace('-', '_')}") as w:
            w.append_json(response.json())

    return 0


if __name__ == "__main__":
    sys.exit(main())
