#!/usr/bin/python

# License: GNU General Public License v2

"""Apply the man page rules of Checkmk to the man pages of this MKP"""

import importlib
from pathlib import Path

import pytest

from cmk.agent_based.v2 import CheckPlugin
from cmk.utils import man_pages

_FAMILY = Path(__file__).parent.parent / "cmk_plugins" / "hyperv_cluster"
_CHECKMAN = _FAMILY / "checkman"


def _check_plugins() -> dict[str, CheckPlugin]:
    plugins = {}
    for path in sorted((_FAMILY / "agent_based").glob("*.py")):
        module = importlib.import_module(f"cmk.plugins.hyperv_cluster.agent_based.{path.stem}")
        plugins.update(
            {
                plugin.name: plugin
                for name, plugin in vars(module).items()
                if name.startswith("check_plugin_") and isinstance(plugin, CheckPlugin)
            }
        )
    return plugins


CHECK_PLUGINS = _check_plugins()
MAN_PAGES = sorted(path.name for path in _CHECKMAN.iterdir())


def test_cluster_check_plugins_have_man_pages() -> None:
    cluster_plugins = {
        name for name in CHECK_PLUGINS if name.startswith(("hyperv_cluster_", "hyperv_host_io"))
    }
    assert cluster_plugins <= set(MAN_PAGES)


def test_every_man_page_belongs_to_a_check_plugin() -> None:
    assert set(MAN_PAGES) <= set(CHECK_PLUGINS)


@pytest.mark.parametrize("name", MAN_PAGES)
def test_man_page(name: str) -> None:
    page = man_pages.parse_man_page(name, _CHECKMAN / name, debug=True)

    assert page.license == "GPLv2"
    assert page.agents == ["windows"]
    assert set(page.catalog) <= set(man_pages.CATALOG_TITLES)
    assert bool(page.cluster) is (CHECK_PLUGINS[name].cluster_check_function is not None)
