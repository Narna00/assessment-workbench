# Platform blueprint and operating model

## Purpose and boundary

Turn an assessment request into reviewed claims supported by reproducible observations. Coverage is expressed as tested, blocked, inconclusive, or not tested; a test not performed is never silently treated as a pass. The workbench supports a human operator and reviewer. It does not turn broad scope into permission to execute arbitrary tools.

The current release is a working offline reference and planning platform. Future connectors, multi-user access, cryptographic signatures, and hosted storage are explicitly unimplemented. The HTML portal works without a backend; its catalog values are rendered through textContent and inert embedded JSON.

## Architecture

```text
Owner-approved authorization + versioned catalog
                    |
             immutable plan
                    |
   human-controlled tools / local lab fixtures
                    |
     raw artifacts + observations + reviewer
                    |
         mechanical evidence review
                    |
        scoped findings and retest package
```

The catalog is the source of truth for procedures. The generated manuals and portal are views of that catalog. A plan fixes case IDs, domain, targets, catalog hash, and authorization hash. A results file retains those fields and adds status, observations, reviewer identity, and artifact path/hash pairs.

## Engagement phases

1. **Define the question.** State business assets, expected trust boundaries, assessment vantage points, excluded systems, and what would count as a finding. Web object ownership, AD delegation, Wi-Fi segmentation, and endpoint service ACLs need different evidence.
2. **Obtain written scope.** Record exact hosts/URLs/BSSIDs, identities, dates, allowed cases, prohibited actions, owner contact, incident stop conditions, and recovery responsibilities. A JSON approver field is not a signature.
3. **Map prerequisites.** Confirm test credentials and fixture ownership. Export relevant configuration. Establish time synchronization, positive controls, telemetry, and evidence storage. Do not collect real secrets when a canary or metadata check answers the question.
4. **Plan cases.** Choose applicable case IDs, document exclusions, and retain immutable authorization/catalog baselines. Cases that need hardware, permissions, or unavailable telemetry remain blocked.
5. **Execute one controlled hypothesis.** Keep baseline and probe differing in one variable when possible. Record target, principal, object, vantage point, request/command, tool version, time, and observed effect. Automated scanner output is a lead until validated.
6. **Review causality and impact.** Rule out cache effects, account-role differences, network outages, stale exports, parser differences, and measurement gaps. Distinguish vulnerable configuration from demonstrated action and business impact.
7. **Retest the same claim.** Reuse the same fixture, identity, object, and route; note changed dependencies. A disappearing service or missing log is not automatically remediation.
8. **Deliver and close.** Give owners a prioritized finding with bounded impact, evidence references, remediation, and a reproducible retest. Restore lab changes, revoke test credentials, and apply evidence retention policy.

## Result record

Edit only the result fields of each planned case:

```json
{
  "case_id": "WEB-01",
  "status": "finding_confirmed",
  "observations": "B retrieved A's synthetic object; B-own-object control and backend ownership records agree.",
  "reviewed_by": "named reviewer",
  "artifacts": [{"path": "web01/control-and-probe.txt", "sha256": "64 lowercase hexadecimal characters"}]
}
```

Allowed statuses are `not_tested`, `blocked`, `inconclusive`, `secure_observed`, and `finding_confirmed`. Completed conclusions require observations, reviewer, and at least one artifact. The reviewer must assess whether those artifacts are sufficient; the CLI checks availability and integrity only. A result can be mechanically complete while containing confirmed findings: completeness is not security.

## Deployment blueprint

For a local virtual lab, use separate management and experiment networks, no bridge to third-party networks, disposable snapshots, synthetic identities, and a clock reference. The lab web fixture needs only Python. An AD lab requires legitimately licensed evaluation images, a DC and member endpoint, and a separate low-privilege test account. Wi-Fi negotiation/RF claims cannot be validated by a VM-only setup without appropriate owned radio hardware; offline capture fixtures cover parser and inventory work only.

If a future hosted edition is built, use tenant isolation, project-level access controls, encrypted evidence storage, integrity-protected audit records, signed catalog releases, an approved worker sandbox, explicit destination gates, rate/concurrency budgets, and no secrets in generated reports. These are design requirements, not implemented capabilities of this release.

## Integrating the six existing tools

| Component | Integration point | Important boundary |
|---|---|---|
| [engagement-scope-gate](https://github.com/Narna00/engagement-scope-gate) | Validate a proposed network target inventory before manual tool use | Not an egress enforcement mechanism |
| [evidence-seal](https://github.com/Narna00/evidence-seal) | Seal copied artifacts before handover | Baseline must remain trusted |
| [audit-evidence-engine](https://github.com/Narna00/audit-evidence-engine) | Map technical evidence into an organization-owned control register | Mechanical readiness is not ISO compliance |
| [nmap-exposure-diff](https://github.com/Narna00/nmap-exposure-diff) | Compare approved scan observations at retest | Absence is not proof of remediation |
| [iam-path-review](https://github.com/Narna00/iam-path-review) | Review normalized effective entitlements | Not a cloud policy simulator |
| [audit-sample-ledger](https://github.com/Narna00/audit-sample-ledger) | Choose controlled test samples from a frozen population | Sample sufficiency remains an auditor judgment |

## Finding template

Title; affected asset and exact scope; tested principal and preconditions; violated requirement; baseline/control/probe; raw evidence references; demonstrated result; bounded business impact; untested implications; severity rationale; remediation; retest procedure; owner; status; residual uncertainty. Avoid CVSS scores computed from unverified assumptions. Link to the relevant standard/control only after confirming applicability with the owner.

## Reference foundation

The engagement lifecycle is informed by [NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final), a foundational 2008 guide rather than a modern exhaustive test catalog. Web categories reference the versioned [OWASP WSTG v4.2](https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/). Individual cards use original procedures and link to primary tool documentation. Neither reference implies this implementation has been certified by those organizations.
