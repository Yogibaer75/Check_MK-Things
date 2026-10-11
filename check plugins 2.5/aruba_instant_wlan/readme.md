# Aruba Instant WLAN Checks

Checks for Aruba Instant WLAN virtual controllers and access points on Checkmk 2.5.

## Discovery behavior

- Aruba virtual controllers (`sysObjectID` ending in `.71`) provide cluster and per-AP services.
- Physical Aruba Instant APs (`sysObjectID` ending in `.87`) provide these services only when their AP inventory contains exactly one AP.
- Physical APs with an empty inventory or multiple inventory entries suppress these services to avoid duplicate cluster monitoring.
- Other supported Aruba device IDs retain their existing behavior.

The standalone physical-AP behavior is based on the assumption that its AP inventory contains exactly one entry and still requires validation against a real standalone device.

## Changelog

- 1.1.0 - Update for Checkmk 2.3.
- 1.2.0 - Migrated to the Checkmk 2.3 API.
- 1.2.1 - Typo fix.
- 1.2.2 - Fixed levels bug.
- 1.2.3 - Added new OIDs for detection.
- 1.2.4 - Added new OIDs for detection.
- 1.3.0 - Update for Checkmk 2.5; added per-AP client and radio checks and filtered duplicate cluster services on physical APs.
