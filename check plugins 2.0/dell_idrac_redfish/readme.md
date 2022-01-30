# Dell iDRAC Restful Redfish API Agent for CMK 2.0

To use this agent you need to install the "redfish" library.

for CMK 2.0

`pip3 install redfish`

The agent call is

/omd/sites/**your-site**/local/share/check_mk/agent/special/agent_dell_idrac -u USER -p PASSWORD **IP**

For the user the minimal access rights inside iDRAC should be enought.
