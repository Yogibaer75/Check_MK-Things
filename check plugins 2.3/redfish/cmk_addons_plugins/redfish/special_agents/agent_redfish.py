#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""Special Agent to fetch Redfish data from management interfaces"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

import json
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import redfish
import urllib3
from cmk.special_agents.v0_unstable.agent_common import (
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser,
)
from cmk.utils import password_store, paths, store
from redfish.rest.v1 import (
    RetriesExhaustedError,
    ServerDownOrUnreachableError,
    JsonDecodingError,
)
from cmk_addons.plugins.redfish.tools import (
    verify_response,
    get_object_ids,
)


def parse_arguments(argv: Sequence[str] | None) -> Args:
    """Parse arguments needed to construct an URL and for connection conditions"""
    sections = [
        "Power",
        "Thermal",
        "Memory",
        "NetworkAdapters",
        "NetworkInterfaces",
        "Processors",
        "Storage",
        "EthernetInterfaces",
        "FirmwareInventory",
        "SmartStorage",
        "ArrayControllers",
        "HostBusAdapters",
        "LogicalDrives",
        "PhysicalDrives",
        "SimpleStorage",
        "Drives",
        "Volumes",
    ]

    parser = create_default_argument_parser(description=__doc__)
    # required
    parser.add_argument(
        "-u", "--user", default=None, help="Username for Redfish Login", required=True
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--password",
        default=None,
        help="""Password for Redfish Login. Preferred over --password-id""",
    )
    group.add_argument(
        "--password-id",
        default=None,
        help="""Password store reference to the password for Redfish login""",
    )
    # optional
    parser.add_argument(
        "-P",
        "--proto",
        default="https",
        help="""Use 'http' or 'https' (default=https)""",
    )
    parser.add_argument(
        "-p",
        "--port",
        default=443,
        type=int,
        help="Use alternative port (default: 443)",
    )
    parser.add_argument(
        "-m",
        "--sections",
        default=",".join(sections),
        help=f"Comma separated list of data to query. \
               Possible values: {','.join(sections)} (default: all)",
    )
    parser.add_argument(
        "-n",
        "--disabled_sections",
        help=f"Comma separated list of data to ignore. \
               Possible values: {','.join(sections)} (default: None)",
    )
    parser.add_argument(
        "--verify_ssl",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--timeout",
        default=3,
        type=int,
        help="""Timeout in seconds for a connection attempt""",
    )
    parser.add_argument(
        "--retries",
        default=2,
        type=int,
        help="""Number auf connection retries before failing""",
    )
    # required
    parser.add_argument(
        "host",
        metavar="HOSTNAME",
        help="""IP address or hostname of your Redfish compatible BMC""",
    )

    return parser.parse_args(argv)


def dropnonascii(input_str):
    """Drop all non ASCII characters from string"""
    output_str = ""
    for i in input_str:
        num = ord(i)
        if num >= 0:
            if num <= 127:
                output_str = output_str + i

    return output_str


def fetch_data(redfishobj, url, component):
    """fetch a single data object from Redfish"""
    response_url = redfishobj.get(url, None)
    if response_url.status == 200:
        try:
            response_dict = response_url.dict
            return response_dict
        except JsonDecodingError:
            return {"error": f"{component} data had a JSON decoding problem\n"}

    return {"error": f"{component} data could not be fetched\n"}


def fetch_collection(redfishobj, data, component):
    """fetch a whole collection from Redfish data"""
    member_list = data.get("Members")
    data_list = []
    if not member_list:
        return data_list
    for element in member_list:
        if element.get("@odata.id"):
            element_data = fetch_data(redfishobj, element.get("@odata.id"), component)
            data_list.append(element_data)
    return data_list


def fetch_list_of_elements(redfishobj, fetch_elements, sections, data):
    """fetch a list of single elements from Redfish"""
    result_set = {}
    for element in fetch_elements:
        result_list = []
        element_list = []
        if element not in sections:
            continue
        if element not in data.keys():
            continue

        fetch_result = data.get(element)
        if isinstance(fetch_result, dict):
            element_list.append(fetch_result)
        else:
            element_list = fetch_result
        for entry in element_list:
            result = fetch_data(redfishobj, entry.get("@odata.id"), element)
            # debug output of fetching element
            # sys.stdout.write(f'Fetching {entry.get("@odata.id")}')
            if "error" in result.keys():
                continue
            if "Collection" in result.get("@odata.type", "No Data"):
                result_list.extend(fetch_collection(redfishobj, result, element))
            else:
                result_list.append(result)
        result_set[element] = result_list
    return result_set


