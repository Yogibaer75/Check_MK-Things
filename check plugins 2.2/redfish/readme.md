This is the frist version of an universal Redfish agent.
To use this agent you need the Redfish Python module installed.

**Attention: after the release of urllib3 v2 now please do**

**pip3 install 'urllib3<2' redfish**

- 1.0 - first version with support for Dell und HPE
- 1.1 - fetched section configureable from setup
- 1.2 - command line options for port and protocol
- 1.3 - added system and storage controller status
- 1.4 - memory summary added
- 2.0.0 - portet to CMK 2.2
- 2.0.1 - bug in special agent command line building
- 2.0.2 - fan item name building, network adapter data
- 2.0.3 - networkadapter status crash
- 2.2.3 - new numbering corresponding to the CMK version
- 2.2.4 - added retry and timeout option to the special agent
- 2.2.5 - item name building for HPE disks & volumes fixed
- 2.2.6 - missing optional section defenition inside WATO rule
- 2.2.7 - small bug if no oem section is found
- 2.2.8 - discovery bug for iLO 4 raidcontrollers
- 2.2.9 - resuse session token for login
- 2.2.10 - clarification for urllib3 v2 problem
- 2.2.11 - small formatting problems
- 2.2.12 - CPU discovery modified, storage controller check modified
- 2.2.13 - memory check respects HPE special states
- 2.2.16 - bugfixes for PSU & Temp discovery
- 2.2.17 - small bug fix to not discover ethernetinterfaces not connected
- 2.2.18 - rework special agent to use CMK included functions
- 2.2.19 - agent can handle a device without manager
- 2.2.20 - output connection error message as agent version string
- 2.2.28 - changes in sync with 2.3 version - HDD/raid controller discovery improved - 
    multi system is now possible (blade chassis)
- 2.2.29 - Temp, PSU, Voltage and Fan also multi system aware
- 2.2.30 - ignore offline interfaces & code formatting
- 2.2.31 - discovery fix for drives and volumes
- 2.2.33 - fixed bug for iLO5 firmware 3.0 and newer to detect
           disk, controller and volumes + typo fix
- 2.2.41 - explicitly don't try to fetch collections without members + changes from upstream
- 2.2.42 - added extra special agent for power equipment with Redfish support
- 2.2.43 - fixed crash for components without state information
- 2.2.45 - outlets without measurements working
- 2.2.46 - firmware inventory is back for HPE devices
- 2.2.47 - changed behaviour if data could not be fetched
           small fix for firmware checks
- 2.2.48 - fixed exception in message decoding
- 2.2.49 - fixed firmware inventory for ilo4 & added dedicated view for inventory & exception fix
- 2.2.50 - voltage sensor without names are ignored
- 2.2.51 - small naming modification for HW/SW inventory table
