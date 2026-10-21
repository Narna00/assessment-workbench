# AD assessment procedures

Version 0.1.0. Original procedures with primary references. Commands are reference probes; the workbench never executes them.

## AD-01: Password policy and effective fine-grained policy

Review the effective policy of a specific test principal, including exceptions.

### Interaction

read-only directory inspection

### Prerequisites

- Authorized domain read account and RSAT ActiveDirectory module.
- Known test principal lab.user; no password guessing.

### Procedure

- Export the domain default.
- Query resultant policy for lab.user.
- If no resultant policy is returned, document default inheritance.
- Compare to the organization-approved standard and lockout monitoring.

### Lab probes / inspection commands

```text
Get-ADDefaultDomainPasswordPolicy
```

```text
Get-ADUserResultantPasswordPolicy -Identity lab.user
```

### Expected secure behavior

Effective controls meet the approved standard; exceptions have an owner and expiry.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A strong domain default can be overridden by a fine-grained policy. A missing resultant policy is not automatically a collection failure.

### Remediation

Reconcile policy precedence and exceptions, then retest the actual assigned policy.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- RSAT ActiveDirectory
- AD policy exports

### Primary references

- https://learn.microsoft.com/powershell/module/activedirectory/get-addefaultdomainpasswordpolicy
- https://learn.microsoft.com/powershell/module/activedirectory/get-aduserresultantpasswordpolicy

## AD-02: Nested privileged membership

Find indirect administrative access and explain every membership hop.

### Interaction

read-only directory inspection

### Prerequisites

- Approved directory snapshot and privileged group inventory.
- Document domain SID and custom delegated admin groups.

### Procedure

- Enumerate direct and recursive privileged membership.
- Compare SID-based group identities across domains.
- Trace suspicious principals to their source group.
- Review stale and service-account members with the owner.

### Lab probes / inspection commands

```text
Get-ADGroupMember -Identity 'Domain Admins'
```

```text
Get-ADGroupMember -Identity 'Domain Admins' -Recursive
```

### Expected secure behavior

Privileged membership is limited, justified, and attributable through a complete path.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Localized group names differ. Recursive output can hide the path; keep direct membership records too.

### Remediation

Remove unjustified inherited privileges, separate administrative identities, and review nested groups.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- BloodHound CE
- RSAT
- iam-path-review normalized export

### Primary references

- https://bloodhound.specterops.io/
- https://learn.microsoft.com/powershell/module/activedirectory/get-adgroupmember

## AD-03: Delegation configuration

Locate unconstrained, constrained, and resource-based delegation settings for owner review.

### Interaction

read-only directory inspection

### Prerequisites

- Read access to approved computer and service-account objects.
- Snapshot the lab before any later validation; this card changes no delegation.

### Procedure

- Export delegation-related attributes for scoped objects.
- Map each allowed service to an actual business dependency.
- Review who can modify the relevant objects and delegation attributes.
- Flag stale/overbroad entries for a separately approved validation.

### Lab probes / inspection commands

```text
Get-ADComputer -Filter * -Properties TrustedForDelegation,msDS-AllowedToDelegateTo,msDS-AllowedToActOnBehalfOfOtherIdentity | Select-Object Name,TrustedForDelegation,msDS-AllowedToDelegateTo,msDS-AllowedToActOnBehalfOfOtherIdentity
```

### Expected secure behavior

Delegation is constrained to documented needs and its configuration is writable only by authorized administrators.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Attribute presence alone does not prove a usable attack path; service availability, identity protections, and ACLs matter.

### Remediation

Remove obsolete delegation, restrict configuration ACLs, and prefer least-privilege delegation designs.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- RSAT
- BloodHound CE

### Primary references

- https://learn.microsoft.com/powershell/module/activedirectory/get-adcomputer
- https://bloodhound.specterops.io/

## AD-04: AD CS template and enrollment review

Assess whether certificate issuance rules can overstate identity or privilege.

### Interaction

configuration review; lab enrollment is separate

### Prerequisites

- Authorized CA/template read access; dedicated test template for any enrollment proof.
- Never request a certificate for another real user.

### Procedure

