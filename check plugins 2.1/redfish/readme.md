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
- 2.1.3 - new numbering corresponding to the CMK version
- 2.1.4 - added retry and timeout option to the special agent
- 2.1.5 - item name building for HPE disks & volumes fixed
- 2.1.6 - missing optional section defenition inside WATO rule
- 2.1.7 - small bug if no oem section is found
- 2.1.8 - discovery bug for iLO 4 raidcontrollers
- 2.1.9 - resuse session token for login
- 2.1.10 - clarification for urllib3 v2 problem
- 2.1.11 - small formatting problems
- 2.1.12 - CPU discovery modified, storage controller check modified
- 2.1.13 - memory check respects HPE special states
- 2.1.16 - bugfixes for PSU & Temp discovery
- 2.1.17 - small bug fix to not discover ethernetinterfaces not connected
- 2.1.18 - rework special agent to use CMK included functions
- 2.1.19 - agent can handle a device without manager
- 2.1.28 - HDD/raid controller discovery improved
	multi system is now possible (blade chassis)
- 2.1.29 - Temp, PSU and Fan also multi system aware
- 2.1.30 - ignore offline interfaces
plugin in sync with 2.2 and 2.3 version
