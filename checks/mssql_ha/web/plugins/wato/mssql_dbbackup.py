#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#

group = "checkparams"

subgroup_applications = _("Applications, Processes & Services")

register_check_parameters(
    subgroup_applications,
    "mssql_backup",
    _("MSSQL Time since last Backup"),
    Transform(
        Dictionary(
            help = _("This rule allows you to set limits on the age of backups for "
                     "different backup types. If your agent does not support "
                     "backup types (e.g. <i>Log Backup</i>, <i>Database Diff "
                     "Backup</i>, etc.) you can use the option <i>Database Backup"
                     "</i> to set a general limit"),
            elements = [
                ("database", Tuple(
                    title = _("Database Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("database_diff", Tuple(
                    title = _("Database Diff Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("log", Tuple(
                    title = _("Log Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("file_or_filegroup", Tuple(
                    title = _("File or Filegroup Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("file_diff", Tuple(
                    title = _("File Diff Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("partial", Tuple(
                    title = _("Partial Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("partial_diff", Tuple(
                    title = _("Partial Diff Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),
                ("unspecific", Tuple(
                    title = _("Unspecific Backup"),
                    elements = [
                        Age(title = _("Warning if older than")),
                        Age(title = _("Critical if older than")),
                ])),

            ]
        ),
        forth = lambda params: (params if type(params) == dict
                                else {'database': (params[0], params[1])})
    ),
    TextAscii(
        title = _("Service descriptions"),
        allow_empty = False),
    "first",
)

