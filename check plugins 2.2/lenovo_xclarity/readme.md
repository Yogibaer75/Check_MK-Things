# Redfish based API checks for Lenovo XClarity controller

First version of redfish API based special agent for Lenovo
XClarity controller.

Redfish Python module must be installed

Attention:

pip3 install 'urllib3<2' redfish

Changelog

- 2.0 - migrated to CMK 2.0
- 2.1 - import statement fixed inside the utils file
- 2.2 - next migration bug fixed and some adjustments to the performance data processing
- 2.3 - missing lenovo_utils file added
- 2.4 - bug in temperature header and value conversion inside fans check adjusted
- 2.5 - metric handling fixed for power supplies
- 2.6 - fan sensors are configureable with setup rules
- 2.7 - removed exception error
- 2.8 - ignore absent devices at discovery time / rework temp check
- 2.9 - fan check respect rpm vs. percent values, system state check added
- 3.0.0 - CMK 2.2 modifications
