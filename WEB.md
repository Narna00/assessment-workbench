# WEB assessment procedures

Version 0.1.0. Original procedures with primary references. Commands are reference probes; the workbench never executes them.

## WEB-01: Object-level and tenant authorization

Establish whether identity and tenant boundaries are enforced per object, not just in the UI.

### Interaction

controlled active validation

### Prerequisites

- Two seeded users A/B with separate objects; two test tenants; no customer records.
- Map the owner and tenant of every fixture before testing.

### Procedure

- Capture a successful request for A object 1001.
- With B credentials, replay the same method and object ID; change only the token.
- Repeat on export, nested, bulk, and alternate-version endpoints.
- Check server-side owner/tenant audit records.

### Lab probes / inspection commands

```text
GET /orders?id=1001 HTTP/1.1
Host: 127.0.0.1:8765
Authorization: Bearer lab-b
```

```text
curl --max-time 5 -H "Authorization: Bearer lab-b" "http://127.0.0.1:8765/orders?id=1001"
```

### Expected secure behavior

The foreign object is withheld; own-object access still works. Status code alone is insufficient: inspect the body and backend action.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A shared object or administrative test role can legitimately cross ownership. A 404 is not proof of enforcement if an asynchronous job still runs.

### Remediation

Bind authorization to subject, tenant, action, and object on every backend path; add cross-tenant regression tests.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- ZAP manual request editor
- Included loopback lab

### Primary references

- https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/
- https://portswigger.net/web-security

## WEB-02: SQL injection through boolean differentials

Detect data-query interpretation of untrusted input with a minimal non-destructive fixture.

### Interaction

controlled active validation

### Prerequisites

- Disposable database with synthetic products only.
- A known query route and one baseline result; disable caches for comparison.

### Procedure

- Request a normal product ID.
- Compare true/false boolean predicates encoded in the same input.
- Record returned fixture IDs and query logs.
- Stop after proof of altered query semantics; do not enumerate real data.

### Lab probes / inspection commands

```text
Baseline: /search?id=1
```

```text
True: /search?id=1%20AND%201%3D1
```

```text
False: /search?id=1%20AND%201%3D2
```

### Expected secure behavior

Inputs remain typed data. Invalid numeric syntax is rejected or safely parameterized; the true/false pair cannot alter query logic.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Different errors, cache keys, validation rules, or nondeterministic data can mimic a differential. Use control requests and database traces.

### Remediation

Use parameterized queries and typed validation. Query builders must not interpolate raw fragments.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- SQLite fixture in lab_web.py
- sqlmap only in separately approved disposable labs

### Primary references

- https://portswigger.net/web-security
- https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/

## WEB-03: Reflected and DOM script execution

Determine whether attacker-controlled markup reaches an executable browser context.

### Interaction

controlled active validation

### Prerequisites

- Disposable browser profile and synthetic account.
- Use a lab-only DOM marker; no credential collection or external callback.

### Procedure

- Insert a plain canary and locate its output context.
- Submit the marker payload in that context.
- Inspect DOM, console, response encoding, and CSP.
- Repeat through client-side routing and stored-field display using synthetic records.

### Lab probes / inspection commands

```text
Plain marker: WB_CANARY_01
```

```text
<svg onload="document.documentElement.dataset.wbprobe='executed'"></svg>
```

```text
Inspect: document.documentElement.dataset.wbprobe
```

### Expected secure behavior

Untrusted text is encoded for its precise context; the dataset marker never changes due to injected input.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A reflected string is not script execution. A blocked payload under CSP can leave a real injection defect; distinguish the sink defect from demonstrated impact.

### Remediation

Use contextual encoding and safe DOM APIs; sanitize permitted HTML with a maintained library; use CSP as an additional layer.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp DOM Invader
- Browser developer tools
- ZAP

### Primary references

- https://portswigger.net/web-security
- https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/

## WEB-04: Server-side template expression evaluation

Check whether user text is compiled as template code.

### Interaction

controlled active validation

### Prerequisites

- Disposable template fixture; approved message field.
- Arithmetic-only expressions; no object traversal or operating-system access.

### Procedure

- Submit a literal marker, then arithmetic expressions.
- Compare returned bytes to literal and calculated values.
- Inspect server template logs to distinguish rendering from client-side evaluation.

### Lab probes / inspection commands

```text
WB_{{7*7}}_END
```

```text
WB_${7*7}_END
```

```text
WB_<%= 7*7 %>_END
```

### Expected secure behavior

The expressions are rendered as data, not evaluated as template programs.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

49 can appear coincidentally. Engine syntax varies; three negative probes do not exhaust template engines.

### Remediation

Keep template source static, bind data through variables, and remove dangerous interpolation paths.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Application template logs