- Inventory templates, enrollment permissions, subject controls, EKUs, approval settings, and CA publication.
- Review conjunctions of settings rather than one flag.
- If approved, enroll only as the synthetic principal using a test template and verify the resulting subject.

### Lab probes / inspection commands

```text
certutil -CATemplates
```

```text
Review a sanitized template export for: enrollment ACL, subject-name control, EKUs, issuance requirements, and publication state.
```

### Expected secure behavior

Enrollment and identity-binding rules match intended certificate use; unauthorized principals cannot obtain higher-privilege identities.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A risky template flag without enrollment permission, CA publication, or compatible authentication settings is not demonstrated exploitation.

### Remediation

Tighten enrollment rights and subject controls, remove unused authentication templates, and review CA-level settings.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Certipy discovery mode after owner review
- certutil
- CA audit logs

### Primary references

- https://github.com/ly4k/Certipy
- https://bloodhound.specterops.io/

## AD-05: LDAP transport and signing evidence

Determine whether directory authentication and query transport meet policy at both client and server.

### Interaction

read-only configuration plus controlled bind

### Prerequisites

- Known test account; owner-defined LDAP/LDAPS endpoint and TLS trust store.
- Capture no real user passwords.

### Procedure

- Review server signing/channel-binding policy and client compatibility.
- Connect with the approved LDAP client using certificate validation.
- Record negotiated transport and rejection of the explicitly prohibited lab configuration.
- Check directory server events for the same test time.

### Lab probes / inspection commands

```text
Use ldp.exe against the lab DC with the approved TLS/signing configuration; record connection properties.
```

```text
Offline filter canary: (sAMAccountName=lab.user)
```

```text
Escaped filter value for literal star: lab\2auser
```

### Expected secure behavior

Required signing, TLS trust, and channel-binding policy are enforced as designed without weakening client validation.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A successful LDAPS socket connection does not establish authentication policy. A failed bind can be caused by identity errors.

### Remediation

Stage enforcement with client inventory, use validated certificates, and investigate incompatible clients.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- ldp.exe
- Directory event logs
- Included ldap_escape.py

### Primary references

- https://learn.microsoft.com/powershell/module/activedirectory/
- https://learn.microsoft.com/windows/win32/ldap/ldap-ssl-connections

## AD-06: SMB signing and legacy protocol posture

Review signing requirements and legacy protocol exposure on scoped lab hosts.

### Interaction

read-only host inspection

### Prerequisites

- Authorized local configuration read on a member host and server.
- Identify client/server roles separately.

### Procedure

- Export SMB client and server settings.
- Compare configured requirements to negotiated sessions from approved clients.
- Correlate with the role and approved compatibility exceptions.

### Lab probes / inspection commands

```text
Get-SmbServerConfiguration | Select-Object RequireSecuritySignature,EnableSecuritySignature,EnableSMB1Protocol,EnableSMB2Protocol
```

```text
Get-SmbClientConfiguration | Select-Object RequireSecuritySignature,EnableSecuritySignature
```

### Expected secure behavior

Signing and supported protocols satisfy policy on both ends; exceptions are documented and bounded.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Configuration capability is not negotiated protection. Client and server policies differ; defaults vary by release.

### Remediation

Remove obsolete protocol dependencies and enforce signing through staged policy rollout.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- PowerShell SMB cmdlets
- Wireshark on owned captures

### Primary references

- https://learn.microsoft.com/windows-server/storage/file-server/troubleshoot/detect-enable-and-disable-smbv1-v2-v3

## AD-07: Kerberos account attribute review

Identify service accounts and authentication exceptions that warrant deeper review.

### Interaction

read-only directory inspection

### Prerequisites

- Approved scoped account list, directory read access, and account owners.
- No ticket harvesting, offline password cracking, or password spraying is performed by this procedure.

### Procedure

- Export SPNs, preauthentication exceptions, encryption configuration, and password-change dates.
- Reconcile service dependencies and account management model.
- Review effective privilege paths before prioritizing a finding.

### Lab probes / inspection commands

