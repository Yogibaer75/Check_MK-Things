#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

def bake_hyperv_vms_guestinfos(opsys, conf, conf_dir, plugins_dir):
    if conf:
        shutil.copy2(omd_root + "/local/share/check_mk/agents/windows/plugins/hyperv_vms_guestinfos.ps1",
                     plugins_dir + "/hyperv_vms_guestinfos.ps1")

bakery_info["hyperv_vms_guestinfos"] = {
    "bake_function" : hyperv_vms_guestinfos,
    "os"            : [ "windows" ],
}