### Primary references

- https://portswigger.net/web-security

## WEB-05: Command-injection canary

Establish whether a field enters a shell rather than an argument-safe process API.

### Interaction

controlled active validation

### Prerequisites

- Dedicated local container with a harmless text-processing endpoint.
- Approve one marker-print action; never use an external callback or shell session.

### Procedure

- Record a baseline argument.
- Try a shell delimiter followed by a marker print.
- Correlate output with process creation logs.
- Stop when interpretation is demonstrated.

### Lab probes / inspection commands

```text
example; printf WB_CMD_01
```

```text
example && printf WB_CMD_02
```

```text
example & echo WB_CMD_03
```

### Expected secure behavior

Input stays one argument or is rejected; no second command is invoked.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A reflected marker is not command execution. Shell syntax depends on OS; inspect process telemetry.

### Remediation

Avoid the shell; invoke a fixed executable with an argument list and an allowlist of expected values.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- osquery process events where configured
- Server logs

### Primary references

- https://portswigger.net/web-security

## WEB-06: Path traversal against a planted sentinel

Check file-path confinement without reading real operating-system or application secrets.

### Interaction

controlled active validation

### Prerequisites

- Create public/readme.txt and a synthetic canary outside the intended public directory.
- Use only files deliberately planted for the test.

### Procedure

- Fetch the allowed readme.
- Try relative, encoded, and absolute references to the planted canary.
- Record canonical path resolution in server logs.
- Repeat with mixed separators only if the target OS supports them.

### Lab probes / inspection commands

```text
../lab-canary.txt
```

```text
%2e%2e%2flab-canary.txt
```

```text
..%2flab-canary.txt
```

### Expected secure behavior

The resolved file remains within the approved root; the sentinel is inaccessible through the download route.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Uniform error pages and WAF blocking can obscure vulnerable backend normalization. Encodings can be decoded at different layers.

### Remediation

Use opaque file identifiers and canonical containment checks; reject linked paths and normalize once at a defined boundary.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Filesystem audit logs

### Primary references

- https://portswigger.net/web-security

## WEB-07: SSRF with an owned loopback canary

Test server-side URL fetching and redirect checks without touching cloud metadata or third-party hosts.

### Interaction

controlled active validation

### Prerequisites

- Two owned lab services: allowed fetch target and disallowed loopback canary.
- Log connections at the canary; document the exact allowlist.

### Procedure

- Fetch the allowed URL.
- Submit the disallowed canary URL.
- Use a lab redirect from allowed service to disallowed service.
- Inspect egress logs and resolve/pin behavior.

### Lab probes / inspection commands

```text
http://127.0.0.1:9001/wb-canary
```

```text
http://allowed.example.test/redirect-to-lab-canary
```

### Expected secure behavior

Policy is applied to resolved destination addresses and every redirect; disallowed canary sees no request.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A response timeout cannot prove no request occurred. DNS results and redirects can change between checks.

### Remediation

Restrict protocols, resolve and validate every destination, pin addresses during connection, limit redirects and response sizes, and enforce egress controls.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Owned canary HTTP logs
- Container network telemetry

### Primary references

- https://portswigger.net/web-security

## WEB-08: Session lifecycle and privilege transitions

Check token invalidation across logout, password reset, role change, and account suspension.

### Interaction

controlled active validation

### Prerequisites

- Two synthetic sessions and a reversible test account.
- Owner-approved role change; capture tokens only in restricted evidence storage.

### Procedure

- Record successful authorized action with session A.
- Log out A and replay the same token.
- Repeat after changing test password, removing a role, and suspending the fixture account.
- Measure documented revocation latency.

### Lab probes / inspection commands

```text
Replay GET /account using the exact old Cookie or Bearer token after each transition.
```

```text
Compare old token vs newly issued token on the same object and action.
```

### Expected secure behavior

Revocation and privilege changes take effect within the documented threat-model window; old tokens cannot retain revoked actions.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Stateless short-lived tokens may intentionally have a revocation delay. A changed UI is not backend invalidation.

### Remediation

Define session lifecycle requirements, rotate tokens on privilege changes, and use server-side revocation where the risk warrants it.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Identity provider audit logs

### Primary references

- https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/
- https://portswigger.net/web-security

## WEB-09: CSRF and cross-origin policy

Check whether ambient credentials can authorize an unintended state-changing request.

### Interaction

controlled active validation

### Prerequisites

- Test account and a disposable preference field.
- Two owned origins; record actual cookie SameSite behavior.

### Procedure

- Capture an authorized preference update.
- From the second owned origin submit the equivalent form without the anti-CSRF token.
- Check backend state rather than relying on a browser CORS error.
- Repeat with missing, null, and untrusted Origin values where applicable.

