# ENDPOINT assessment procedures

Version 0.1.0. Original procedures with primary references. Commands are reference probes; the workbench never executes them.

## ENDPOINT-01: Local administrative privilege and identity

Review assigned and effective local privilege on Windows or Linux.

### Interaction

read-only local inspection

### Prerequisites

- Owner-authorized local account and host inventory.
- Do not change group membership during the baseline.

### Procedure

- Record host identity and current user/groups.
- Review local administrators or sudo policy using approved read access.
- Map entries to business owners and check stale principals.

### Lab probes / inspection commands

```text
whoami /all
```

```text
Get-LocalGroupMember -Group Administrators
```

```text
id; sudo -l
```

### Expected secure behavior

Effective administrative access is necessary and attributable; day-to-day identities are separated from elevated roles.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Localized group names and directory resolution failures can hide membership. sudo -l may prompt; use only your authorized credentials.

### Remediation

Remove unjustified privilege and deploy scoped elevation workflows.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell
- Native identity tools
- osquery

### Primary references

- https://osquery.readthedocs.io/en/stable/

## ENDPOINT-02: Service executable and configuration permissions

Review whether a low-privilege identity can alter a privileged service dependency.

### Interaction

read-only configuration; planted-file lab validation

### Prerequisites

- Scoped service list and read access to service/registry/file ACLs.
- No service restart or executable replacement on production.

### Procedure

- Export service account and executable path.
- Inspect ACLs on the binary, parent directories, and configuration.
- Resolve quoting and path ambiguity in a lab clone.
- Validate effective write capability on a planted harmless file only.

### Lab probes / inspection commands

```text
Get-CimInstance Win32_Service | Select-Object Name,StartName,PathName,StartMode
```

```text
icacls "C:\Lab\Service\service.exe"
```

```text
systemctl cat lab-canary.service
```

### Expected secure behavior

Unprivileged identities cannot alter privileged service code or configuration.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

An unquoted path is not automatically exploitable if no candidate path is writable. An ACL listing does not alone prove effective write access.

### Remediation

Quote service paths correctly, lock down dependencies, and use least-privilege service identities.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell CIM
- icacls
- systemctl
- osquery

### Primary references

- https://osquery.readthedocs.io/en/stable/

## ENDPOINT-03: Scheduled task and startup boundaries

Identify writable startup dependencies that cross privilege boundaries.

### Interaction

read-only inventory; reversible lab canary

### Prerequisites

- Authorized startup/task inventory and ACL read access.
- Use a disposable scheduled task for any execution proof.

### Procedure

- Export task principal, trigger, action, and startup location.
- Inspect write permissions on each referenced file and directory.
- In the clone, replace only the planted canary action and observe a marker file.
- Restore and verify the fixture.

### Lab probes / inspection commands

```text
Get-ScheduledTask | Select-Object TaskName,TaskPath,State
```

```text
Get-CimInstance Win32_StartupCommand | Select-Object Name,Command,Location
```

```text
systemctl list-timers --all
```

### Expected secure behavior

Only trusted administrators can change dependencies executed with higher privilege.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Disabled tasks and unreachable triggers may not execute. Separate configuration weakness from demonstrated execution.

### Remediation

Restrict task/startup write permissions and reduce run-as privilege.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell ScheduledTasks
- osquery
- systemd tools

### Primary references

- https://osquery.readthedocs.io/en/stable/

## ENDPOINT-04: Patch and exposure validation

Reconcile package/build inventory with actual reachable services and vendor advisories.

### Interaction

read-only inventory

### Prerequisites

- Approved host and package inventory; dated vendor advisory for the relevant product.
- Do not equate a banner string with exploitability.

### Procedure

- Record OS build and installed package versions.
- Map relevant advisories to affected configuration and vendor backports.
- Validate listed service reachability from the approved vantage point.
- Record unavailable or contradictory evidence.

### Lab probes / inspection commands

```text
Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion,OsBuildNumber
```

```text
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 20
```

```text
osqueryi --json "select name,version from deb_packages limit 100;"
```

### Expected secure behavior

Relevant fixes are present or compensating controls are independently verified for the actual configuration.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Get-HotFix is not a complete software inventory; package backports and feature configuration affect applicability.

### Remediation

Apply vendor-supported updates and verify affected component state, not only update installation history.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Vendor advisories
- osquery
- Nmap scoped service validation

### Primary references

- https://osquery.readthedocs.io/en/stable/
- https://nmap.org/book/man.html

## ENDPOINT-05: Disk protection and boot integrity

Review encryption and boot protection states with the system owner.

### Interaction

read-only protection review

### Prerequisites

- Approved host and administrative read capability if needed.
- Never collect recovery keys or alter boot settings.

### Procedure

- Export encryption and secure-boot status.
- Check management escrow/rotation evidence without revealing keys.
- Compare device role and approved baseline.

### Lab probes / inspection commands

```text
Get-BitLockerVolume | Select-Object MountPoint,VolumeStatus,ProtectionStatus,EncryptionMethod
```

```text
Confirm-SecureBootUEFI
```

```text
lsblk -o NAME,TYPE,FSTYPE,MOUNTPOINTS
```

### Expected secure behavior

Required volumes and boot configuration meet the approved baseline; key handling is independently controlled.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Encrypted volume status differs from active protection. Firmware/VM capability can make some commands unsupported.

### Remediation

Enable supported protection through managed rollout and validate recovery processes separately.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell BitLocker
- Firmware configuration
- lsblk

