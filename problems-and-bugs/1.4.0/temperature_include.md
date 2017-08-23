temperature.include not working correctly for device levels

diff --git a/checks/temperature.include b/checks/temperature.include
index a38a8ebdd6..73268d5aca 100644
--- a/checks/temperature.include
+++ b/checks/temperature.include
@@ -132,5 +132,5 @@ def check_temperature_determine_levels(dlh, usr_warn, usr_crit, usr_warn_lower,
     # Use device's levels if present, otherwise yours
     elif dlh == "devdefault":
-        if dev_warn is not None and dev_crit is None:
+        if dev_warn is not None and dev_crit is not None:
             warn, crit = dev_warn, dev_crit
         else:
