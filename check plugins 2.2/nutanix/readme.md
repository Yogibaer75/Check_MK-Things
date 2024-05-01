# Nutanix checks

This package is an improved version of the included Nutanix special agent.

***Attention with CMK 2.3 this package is not needed anymore as it is already included in CMK.***

 - 3.1 - wrong api version for containers
 - 3.2 - camelCase vs. snake_case problem for different API versions
 - 3.3 - fix for hosts without disks
 - 3.5 - same version number as 2.0 version
 - 3.6 - fix for disconnected hosts
 - 3.7 - df_translation for containers and storage pools added
 - 3.8 - small bug in special agent
 - 3.9 - new checks for cluster cpu/mem/io, ha state and protection domains - Jeronimo Wiederhold (SVA)
 - 4.0 - some fixes and added missing files from Github PR
 - 4.0.0 - new version numbering for CMK Exchange
 - 4.0.1 - possible to ignore vm state - from https://github.com/jwiederh - cluster mem parameter name was wrong
 - 5.0.1 - starting version for CMK 2.2
 - 5.0.2 - some CMK 2.2 bugs fixed - added dummy files for existing legacy checks
 - 5.0.3 - VM tools state can be ignored
 - 5.0.4 - fixed unkown result if no vm memory values available
 - 5.0.5 - added network interface checks for hosts
 - 5.0.6 - bugfix for interface checks & metric definition
 - 5.0.7 - rate calculation problem fixed with host interfaces
 - 5.0.8 - reformating interface check
 - 5.0.9 - only set version number for working until
