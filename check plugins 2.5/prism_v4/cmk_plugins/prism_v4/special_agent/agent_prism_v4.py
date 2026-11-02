#!/usr/bin/env python3
# Copyright (C) 2019-2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# ported to API v4 by (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

import base64
import logging
import sys
import time
from collections.abc import Mapping, Sequence
from contextlib import nullcontext
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, TypedDict

import requests
from cmk.plugins.prism_v4.lib_v4 import alert_message, latest_stats
from cmk.server_side_programs.v1_unstable import (
    HostnameValidationAdapter,
)
from cmk.special_agents.v0_unstable.agent_common import (
    ConditionalPiggybackSection,
    SectionWriter,
    special_agent_main,
)
from cmk.special_agents.v0_unstable.argument_parsing import (
    Args,
    create_default_argument_parser,
)
from cmk.utils import password_store
from cmk.utils.paths import var_dir
from dateutil import parser
from requests.adapters import HTTPAdapter

LOGGING = logging.getLogger("agent_prism")

# maximum page size of the v4 list endpoints
PAGE_LIMIT = 100

# API versions the agent is known to work with, newest first. Every API namespace
# uses the newest of them the system supports. Add new versions only after testing,
# newer versions may change the returned fields.
API_VERSIONS = ("v4.3", "v4.2", "v4.1", "v4.0")
# lightweight list endpoint per API namespace, used to detect the supported version
API_PROBES = {
    "vmm": "ahv/config/vms",
    "clustermgmt": "config/clusters",
    "prism": "config/categories",
    "monitoring": "serviceability/alerts",
}

# how the alerts are written: "service" -> prism_alerts_v4 section (one service),
# "logwatch" -> logwatch section with only the new alerts since the last run
ALERT_OUTPUTS = ("service", "logwatch", "both")
LOGWATCH_LOGFILE = "Nutanix Prism Alerts"
# logwatch level per alert severity, "FALLBACK" is used for unknown severities
DEFAULT_ALERT_LEVELS = {"INFO": "O", "WARNING": "W", "CRITICAL": "C", "FALLBACK": "u"}


class HostNameValidationAdapter(HTTPAdapter):
    def __init__(self, host_name: str) -> None:
        super().__init__()
        self._reference_host_name = host_name

    def cert_verify(self, conn, url, verify, cert):
        conn.assert_hostname = self._reference_host_name
        return super().cert_verify(conn, url, verify, cert)


Stats = dict[str, Any]


class GatewayData(TypedDict):
    """TypedDict for data fetched from Prism API.

    All *_stats entries are mappings from the entity extId to the latest
    value of every metric (see latest_stats)."""

    clusters: list[dict[str, Any]]
    cluster_stats: dict[str, Stats]
    disks: list[dict[str, Any]]
    disks_stats: dict[str, Stats]
    hosts: list[dict[str, Any]]
    hosts_stats: dict[str, Stats]
    host_nics: dict[str, list[dict[str, Any]]]
    vms: list[dict[str, Any]]
    vms_stats: dict[str, Stats]
    storage_containers: list[dict[str, Any]]
    storage_containers_stats: dict[str, Stats]
    alerts: list[dict[str, Any]]
    categories: list[dict[str, Any]]


