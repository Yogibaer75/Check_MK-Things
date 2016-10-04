Alt

battery_status    "2.1.1.0",  # PowerNet-MIB::upsBasicBatteryStatus,
output_status     "4.1.1.0",  # PowerNet-MIB::upsBasicOutputStatus,
battery_capacity  "2.2.1.0",  # PowerNet-MIB::upsAdvBatteryCapacity,
system_temp       "2.2.2.0",  # PowerNet-MIB::upsAdvBatteryTemperature,
battery_replace   "2.2.4.0",  # PowerNet-MIB::upsAdvBatteryReplaceIndicator,
num_batt_packs    "2.2.6.0",  # PowerNet-MIB::upsAdvBatteryNumOfBadBattPacks,
battery_current   "2.2.9.0",  # PowerNet-MIB::upsAdvBatteryCurrent,
input_voltage     "3.2.1.0",  # PowerNet-MIB::upsAdvInputVoltage,
output_voltage    "4.2.1.0",  # PowerNet-MIB::upsAdvOutputVoltage,
output_current    "4.2.4.0",  # PowerNet-MIB::upsAdvOutputCurrent,
time_remaining    "2.2.3.0",  # PowerNet-MIB::upsAdvBatteryRunTimeRemaining,
calib_result      "7.2.6.0",  # PowerNet-MIB::upsAdvTestCalibrationResults
output_load       "4.2.3.0",  # PowerNet-MIB::upsAdvOutputLoad
last_diag_date    "7.2.4.0",  # PowerNet-MIB::upsLastDiagnosticsDate
                  "11.1.1.0", # PowerNet-MIB::upsBasicStateOutputState

Neu

battery_status      "2.1.1.0",  # PowerNet-MIB::upsBasicBatteryStatus,
output_status       "4.1.1.0",  # PowerNet-MIB::upsBasicOutputStatus,
state_output_state  "11.1.1.0", # PowerNet-MIB::upsBasicStateOutputState
battery_capacity    "2.2.1.0",  # PowerNet-MIB::upsAdvBatteryCapacity,
battery_temp        "2.2.2.0",  # PowerNet-MIB::upsAdvBatteryTemperature,
battery_replace     "2.2.4.0",  # PowerNet-MIB::upsAdvBatteryReplaceIndicator,
battery_num_batt_packs  "2.2.6.0",  # PowerNet-MIB::upsAdvBatteryNumOfBadBattPacks,
battery_current     "2.2.9.0",  # PowerNet-MIB::upsAdvBatteryCurrent,
input_voltage       "3.2.1.0",  # PowerNet-MIB::upsAdvInputVoltage,
output_voltage      "4.2.1.0",  # PowerNet-MIB::upsAdvOutputVoltage,
output_current      "4.2.4.0",  # PowerNet-MIB::upsAdvOutputCurrent,
battery_time_remain "2.2.3.0",  # PowerNet-MIB::upsAdvBatteryRunTimeRemaining,
calib_result        "7.2.6.0",  # PowerNet-MIB::upsAdvTestCalibrationResults
output_load         "4.2.3.0",  # PowerNet-MIB::upsAdvOutputLoad
last_diag_date      "7.2.4.0",  # PowerNet-MIB::upsLastDiagnosticsDate
 
 
state_output_state  "11.1.1.0", # PowerNet-MIB::upsBasicStateOutputState
Muss als letztes abgefragt werden - wenn die vor "battery_current" erfolgt so wird bei einigen APC USV der 
"battery_current" mit einem Wert von "Battery current: 1000000000 A" ausgegeben was wirklich etwas unrealistisch ist.
