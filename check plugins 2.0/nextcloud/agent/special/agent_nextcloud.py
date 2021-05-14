#!/usr/bin/env python3
import json
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--debug",
                        action="store_true",
                        help='''Debug mode: raise Python exceptions''')
    parser.add_argument("-v",
                        "--verbose",
                        action="count",
                        default=0,
                        help='''Verbose mode (for even more output use -vvv)''')
    parser.add_argument("-u",
                        "--username",
                        type=str,
                        help='''username for connection''')
    parser.add_argument("-p",
                        "--password",
                        type=str,
                        help='''password for connection''')
    parser.add_argument("-s",
                        "--server",
                        type=str,
                        help='''server to connect to''')
    parser.add_argument("-t",
                        "--schema",
                        type=str,
                        default="http",
                        help='''Connection type http or https''')
    parser.add_argument("-e",
                        "--prefix",
                        type=str,
                        help='''Path prefix before the normal API url must end with /''')

    args = parser.parse_args(argv)
    return args


def main(argv=None):

    if argv is None:
        argv = sys.argv[1:]

    print('<<<nextcloud:sep(0)>>>')

    args = parse_arguments(argv)
    api_path = 'ocs/v2.php/apps/serverinfo/api/v1/info?format=json'
    if args.prefix:
        api_path = args.prefix + api_path
    url =  args.schema + '://' + args.server + '/' + api_path

    response = requests.get(url, auth=HTTPBasicAuth(args.username, args.password))
    json_response = json.loads(response.text)
    print(json_response)


if __name__ == '__main__':
    sys.exit(main())
