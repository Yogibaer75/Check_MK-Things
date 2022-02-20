#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from cmk.gui.plugins.views.inventory import (
    declare_invtable_view,
    render_inv_dicttable,
)

inventory_displayhints.update({
    # iLO firmware display hints
    '.hardware.firmware.hpe:': {
        'title': _('HPE iLO Hardware versions'),
        'render': render_inv_dicttable,
        'keyorder': ['component', 'version'],
        'view': 'invhpefirmware_of_host',
    },
    '.hardware.firmware.hpe:*.component': {
        'title': _('Hardware Component')
    },
    '.hardware.firmware.hpe:*.version': {
        'title': _('Version')
    },
})

declare_invtable_view(
    "invhpefirmware",
    ".hardware.firmware.hpe:",
    _("HPE iLO Firmware versions"),
    _("HPE iLO Firmware versions"),
)
