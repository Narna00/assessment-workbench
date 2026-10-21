"""Offline assessment catalog, engagement plans, evidence review, and portable portal."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
DOMAINS = ('web', 'ad', 'wifi', 'endpoint')
STATUSES = ('not_tested', 'blocked', 'inconclusive', 'secure_observed', 'finding_confirmed')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def timestamp(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Timestamp needs a timezone')
    return result.astimezone(timezone.utc)


def catalog(path=None):
    data = read(path or HERE / 'catalog.json')
    if data.get('schema') != 'assessment-catalog/v1' or not isinstance(data.get('cases'), list):
        raise ValueError('Unsupported catalog schema')
    ids = set()
    for case in data['cases']:
        for field in ('id', 'domain', 'title', 'objective', 'prerequisites', 'procedure', 'probes', 'secure_behavior', 'evidence', 'false_positives', 'remediation', 'retest', 'tools', 'sources', 'impact'):
            if not case.get(field):
                raise ValueError(f'Missing {field} on case {case.get("id")}')
        if case['id'] in ids or case['domain'] not in DOMAINS:
            raise ValueError('Duplicate ID or invalid domain')
        ids.add(case['id'])
        for source in case['sources']:
            if not source.startswith('https://'):
                raise ValueError('Sources must be HTTPS URLs')
    return data


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def plan(data, authorization, domain, now):
    if authorization.get('schema') != 'assessment-authorization/v1':
        raise ValueError('Unsupported authorization schema')
    if not authorization.get('engagement_id') or not authorization.get('approved_by'):
        raise ValueError('Engagement ID and approver are required')
    if not timestamp(authorization['valid_from']) <= now < timestamp(authorization['valid_until']):
        raise ValueError('Authorization window is closed')
    scope = authorization['domains'][domain]
    if not isinstance(scope['targets'], list) or not scope['targets'] or not all(isinstance(x, str) and x for x in scope['targets']):
        raise ValueError('Explicit nonempty target list required')
    permitted = scope['permitted_cases']
    if not isinstance(permitted, list) or not permitted or len(set(permitted)) != len(permitted):
        raise ValueError('Explicit unique case IDs required')
    known = {case['id'] for case in data['cases'] if case['domain'] == domain}
    if not set(permitted) <= known:
        raise ValueError('Unknown or cross-domain case permission')
    return {'schema': 'assessment-plan/v1', 'engagement_id': authorization['engagement_id'],
            'domain': domain, 'targets': scope['targets'], 'created_at': now.isoformat(),
            'authorization_sha256': fingerprint(authorization), 'catalog_sha256': fingerprint(data),
            'cases': [{'case_id': case_id, 'status': 'not_tested', 'observations': '', 'reviewed_by': '', 'artifacts': []} for case_id in permitted]}


def artifact_hash(root, name):
    root = Path(root).resolve(strict=True)
    if not isinstance(name, str) or not name or '\\' in name or ':' in name:
        raise ValueError('Unsafe evidence path')
    path = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or not path.resolve().is_relative_to(root):
        raise ValueError('Evidence path escapes root')
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
            raise ValueError('Linked artifacts are not accepted')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            digest.update(chunk)
    return digest.hexdigest()


def review(original, results, root):
    if original.get('schema') != 'assessment-plan/v1' or results.get('schema') != original['schema']:
        raise ValueError('Unsupported result schema')
    for field in ('engagement_id', 'domain', 'targets', 'authorization_sha256', 'catalog_sha256', 'created_at'):
        if original[field] != results[field]:
            raise ValueError(f'Result metadata changed: {field}')
    expected = [item['case_id'] for item in original['cases']]
    actual = [item['case_id'] for item in results['cases']]
    if len(actual) != len(set(actual)) or set(actual) != set(expected):
        raise ValueError('Results must cover exactly the planned cases once')
    counts = {status: 0 for status in STATUSES}
    issues = []
    for item in results['cases']:
        case_id, status = item['case_id'], item['status']
        if status not in STATUSES:
            raise ValueError(f'Unsupported status: {status}')
        counts[status] += 1
        if status in ('secure_observed', 'finding_confirmed'):
            if not item.get('observations') or not item.get('reviewed_by') or not item.get('artifacts'):
                issues.append({'case_id': case_id, 'issue': 'conclusion_missing_review_or_evidence'})
        for artifact in item['artifacts']:
            expected_hash = artifact['sha256']
            if not isinstance(expected_hash, str) or len(expected_hash) != 64 or any(c not in '0123456789abcdef' for c in expected_hash):
                raise ValueError('Invalid artifact digest')
            try:
                actual_hash = artifact_hash(root, artifact['path'])
            except FileNotFoundError:
                issues.append({'case_id': case_id, 'issue': 'artifact_missing', 'path': artifact['path']})
            else:
                if actual_hash != expected_hash:
                    issues.append({'case_id': case_id, 'issue': 'artifact_modified', 'path': artifact['path']})
    return {'engagement_id': original['engagement_id'], 'counts': counts, 'evidence_issues': issues,
            'complete': not issues and not any(counts[key] for key in ('not_tested', 'blocked', 'inconclusive')),
            'interpretation': 'Mechanical evidence review only. secure_observed is limited to recorded tests, not proof of absence.'}


def portal(data):
    # Embed data as inert JSON with HTML-sensitive characters escaped. Render
    # untrusted catalog values through textContent, never innerHTML.
    embedded = json.dumps(data, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Assessment Workbench</title><style>
:root{color-scheme:dark;font-family:system-ui;background:#0d1420;color:#e8eef7}body{margin:0}header,main{max-width:1200px;margin:auto;padding:24px}header{border-bottom:1px solid #344257}h1{font-size:2.4rem;letter-spacing:-.04em;margin-bottom:8px}p{line-height:1.6;color:#becbdd}.label{color:#61dbc1;text-transform:uppercase;letter-spacing:.12em;font-size:.75rem}nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}input,select{font:inherit;background:#172337;color:inherit;padding:12px;border:1px solid #4f637e;border-radius:8px}input{flex:1;min-width:180px}article{background:#172337;border:1px solid #344257;padding:22px;border-radius:12px;margin-bottom:18px}h2{margin:8px 0 16px;font-size:1.3rem}h3{font-size:.95rem;color:#83e8d1}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#0d1420;padding:14px;border-radius:6px;color:#d4f5d8}li{line-height:1.65;margin-bottom:6px}a{color:#91bcff}summary{cursor:pointer;padding:10px 0}details[open] summary{color:#61dbc1}#count{font-variant-numeric:tabular-nums}footer{padding:20px;color:#b6c7dd}small{color:#b6c7dd}a:focus,input:focus,select:focus,summary:focus{outline:3px solid #61dbc1;outline-offset:3px}</style>
<header><div class="label">Field methodology / evidence / retest</div><h1>Assessment Workbench</h1><p>Web applications · Active Directory · Wi-Fi · endpoints. Search test cards, inspect lab probes, and retain evidence that supports the conclusion.</p><nav aria-label="Catalog filters"><input id="q" type="search" aria-label="Search tests" placeholder="Search tests, tools, payloads…"><select id="domain" aria-label="Domain"><option value="">All domains</option><option value="web">Web applications</option><option value="ad">Active Directory</option><option value="wifi">Wi-Fi</option><option value="endpoint">Endpoints</option></select></nav><p id="count" role="status" aria-live="polite"></p></header><main id="cards"></main><footer>Offline reference. Commands are displayed, never executed. Use written scope and the lab prerequisites on each card. Version 0.1.0.</footer>
<script id="catalog" type="application/json">''' + embedded + '''</script><script>
const data=JSON.parse(document.getElementById('catalog').textContent),cards=document.getElementById('cards'),q=document.getElementById('q'),domain=document.getElementById('domain');
function el(tag,text,parent){const n=document.createElement(tag);n.textContent=text;parent.appendChild(n);return n}
function section(parent,title,value){el('h3',title,parent);if(Array.isArray(value)){const ul=el('ul','',parent);for(const v of value)el('li',v,ul)}else el('p',value,parent)}
function render(){cards.replaceChildren();const search=q.value.toLowerCase();const found=data.cases.filter(c=>(!domain.value||c.domain===domain.value)&&JSON.stringify(c).toLowerCase().includes(search));document.getElementById('count').textContent=found.length+' of '+data.cases.length+' test cases';for(const c of found){const a=el('article','',cards);el('small',c.id+' · '+c.domain+' · '+c.impact,a);el('h2',c.title,a);el('p',c.objective,a);const d=el('details','',a);el('summary','Procedure, probes, and evidence',d);section(d,'Prerequisites',c.prerequisites);section(d,'Procedure',c.procedure);el('h3','Lab probes / read-only inspection commands',d);for(const p of c.probes)el('pre',p,d);for(const [key,title] of [['secure_behavior','Expected secure behavior'],['evidence','Evidence to retain'],['false_positives','False positives / limits'],['remediation','Remediation'],['retest','Retest'],['tools','Tools']])section(d,title,c[key]);el('h3','Primary references',d);const ul=el('ul','',d);for(const url of c.sources){const li=el('li','',ul),link=el('a',url,li);link.href=url;link.target='_blank';link.rel='noopener noreferrer'}}}
q.addEventListener('input',render);domain.addEventListener('change',render);render();</script></html>'''


def exclusive(path, text):
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    listing = commands.add_parser('list')
    listing.add_argument('--domain', choices=DOMAINS)
    show = commands.add_parser('show')
    show.add_argument('case_id')
    make = commands.add_parser('plan')
    make.add_argument('authorization', type=Path)
    make.add_argument('--domain', required=True, choices=DOMAINS)
    make.add_argument('--output', required=True, type=Path)
    check = commands.add_parser('review')
    check.add_argument('plan', type=Path)
    check.add_argument('results', type=Path)
    check.add_argument('--evidence-root', required=True, type=Path)
    view = commands.add_parser('portal')
    view.add_argument('--output', required=True, type=Path)
    commands.add_parser('validate')
    args = parser.parse_args(argv)
    try:
        data = catalog(args.catalog)
        if args.command == 'validate':
            print(json.dumps({'cases': len(data['cases']), 'catalog_sha256': fingerprint(data)}))
        elif args.command == 'list':
            for case in data['cases']:
                if not args.domain or case['domain'] == args.domain:
                    print(f'{case["id"]}\t{case["title"]}')
        elif args.command == 'show':
            selected = next((case for case in data['cases'] if case['id'] == args.case_id), None)
            if selected is None:
                raise ValueError('Unknown test ID')
            print(json.dumps(selected, indent=2, ensure_ascii=False))
        elif args.command == 'plan':
            output = plan(data, read(args.authorization), args.domain, datetime.now(timezone.utc))
            exclusive(args.output, json.dumps(output, indent=2) + '\n')
        elif args.command == 'review':
            report = review(read(args.plan), read(args.results), args.evidence_root)
            print(json.dumps(report, indent=2))
            return int(not report['complete'])
        else:
            exclusive(args.output, portal(data))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
