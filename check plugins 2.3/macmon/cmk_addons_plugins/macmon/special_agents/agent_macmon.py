#!/usr/bin/env python3
'''macmon special agent'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

import base64
import csv
from pathlib import Path
from typing import Any, Dict, Optional, Sequence
from urllib.request import Request, build_opener

from cmk.special_agents.v0_unstable.agent_common import special_agent_main
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser,
)
from cmk.special_agents.v0_unstable.request_helper import (
    HTTPSAuthHandler,
    HTTPSConfigurableConnection,
    Requester,
)
from cmk.utils import password_store

StringMap = Dict[str, str]  # should be Mapping[] but we're not ready yet..


class HTTPSAuthRequester(Requester):
    """http requester"""

    def __init__(
        self,
        server: str,
        port: int,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        self._req_headers = {
            "Authorization":
            f'Basic {base64.encodebytes(f"{username}:{password}".encode()).strip().decode()}'
        }
        self._base_url = f"https://{server}:{port}/{base_url}"
        self._opener = build_opener(
            HTTPSAuthHandler(HTTPSConfigurableConnection.IGNORE)
        )

    def get(self, path: str, parameters: Optional[StringMap] = None) -> Any:
        """get date from url"""
        url = f"{self._base_url}/{path}/"
        if parameters is not None:
            url = f"{url}?{'&'.join([f'{par[0]}={par[1]}' for par in parameters.items()])}"

        request = Request(url, headers=self._req_headers)
        response = self._opener.open(request)
        return response.read()


def parse_arguments(argv: Optional[Sequence[str]]) -> Args:
    """argument parser"""
    parser = create_default_argument_parser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for connect",
    )
    parser.add_argument(
        "--server",
        type=str,
        required=True,
        metavar="ADDRESS",
        help="host to connect to",
    )
    parser.add_argument("--port", type=int, metavar="PORT", default=443)
    parser.add_argument(
        "--username", type=str, required=True, metavar="USER", help="user account"
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        metavar="PASSWORD",
        help="password for that account",
    )

    return parser.parse_args(argv)


def agent_macmon_main(args: Args) -> None:
    """agent function"""
    pw_id, pw_path = args.password.split(":")
    password = password_store.lookup(Path(pw_path), pw_id)
    requester = HTTPSAuthRequester(
        args.server,
        args.port,
        "api/v1.1/reports",
        args.username,
        password,
    )

    result = requester.get(
        "unauthorisedMacs",
        parameters={"format": "csv"},
    )

    result = result.decode("utf-8")
    string_list = []
    for line in result:
        string_list.append(line)

    csvdata = "".join(string_list)

    cr = csv.DictReader(csvdata.splitlines(), delimiter=";")

    final_data = {}
    for row in cr:
        final_data.setdefault(row["MAC"], row)

    print("<<<macmon_unauth:sep(124)>>>")
    for line in final_data.items():
        print(f"{final_data[line].get("MAC")}|{final_data[line].get("Last seen (IF)")}"
              f"|{final_data[line].get("Network device")}|{final_data[line].get("IfIndex")}")


def main() -> None:
    """special agent main"""
    special_agent_main(parse_arguments, agent_macmon_main)


if __name__ == "__main__":
    main()
