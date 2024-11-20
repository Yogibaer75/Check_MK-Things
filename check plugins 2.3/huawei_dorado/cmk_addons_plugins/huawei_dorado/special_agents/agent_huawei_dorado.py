#!/usr/bin/python3
'''special agent to fetch data from Huawei storage API'''
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2
# original script from https://github.com/aklyuk/zabbix-huawei-storages

import argparse
import json
import sys
from pathlib import Path

import requests
from cmk.special_agents.v0_unstable.agent_common import SectionWriter
from cmk.utils import password_store
import urllib3
from urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(InsecureRequestWarning)


def api_connect(api_user, api_password, api_ip, api_port):
    """connect to Huawei Dorado API"""
    api_url = f"https://{api_ip}:{api_port}/deviceManager/rest/xxxxx/sessions"
    api_data = json.dumps(
        {"scope": "0", "username": api_user, "password": api_password}
    )
    headers = {
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        api_connection = requests.post(
            api_url, verify=False, data=api_data, headers=headers, timeout=3
        )
        api_connect_info = (
            json.loads(api_connection.content.decode("utf8")),
            api_connection.cookies,
        )
    except requests.exceptions.ConnectTimeout:
        print("Exception: Timeout")
        sys.exit(1)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
    return api_connect_info


def api_logout(api_ip, api_port, api_cookies, device_id, i_base_token):
    '''logout from API'''
    headers = {
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "iBaseToken": i_base_token,
    }
    api_url_exit = f"https://{api_ip}:{api_port}/deviceManager/rest/{device_id}/sessions"
    exit_request = requests.delete(
        api_url_exit, verify=False, headers=headers, cookies=api_cookies, timeout=10
    )

    convert_exit = json.loads(exit_request.content.decode("utf8"))
    return convert_exit["error"]["code"]


def discovering_resources(api_user, api_password, api_ip, api_port, list_resources):
    '''get data from device and output'''
    api_connection = api_connect(api_user, api_password, api_ip, api_port)

    device_id = api_connection[0]["data"]["deviceid"]
    i_base_token = api_connection[0]["data"]["iBaseToken"]
    api_cookies = api_connection[1]
    headers = {
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "iBaseToken": i_base_token,
    }

    try:
        for resource in list_resources:
            resource_url = f"https://{api_ip}:{api_port}/deviceManager/rest/{device_id}/{resource}"
            resource_info = requests.get(
                resource_url, verify=False, cookies=api_cookies, headers=headers, timeout=10
            )
            resource_info = json.loads(resource_info.content.decode("cp1251"))

            if resource_info.get("data"):
                with SectionWriter(f"huawei_dorado_{resource}") as w:
                    for one_res in resource_info["data"]:
                        w.append_json(one_res)

        exit_code = api_logout(api_ip, api_port, api_cookies, device_id, i_base_token)
    except Exception as e:
        print(f"Exception: {e}")
        sys.exit(1)
    return exit_code


def main():
    '''parse args and call the functions'''
    huawei_parser = argparse.ArgumentParser()
    huawei_parser.add_argument(
        "--api_ip", action="store", help="Where to connect", required=True
    )
    huawei_parser.add_argument("--api_port", action="store", required=True)
    huawei_parser.add_argument("--api_user", action="store", required=True)
    huawei_parser.add_argument("--api_password", action="store", required=True)
    arguments = huawei_parser.parse_args()

    pw_id, pw_path = arguments.api_password.split(":")

    password = password_store.lookup(Path(pw_path), pw_id)

    list_resources = [
        "disk",
        "power",
        "enclosure",
        "controller",
        "backup_power",
        "expboard",
        "intf_module",
        "eth_port",
        "sas_port",
        "fc_port",
        "fan",
        "lun",
        "diskpool",
        "storagepool",
    ]
    exit_code = discovering_resources(
        arguments.api_user,
        password,
        arguments.api_ip,
        arguments.api_port,
        list_resources,
    )
    print("<<<>>>")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
