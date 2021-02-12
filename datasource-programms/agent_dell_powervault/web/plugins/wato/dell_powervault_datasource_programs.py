#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
group = 'datasource_programs'

register_rule(group,
    'special_agents:dellpowervault',
    Dictionary(
        elements = [
            ( 'user',
              TextAscii(
                  title = _('Username'),
                  allow_empty = False,
              )
            ),
            ( 'password',
              Password(
                  title = _("Password"),
                  allow_empty = False,
              )
            )
        ],
        optional_keys = False
    ),
    title = _("Dell Powervault M4 storage system"),
    help = _("This rule selects the Agent Dell Powervault M4 instead of the normal Check_MK Agent "
             "which collects the data through the DELLs API"),
    match = 'first')
