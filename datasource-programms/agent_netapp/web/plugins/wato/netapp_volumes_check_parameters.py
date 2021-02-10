#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Alternative,
    Checkbox,
    Dictionary,
    FixedValue,
    Integer,
    Optional,
    Percentage,
    TextAscii,
    Transform,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersStorage,
)
from cmk.gui.plugins.wato.check_parameters.utils import (
    get_free_used_dynamic_valuespec,
    match_dual_level_type,
    transform_filesystem_free,
)


register_check_parameters(
    subgroup_storage,
    "netapp_volumes",
    _("NetApp Volumes"),
    Dictionary(
        elements = [
             ("levels",
                Alternative(
                    title = _("Levels for volume"),
                    show_alternative_title = True,
                    default_value = (80.0, 90.0),
                    match = match_dual_level_type,
                    elements = [
                           get_free_used_dynamic_valuespec("used", "volume"),
                           Transform(
                                    get_free_used_dynamic_valuespec("free", "volume", default_value = (20.0, 10.0)),
                                    allow_empty = False,
                                    forth = transform_filesystem_free,
                                    back  = transform_filesystem_free
                           )
                    ]
                 )
            ),
            ("show_levels",
              DropdownChoice(
                  title = _("Display warn/crit levels in check output..."),
                  choices = [
                     ( "onproblem", _("Only if the status is non-OK")),
                     ( "onmagic",   _("If the status is non-OK or a magic factor is set")),
                     ( "always",    _("Always") ),
                  ],
                  default_value = "onmagic",
                  )
            ),
            ("perfdata",
                ListChoice(
                    title = _("Performance data for protocols"),
                    help = _("Specify for which protocol performance data should get recorded."),
                    choices = [
                       ( "", _("Summarized data of all protocols") ),
                       ( "nfs",    _("NFS") ),
                       ( "cifs",   _("CIFS") ),
                       ( "san",    _("SAN") ),
                       ( "fcp",    _("FCP") ),
                       ( "iscsi",  _("iSCSI") ),
                    ],
                )),
            (  "magic",
               Float(
                  title = _("Magic factor (automatic level adaptation for large volumes)"),
                  default_value = 0.8,
                  minvalue = 0.1,
                  maxvalue = 1.0)),
            (  "magic_normsize",
               Integer(
                   title = _("Reference size for magic factor"),
                   default_value = 20,
                   minvalue = 1,
                   unit = _("GB"))),
            ( "levels_low",
              Tuple(
                  title = _("Minimum levels if using magic factor"),
                  help = _("The volume levels will never fall below these values, when using "
                           "the magic factor and the volume is very small."),
                  elements = [
                      Percentage(title = _("Warning if above"),  unit = _("% usage"), allow_int = True, default_value=50),
                      Percentage(title = _("Critical if above"), unit = _("% usage"), allow_int = True, default_value=60)])),
            ( "inodes_levels",
                Alternative(
                    title = _("Levels for Inodes"),
                    help  = _("The number of remaining inodes on the filesystem. "
                              "Please note that this setting has no effect on some filesystem checks."),
                    elements = [
                            Tuple(title = _("Percentage free"),
                                  elements = [
                                       Percentage(title = _("Warning if less than")),
                                       Percentage(title = _("Critical if less than")),
                                  ]
                            ),
                            Tuple(title = _("Absolute free"),
                                  elements = [
                                       Integer(title = _("Warning if less than"),  size = 10, unit = _("inodes"), minvalue = 0, default_value = 10000),
                                       Integer(title = _("Critical if less than"), size = 10, unit = _("inodes"), minvalue = 0, default_value = 5000),
                                  ]
                            )
                    ],
                    default_value = (10.0, 5.0),
                )
            ),
            ( "show_inodes",
              DropdownChoice(
                  title = _("Display inode usage in check output..."),
                  choices = [
                    ( "onproblem", _("Only in case of a problem")),
                    ( "onlow",     _("Only in case of a problem or if inodes are below 50%")),
                    ( "always",    _("Always")),
                  ],
                  default_value = "onlow",
            )),
            ( "show_reserved",
              DropdownChoice(
                  title = _("Show space reserved for the <tt>root</tt> user"),
                  help = _("Check_MK treats space that is reserved for the <tt>root</tt> user on Linux and Unix as "
                           "used space. Usually, 5% are being reserved for root when a new filesystem is being created. "
                           "With this option you can have Check_MK display the current amount of reserved but yet unused "
                           "space."),
                  choices = [
                    ( True, _("Show reserved space") ),
                    ( False, _("Do now show reserved space") ),
                ])),
            (  "trend_range",
               Optional(
                   Integer(
                       title = _("Time Range for filesystem trend computation"),
                       default_value = 24,
                       minvalue = 1,
                       unit= _("hours")),
                   title = _("Trend computation"),
                   label = _("Enable trend computation"))),
            (  "trend_mb",
               Tuple(
                   title = _("Levels on trends in MB per time range"),
                   elements = [
                       Integer(title = _("Warning at"), unit = _("MB / range"), default_value = 100),
                       Integer(title = _("Critical at"), unit = _("MB / range"), default_value = 200)
                   ])),
            (  "trend_perc",
               Tuple(
                   title = _("Levels for the percentual growth per time range"),
                   elements = [
                       Percentage(title = _("Warning at"), unit = _("% / range"), default_value = 5,),
                       Percentage(title = _("Critical at"), unit = _("% / range"), default_value = 10,),
                   ])),
            (  "trend_timeleft",
               Tuple(
                   title = _("Levels on the time left until the filesystem gets full"),
                   elements = [
                       Integer(title = _("Warning if below"), unit = _("hours"), default_value = 12,),
                       Integer(title = _("Critical if below"), unit = _("hours"), default_value = 6, ),
                    ])),
            ( "trend_showtimeleft",
                    Checkbox( title = _("Display time left in check output"), label = _("Enable"),
                               help = _("Normally, the time left until the disk is full is only displayed when "
                                        "the configured levels have been breached. If you set this option "
                                        "the check always reports this information"))
            ),
            ( "trend_perfdata",
              Checkbox(
                  title = _("Trend performance data"),
                  label = _("Enable generation of performance data from trends"))),
            ("snapshot_levels", Tuple(
                title = _("Snapshot Levels"),
                help = _("A snapshot of more than 100% is called "
                         "overflow and can be usefull for recovery of data in case of unwanted deletion. "
                         "Here you can set levels for the maximum snapshot size compared to the reserved size."
                         "A warning level of 150% will warn at 50% over reserved size."),
                elements = [
                  Percentage(title = _("Warning at a snapshot size of"), maxvalue = None, default_value = 120.0),
                  Percentage(title = _("Critical at a snapshot size of"), maxvalue = None, default_value = 150.0),
                ]
            )),
        ]
    ),
    TextAscii(title = _("Volume name")),
    match_type = "dict",
)

