# iLO Restful Redfish API Agent

Attention: version 2.0 is only usable with CMK 2.0 or newer

To use this agent you need to install the "python-ilorest-library".
Actual version can be found here https://pypi.python.org/pypi/python-ilorest-library

`pip install python-ilorest-library`

for CMK 2.0

`pip3 install python-ilorest-library`

The agent call is

/omd/sites/**your-site**/local/share/check_mk/agent/special/agent_ilo -u USER -p PASSWORD **IP**

For the user the minimal access rights inside iLO should be enought.

