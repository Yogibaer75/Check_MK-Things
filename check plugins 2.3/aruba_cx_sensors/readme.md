# Aruba CX 6k Sensor Status

Checks the state of PSU, temperature and fans on Aruba CX 6k switches.

Only the temperature check can be configured.
For PSU and fans only the ok state is known at the moment.

Changelog:

- 1.0.0 - initial release
- 1.1.0 - detect all CX series switches
- 2.3.0 - CMK 2.3 ready
- 2.4.0 - migrated to CMK 2.3 check API
- 2.4.1 - wrong import in utils fixed
- 2.4.2 - cleaned relative imports
- 2.4.3 - wrong levels check fixed
- 2.4.4 - don't discover empty fans
- 2.4.5 - removed temperature check as it is included with CMK 2.4