def fetch_sections(redfishobj, fetching_sections, sections, data):
    """fetch a single section of Redfish data"""
    result_set = {}
    for section in fetching_sections:
        if section not in sections:
            continue
        if section not in data.keys():
            continue
        section_data = fetch_data(
            redfishobj, data.get(section).get("@odata.id"), section
        )
        if section_data.get("Members@odata.count") == 0:
            continue
        if "Collection" in section_data.get("@odata.type", {}):
            if section_data.get("Members@odata.count", 0) != 0:
                result = fetch_collection(redfishobj, section_data, section)
                result_set[section] = result
        else:
            result_set[section] = section_data
    return result_set


def fetch_hpe_smartstorage(redfishobj, link_list, sections):
    """fetch hpe smartstorage sections"""
    storage_link = link_list.get("SmartStorage", None)
    if storage_link:
        result = fetch_data(redfishobj, storage_link.get("@odata.id"), "SmartStorage")
        storage_links = result.get("Links")
        storage_sections = [
            "ArrayControllers",
            "HostBusAdapters",
        ]
        controller_sections = [
            "LogicalDrives",
            "PhysicalDrives",
        ]
        resulting_sections = list(set(storage_sections).intersection(sections))
        cntrl_result = fetch_sections(
            redfishobj, resulting_sections, sections, storage_links
        )
        process_result(cntrl_result)
        for element in cntrl_result.get("ArrayControllers", []):
            contrl_links = element.get("Links", {})
            resulting_sections = list(set(controller_sections).intersection(sections))
            result = fetch_sections(
                redfishobj, resulting_sections, sections, contrl_links
            )
            process_result(result)


def fetch_extra_data(redfishobj, data_model, extra_links, sections, data):
    """fetch manufacturer specific data"""
    link_list = {}
    link_data = data.get("Oem", {}).get(data_model, {}).get("Links", {})
    if link_data:
        for entry in link_data:
            if entry in extra_links:
                link_list.setdefault(entry, link_data.get(entry))
        if "SmartStorage" in link_list:
            fetch_hpe_smartstorage(redfishobj, link_list, sections)
            link_list.pop("SmartStorage")
        result = fetch_sections(redfishobj, extra_links, sections, link_list)
        process_result(result)


def process_result(result):
    """process and output a fetched result set"""
    for element in list(result.keys()):
        with SectionWriter(f"redfish_{element.lower()}") as w:
            if isinstance(result.get(element), list):
                for entry in result.get(element):
                    w.append_json(entry)
            else:
                w.append_json(result.get(element))


class VendorGeneric:
    """Generic Vendor Definition"""

    name = "Generic"
    version = None
    firmware_version = None
    view_supported = False
    view_select = None
    expand_string = ""
    manager_data = None
    system_data = None
    chassis_data = None
    base_data = None


class VendorHPEData(VendorGeneric):
    """HPE specific settings"""

    name = "HPE"
    version = None
    firmware_version = None
    expand_string = "?$expand=."

    """
        Select and store view (supported from ILO 5)
        ATTENTION: This will only work as long as we are querying servers
        with "1" System, "1" Chassi and "1" Manager
        OK for now but will be changed once we have to query blade centers
    """
    view_supported = False
    view_select = {
        "Select": [
            {
                "From": f"/Systems/1/Memory/{expand_string}",
                "Properties": ["Members AS Memory"],
            },
            {
                "From": f"/Systems/1/Processors/{expand_string}",
                "Properties": ["Members AS Processors"],
            },
            {
                "From": f"/Systems/1/EthernetInterfaces/{expand_string}",
                "Properties": ["Members AS EthernetInterfaces"],
            },
            {
                "From": f"/Systems/1/BaseNetworkAdapters/{expand_string}",
                "Properties": ["Members AS NetworkAdapters"],
            },
            {
                "From": f"/Chassis/1/Power/{expand_string}",
                "Properties": ["PowerSupplies", "Redundancy AS PowerRedundancy"],
            },
            {"From": "/Chassis/1/Thermal/", "Properties": ["Temperatures", "Fans"]},
            {"From": f"/Managers/{expand_string}", "Properties": ["Members as ILO"]},
            {
                "From": f"/Managers/1/EthernetInterfaces/{expand_string}",
                "Properties": ["Members as ILOInterfaces"],
            },
        ]
    }
    view_response = None


