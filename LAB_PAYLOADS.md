# Domain lab payloads and validation recipes

These recipes supplement the 42 case cards. Use only the named synthetic fixtures on an isolated owned lab. They are manual, bounded proofs, not commands executed by the workbench. Retain controls, exact output, timestamps, and rollback evidence. Third-party command syntax must be checked against the installed tool/module version. AD, radio, and endpoint recipes below are reference procedures and have not been executed against a provisioned AD/RF/endpoint lab in this release.

## Web: paired flawed/fixed fixtures

Start `python lab_web.py --port 8765`, then run:

```sh
# A can read A's object: positive control.
curl --max-time 5 -H 'Authorization: Bearer lab-a' 'http://127.0.0.1:8765/orders?id=1001'
# B requests the same A-owned fixture: should be denied in fixed mode.
curl --max-time 5 -H 'Authorization: Bearer lab-b' 'http://127.0.0.1:8765/orders?id=1001'
# B's own object: distinguishes a broken/invalid token from object enforcement.
curl --max-time 5 -H 'Authorization: Bearer lab-b' 'http://127.0.0.1:8765/orders?id=2001'

# Boolean SQL pair: flawed fixture returns one row, then no rows.
curl --max-time 5 'http://127.0.0.1:8765/search?id=1%20AND%201%3D1'
curl --max-time 5 'http://127.0.0.1:8765/search?id=1%20AND%201%3D2'
```

Stop the fixture and rerun with `--secure`. The foreign-order request becomes 404, the own-object controls remain 200, and both SQL expressions are rejected as nonnumeric. This is a control comparison, not a claim about any real app.

For the reflected-markup fixture, enter this complete URL into a disposable browser profile:

```text
http://127.0.0.1:8765/echo?q=%3Csvg%20onload%3D%22document.documentElement.dataset.wbprobe%3D%27executed%27%22%3E%3C%2Fsvg%3E
```

Inspect `document.documentElement.dataset.wbprobe`. Flawed-mode markup can set the marker. Fixed mode HTML-encodes the text. No cookies are read and no data leaves the browser. This URL is a lab payload; the CLI tests verify encoding behavior, not browser-specific event execution.

Other domain-specific web probes are in WEB.md: arithmetic template canaries, planted-file traversal, shell marker printing, owned SSRF callbacks, upload type mismatches, state-transition replay, and isolated parser-boundary fixtures. Most are test specifications for applications you must construct separately; only the three routes above are implemented in the supplied server.

## AD: controlled write-right proof on a synthetic object

Provision `lab.canary` in a disposable OU and establish its ACL independently using an administrator. Run the following under the low-privilege test identity being assessed, using the approved lab DC. The only intended mutation is the canary's Description field. A successful write proves that one property write under that identity, not domain compromise.

```powershell
$labServer = 'dc01.example.test'
$labCanary = 'lab.canary'
$before = Get-ADUser -Identity $labCanary -Server $labServer -Properties Description
if ($before.SamAccountName -ne $labCanary) { throw 'Unexpected fixture identity' }
$changed = $false
try {
    Set-ADUser -Identity $before.DistinguishedName -Server $labServer -Description 'WB_ACL_CANARY_001'
    $changed = $true
    Get-ADUser -Identity $before.DistinguishedName -Server $labServer -Properties Description |
        Select-Object DistinguishedName,Description
} finally {
    if ($changed) {
        if ($null -eq $before.Description) {
            Set-ADUser -Identity $before.DistinguishedName -Server $labServer -Clear Description
        } else {
            Set-ADUser -Identity $before.DistinguishedName -Server $labServer -Description $before.Description
        }
    }
}
```

Retain the administrator's fixture ACL export, effective test identity/group memberships, command result, property readback, audit event, and rollback readback. If replication delay is relevant, read/write the same DC and then measure replication separately. If the canary lacks equivalent ACL inheritance to the modeled target, do not generalize the result.

For the AD-10 reversible group-membership test, the lab owner can use:

```powershell
# Precondition: synthetic group/user exist and lab.user is NOT already a member.
Get-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Server 'dc01.example.test'
Add-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Members 'lab.user' -Server 'dc01.example.test' -WhatIf
# Only after the owner-reviewed preconditions are satisfied:
Add-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Members 'lab.user' -Server 'dc01.example.test'
Get-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Server 'dc01.example.test'
Remove-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Members 'lab.user' -Server 'dc01.example.test' -Confirm:$false
Get-ADGroupMember -Identity 'LAB-CANARY-GROUP' -Server 'dc01.example.test'
```

