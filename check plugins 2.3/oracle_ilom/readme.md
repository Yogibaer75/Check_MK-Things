# Oracle ILOM Checks

Basic Oracle ILOM checks for

- temperature
- fan
- voltage
- other sensors

At the moment own parameters can only be defined for the temperature check.
The other checks can only use the parameters from the device.

Changelog:

- 1.0 - first release
- 2.0 - check migrated to CMK 2.0
- 2.1.0 - migrated to CMK 2.3
- 2.1.1 - added parameters for other sensors than temperature
- 2.2.0 - ported to CMK 2.3 API
- 2.2.1 - fixed levels parameter bug
