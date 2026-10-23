# Assessment Workbench

[Open the public platform](https://narna00.github.io/pentesting.html)

Assessment Workbench is a public reference for penetration testing of web applications, Active Directory, wireless networks and Windows/Linux endpoints. It combines a command and payload library with complete test procedures, an engagement blueprint and downloadable laboratory resources.

## Content

| Domain | Reference entries | Full procedures |
|---|---:|---:|
| Web applications | 33 | 12 |
| Active Directory | 16 | 10 |
| Wireless networks | 14 | 10 |
| Endpoints | 20 | 10 |

Each reference entry records the input or command, prerequisites, intended observation, common misreadings, cleanup and an upstream reference. Procedures cover planning, evidence, remediation and retesting. Examples use synthetic identities, reserved addresses and controlled fixtures. Reference commands have not all been executed against the external products they describe.

The website supports text search, domain/topic filters, direct entry links, copy controls and a saved checklist. Saved selections contain reference IDs and stay in the browser. The Markdown export includes the selected examples and their conditions. The website does not execute assessment commands or collect engagement data.

## Source and local use

`website.html` is the self-contained page published on the Narna portfolio. It embeds its reference data, styles and downloads. Open it locally or serve it through a static HTTP server. `reference-library.json` contains the 83 original reference entries; `catalog.json` contains the 42 procedures.

`website-source.zip` contains the modular website files and build scripts. Extract the archive and run `python build.py` to regenerate `website.html` using Python 3.12 or later. The builder uses only the standard library. The public portfolio repository contains the deployed page and links from its homepage.

## Assessment workflow

Read [BLUEPRINT.md](BLUEPRINT.md), then the relevant [web](WEB.md), [directory](AD.md), [wireless](WIFI.md) or [endpoint](ENDPOINT.md) manual. [LAB_PAYLOADS.md](LAB_PAYLOADS.md) provides controlled recipes. [TOOLS.md](TOOLS.md) records upstream resources; the website also includes a tool directory.

The companion CLI uses Python 3.12 or later and the standard library:

```sh
python workbench.py validate
python workbench.py list --domain web
python workbench.py show WEB-01
python workbench.py plan authorization.example.json --domain web --output plan.json
python workbench.py review plan.json results.json --evidence-root ./evidence
python -m unittest discover -v
```

`authorization.example.json` illustrates the input schema. Replace it with an approved scope record before planning an assessment. Review checks record completeness and evidence paths; it does not decide whether a vulnerability exists. Exit codes are 0 for mechanically complete records, 1 for incomplete records and 2 for invalid input. Outputs are created exclusively.

## Included lab and helpers

`lab_web.py` serves deliberately vulnerable synthetic authorization, SQL and markup examples on loopback. Run `python lab_web.py --port 8765`, then repeat with `--secure` for the paired control. Keep this fixture isolated; it is not part of the public hosted application.

`ldap_escape.py` escapes literal LDAP assertion values. `wifi_inventory.py` compares normalized CSV observations with exact owned BSSIDs. `endpoint_snapshot.ps1` collects a bounded Windows inventory with an expected hostname, exclusive output creation and explicit collection errors. Review each script’s parameters and data fields before use.

## Contributions and verification

Corrections should identify the entry ID, tool version, required context, reproduced behavior and a primary reference. Keep commands scoped and pair a proposed finding with a working control. Do not submit credentials or customer evidence.

The interface, links, filters, saved selection and downloads are checked separately from the technical behavior of external commands. Passing interface checks is not evidence that every procedure has been validated on a real deployment. MIT applies to the original code and notes; external projects retain their own licensing and authorship. The separate research repository is not a dependency of this platform.