### Primary references

- https://learn.microsoft.com/powershell/module/bitlocker/

## ENDPOINT-06: Endpoint firewall and remote administration

Validate intended inbound exposure using explicit owned test services.

### Interaction

read-only inventory plus bounded connections

### Prerequisites

- Expected service/port matrix, known host, and authorized source addresses.
- Do not disable the firewall or widen access for the test.

### Procedure

- Export listening sockets and active firewall profiles.
- Connect to only the listed test services from permitted and prohibited sources.
- Confirm the service is healthy through a permitted control path.

### Lab probes / inspection commands

```text
Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction
```

```text
Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess
```

```text
ss -lntup
```

### Expected secure behavior

Only necessary remote services are reachable from approved origins under the active profile.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A listening socket is not necessarily remotely reachable. Host and network firewalls can overlap.

### Remediation

Restrict listeners and firewall rules; secure remote administration with approved identity controls.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell NetSecurity
- ss
- Nmap explicit ports

### Primary references

- https://nmap.org/book/man.html

## ENDPOINT-07: Telemetry attribution and integrity

Check whether an owned canary action is captured with enough context for investigation.

### Interaction

harmless marker execution

### Prerequisites

- Synthetic marker action, telemetry owner, synchronized clocks.
- Record expected events before execution; never disable or tamper with sensors.

### Procedure

- Run the marker command once with the authorized test identity.
- Find local and centralized records.
- Compare user, host, parent process, command line, and timestamp.
- Record sensor loss or missing configuration explicitly.

### Lab probes / inspection commands

```text
cmd /c echo WB_ENDPOINT_CANARY
```

```text
printf WB_ENDPOINT_CANARY
```

### Expected secure behavior

The action is attributable in approved telemetry within the agreed latency and retention window.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Shell built-ins may not produce a separate process event; identify the shell process and the configured event sources.

### Remediation

Configure adequate logging, protect collection paths, and test ingestion health.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Windows event logs
- osquery configured event tables
- Velociraptor owned collection

### Primary references

- https://docs.velociraptor.app/
- https://osquery.readthedocs.io/en/stable/

## ENDPOINT-08: Secret storage controls without secret extraction

Evaluate whether credential-bearing locations have appropriate access controls.

### Interaction

metadata and synthetic-secret review

### Prerequisites

- Owner-provided inventory of credential storage locations and a planted fake-secret file.
- Do not dump process memory, credential stores, or real key material.

### Procedure

- Inspect ACLs and ownership metadata for listed locations.
- Test low-privilege access only against the fake-secret fixture.
- Review whether real locations use approved OS-protected storage.

### Lab probes / inspection commands

```text
icacls "C:\Lab\Secrets\fake-secret.txt"
```

```text
stat -c "%a %U %G %n" /opt/lab/fake-secret.txt
```

### Expected secure behavior

Only intended principals can access the fixture under equivalent storage policy; real secret handling meets the approved design.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A planted file can fail to model application encryption or service identity correctly. State the equivalence assumptions.

### Remediation

Use approved secret stores, least-privilege ACLs, and lifecycle controls; validate applications without copying secrets.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- icacls
- stat
- Owner configuration review

### Primary references

- https://osquery.readthedocs.io/en/stable/

## ENDPOINT-09: Application control and signed-code policy

Test policy enforcement with benign known files rather than malware or bypass tooling.

### Interaction

benign executable lab validation

### Prerequisites

- Disposable endpoint and owner-approved benign signed/unsigned test binaries.
- Agree rollback and the expected allow/deny matrix.

### Procedure

- Record application-control policy and enforcement mode.
- Attempt the approved benign executable set.
- Compare block/allow decisions and audit events.
- Distinguish audit-only policy from enforced blocking.

### Lab probes / inspection commands

```text
Fixture matrix: approved signed tool; unsigned benign hello-world; approved script; disallowed benign script.
```

### Expected secure behavior

Execution decisions and audit records match the approved policy on the actual user context.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A blocked executable may fail for missing dependencies rather than application control. Use the policy event as corroboration.

### Remediation

Deploy tested enforced policy and review exceptions with accountable owners.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Windows application-control event logs
- Platform-native policy tools

### Primary references

- https://learn.microsoft.com/windows/security/application-security/application-control/

## ENDPOINT-10: Recovery and retest evidence

Demonstrate that a reversible lab incident can be restored without claiming general ransomware resilience.

### Interaction

owner-operated reversible restore exercise

### Prerequisites

- Snapshot of a disposable VM, synthetic files, and an approved restore procedure.
- No destructive encryption or backup deletion.

### Procedure

- Hash a small synthetic directory.
- Have the owner perform a reversible fixture change.
- Restore from the approved snapshot/backup.
- Verify file hashes and measure elapsed recovery against the stated objective.

### Lab probes / inspection commands

```text
Use evidence-seal before the fixture change and after restore.
```

```text
Record restore point, backup age, recovery start/end UTC, and failed verification items.
```

### Expected secure behavior

The defined synthetic recovery objective is met and restored content matches the baseline.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

One VM restore does not validate identity recovery, immutable backups, or organization-wide disaster recovery.

### Remediation

Correct restore gaps and repeat the same bounded recovery scenario with documented dependencies.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Hypervisor snapshot tools
- Backup platform
- evidence-seal

### Primary references

- https://csrc.nist.gov/pubs/sp/800/115/final