class VendorLenovoData(VendorGeneric):
    """Lenovo specific settings"""

    name = "Lenovo"
    version = None
    firmware_version = None
    expand_string = "?$expand=*"


class VendorDellData(VendorGeneric):
    """Dell specific settings"""

    name = "Dell"
    version = None
    firmware_version = None
    expand_string = "?$expand=*($levels=1)"


class VendorHuaweiData(VendorGeneric):
    """Huawei specific settings"""

    name = "Huawei"
    version = None
    firmware_version = None
    expand_string = "?$expand=.%28$levels=1%29"


class VendorFujitsuData(VendorGeneric):
    """Fujitsu specific settings"""

    name = "Fujitsu"
    version = None
    firmware_version = None
    expand_string = "?$expand=Members"


class VendorCiscoData(VendorGeneric):
    """Cisco specific settings"""

    name = "Cisco"
    version = None
    firmware_version = None
    expand_string = ""


class VendorAmiData(VendorGeneric):
    """Ami specific settings"""

    name = "Ami"
    version = None
    firmware_version = None
    expand_string = ""


class VendorSupermicroData(VendorGeneric):
    """Supermicro specific settings"""

    name = "Supermicro"
    version = None
    firmware_version = None
    expand_string = ""


class VendorSeagateData(VendorGeneric):
    """Seagate specific settings"""

    name = "Seagate"
    version = None
    firmware_version = None
    expand_string = ""


def detect_vendor(root_data):
    """Extract Vendor information from base data"""
    vendor_string = ""
    if root_data.get("Oem"):
        if len(root_data.get("Oem")) > 0:
            vendor_string = list(root_data.get("Oem"))[0]
    if vendor_string == "" and root_data.get("Vendor") is not None:
        vendor_string = root_data.get("Vendor")

    if vendor_string in ["Hpe", "Hp"]:
        vendor_data = VendorHPEData()
        if vendor_string in ["Hp"]:
            vendor_data.expand_string = ""
        manager_data = (
            root_data.get("Oem", {}).get(vendor_string, {}).get("Manager", {})[0]
        )
        if manager_data:
            vendor_data.version = manager_data.get("ManagerType")
            if vendor_data.version is None:
                vendor_data.version = (
                    root_data.get("Oem", {})
                    .get(vendor_string, {})
                    .get("Moniker", {})
                    .get("PRODGEN")
                )
            vendor_data.firmware_version = manager_data.get("ManagerFirmwareVersion")
            if vendor_data.firmware_version is None:
                vendor_data.firmware_version = manager_data.get("Languages", {})[0].get(
                    "Version"
                )
            if vendor_data.version.lower() == "ilo 5":
                vendor_data.view_supported = True
    elif vendor_string in ["Lenovo"]:
        vendor_data = VendorLenovoData()
    elif vendor_string in ["Dell"]:
        vendor_data = VendorDellData()
        vendor_data.version = "iDRAC"
    elif vendor_string in ["Huawei"]:
        vendor_data = VendorHuaweiData()
    elif vendor_string in ["ts_fujitsu"]:
        vendor_data = VendorFujitsuData()
        vendor_data.version = "iRMC"
    elif vendor_string in ["Ami"]:
        vendor_data = VendorAmiData()
    elif vendor_string in ["Supermicro"]:
        vendor_data = VendorSupermicroData()
    elif vendor_string in ["Cisco", "Cisco Systems Inc."]:
        vendor_data = VendorCiscoData()
        vendor_data.version = "CIMC"
    elif vendor_string in ["Seagate"]:
        vendor_data = VendorSeagateData()
    else:
        vendor_data = VendorGeneric()

    return vendor_data


