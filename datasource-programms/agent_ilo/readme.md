# iLO Restful Redfish API Agent

To use this agent you need to install the "python-ilorest-library".
Actual version can be found here https://pypi.python.org/pypi/python-ilorest-library

`pip install python-ilorest-library`

The agent call is

/omd/sites/**your-site**/local/share/check_mk/agent/special/agent_ilo -u USER -p PASSWORD **IP**

For the user the minimal access rights inside iLO should be enought.
