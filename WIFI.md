# WIFI assessment procedures

Version 0.1.0. Original procedures with primary references. Commands are reference probes; the workbench never executes them.

## WIFI-01: BSSID inventory and scope attribution

Separate authorized radios from neighboring or unowned networks before any active test.

### Interaction

passive observation

### Prerequisites

- Owned AP list with BSSID, channel, band, SSID, and location.
- Legal capture authority and an adapter that supports the required band.

### Procedure

- Collect a bounded passive inventory in the approved area.
- Match BSSIDs to controller records; account for multi-BSSID and roaming.
- Mark unmatched radios unknown and refer them to the owner; do not connect to them.

### Lab probes / inspection commands

```text
tshark -r lab.pcapng -Y "wlan.fc.type_subtype == 8" -T fields -e wlan.bssid -e wlan.ssid
```

```text
Offline BSSID canary: 02:00:00:00:00:01
```

### Expected secure behavior

Every tested radio maps to written scope; neighbor observations remain out of scope.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

SSID names are not identity. MAC randomization and multiple radios can confound inventory.

### Remediation

Maintain controller-backed inventory and scoped capture handling; investigate unknown transmitters through ownership records.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Kismet passive capture
- Wireshark/TShark
- Controller export

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html
- https://www.kismetwireless.net/docs/

## WIFI-02: Advertised authentication and cipher posture

Compare advertised RSN capabilities to controller policy and actual authorized client negotiation.

### Interaction

passive plus owned-client association

### Prerequisites

- Owned beacon capture and sanitized WLAN configuration.
- At least one approved test client per relevant device class.

### Procedure

- Inspect beacon/probe-response RSN information elements.
- Compare allowed AKMs and ciphers to the configured WLAN.
- Observe one approved association and record the actual negotiated mode.

### Lab probes / inspection commands

```text
tshark -r lab.pcapng -Y "wlan.bssid == 02:00:00:00:00:01 && wlan.fc.type_subtype == 8" -V
```

### Expected secure behavior

Advertisement, configuration, and negotiated protection all meet the owner-approved policy.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A strong advertised capability does not mean every client uses it. Transition modes and legacy SSIDs need separate analysis.

### Remediation

Remove unnecessary legacy modes and isolate unavoidable exceptions.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Wireshark
- Controller configuration
- Test client connection details

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html
- https://aircrack-ng.org/doku.php?id=airodump-ng

## WIFI-03: Protected management frame configuration

Check management-frame protection support and enforcement without disconnecting clients.

### Interaction

configuration review; RF-isolated compatibility test

### Prerequisites

- Owned AP and client; vendor configuration export and beacon/association capture.
- No deauthentication injection on shared spectrum.

### Procedure

- Inspect PMF capability/requirement in RSN details.
- Compare AP configuration and test-client negotiated state.
- In an RF-isolated lab, associate a deliberately incompatible client and record whether policy rejects it.

### Lab probes / inspection commands

```text
tshark -r lab.pcapng -Y "wlan.bssid == 02:00:00:00:00:01 && wlan.fc.type_subtype == 8" -V
```

```text
Configuration review fields: PMF capable, PMF required, client negotiated PMF.
```

### Expected secure behavior

Required PMF is consistently enforced for the intended WLAN/client population.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

PMF protects specified robust management frames, not every possible disruption or all RF interference.

### Remediation

Align PMF enforcement with the approved client fleet and separate unsupported devices.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Wireshark
- AP controller
- Owned client diagnostics

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html

## WIFI-04: Enterprise EAP server trust

Verify that managed clients validate the intended authentication server and trust chain.

### Interaction

RF-isolated authentication validation

### Prerequisites

- RF-isolated owned enterprise WLAN, test RADIUS service, and synthetic account.
- No production SSID impersonation or collection of real credentials.

### Procedure

- Export the client EAP profile and intended server identity.
- Connect normally to the legitimate lab server.
- Change only the lab server certificate to an untrusted or wrong-name certificate.
- Verify rejection before authentication data is released; inspect client/RADIUS logs.

### Lab probes / inspection commands

```text
Test matrix: valid chain + correct name; valid chain + wrong name; untrusted chain; expired certificate.
```

### Expected secure behavior

The client accepts only the approved identity and trust policy; invalid identity is rejected without a user bypass prompt.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A failed login can result from incorrect credentials rather than certificate validation. Observe the reason and protocol stage.

### Remediation

Deploy explicit EAP trust/name configuration through managed profiles and remove user-overridable trust prompts where supported.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Managed Wi-Fi profile export
- RADIUS logs
- Wireshark

### Primary references

- https://www.kismetwireless.net/docs/
- https://www.wireshark.org/docs/man-pages/tshark.html

## WIFI-05: Guest and client isolation

Check segmentation with owned canary services rather than broad internal discovery.

### Interaction

bounded owned-service connection

### Prerequisites

- Two test clients and a wired canary server in each explicitly approved segment.
- Document a reachability matrix of source, destination, protocol, and expected result.

### Procedure

- From each approved source test a single fixed canary endpoint.
- Compare guest-to-corporate, guest-to-guest, and client-to-management paths.
- Repeat IPv4 and IPv6 where enabled.
- Inspect firewall/controller logs.

### Lab probes / inspection commands

```text
curl --connect-timeout 2 --max-time 4 http://192.0.2.20:8080/wb-canary
```

```text
Repeat only for listed source/destination pairs from the approved matrix.
```

