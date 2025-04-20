# Arcserve UDP Backup Check

With the two checks the last job status and the recovery point status of the Arcserve UDP backup jobs can be checked.
Parameters can be defined for the age of the backup job and the amount of available recovery points.
For booth checks it can also be defined what the status of the job should be in case no backup exists of one host.

Changelog:

- 1.0.0 - initial version
- 2.1.0 - missing closing brackets for second section of plugin output
- 2.2.0 - moved files to correct location for CMK 2.3/2.4
- 2.2.1 - migrated rulesets and checks to new API
- 2.2.2 - small migration bugs fixed