Use no privileged production group. Preserve preexisting membership: do not use the sequence if the test user was already present. Coordinate the audit observation window and revert even if the detection test fails. Discovery/attribute queries for delegation, Kerberos configuration, AD CS, trusts, and GPOs are in AD.md. An exploitation claim for those areas requires all actual prerequisites, which a directory flag alone cannot prove.

## Wi-Fi: managed EAP trust test matrix

With VMs only, use this as a configuration-review exercise. Real association and RF behavior require an owned adapter/AP and isolation. A Linux `wpa_supplicant` test-profile shape for a dedicated enterprise lab is:

```text
network={
    ssid="WB-LAB-EAP"
    key_mgmt=WPA-EAP
    eap=PEAP
    identity="lab-user"
    anonymous_identity="anonymous@example.test"
    password="REPLACE_WITH_SYNTHETIC_LAB_PASSWORD"
    ca_cert="/etc/wb-lab/lab-ca.pem"
    domain_suffix_match="radius.example.test"
    phase2="auth=MSCHAPV2"
    ieee80211w=2
}
```

The example is one explicit PEAP fixture, not a recommendation to choose it over certificate-based EAP for a real organization. Keep profile permissions restrictive and use only fabricated credentials. Do not disable CA/name validation to make a failed test pass. Check installed-client support before adopting the options.

Run four lab-server certificate cases while preserving the client profile: valid trusted certificate with matching name; trusted certificate with wrong name; untrusted issuer; expired certificate. The intended result is acceptance only for the first case, with client/RADIUS evidence identifying rejection at the certificate-validation stage for the others. A credential error is not a valid negative control for server trust.

For passive inventory, export only owned-lab fields:

```sh
tshark -r lab.pcapng -Y 'wlan.fc.type_subtype == 8' -T fields -e wlan.bssid -e wlan.ssid
tshark -r lab.pcapng -Y 'wlan.bssid == 02:00:00:00:00:01 && wlan.fc.type_subtype == 8' -V
```

Inspect RSN/PMF details in verbose output instead of assuming a dissector field name is stable across versions. Store adapter, driver, channel, band, timing, and drop counts. No observed frame is not proof of no transmitted frame. Do not use deauthentication or an impersonated production SSID to obtain a test handshake.

## Endpoints: benign privilege-boundary canary

In a disposable Windows VM, have an administrator provision a **synthetic** elevated task whose action is `C:\Lab\Canary\action.cmd`. Record its task principal and the intended ACLs. Under the low-privilege identity, inspect:

```powershell
Get-ScheduledTask -TaskName 'WB-LAB-CANARY' | Select-Object TaskName,TaskPath,State
icacls 'C:\Lab\Canary\action.cmd'
icacls 'C:\Lab\Canary'
```

For a deliberately vulnerable fixture, the planted action can contain only:

```bat
@echo off
whoami > C:\Lab\CanaryOutput\identity.txt
echo WB_TASK_CANARY_001 >> C:\Lab\CanaryOutput\identity.txt
```

The administrator, under the approved change record, triggers the canary task once and collects the output plus process/task events. The low-privilege identity should not be able to change this action if it runs with higher privilege. If an equivalent synthetic writable task action is demonstrated, preserve the effective write result and observed elevated identity. Do not modify any existing system task or infer exploitability only from the presence of an unquoted path.

Restore the task action and ACLs from the fixture baseline, delete the synthetic task through the lab-owner workflow, and verify restoration. Repeat with fixed ACLs: the low-privilege write should fail while the approved task still runs. Linux equivalents require a dedicated lab unit/action and a similarly bounded output file; do not alter a real service or sudoers policy.

For read-only host collection, run the supplied snapshot script with the exact approved machine name:

```powershell
.\endpoint_snapshot.ps1 -ExpectedComputerName 'LAB-PC01' -OutputPath '.\snapshot.json'
```

The script refuses a host-name mismatch and existing output file. Inspect collection errors before interpreting results; no secrets or process memory are intentionally collected. Host/service metadata can still be sensitive and belongs in restricted engagement evidence.

## Primary syntax references

- [Microsoft Set-ADUser](https://learn.microsoft.com/powershell/module/activedirectory/set-aduser)
- [Microsoft Add-ADGroupMember](https://learn.microsoft.com/powershell/module/activedirectory/add-adgroupmember)
- [Microsoft Remove-ADGroupMember](https://learn.microsoft.com/powershell/module/activedirectory/remove-adgroupmember)
- [wpa_supplicant configuration source in Android's maintained source tree](https://android.googlesource.com/platform/external/wpa_supplicant_8/+/master/wpa_supplicant/wpa_supplicant.conf)
- [TShark manual](https://www.wireshark.org/docs/man-pages/tshark.html)
