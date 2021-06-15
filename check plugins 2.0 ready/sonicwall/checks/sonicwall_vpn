#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def parse_sonicwall_vpn(info):
    parsed = {}
    for vpn_name, ip,bytes_encrypted, bytes_decrypted in info:
        parsed.setdefault(vpn_name, {"ip":ip, "bytes_enc":bytes_encrypted, "bytes_dec":bytes_decrypted})

    return parsed

@get_parsed_item_data
def check_sonicwall_vpn(item, _no_params, data):
    this_time = int(time.time())

    encryptedbytes=int(data["bytes_enc"])
    decryptedbytes=int(data["bytes_dec"])
    encrate = get_rate("vpn.enc.%s" % item, this_time, int(encryptedbytes), onwrap=SKIP)
    decrate = get_rate("vpn.dec.%s" % item, this_time, int(decryptedbytes), onwrap=SKIP)
    perfdata = [ ( "sa_bytes_encrypted", encrate ), ( "sa_bytes_decrypted", decrate ) ]
    return (0, "SA (%s/%s) active" % (item , data.get("ip")), perfdata)


check_info["sonicwall_vpn"] = {
    "parse_function": parse_sonicwall_vpn,
    "check_function": check_sonicwall_vpn,
    "inventory_function": discover(),
    "service_description": "VPN - %s",
    "has_perfdata": True,
    "snmp_scan_function": lambda oid: "sonicwall" in oid(".1.3.6.1.2.1.1.1.0").lower(),
    "snmp_info": (".1.3.6.1.4.1.8741.1.3.2.1.1.1", [ "14", "2", "9", "11" ]),
}