class SessionManager:
    """Manages HTTP sessions with Prism API including authentication and certificate handling."""

    def __init__(
        self,
        username: str,
        password: str,
        timeout: int,
        cert_check: bool | str,
        base_url: str,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        auth_encoded = base64.b64encode(f"{username}:{password}".encode()).decode()
        # keep basic auth header only until a cookie is acquired
        self._session.headers.update({"Authorization": f"Basic {auth_encoded}"})
        self._verify = cert_check is not False
        self._timeout = timeout
        # API namespace -> newest supported version, filled by _probe_api
        self._api_versions: dict[str, str] = {}
        if isinstance(cert_check, str):
            self._session.mount(base_url, HostnameValidationAdapter(cert_check))

        # Try to obtain an auth cookie at init if none exists
        try:
            if not self._has_auth_cookie():
                self._acquire_cookie()
        except Exception:
            # don't fail initialization here; callers will handle connection errors
            LOGGING.debug(
                "initial cookie acquisition failed; will retry on demand", exc_info=True
            )

    def _has_auth_cookie(self) -> bool:
        """Return True if the session currently has any cookie that could be used for auth."""
        # Treat presence of any cookie as auth cookie (Prism sets session cookies on login)
        return bool(self._session.cookies)

    def _handle_rate_limit(self, resp: requests.Response) -> None:
        """Check X-API-Ratelimit-Remaining header and sleep briefly if low"""
        header = resp.headers.get("X-API-Ratelimit-Remaining")
        if header is None:
            return
        try:
            remaining = int(header)
        except (TypeError, ValueError):
            return
        if remaining <= 1:
            LOGGING.info(
                "API rate limit remaining low (%d); sleeping 0.5s to avoid exhaustion",
                remaining,
            )
            time.sleep(0.5)

    def _probe_api(self, namespace: str) -> requests.Response:
        """GET the probe endpoint of an API namespace, trying the API versions newest first.

        Nutanix has no endpoint listing the supported versions, an unsupported version
        is answered with an error. The first version that works is remembered."""
        for version in API_VERSIONS:
            resp = self._session.get(
                f"{self._base_url}/api/{namespace}/{version}/{API_PROBES[namespace]}",
                params={"$limit": 1},
                verify=self._verify,
                timeout=self._timeout,
            )
            self._handle_rate_limit(resp)
            # authentication errors are no version problem, the caller has to handle them
            if resp.ok or resp.status_code in (401, 403):
                self._api_versions[namespace] = version
                return resp
            LOGGING.debug(
                "API %s/%s not supported: HTTP %s", namespace, version, resp.status_code
            )
        return resp

    def api_base(self, namespace: str) -> str:
        """Base URL of an API namespace in the newest version supported by the system"""
        if namespace not in self._api_versions:
            self._probe_api(namespace).raise_for_status()
            LOGGING.info("using API %s/%s", namespace, self._api_versions[namespace])
        return f"{self._base_url}/api/{namespace}/{self._api_versions[namespace]}"

    def _acquire_cookie(self) -> None:
        """Attempt to fetch an authorization cookie using existing Basic auth header."""
        # Use a lightweight, commonly available API endpoint as probe to get Set-Cookie.
        try:
            resp = self._probe_api("clustermgmt")
            probe = resp.url
        except requests.exceptions.ReadTimeout as e:
            LOGGING.error("Timeout while acquiring auth cookie: %s", e)
            raise e
        except requests.exceptions.ConnectionError as e:
            LOGGING.error("Connection failed while acquiring auth cookie: %s", e)
            raise e

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            LOGGING.error("HTTP error while acquiring auth cookie: %s", e)
            raise e

        if not self._has_auth_cookie():
            LOGGING.warning("No auth cookie received from server after probe %s", probe)
        else:
            # If we obtained a cookie, drop Basic Authorization header for subsequent requests.
            self._session.headers.pop("Authorization", None)
            LOGGING.debug("Auth cookie acquired and basic auth header removed.")

    def get(self, url: str, params: dict[str, str | int] | None = None) -> Any:
        """Perform a GET request and return the JSON response. Re-acquire cookie on demand."""
        # Ensure we have a cookie before the request; if not, try to acquire one.
        if not self._has_auth_cookie():
            try:
                self._acquire_cookie()
            except Exception:
                # Let caller handle connection failures
                raise

        try:
            resp = self._session.get(
                url, params=params, verify=self._verify, timeout=self._timeout
            )
        except requests.exceptions.ReadTimeout as e:
            LOGGING.error("Timeout: %s", e)
            LOGGING.error(f"Connection timed out after {self._timeout} seconds.")
            raise e
        except requests.exceptions.ConnectionError as e:
            LOGGING.error("Connection failed: %s", e)
            raise e

        # Check rate limit header
        try:
            self._handle_rate_limit(resp)
        except Exception:
            LOGGING.debug("Rate limit handling failed", exc_info=True)

        # If unauthorized, try to fetch a fresh cookie once and retry the request.
        if resp.status_code in (401, 403):
            LOGGING.info(
                "Unauthorized (%s) requesting %s, attempting to refresh cookie and retry",
                resp.status_code,
                url,
            )
            try:
                self._acquire_cookie()
            except Exception:
                LOGGING.error("Failed to refresh cookie after unauthorized response")
                resp.raise_for_status()
            try:
                resp = self._session.get(
                    url, params=params, verify=self._verify, timeout=self._timeout
                )
            except requests.exceptions.ReadTimeout as e:
                LOGGING.error("Timeout on retry: %s", e)
                LOGGING.error(f"Connection timed out after {self._timeout} seconds.")
                raise e
            except requests.exceptions.ConnectionError as e:
                LOGGING.error("Connection failed on retry: %s", e)
                raise e

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            LOGGING.debug("Response headers: %s", resp.headers)
            LOGGING.error("HTTP error: %s", e)
            raise e

        return self._remove_keys(resp.json(), "$reserved")

    def get_all_entities(
        self, url: str, params: dict[str, str | int] | None = None
    ) -> list[dict[str, Any]]:
        """Iterate through all pages and return a list of all entities.

        API v4 paginates with $page/$limit, the total number of entities is
        reported in metadata.totalAvailableResults."""
        entities: list[dict[str, Any]] = []
        page = 0
        while True:
            page_params: dict[str, str | int] = {
                **(params or {}),
                "$page": page,
                "$limit": PAGE_LIMIT,
            }
            data = self.get(url, page_params)
            page_data = data.get("data") or []
            entities.extend(page_data)
            total = data.get("metadata", {}).get("totalAvailableResults")
            if not page_data or total is None or len(entities) >= total:
                break
            page += 1
            LOGGING.info("Fetching page %d of %s", page, url)
        return entities

    def get_optional(
        self, url: str, params: dict[str, str | int] | None = None
    ) -> Any | None:
        """GET for endpoints that are not available on every system/version.

        An HTTP error is logged and None is returned instead of aborting the agent."""
        try:
            return self.get(url, params)
        except requests.exceptions.HTTPError as e:
            LOGGING.warning("Optional endpoint %s not available: %s", url, e)
            return None

    def _remove_keys(
        self, data: dict[str, str] | list[Any] | Any, target_key: str
    ) -> dict[str, str] | list[Any] | Any:
        """Recursively remove all occurrences of target_key from data."""
        if isinstance(data, dict):
            return {
                k: self._remove_keys(v, target_key)
                for k, v in data.items()
                if k != target_key
            }
        if isinstance(data, list):
            return [self._remove_keys(item, target_key) for item in data]
        return data


# TODO: Move to a common library
def parse_arguments(argv: Sequence[str] | None) -> Args:
    parser = create_default_argument_parser(description=__doc__)
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Timeout in seconds for network connects (default=10)",
    )
    parser.add_argument(
        "--server",
        type=str,
        required=True,
        metavar="ADDRESS",
        help="host to connect to",
    )
    parser.add_argument("--port", type=int, metavar="PORT", default=9440)
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        metavar="USER",
        help="user account on prism",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--password",
        type=str,
        metavar="PASSWORD",
        help="password for that account",
    )
    group.add_argument(
        "--password-id",
        type=str,
        metavar="PWID",
        help="password store reference for that account",
    )
    cert_args = parser.add_mutually_exclusive_group()
    cert_args.add_argument(
        "--no-cert-check", action="store_true", help="Do not verify TLS certificate"
    )
    cert_args.add_argument(
        "--cert-server-name",
        help="Expect this as the servers name in the ssl certificate. Overrides '--no-cert-check'.",
    )
    parser.add_argument(
        "--alert-output",
        choices=ALERT_OUTPUTS,
        default="service",
        help="Output alerts as one service, as logwatch logfile or both (default=service)",
    )
    parser.add_argument(
        "--alert-levels",
        type=parse_alert_levels,
        default=DEFAULT_ALERT_LEVELS,
        metavar="SEVERITY=LEVEL,...",
        help="Logwatch level (C, W, O, u, .) per alert severity, "
        "e.g. INFO=O,WARNING=W,CRITICAL=C,FALLBACK=u",
    )

    return parser.parse_args(argv)