```text
Get-ADUser -Filter * -Properties ServicePrincipalName,DoesNotRequirePreAuth,msDS-SupportedEncryptionTypes,PasswordLastSet | Select-Object SamAccountName,ServicePrincipalName,DoesNotRequirePreAuth,msDS-SupportedEncryptionTypes,PasswordLastSet
```

### Expected secure behavior

Authentication exceptions are justified; service identities have appropriate managed credentials and least privilege.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

An SPN or old timestamp does not prove a weak password or a usable compromise. Configuration flags need context.

### Remediation

Use suitable managed service accounts, remove obsolete exceptions, and minimize service-account privileges.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- RSAT
- BloodHound CE

### Primary references

- https://learn.microsoft.com/powershell/module/activedirectory/get-aduser
- https://bloodhound.specterops.io/

## AD-08: Trust boundaries and cross-domain privilege

Verify intended trust direction and privileged access across domain boundaries.

### Interaction

read-only directory inspection

### Prerequisites

- Written scope listing every participating forest/domain.
- Read access and an owner-provided trust design.

### Procedure

- Export trust metadata.
- Compare direction, transitivity, and filtering settings to the design.
- Trace approved cross-domain membership paths.
- Mark inaccessible domains as coverage gaps rather than secure.

### Lab probes / inspection commands

```text
Get-ADTrust -Filter * | Select-Object Name,Direction,ForestTransitive,IntraForest,SIDFilteringForestAware,SIDFilteringQuarantined
```

### Expected secure behavior

Trust properties and cross-domain privileges are necessary, documented, and restricted.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A trust object alone does not imply universal authorization; selective authentication and resource ACLs matter.

### Remediation

Remove obsolete trusts and constrain cross-boundary authentication and administrative paths.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- RSAT
- BloodHound CE

### Primary references

- https://learn.microsoft.com/powershell/module/activedirectory/get-adtrust
- https://bloodhound.specterops.io/

## AD-09: GPO and administrative object write paths

Review whether low-privilege principals can alter privileged policy objects.

### Interaction

read-only directory inspection

### Prerequisites

- Approved GPO GUIDs and group policy administration read access.
- No GPO modification is needed for this card.

### Procedure

- Export delegated GPO permissions.
- Inspect linked OU targets and inheritance.
- Review write access to policy content and directory objects.
- Use a lab clone for any later change-and-revert demonstration.

### Lab probes / inspection commands

```text
Get-GPPermission -Guid '00000000-0000-0000-0000-000000000001' -All
```

```text
Get-Acl 'AD:OU=Lab,DC=example,DC=test' | Format-List
```

### Expected secure behavior

Write-capable identities and links match the approved administrative boundary.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

An ACL string can omit effective group membership or deny interactions. Read permission is not write permission.

### Remediation

Restrict delegation, validate OU inheritance, and monitor policy changes.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- GroupPolicy module
- AD ACL export
- BloodHound CE

### Primary references

- https://learn.microsoft.com/powershell/module/grouppolicy/get-gppermission
- https://bloodhound.specterops.io/

## AD-10: Detection and recovery of an approved directory action

Check whether a harmless approved directory action is visible and attributable.

### Interaction

reversible lab-only state change

### Prerequisites

- A synthetic group and synthetic user; explicit permission for a reversible membership change.
- Defender contact and rollback owner; telemetry time synchronization.

### Procedure

- Record the expected audit event and detection latency budget.
- Have the authorized operator perform the lab membership change.
- Verify the event identifies subject, target, and time.
- Revert the change and verify removal plus event visibility.

### Lab probes / inspection commands

```text
Lab action specification: add lab.user to LAB-CANARY-GROUP, then remove it under the owner-approved change record.
```

```text
Query the collected security events for the exact principal, group, and UTC test interval.
```

### Expected secure behavior

The approved change and rollback are detected within the agreed interval with correct identity attribution.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Missing centralized logs can reflect ingestion delay rather than absent host auditing. Clock skew distorts latency.

### Remediation

Enable appropriate auditing, repair collection paths, and test alert logic with owned canaries.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Windows event logs
- SIEM
- MITRE ATT&CK mapping

### Primary references

- https://attack.mitre.org/resources/get-started/adversary-emulation-and-red-teaming/

