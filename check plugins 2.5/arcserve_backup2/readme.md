# Rewrite of the old Arcserve backup status check

## Changelog:

- 1.0.0 - first version of Powershell script and check - no parameters possible at this version
- 1.0.1 - changed parsing of agent data
- 1.0.2 - parsing problem with empty lists solved
- 1.1.0 - CMK 2.3 API migration + bakery plugin
- 1.1.1 - typo in agent ps1
- 1.1.2 - formatting
- 1.1.3 - connect string fixed in agent plugin
- 1.1.4 - make mypy happy
- 1.1.5 - small format issues
- 1.2.0 - migrated bakery files to agent folder

# Options

No Setup options available at the moment.
Job state is evaluated against the event ids from the job database.
