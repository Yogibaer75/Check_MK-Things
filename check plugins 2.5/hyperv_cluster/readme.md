# Hyper-V Checks for Cluster and VM Date

## Informations

- Only one rule for all the agent plugins - "Hyper-V" - **don't** use the deprecated one "Hyper-V VMs (Windows)"
- Inside this rule you can select what plugins should be deployed
  - "Hyper-V host monitoring" - for Hyper-V VMs 
  - "Hyper-V cluster monitoring" - for Hyper-V cluster nodes and cluster resources
  - "Hyper-V host CSV monitoring" - for Hyper-V cluster shared volume monitoring

## Changelog

* 3.2.7  - small modifications for CMK 2.3
* 3.2.8  - hyperv-vm-nic fix if no data
* 3.2.9  - cluster-roles angepasst
* 3.2.10 - parsing hyperv_io angepasst
* 3.2.11 - more fixes
* 3.2.13 - next fix host io
* 3.2.13 - next fix :)
* 3.3.0  - migrated to CMK 2.3 API
* 3.3.1  - fixed params handling
* 3.3.2  - typo in check function
* 3.3.3  - some spelling corrected
* 3.3.5  - naming error in bakery rule
* 3.3.7  - default parameter problem with vm integration
* 3.3.8  - modified deployment rule for cluster plugin
* 3.3.10 - typo
* 3.3.11 - HyperV roles cluster check function added
* 3.3.15 - wrong default params fixed
* 3.3.16 - second fix for default params
* 3.3.17 - make mypy happy
* 3.4.2  - CMK 2.5 modifications
* 3.4.3  - fixed detection inside parse_hyperv
* 3.4.4  - same patchlevel as 2.4 version
* 3.4.5 - improved runtime of agent plugins
* 3.4.6 - fixed cluster role cluster function
* 3.4.7 - temp version
* 3.4.8 - replaced hyperv_host.ps1 with new version and modified checks to support old and new one