def get_information(redfishobj, sections):
    """get a the information from the Redfish management interface"""
    base_data = fetch_data(redfishobj, "/redfish/v1", "Base")

    vendor_data = detect_vendor(base_data)

    manager_url = base_data.get("Managers", {}).get("@odata.id")
    chassis_url = base_data.get("Chassis", {}).get("@odata.id")
    systems_url = base_data.get("Systems", {}).get("@odata.id")

    data_model = ""
    manager_data = False

    # fetch managers
    if manager_url:
        if vendor_data.expand_string:
            manager_col = fetch_data(
                redfishobj, manager_url + vendor_data.expand_string, "Manager"
            )
            manager_data = manager_col.get("Members", [])
        else:
            manager_col = fetch_data(redfishobj, manager_url, "Manager")
            manager_data = fetch_collection(redfishobj, manager_col, "Manager")

        for element in manager_data:
            data_model = list(element.get("Oem", {"Unknown": "Unknown model"}).keys())[
                0
            ]
            if not vendor_data.firmware_version:
                vendor_data.firmware_version = element.get("FirmwareVersion", "")

    with SectionWriter("check_mk", " ") as w:
        w.append("Version: 2.0")
        w.append(f"AgentOS: {vendor_data.version} - {vendor_data.firmware_version}")

    # fetch systems
    systems_col = fetch_data(redfishobj, systems_url, "System")
    systems_data = fetch_collection(redfishobj, systems_col, "System")

    if data_model in ["Hpe", "Hp"]:
        data_model_links = []
        for system in systems_data:
            system_oem_links = list(
                system.get("Oem", {"Unknown": "Unknown model"})
                .get(data_model, {"Unknown": "Unknown model"})
                .get("Links", {})
                .keys()
            )
            data_model_links.extend(system_oem_links)
        extra_links = list(set(data_model_links).intersection(sections))
    else:
        extra_links = []

    if data_model in ["Hp"]:
        res_dir = (
            base_data.get("Oem", {"Unknown": "Unknown model"})
            .get(data_model, {"Unknown": "Unknown model"})
            .get("Links", {})
            .get("ResourceDirectory", {})
            .get("@odata.id")
        )
        if res_dir:
            res_data = fetch_data(redfishobj, res_dir, "ResourceDirectory")
            res_instances = res_data.get("Instances", [])
            for instance in res_instances:
                if "#FwSwVersionInventory." in instance.get(
                    "@odata.type", ""
                ) and "FirmwareInventory" in instance.get("@odata.id", ""):
                    firmwares = fetch_data(
                        redfishobj,
                        instance["@odata.id"] + vendor_data.expand_string,
                        "FirmwareDirectory",
                    )
                    if firmwares.get("Current"):
                        with SectionWriter("redfish_firmware_hpe_ilo4") as w:
                            w.append_json(firmwares.get("Current"))

    if manager_data:
        with SectionWriter("redfish_manager") as w:
            w.append_json(manager_data)

    with SectionWriter("redfish_system") as w:
        w.append_json(systems_data)

    systems_sections = list(
        set(
            [
                "FirmwareInventory",
                "EthernetInterfaces",
                "NetworkInterfaces",
                "Processors",
                "Storage",
                "Memory",
            ]
        ).union(extra_links)
    )
    systems_sub_sections = [
        "Drives",
        "Volumes",
    ]

    resulting_sections = list(set(systems_sections).intersection(sections))
    if "FirmwareInventory" in resulting_sections and base_data.get(
        "UpdateService", {}
    ).get("@odata.id"):
        firmware_url = (
            base_data.get("UpdateService").get("@odata.id"),
            "/FirmwareInventory",
            vendor_data.expand_string,
        )
        if vendor_data.expand_string:
            firmwares = fetch_data(
                redfishobj,
                ''.join(firmware_url),
                "FirmwareDirectory",
            )
            if firmwares.get("Members"):
                with SectionWriter("redfish_firmware") as w:
                    w.append_json(firmwares.get("Members"))
        else:
            firmware_col = fetch_data(
                redfishobj,
                ''.join(firmware_url),
                "FirmwareDirectory",
            )
            firmwares = fetch_collection(redfishobj, firmware_col, "Manager")
            with SectionWriter("redfish_firmware") as w:
                w.append_json(firmwares)

    for system in systems_data:
        if data_model in ["Hpe", "Hp"] and "SmartStorage" in resulting_sections:
            if vendor_data.firmware_version.startswith("3."):
                resulting_sections.remove("SmartStorage")
            elif "Storage" in resulting_sections:
                resulting_sections.remove("Storage")
        result = fetch_sections(redfishobj, resulting_sections, sections, system)
        process_result(result)
        if "Storage" in result:
            storage_data = result.get("Storage")
            if isinstance(storage_data, list):
                for entry in storage_data:
                    if entry.get("error"):
                        continue
                    if (
                        entry.get("Drives@odata.count", 0) != 0
                        or len(entry.get("Drives", [])) >= 1
                    ):
                        result = fetch_list_of_elements(
                            redfishobj, systems_sub_sections, sections, entry
                        )
                        process_result(result)
            else:
                result = fetch_list_of_elements(
                    redfishobj, systems_sub_sections, sections, storage_data
                )
                process_result(result)

        if extra_links:
            fetch_extra_data(redfishobj, data_model, extra_links, sections, system)

    # fetch chassis
    chassis_col = fetch_data(redfishobj, chassis_url, "Chassis")
    chassis_data = fetch_collection(redfishobj, chassis_col, "Chassis")
    with SectionWriter("redfish_chassis") as w:
        w.append_json(chassis_data)
    chassis_sections = [
        "NetworkAdapters",
        "Power",
        "Thermal",
    ]
    new_environment_resources = [
        "Sensors",
        "EnvironmentMetrics",
        "PowerSubsystem",
        "ThermalSubsystem",
    ]

    resulting_sections = list(set(chassis_sections).intersection(sections))
    for chassis in chassis_data:
        result = fetch_sections(redfishobj, resulting_sections, sections, chassis)
        process_result(result)

    return 0


