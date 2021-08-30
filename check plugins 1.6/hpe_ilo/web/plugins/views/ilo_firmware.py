#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.plugins.views.inventory import (
    declare_invtable_view,
    render_inv_dicttable,
)

inventory_displayhints.update({
    # iLO firmware display hints
    '.hardware.firmware.hpe:': {'title': _('HPE iLO Hardware versions'),
                                           'render'  : render_inv_dicttable,
                                           'keyorder': ['component', 'version'],
                                           'view': 'invhpefirmware_of_host',
                                },
    '.hardware.firmware.hpe:*.component': {'title': _('Hardware Component') },
    '.hardware.firmware.hpe:*.version': {'title': _('Version') },
})

declare_invtable_view(
    "invhpefirmware",
    ".hardware.firmware.hpe:",
    _("HPE iLO Firmware versions"),
    _("HPE iLO Firmware versions"),
)

