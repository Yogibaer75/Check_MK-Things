#!/usr/bin/python

# License: GNU General Public License v2

"""Load the plug-in family of this MKP instead of the one shipped with Checkmk

The tests need the Checkmk plug-in APIs. Run them with the Python environment
of a Checkmk source checkout, for example:

    ~/git/check_mk/.venv/bin/python -m pytest "check plugins 2.5/hyperv_cluster/tests"
"""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

import cmk.plugins

_NAME = "cmk.plugins.hyperv_cluster"
_FAMILY = Path(__file__).parent.parent / "cmk_plugins" / "hyperv_cluster"

_spec = importlib.machinery.ModuleSpec(_NAME, None, is_package=True)
_spec.submodule_search_locations = [str(_FAMILY)]
_family = importlib.util.module_from_spec(_spec)
sys.modules[_NAME] = _family
cmk.plugins.hyperv_cluster = _family  # type: ignore[attr-defined]
