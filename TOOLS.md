# Tool and resource register

Checked against primary project documentation on 2026-10-21. Pin an actual release and record its checksum/version when preparing a lab; no third-party binary is bundled or installed. Capabilities and licensing differ by edition. Review each tool's modules before use rather than running its broadest default mode.

| Domain | Tool/resource | Use here | Boundary |
|---|---|---|---|
| Web | [OWASP WSTG v4.2](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/) | Versioned methodology reference | Adapt tests to application invariants |
| Web | [PortSwigger Academy](https://portswigger.net/web-security) | Dedicated practice labs and vulnerability explanations | Academy labs are separate from client scope |
| Web | [Burp desktop documentation](https://portswigger.net/burp/documentation/desktop) | Manual proxy, request replay, DOM analysis | Automated capabilities depend on edition |
| Web | [ZAP documentation](https://www.zaproxy.org/docs/) | Manual inspection and explicitly scoped automation | Active scans require a separate activity plan |
| Network | [Nmap reference](https://nmap.org/book/man.html) | Explicit host/port/service observations | No `-A`, broad scripts, or full-network scan is implied |
| AD | [RSAT ActiveDirectory cmdlets](https://learn.microsoft.com/powershell/module/activedirectory/) | Authenticated directory configuration review | Effective permissions and domain coverage matter |
| AD | [BloodHound CE](https://bloodhound.specterops.io/) | Relationship/path investigation | A graph edge is not proof that every transition succeeds |
| AD | [SharpHound](https://github.com/SpecterOps/SharpHound) | Approved relationship collection | Collection methods can contact hosts; review methods and scope first |
| AD CS | [Certipy](https://github.com/ly4k/Certipy) | Template/CA discovery in an approved lab | Discovery and abuse modules have different consequences; no abuse automation is bundled |
| Wi-Fi | [Kismet](https://www.kismetwireless.net/docs/) | Passive owned-environment inventory | RF observation can include neighbors; minimize retention |
| Wi-Fi | [Aircrack-ng/airodump-ng](https://aircrack-ng.org/doku.php?id=airodump-ng) | Controlled passive capture context | The workbench supplies no deauthentication or credential-cracking automation |
| Evidence | [Wireshark/TShark](https://www.wireshark.org/docs/man-pages/tshark.html) | Owned capture analysis | Display filters and capture filters use different syntax; verify fields against the installed version |
| Endpoint | [osquery](https://osquery.readthedocs.io/en/stable/) | Structured host inventory | Tables/events depend on OS and configured collectors |
| Endpoint | [Velociraptor](https://docs.velociraptor.app/) | Owner-approved artifact collection | Artifact queries can collect sensitive content; inspect before running |
| Purple team | [MITRE ATT&CK emulation resources](https://attack.mitre.org/resources/get-started/adversary-emulation-and-red-teaming/) | Detection and validation vocabulary | Technique mapping is not proof of exploitability or complete coverage |

## Selecting a tool

Choose the smallest tool action that can falsify the case hypothesis. Prefer an authenticated configuration export where it answers the question. Use a controlled action when configuration alone cannot establish enforcement. Retain both the original export and the exact transformation used to normalize it. Deduplicate re-exports by source lineage; three dashboards backed by one collector are not three independent observations.

Avoid importing large public payload collections as an undifferentiated test plan. Choose payloads by input context, application semantics, preconditions, and the result needed to distinguish secure from insecure behavior. Store external resources as links and pin the specific upstream version in an engagement record rather than silently vendoring material with another license.
