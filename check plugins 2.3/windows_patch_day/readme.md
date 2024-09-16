# Windows Patch Day Status

This plugin will read the patch history and shows installed patches for a given number of installs in history. It is possible to filter unwanted install entries. It is possible to set a value in days since the last install of patches/updates.

- 1.1 - Deployment definition and first rule plugin
- 1.2 - modified config file creation and the config reading to be UTF-8 save on older Powershells (<= v5.1) - v6 and higher reads all files as UTF-8 also without BOM
- 1.3 - windows plugin output encoding set to UTF-8
- 1.4 - same header for all powershell plugins
- 1.5 - error in agent bakery script
- 1.6 - small error fixed
- 1.7 - fixed rule to check assignment and also checking against the rule values
- 1.8 - filter string fixed for Powershell script
- 1.9 - empty agent output respected
- 2.1.0 - small import adjustments for CMK 2.1 & check if UpdateCount is 0 inside PS Script
- 2.3.0 - migrated check function and rulesets to CMK 2.3 API
- 2.3.1 - moved files to plugin folder, no updates found don't result in UNKN anymore
- 2.3.2 - some code formatting