### Expected secure behavior

Only the explicitly approved paths are reachable across both address families.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A silent host, host firewall, or service outage can look like network isolation. Verify a permitted control path simultaneously.

### Remediation

Enforce segmentation at the correct network boundary, include IPv6, and validate management-plane rules.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Owned canary services
- Firewall logs
- Nmap limited to approved hosts/ports

### Primary references

- https://nmap.org/book/man.html

## WIFI-06: Management-plane exposure

Verify AP/controller administrative access from only the intended management network.

### Interaction

bounded management connection

### Prerequisites

- Owner-listed management addresses and services.
- Known test account; no credential guessing.

### Procedure

- Test the listed management endpoint from management, corporate, and guest sources.
- Record TLS identity and login boundary.
- Check controller ACLs and management VLAN assignments.

### Lab probes / inspection commands

```text
curl --connect-timeout 2 --max-time 4 -I https://controller.example.test/
```

### Expected secure behavior

Management is restricted to approved origins and protected by the required authentication and transport.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A visible login page can differ from administrative access; distinguish exposure from successful authentication.

### Remediation

Restrict administrative interfaces and enforce least privilege, MFA where supported, and validated TLS.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Browser
- curl
- Controller audit logs

### Primary references

- https://nmap.org/book/man.html

## WIFI-07: WPS and onboarding policy

Review whether unintended enrollment mechanisms bypass the approved onboarding process.

### Interaction

configuration and controlled enrollment

### Prerequisites

- Owned AP configuration and onboarding workflow.
- No PIN brute force or unsolicited enrollment attempts.

### Procedure

- Review WPS/alternate enrollment settings and physical access requirements.
- In a disconnected lab, perform one approved enrollment using a test device.
- Verify audit visibility and the resulting network role.

### Lab probes / inspection commands

```text
Configuration canary: WPS disabled on enterprise SSID; test-device enrollment confined to LAB-ONBOARD.
```

### Expected secure behavior

Only approved enrollment paths exist and newly enrolled devices receive the intended role.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

An advertised capability may be administratively disabled; configuration and one controlled enrollment are stronger evidence.

### Remediation

Disable unused enrollment methods and constrain onboarding roles and credentials.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- AP controller
- Owned test client
- Passive capture

### Primary references

- https://aircrack-ng.org/doku.php?id=airodump-ng

## WIFI-08: Roaming and policy consistency

Check that roaming cannot move a test client into a weaker role or authentication policy.

### Interaction

owned-client mobility test

### Prerequisites

- Two owned APs and a test client; identical intended WLAN policy.
- Coordinate a small test window to avoid disrupting users.

### Procedure

- Record policy, VLAN/role, and negotiated security on AP A.
- Move the test client to AP B using normal roaming.
- Compare session/role continuity and enforcement.
- Repeat once per relevant band.

### Lab probes / inspection commands

```text
Record before/after: BSSID, AP policy, client role, VLAN, authentication mode, UTC time.
```

### Expected secure behavior

Roaming preserves the intended identity, segmentation, and security policy.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A reconnect is not always a roam; cached credentials and controller policy propagation can alter observations.

### Remediation

Align AP group policy, firmware, and role assignment; validate reauthentication boundaries.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Client diagnostics
- Controller logs
- Wireshark

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html

## WIFI-09: Passive identity and privacy leakage

Assess whether an approved capture exposes more identifying data than the assessment needs.

### Interaction

passive privacy review

### Prerequisites

- Synthetic client identifiers and a short, purpose-limited capture.
- Evidence retention and redaction rules; capture metadata only when sufficient.

### Procedure

- Review beacon, probe, and EAP identity fields for the synthetic client.
- Check whether outer identity differs from the real account identifier.
- Measure minimum fields required for the assessment and redact the rest.

### Lab probes / inspection commands

```text
tshark -r lab.pcapng -Y "eap || wlan.fc.type_subtype == 4" -V
```

### Expected secure behavior

Identity exposure matches the protocol design and documented privacy policy; retained evidence is minimized.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

An outer anonymous identity is not a guarantee that all exchanges are anonymous; capture visibility depends on protocol stage.

### Remediation

Use privacy-preserving managed profiles where appropriate and minimize retained capture content.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Wireshark
- EAP client profile
- RADIUS logs

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html

## WIFI-10: Wireless evidence reproducibility

Record RF conditions and sensor constraints so negative observations are not overstated.

### Interaction

passive measurement quality

### Prerequisites

- Owned capture sensor with documented adapter/driver/firmware.
- Known channel, test interval, and AP/client fixture.

### Procedure

- Record channel/band, sensor position category, driver, capture drops, and filter.
- Capture a known beacon/control association.
- Compare observed fixture packets to expected events.
- Mark unsupported bands and missed channels as not tested.

### Lab probes / inspection commands

```text
tshark -r lab.pcapng -c 20 -V
```

```text
Evidence manifest: sensor_id, adapter, driver, channel, band, start_utc, end_utc, packet_drop_count.
```

### Expected secure behavior

Coverage claims are bounded by recorded sensor capability and successful positive controls.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Channel hopping can miss short events; no observed frame is not proof that no frame was transmitted.

### Remediation

Use fixed-channel captures for timed tests and retain positive controls with capture metadata.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Kismet
- TShark
- evidence-seal

### Primary references

- https://www.wireshark.org/docs/man-pages/tshark.html
- https://aircrack-ng.org/doku.php?id=airodump-ng

