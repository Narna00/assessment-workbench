import copy
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from workbench import catalog,plan,review,portal
from lab_web import handle
from ldap_escape import escape
from wifi_inventory import compare


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.data=catalog()
        self.authorization=json.loads(Path(__file__).with_name('authorization.example.json').read_text())
        self.now=datetime(2026,10,21,tzinfo=timezone.utc)

    def make_plan(self):
        return plan(self.data,self.authorization,'web',self.now)

    def test_catalog_domains_and_unique_ids(self):
        self.assertEqual(len(self.data['cases']),42)
        self.assertEqual({x['domain'] for x in self.data['cases']},{'web','ad','wifi','endpoint'})

    def test_scope_expires_and_cross_domain_rejected(self):
        with self.assertRaises(ValueError):
            plan(self.data,self.authorization,'web',datetime(2027,1,1,tzinfo=timezone.utc))
        self.authorization['domains']['web']['permitted_cases']=['AD-01']
        with self.assertRaises(ValueError): self.make_plan()

    def test_untested_is_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            initial=self.make_plan()
            self.assertFalse(review(initial,initial,folder)['complete'])

    def test_conclusions_require_review_and_artifacts(self):
        initial=self.make_plan(); result=copy.deepcopy(initial)
        result['cases'][0]['status']='finding_confirmed'
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(review(initial,result,folder)['evidence_issues'][0]['issue'],'conclusion_missing_review_or_evidence')

    def test_metadata_tampering_and_duplicate_results_rejected(self):
        initial=self.make_plan();result=copy.deepcopy(initial);result['targets']=['other']
        with self.assertRaises(ValueError):review(initial,result,'.')
        result=copy.deepcopy(initial);result['cases'].append(result['cases'][0])
        with self.assertRaises(ValueError):review(initial,result,'.')

    def test_evidence_integrity(self):
        initial=self.make_plan();result=copy.deepcopy(initial)
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'probe.txt';file.write_bytes(b'proof')
            result['cases'][0].update(status='finding_confirmed',observations='Control pair validated',reviewed_by='Reviewer',artifacts=[{'path':'probe.txt','sha256':hashlib.sha256(b'proof').hexdigest()}])
            self.assertEqual(review(initial,result,folder)['evidence_issues'],[])
            file.write_bytes(b'changed')
            self.assertEqual(review(initial,result,folder)['evidence_issues'][0]['issue'],'artifact_modified')
            result['cases'][0]['artifacts'][0]['path']='../outside'
            with self.assertRaises(ValueError):review(initial,result,folder)

    def test_portal_escapes_script_breakout(self):
        self.data['cases'][0]['title']='</script><script>alert(1)</script>'
        output=portal(self.data)
        self.assertNotIn('</script><script>alert(1)',output)
        self.assertIn('textContent',output)

    def test_lab_authorization_control_pair(self):
        self.assertEqual(handle('/orders?id=1001','Bearer lab-b',False)[0],200)
        self.assertEqual(handle('/orders?id=1001','Bearer lab-b',True)[0],404)
        self.assertEqual(handle('/orders?id=1001','Bearer lab-a',True)[0],200)
        self.assertEqual(handle('/orders?id=1001','',False)[0],401)

    def test_lab_sql_boolean_pair(self):
        self.assertEqual(json.loads(handle('/search?id=1%20AND%201=1')[2]),[[1,'synthetic notebook']])
        self.assertEqual(json.loads(handle('/search?id=1%20AND%201=2')[2]),[])
        self.assertEqual(handle('/search?id=1%20AND%201=1',secure=True)[0],400)

    def test_lab_html_encoding(self):
        self.assertIn('<svg',handle('/echo?q=%3Csvg%3E',secure=False)[2])
        self.assertNotIn('<svg',handle('/echo?q=%3Csvg%3E',secure=True)[2])

    def test_ldap_literal_escaping(self):
        self.assertEqual(escape('a*)(b\\\x00'),r'a\2a\29\28b\5c\00')
        self.assertEqual(escape('café'),'café')

    def test_wifi_dedup_and_unknown_not_rogue(self):
        rows=[{'bssid':'02:00:00:00:00:01','ssid':'LAB','channel':'6'}]*2
        self.assertEqual(len(compare(rows,['02:00:00:00:00:01'])),1)
        self.assertFalse(compare(rows,[])[0]['owned'])
        with self.assertRaises(ValueError):compare([dict(rows[0],bssid='invalid')],[])


if __name__=='__main__':unittest.main()