def parse_alert_levels(value: str) -> dict[str, str]:
    levels = dict(DEFAULT_ALERT_LEVELS)
    for item in value.split(","):
        severity, _, level = item.partition("=")
        if level not in ("C", "W", "O", "u", "."):
            raise ValueError(f"invalid logwatch level: {item!r}")
        levels[severity.strip().upper()] = level
    return levels


def is_prism_central(cluster: Mapping[str, Any]) -> bool:
    return "PRISM_CENTRAL" in cluster.get("config", {}).get("clusterFunction", [])


def fetch_from_gateway(
    server: str,
    port: int,
    username: str,
    password: str,
    timeout: int,
    cert_check: bool | str,
) -> GatewayData:
    LOGGING.info("setup HTTPS connection..")
    base_url = f"https://{server}:{port}"
    session_manager = SessionManager(
        username=username,
        password=password,
        timeout=timeout,
        cert_check=cert_check,
        base_url=base_url,
    )

    # API v4 uses different root paths for different components, every component
    # is used in the newest version supported by the system (see API_VERSIONS)
    # See: https://developers.nutanix.com/
    vmm_api_base = session_manager.api_base("vmm")
    prism_api_base = session_manager.api_base("prism")
    cluster_api_base = session_manager.api_base("clustermgmt")
    monitoring_api_base = session_manager.api_base("monitoring")

    LOGGING.info("fetching data from gateway..")

    now = datetime.now(UTC)
    params: dict[str, str | int] = {
        "$startTime": f"{(now - timedelta(minutes=5)).isoformat(timespec='seconds').replace('+00:00', '')}Z",
        "$endTime": f"{now.isoformat(timespec='seconds').replace('+00:00', '')}Z",
        "$select": "*",
        "$statType": "LAST",
        "$samplingInterval": 60,
    }

    # These endpoints are common for Prism Central and Prism Element
    clusters = session_manager.get_all_entities(f"{cluster_api_base}/config/clusters")
    cluster_stats: dict[str, Stats] = {}
    hosts: list[dict[str, Any]] = []
    hosts_stats: dict[str, Stats] = {}
    host_nics: dict[str, list[dict[str, Any]]] = {}
    for cluster in clusters:
        # Prism Central lists itself as a cluster, but it has no hosts or cluster stats
        if is_prism_central(cluster) or not (cluster_id := cluster.get("extId")):
            continue
        cluster_stat = session_manager.get(
            f"{cluster_api_base}/stats/clusters/{cluster_id}", params
        )
        cluster_stats[cluster_id] = latest_stats(cluster_stat.get("data"))
        cluster_hosts = session_manager.get_all_entities(
            f"{cluster_api_base}/config/clusters/{cluster_id}/hosts"
        )
        hosts.extend(cluster_hosts)
        for host in cluster_hosts:
            if not (host_id := host.get("extId")):
                continue
            host_stat = session_manager.get(
                f"{cluster_api_base}/stats/clusters/{cluster_id}/hosts/{host_id}",
                params,
            )
            hosts_stats[host_id] = latest_stats(host_stat.get("data"))
            nics = session_manager.get_optional(
                f"{cluster_api_base}/config/clusters/{cluster_id}/hosts/{host_id}/host-nics",
                {"$limit": PAGE_LIMIT},
            )
            if nics is not None:
                host_nics[host_id] = nics.get("data") or []

    vms = session_manager.get_all_entities(f"{vmm_api_base}/ahv/config/vms")
    vms_stats: dict[str, Stats] = {}
    for vm_stat in session_manager.get_all_entities(f"{vmm_api_base}/ahv/stats/vms", params):
        if not (vm_id := vm_stat.get("extId")) or not (samples := vm_stat.get("stats")):
            continue
        newest = max(samples, key=lambda x: parser.parse(x["timestamp"]))
        vms_stats[vm_id] = {k: v for k, v in newest.items() if k != "$objectType"}

    disks = session_manager.get_all_entities(f"{cluster_api_base}/config/disks")
    disks_stats: dict[str, Stats] = {}
    for disk in disks:
        if not (disk_id := disk.get("extId")):
            continue
        disk_stat = session_manager.get_optional(
            f"{cluster_api_base}/stats/disks/{disk_id}", params
        )
        if disk_stat is not None:
            disks_stats[disk_id] = latest_stats(disk_stat.get("data"))

    storage_containers = session_manager.get_all_entities(
        f"{cluster_api_base}/config/storage-containers"
    )
    container_stats: dict[str, Stats] = {}
    for storage_container in storage_containers:
        # storage containers use containerExtId instead of extId
        if not (container_id := storage_container.get("containerExtId")):
            continue
        container_stat = session_manager.get_optional(
            f"{cluster_api_base}/stats/storage-containers/{container_id}", params
        )
        if container_stat is not None:
            container_stats[container_id] = latest_stats(container_stat.get("data"))

    alerts = session_manager.get_all_entities(
        f"{monitoring_api_base}/serviceability/alerts",
        {"$filter": "isResolved eq false"},
    )

    categories = session_manager.get_all_entities(f"{prism_api_base}/config/categories")

    gateway_data: GatewayData = {
        "clusters": clusters,
        "cluster_stats": cluster_stats,
        "disks": disks,
        "disks_stats": disks_stats,
        "hosts": hosts,
        "hosts_stats": hosts_stats,
        "host_nics": host_nics,
        "vms": vms,
        "vms_stats": vms_stats,
        "storage_containers": storage_containers,
        "storage_containers_stats": container_stats,
        "alerts": alerts,
        "categories": categories,
    }

    LOGGING.debug("got %d clusters", len(gateway_data["clusters"]))
    LOGGING.debug("got %d hosts", len(gateway_data["hosts"]))
    LOGGING.debug("got %d vms", len(gateway_data["vms"]))
    LOGGING.debug("got %d storage_containers", len(gateway_data["storage_containers"]))
    LOGGING.debug("got %d alerts", len(gateway_data["alerts"]))
    LOGGING.debug("got %d categories", len(gateway_data["categories"]))

    return gateway_data