def store_session_key(redfishobj, host):
    """save session data to file"""
    store_data = {}
    store_path = paths.tmp_dir / "agents" / "agent_redfish" / f"{host}.json"
    store_data.setdefault("location", redfishobj.get_session_location())
    store_data.setdefault("session", redfishobj.get_session_key())
    store.save_text_to_file(store_path, json.dumps(store_data))


def load_session_key(host):
    """load existing redfish session data"""
    store_path = paths.tmp_dir / "agents" / "agent_redfish" / f"{host}.json"
    data = json.loads(store.load_text_from_file(store_path, default="{}"))
    if data.get("session") and data.get("location"):
        return data
    return None


def get_session(args: Args):
    """create a Redfish session with given arguments"""
    try:
        redfish_host = f"{args.proto}://{args.host}:{args.port}"
        if args.password_id:
            pw_id, pw_path = args.password_id.split(":")
        # Create a Redfish client object
        redfishobj = redfish.redfish_client(
            base_url=redfish_host,
            username=args.user,
            password=(
                args.password
                if args.password is not None
                else password_store.lookup(Path(pw_path), pw_id)
            ),
            cafile="",
            default_prefix="/redfish/v1",
            timeout=args.timeout,
            max_retry=args.retries,
        )
        existing_session = load_session_key(args.host)
        # existing session with key found reuse this session instead of login
        if existing_session:
            redfishobj.set_session_location(existing_session.get("location"))
            redfishobj.set_session_key(existing_session.get("session"))
            response_url = redfishobj.get("/redfish/v1/SessionService/Sessions", None)
            if response_url.status == 200:
                return redfishobj
            response_url = redfishobj.get("/redfish/v1/Sessions", None)
            if response_url.status == 200:
                return redfishobj

        # Login with the Redfish client
        # cleanup old session information
        redfishobj.set_session_location(None)
        redfishobj.set_session_key(None)
        redfishobj.login(auth="session")
    except ServerDownOrUnreachableError as excp:
        sys.stderr.write(
            f"ERROR: server not reachable or does not support RedFish. Error Message: {excp}\n"
        )
        sys.exit(1)
    except RetriesExhaustedError as excp:
        sys.stderr.write(f"ERROR: too many retries for connection attempt: {excp}\n")
        sys.exit(1)
    store_session_key(redfishobj, args.host)
    return redfishobj


def agent_redfish_main(args: Args) -> int:
    """main function for the special agent"""

    if not args.verify_ssl:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    if args.debug:
        # Config logger used by Restful library
        logger_file = "RedfishApi.log"
        logger_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logger = redfish.redfish_logger(logger_file, logger_format, logging.INFO)
        logger.info("Redfish API")

    # Start Redfish Session Object
    redfishobj = get_session(args)
    sections = args.sections.split(",")
    if args.disabled_sections:
        sections_disabled = args.disabled_sections.split(",")
        sections = list(set(sections).difference(sections_disabled))
    get_information(redfishobj, sections)
    # logout not needed anymore if no problem - session saved to file
    # logout is done if some query fails
    # REDFISHOBJ.logout()

    return 0


def main() -> int:
    """Main entry point to be used"""
    return special_agent_main(parse_arguments, agent_redfish_main)


if __name__ == "__main__":
    sys.exit(main())
