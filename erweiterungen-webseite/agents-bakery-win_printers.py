#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

def bake_win_printers(opsys, conf, conf_dir, plugins_dir):
    if conf:
        shutil.copy2(agents_dir + "/windows/plugins/win_printers.ps1",
                     plugins_dir + "/win_printers.ps1")

bakery_info["win_printers"] = {
    "bake_function" : bake_win_printers,
    "os"            : [ "windows" ],
}
