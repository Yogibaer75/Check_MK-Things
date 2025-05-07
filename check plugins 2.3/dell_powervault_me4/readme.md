# Monitoring for Dell/EMC Powervault ME4 Storage devices

Changelog:

- 2.2 - python path corrected in special agent for python3 disk check set to the right check parameters for temperature checks
- 2.3 - global hot spare status is ok for disks
- 2.4 - disks check now uses TempParamDict as params
- 2.5 - set user/pw hash to sha256
- 3.0.0 - ported to CMK 2.2
- 3.1.0 - prevent crashes if no data is present
- 3.3.0 - changes to be CMK 2.3 rdy
- 3.3.1 - writing json data fixed in special agent
- 3.3.2 - added option for certificate verification
- 3.4.0 - ported to CMK 2.3 API
- 3.4.3 - bug fix for passwords from password store - thx aeckstein
