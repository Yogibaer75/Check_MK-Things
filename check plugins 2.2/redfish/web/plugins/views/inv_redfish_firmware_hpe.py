#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""View for HW/SW inventory data of HPE devices"""

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from cmk.gui.views.inventory.registry import inventory_displayhints
from cmk.gui.i18n import _l


inventory_displayhints.update(
    {
        ".hardware.firmware.hpe:": {
            "title": _l("HPE Firmware"),
            "keyorder": ["component", "version", "location", "description"],
            "view": "invfirmwarehpe_of_host",
        },
        ".hardware.firmware.hpe:*.component": {"title": _l("Component")},
        ".hardware.firmware.hpe:*.version": {"title": _l("Version")},
        ".hardware.firmware.hpe:*.location": {"title": _l("Location")},
        ".hardware.firmware.hpe:*.description": {"title": _l("Description")},
        ".hardware.firmware.hpe:*.updateable": {"title": _l("Update possible"), "paint": "bool"},
    }
)