def output_entities(entities: Any, target_name: str) -> None:
    with SectionWriter(f"prism_{target_name}") as w:
        w.append_json(entities)


def write_sections(gateway_objs: GatewayData, alert_service: bool = True) -> None:
    """Write all agent sections and piggyback data.

    Cluster related sections are written to the monitored host if there is only one
    cluster (Prism Element or Prism Central with one cluster). With more clusters every
    cluster gets its own piggyback host, so the cluster services keep their names."""
    aos_clusters = [c for c in gateway_objs["clusters"] if not is_prism_central(c)]
    for cluster in aos_clusters:
        cluster_id = cluster.get("extId", "")
        target = (
            nullcontext()
            if len(aos_clusters) == 1
            else ConditionalPiggybackSection(cluster.get("name"))
        )
        with target:
            output_entities(cluster, "cluster_v4")
            if cluster_id in gateway_objs["cluster_stats"]:
                output_entities(gateway_objs["cluster_stats"][cluster_id], "cluster_stats_v4")
            output_entities(
                [
                    {
                        **container,
                        "stats": gateway_objs["storage_containers_stats"].get(
                            container.get("containerExtId", ""), {}
                        ),
                    }
                    for container in gateway_objs["storage_containers"]
                    if container.get("clusterExtId") == cluster_id
                ],
                "storage_containers_v4",
            )

    host_names = {
        host["extId"]: host.get("hostName", "unknown")
        for host in gateway_objs["hosts"]
        if "extId" in host
    }
    vms = [
        {**vm, "hostName": host_names.get(vm.get("host", {}).get("extId", ""))}
        for vm in gateway_objs["vms"]
    ]

    output_entities(gateway_objs["hosts"], "hosts_v4")
    output_entities(vms, "vms_v4")
    if alert_service:
        output_entities(gateway_objs["alerts"], "alerts_v4")
    output_entities(gateway_objs["categories"], "categories_v4")

    categorie_dict: dict[str, dict[str, str]] = {
        element["extId"]: {k: v for k, v in element.items() if k not in ("extId", "links")}
        for element in gateway_objs["categories"]
    }

    # Create piggyback data for individual hosts and VMs
    for host in gateway_objs["hosts"]:
        host_id = host.get("extId", "")
        with ConditionalPiggybackSection(host.get("hostName")):
            output_entities(host, "host_v4")
            if host_id in gateway_objs["hosts_stats"]:
                output_entities(gateway_objs["hosts_stats"][host_id], "host_stats_v4")
            output_entities(
                [
                    {**disk, "stats": gateway_objs["disks_stats"].get(disk.get("extId", ""), {})}
                    for disk in gateway_objs["disks"]
                    if disk.get("nodeExtId") == host_id
                ],
                "host_disks_v4",
            )
            if host_id in gateway_objs["host_nics"]:
                output_entities(gateway_objs["host_nics"][host_id], "host_nics_v4")

    for vm in vms:
        with ConditionalPiggybackSection(vm.get("name")):
            output_entities(vm, "vm_v4")
            categories = [
                categorie_dict[categorie["extId"]]
                for categorie in vm.get("categories", [])
                if categorie.get("extId") in categorie_dict
            ]
            output_entities(categories, "vm_categories_v4")
            if (vm_stats := gateway_objs["vms_stats"].get(vm.get("extId", ""))) is not None:
                output_entities(vm_stats, "vm_stats_v4")