### Lab probes / inspection commands

```text
<form action="http://127.0.0.1:8765/preferences" method="POST"><input name="theme" value="canary"></form>
```

```text
Origin: https://untrusted.example.test
```

### Expected secure behavior

Untrusted-origin state changes are rejected by appropriate token/origin/session controls; readable cross-origin responses are restricted.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

CORS response blocking does not prevent a request from changing state. Bearer tokens explicitly attached by scripts have a different CSRF model from ambient cookies.

### Remediation

Use CSRF defenses for ambient authentication, explicit trusted origins, and appropriate cookie attributes.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Browser developer tools
- Burp Repeater

### Primary references

- https://portswigger.net/web-security

## WEB-10: Business logic and idempotency

Verify that repeated or reordered operations cannot violate a defined business invariant.

### Interaction

controlled active validation

### Prerequisites

- Synthetic order and fake-credit balance; no payment gateway.
- An invariant written by the owner, e.g. one refund per paid fixture.

### Procedure

- Run the normal workflow once.
- Replay one request with the same idempotency key.
- Try the same key with a different body.
- Attempt one out-of-order transition and inspect committed state.
- Use a separate approved concurrency experiment if races are in scope.

### Lab probes / inspection commands

```text
Idempotency-Key: wb-order-0001
```

```text
POST /refunds {"order_id":"LAB-001","amount":1}
```

### Expected secure behavior

Repeated actions are deduplicated, conflicting key reuse is rejected, and invalid state transitions cannot commit.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A retry response may differ while the backend state remains correct. Delayed workers require a bounded observation period.

### Remediation

Enforce invariants transactionally, bind idempotency to principal and request content, and validate state transitions server-side.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Application/database transaction logs

### Primary references

- https://wstg.owasp.org/v4.2/4-Web_Application_Security_Testing/

## WEB-11: Upload content and serving isolation

Validate content handling and origin separation using benign files with mismatched types.

### Interaction

controlled active validation

### Prerequisites

- Dedicated upload space and a synthetic account.
- Small text/HTML/SVG fixtures; no executable web shells or malware.

### Procedure

- Upload a permitted plain-text file.
- Repeat with a mismatched extension and Content-Type.
- Download it and inspect disposition, MIME, and serving origin.
- Check authorization on the uploaded object.

### Lab probes / inspection commands

```text
Filename: wb-canary.jpg; body: <p>WB_UPLOAD_MARKER</p>
```

```text
Content-Type: image/jpeg; actual content: plain ASCII marker
```

### Expected secure behavior

Validation follows the actual permitted content; untrusted uploads are served with suitable disposition and isolated privileges/origin.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

Accepting a harmless mismatch is not itself code execution. Establish a reachable dangerous interpretation before rating impact.

### Remediation

Allowlist formats, validate signatures/structure, randomize names, enforce storage authorization, and isolate untrusted serving.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Burp Repeater
- Browser developer tools

### Primary references

- https://portswigger.net/web-security

## WEB-12: HTTP parsing and cache boundaries

Identify disagreement between intermediaries and backends without probing a shared production connection pool.

### Interaction

controlled active validation

### Prerequisites

- Owned reverse proxy/backend pair, packet capture, isolated connection pool.
- Build one malformed request fixture at a time and reset the lab between tests.

### Procedure

- Record normal request framing and cache policy.
- Submit duplicate header fields to the parser fixture and compare normalized values.
- In the isolated lab test conflicting length metadata under explicit approval.
- Check whether a second synthetic request is misassociated; never use another user request as the detector.

### Lab probes / inspection commands

```text
Offline parser fixture: Content-Length: 4\r\nContent-Length: 5
```

```text
Cache-control probe: repeat a synthetic private response under two test identities.
```

### Expected secure behavior

Malformed framing is rejected consistently; private responses cannot be served to another identity.

### Evidence

- Written scope ID; case ID; UTC timestamp; tester identity; exact target and tool version.
- Baseline and probe artifacts, sanitized before reporting; SHA-256 hashes of retained originals.
- Record observed result, control comparison, and any missing telemetry; do not replace raw evidence with a screenshot alone.

### False positives and limits

A 400 from one hop does not prove all hops agree; connection reuse and cache configuration materially affect outcomes.

### Remediation

Normalize or reject ambiguous framing, align proxy/backend parsers, and exclude personalized responses from shared caches.

### Retest

Repeat the identical baseline and probe after the change with the same principal, target, and vantage point. Record changed preconditions and verify the original failure is blocked without breaking the authorized workflow.

### Tools

- Owned proxy debug logs
- Wireshark
- Burp Repeater in the isolated lab

### Primary references

- https://portswigger.net/web-security

