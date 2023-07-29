# iLO Restful Redfish API Agent for CMK 2.0

To use this agent you need to install the "redfish" library.

for CMK 2.0

**Attention: after the release of urllib3 v2 now please do**

`pip3 install 'urllib3<2' redfish`

The agent call is

/omd/sites/**your-site**/local/share/check_mk/agents/special/agent_ilo -u USER -p PASSWORD **IP**

For the user the minimal access rights inside iLO should be enought.
