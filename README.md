# Assessment Workbench

An offline methodology platform for authorized penetration tests of web applications, Active Directory, Wi-Fi, and endpoints. It combines 42 structured test cards, a searchable browser portal, engagement planning, evidence checks, scripts, and a synthetic loopback web lab.

## Start here

Open [portal.html](portal.html) locally for search and filtering. GitHub displays HTML source; download the repository to use the portal. Read [BLUEPRINT.md](BLUEPRINT.md) for the engagement workflow and architecture, [TOOLS.md](TOOLS.md) for primary tool references, and the domain manuals:

| Domain | Cases | Manual |
|---|---:|---|
| Web applications | 12 | [WEB.md](WEB.md) |
| Active Directory | 10 | [AD.md](AD.md) |
| Wi-Fi | 10 | [WIFI.md](WIFI.md) |
| Windows/Linux endpoints | 10 | [ENDPOINT.md](ENDPOINT.md) |

Each card defines scope prerequisites, a procedure, probes or inspection commands, expected secure behavior, evidence, false positives, remediation, and retest criteria. A configuration command is labeled as inspection rather than presented as an exploit. Some commands require Windows modules, administrative read privileges, specific hardware, or a separately built lab. They have not all been executed against those external products in this repository.

## CLI

Python 3.12+, standard library only. Run from the repository directory:

```sh
python workbench.py validate
python workbench.py list --domain web
python workbench.py show WEB-01
python workbench.py plan authorization.example.json --domain web --output plan.json
python workbench.py review plan.json results.json --evidence-root ./evidence
python workbench.py portal --output custom-portal.html
python -m unittest discover -v
```

The example authorization is a schema example, not permission to test anything. Replace its metadata, targets, dates, and case permissions with an actual lab-owner-approved record. Plans contain hashes of the authorization and catalog. Copy a plan to `results.json`, record results and evidence, and keep the original plan unchanged.

`review` exits 1 for incomplete/evidence-deficient work and 0 for mechanically complete records. It does not decide whether a vulnerability exists, establish legal authorization, or prove absence of vulnerabilities. Malformed input exits 2. Plan and portal outputs are created exclusively and never overwrite existing files.

## Payload and lab scope

Web payloads use synthetic IDs, arithmetic, DOM markers, and owned canaries. AD cards include detailed read-only queries and controlled validation specifications. Wireless cards prioritize owned captures, explicit BSSIDs, test-client negotiation, and RF-isolated experiments. Endpoint cards inspect actual privilege/configuration boundaries and use benign fixture actions.

The project does not install tools, execute catalog commands, obtain credentials, perform password guessing, start radio disruption, or run live assessment activity. No missing command should be interpreted as a successful test. This is a methodology and evidence workbench, not an autonomous scanner.

## Synthetic web lab

```sh
python lab_web.py --port 8765
```

In another terminal, use the WEB-01, WEB-02, and WEB-03 probes. Tokens `lab-a` and `lab-b` identify fabricated users. `/orders`, `/search`, and `/echo` intentionally demonstrate object authorization, query interpretation, and reflected markup defects. The server binds only to `127.0.0.1`, enforces the exact Host header, retains no database between requests, and makes no external calls. Stop it with Ctrl+C; rerun with `--secure` for the paired fixed behavior. Do not expose this deliberately flawed fixture through a proxy, tunnel, or public listener.

## Helper scripts

- `ldap_escape.py`: escape a literal LDAP assertion value; this is not a DN escaper or an LDAP client.
- `wifi_inventory.py`: consume CSV columns `bssid,ssid,channel` and a JSON owned-BSSID array; unknown ownership is not a rogue-AP verdict.
- `endpoint_snapshot.ps1`: read-only Windows inventory, explicit expected host name, exclusive output creation, and recorded collection errors. Run only after approving the data fields. Do not publish host snapshots.

The portal contains reference material only and stores no engagement data. Evidence review assumes immutable files during hashing; it is not a defense against a privileged adversary racing filesystem changes. Source-register hashes provide integrity comparison only while the originals remain trusted.

Version 0.1.0. Original methodology/code is MIT-licensed. Linked tools, standards, and upstream documentation retain their own licenses.
