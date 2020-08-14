#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

register_check_parameters(
    subgroup_os,
    "win_cert",
    _("Windows System Certificates"),
          Tuple(
              title = _("Time left for installed certificates before renew is needed"),
              help = _("This rule sets the days before a certificate needs renew."),
              elements = [
                  Integer(title = _("Warning at"), unit = _("days"), default_value = 30),
                  Integer(title = _("Critical at"), unit = _("days"), default_value = 15)
              ],
          ),
    None,
    "first"
)