def _alert_time(alert: Mapping[str, Any]) -> datetime:
    return datetime.fromisoformat(alert["creationTime"].replace("Z", "+00:00"))


def write_logwatch_alerts(
    alerts: Sequence[Mapping[str, Any]],
    levels: Mapping[str, str],
    state_file: Path,
) -> None:
    """Write the alerts created since the last run as logwatch logfile.

    The creation time of the newest alert is remembered in state_file. Without
    state file (first run) all currently unresolved alerts are written."""
    try:
        last_seen: datetime | None = datetime.fromisoformat(state_file.read_text().strip())
    except (OSError, ValueError):
        last_seen = None

    alerts = sorted((a for a in alerts if a.get("creationTime")), key=_alert_time)
    new_alerts = [a for a in alerts if last_seen is None or _alert_time(a) > last_seen]
    LOGGING.debug("got %d new alerts for logwatch", len(new_alerts))

    # the logfile header is always written, otherwise the logwatch service would vanish
    sys.stdout.write(f"<<<logwatch>>>\n[[[{LOGWATCH_LOGFILE}]]]\n")
    for alert in new_alerts:
        level = levels.get(alert.get("severity", ""), levels["FALLBACK"])
        message = " ".join(alert_message(alert).split())
        cluster = alert.get("clusterName") or alert.get("clusterUUID") or "unknown"
        sys.stdout.write(
            f"{level} {alert['creationTime']} {alert.get('severity', 'UNKNOWN')} "
            f"{alert.get('alertType', '')}: {message}, cluster: {cluster}\n"
        )

    if new_alerts:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.write_text(_alert_time(new_alerts[-1]).isoformat())


def agent_prism_main(args: Args) -> int:
    """Establish a connection to a Prism server and process clusters, hosts, vms,
    disks, storage containers and alerts"""
    if args.password_id:
        pw_id, pw_path = args.password_id.split(":")
        pw_result = password_store.lookup(Path(pw_path), pw_id)
    else:
        pw_result = args.password

    try:
        gateway_objs = fetch_from_gateway(
            server=args.server,
            port=args.port,
            username=args.username,
            password=pw_result,
            timeout=args.timeout,
            cert_check=args.cert_server_name or not args.no_cert_check,
        )
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError):
        return 1

    write_sections(gateway_objs, alert_service=args.alert_output in ("service", "both"))
    if args.alert_output in ("logwatch", "both"):
        write_logwatch_alerts(
            gateway_objs["alerts"],
            args.alert_levels,
            Path(var_dir, "prism_v4", args.server, "alerts_last_seen"),
        )

    LOGGING.info("all done. bye.")
    return 0


def main() -> int:
    """Main entry point to be used"""
    return special_agent_main(parse_arguments, agent_prism_main)


if __name__ == "__main__":
    sys.exit(main())
