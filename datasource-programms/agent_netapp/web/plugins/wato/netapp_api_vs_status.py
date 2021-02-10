#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

subgroup_storage =      _("Storage, Filesystems and Files")

register_check_parameters(
    subgroup_storage,
    "netapp_vserver_status",
    _("Netapp vServer status"),
    Transform(
    Dictionary(
        elements = [
            ("state",
                DropdownChoice(
                    title = _("vServer state"),
                    help = _("Expected vServer state."),
                    choices = [
                            ( "running" , _("running") ),
                            ( "stopped" , _("stopped") ),
                    ],
                    default_value = "running"
                )
            ),
        ],
        required_keys = ["state"]
    ),
    ),
    TextAscii(
        title = _("vServer Name"),
        allow_empty = True
    ),
    match_type = "first",
)
