Perf-O-Meter not working correctly for bits/s output of check.

diff --git a/web/plugins/perfometer/check_mk.py b/web/plugins/perfometer/check_mk.py
index 4457d28690..d958a26156 100644
--- a/web/plugins/perfometer/check_mk.py
+++ b/web/plugins/perfometer/check_mk.py
@@ -340,5 +340,5 @@ def perfometer_bandwidth(in_traffic, out_traffic, in_bw, out_bw, unit = "B"):

 def perfometer_check_mk_if(row, check_command, perf_data):
-    unit = "Bit" if  "Bit/s" in row["service_plugin_output"] else "B"
+    unit = "Bit" if  "Bit/s" in row["service_plugin_output"] or "bit/s" in row["service_plugin_output"] else "B"
     return perfometer_bandwidth(
         in_traffic  = savefloat(perf_data[0][1]),
