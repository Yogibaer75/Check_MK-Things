# Knoerr Checks 
## Knoerr Schrank Status

Um den Status alles Sensoren in einem Knoerr Schrank abzufragen wurde ein kleiner Check erstellt.
Dieser Check liefert keine Performance Daten da nur der Status der einzelnen Elemente ausgelesen wird.

```python
#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

knoerr_coolloop_map = {
    1: "Fan1",
    2: "Fan2",
    3: "Fan3",
    4: "Water",
    5: "Smoke",
    6: "mainsA",
    7: "mainsB",
}

def inventory_knoerr_coolloop_status(info):
    if len(info) > 0:
        return [ (None, None) ]

def check_knoerr_coolloop_status(item, params, info):
    status = info[0]
    x = 1
    single_states = []
    for line in status:
        if saveint(line[0]) == 0:
            infotxt = "Sensor %s is OK" % knoerr_coolloop_map[int(x)]
            state = 0
        else:
            infotxt = "Sensor %s is CRIT(!!)" % knoerr_coolloop_map[int(x)]
            state = 2
        single_states.append( (state, infotxt) )
        x = x + 1
    worst_state = max([x[0] for x in single_states])
    info_text = ", ".join([x[1] for x in single_states])
    return(worst_state, info_text)

check_info['knoerr_coolloop_status'] = {
  "inventory_function"  : inventory_knoerr_coolloop_status,
  "check_function"      : check_knoerr_coolloop_status,
  "service_description" : "Enviroment",
  "has_perfdata"        : False,
  "group"               : "knoerr_coolloop_status",
  "snmp_info"           : ( ".1.3.6.1.4.1.2769.2.1.2.4", [ "1", "2", "3", "5", "6", "7", "8" ]),
  "snmp_scan_function"  : lambda oid: "coolcon" in oid(".1.3.6.1.2.1.1.1.0").lower()
}
```

## Knoerr Schrank Temperatur

```python
#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

def inventory_knoerr_coolloop_temp(info):
    if len(info) > 0:
        return [ (None, None) ]

def check_knoerr_coolloop_temp(item, params, info):
    temperature = info[0]
    warmluft = saveint(temperature[0]) / 10.0
    kaltluft = saveint(temperature[3]) / 10.0
    single_states = []
    if saveint(temperature[0]) >= saveint(temperature[2]):
        infotxt = "Warmluft ist %4.1f (!!)" % warmluft
        state = 2
        single_states.append( (state, infotxt, ("Warmluft", warmluft, saveint(temperature[1])/10.0, saveint(temperature[2])/10.0, 0, 50) ))
    elif saveint(temperature[0]) >= saveint(temperature[1]):
        infotxt = "Warmluft ist %4.1f (!)" % warmluft
        state = 1
        single_states.append( (state, infotxt, ("Warmluft", warmluft, saveint(temperature[1])/10.0, saveint(temperature[2])/10.0, 0, 50) ))
    else:
        infotxt = "Warmluft ist %4.1f" % warmluft
        state = 0
        single_states.append( (state, infotxt, ("Warmluft", warmluft, saveint(temperature[1])/10.0, saveint(temperature[2])/10.0, 0, 50) ))

    if saveint(temperature[3]) >= saveint(temperature[5]):
        infotxt = "Kaltluft ist %4.1f (!!)" % kaltluft
        state = 2
        single_states.append( (state, infotxt, ("Kaltluft", kaltluft, saveint(temperature[4])/10.0, saveint(temperature[5])/10.0, 0, 50) ))
    elif saveint(temperature[3]) >= saveint(temperature[4]):
        infotxt = "Kaltluft ist %4.1f (!)" % kaltluft
        state = 1
        single_states.append( (state, infotxt, ("Kaltluft", kaltluft, saveint(temperature[4])/10.0, saveint(temperature[5])/10.0, 0, 50) ))
    else:
        infotxt = "Kaltluft ist %4.1f" % kaltluft
        state = 0
        single_states.append( (state, infotxt, ("Kaltluft", kaltluft, saveint(temperature[4])/10.0, saveint(temperature[5])/10.0, 0, 50) ))

    worst_state = max([x[0] for x in single_states])
    info_text = ", ".join([x[1] for x in single_states])
    return(worst_state, info_text, [x[2] for x in single_states if x[2] != None])

check_info['knoerr_coolloop_temp'] = {
  "inventory_function"  : inventory_knoerr_coolloop_temp,
  "check_function"      : check_knoerr_coolloop_temp,
  "service_description" : "Temperature",
  "has_perfdata"        : True,
  "group"               : "knoerr_coolloop_temp",
  "snmp_info"           : ( ".1.3.6.1.4.1.2769.2.1.1", [ "1.3", "1.5", "1.6", "2.3", "2.5", "2.6" ]),
  "snmp_scan_function"  : lambda oid: "coolcon" in oid(".1.3.6.1.2.1.1.1.0").lower()
}
```

## Knoerr Schrank Temperatur Perf-O-Meter

```Python
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
```
