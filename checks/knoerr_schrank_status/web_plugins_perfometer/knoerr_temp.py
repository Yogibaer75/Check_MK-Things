#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
 
def perfometer_temperature_knoerr(row, check_command, perf_data):
    display_color_warm = "#60f020"
    display_color_kalt = "#60f020"
    h = '<div class="stacked">'
    warmluft = float(perf_data[0][1])
    kaltluft = float(perf_data[1][1])
    if warmluft > saveint(perf_data[0][3]):
        display_color_warm = "#FFC840"
    if warmluft > saveint(perf_data[0][4]):
        display_color_warm = "#FF0000"
    if kaltluft > saveint(perf_data[1][3]):
        display_color_kalt = "#FFC840"
    if kaltluft > saveint(perf_data[1][4]):
        display_color_kalt = "#FF0000"
    h += perfometer_linear(warmluft, display_color_warm)
    h += perfometer_linear(kaltluft, display_color_kalt)
    h += '</div>'
    return "Warm %.1f / Kalt %.1f" % (warmluft, kaltluft), h
 
perfometers["check_mk-knoerr_coolloop_temp"] = perfometer_temperature_knoerr
