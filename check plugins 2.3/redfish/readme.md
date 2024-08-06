# Redfish Special Agent

This is the frist version of an universal Redfish agent.
With CMK 2.3 the extra installation of Python module is not needed anymore.
The Redfish library is already existing inside CMK.

- 2.3.20 - fast alles nach 2.3 migriert
- 2.3.21 - small API changes
- 2.3.22 - last migration for special agent rule
- 2.3.23 - file renaming
- 2.3.24 - all migrated - only password cannot entered
  correctly in rule (hidden)
- 2.3.25 - update daily build
- 2.3.26 - migration for the last API v2 changes
- 2.3.28 - HDD/raid controller discovery improved
  multi system is now possible (blade chassis)
- 2.3.29 - Temp, PSU and Fan also multi system aware
- 2.3.30 - ignore offline interfaces
  without number - modifications for 2.3alpha
- 2.3.31 - 2.3b1 ready and discovery fix for drives and volumes
- 2.3.32 - ruleset changes for 2.3.0b4, typo
- 2.3.33 - fixed bug for iLO5 firmware 3.0 and newer to detect disk, controller and volumes - typo fix
- 2.3.34-36 - 2.3 beta fixes for some API changes and passwords
- 2.3.37 - moved last file to new plugin folder structure
- 2.3.38 - fix SSC plugin if retries and timeout are selected
- 2.3.39 - exit code of special agent now reflects errors
- 2.3.40 - removed print statement
- 2.3.41 - explicitly don't try to fetch collections without members
- 2.3.42 - added extra special agent for power equipment with Redfish support
- 2.3.43 - fixed crash for components without state information
- 2.3.44 - moved all files to addon folder
- 2.3.45 - forgotten paths from last patch fixed and outlets without measurements working
- 2.3.46 - firmware inventory is back for HPE devices
- 2.3.47 - changed behaviour if data could not be fetched
- 2.3.48 - fixed exception in message decoding
- 2.3.49 - fixed firmware inventory for ilo4 & added dedicated view for inventory & exception fix
- 2.3.50 - voltage sensor without names are ignored
- 2.3.51 - small naming modification for HW/SW inventory table
- 2.3.52 - firmware inventory for all vendors that use the path UpdateService/FirmwareInventory
- 2.3.53 - standby Firmware is shown as ok
- 2.3.54 - fixed crash if no fans or temperatures exists in the thermal section
- 2.3.55 - removed autoexpand for iLO4
- 2.3.56 - changed location of inventory view file
- 2.3.57 - add "StandbyOffline" to ignored states for discovery of ethernet interfaces
