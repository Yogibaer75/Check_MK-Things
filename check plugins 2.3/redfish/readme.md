This is the frist version of an universal Redfish agent.
To use this agent you need the Redfish Python module installed.

**Attention: after the release of urllib3 v2 now please do**

**pip3 install 'urllib3<2' redfish**

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
