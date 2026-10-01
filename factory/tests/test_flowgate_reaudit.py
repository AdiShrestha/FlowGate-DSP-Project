"""Disclosed fixtures proving repaired guards; never research evidence."""
import base64
import contextlib
import hashlib
import hmac
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import gatekeeper as g
from engine import supervisor
from engine.metrics import paired_inference, EvidenceError
from engine.io import read_json,write_json,sha,canonical
from test_v3 import fixture,evaluate,forged_output_rehash
from verify_bundle_standalone import _verify_receipt_sig,verify_bundle
from engine.bundle import create_bundle
from engine.io import inventory


class ReauditStatistics(unittest.TestCase):
    def test_sign_flip_unit_scaling_matches_combinatorial_oracle(self):
        # Of 32 assignments only all + or all - reach the observed maximum.
        for scale in (1e-100,1e-16,1,1e100):
            self.assertEqual(paired_inference([scale]*5,[0]*5,draws=1000)['p_raw'],2/32)

    def test_nonfinite_difference_is_rejected(self):
        with self.assertRaises(EvidenceError):paired_inference([1e308]*2,[-1e308]*2)

    def test_f1_has_no_universal_chance_baseline(self):
        self.assertEqual(g._result_findings({'metric':'f1','value':.01}),[])
        self.assertEqual(g._result_findings({'metric':'accuracy','value':.01}),[])

    def test_narrow_interval_is_not_invalid_due_to_units(self):
        self.assertEqual(g._result_findings({'ci':[1e-20,2e-20],'n':5}),[])

    def test_malformed_p_or_interval_cannot_be_waived(self):
        for entry in ({'p_value':2},{'p_value':True},{'ci':[1,0]},{'ci':[1,'2']}):
            self.assertNotEqual(g.verify_result_plausibility({**entry,'investigation_note':'checked'}),0)

    def test_unresolved_investigation_blocks(self):
        self.assertNotEqual(g.verify_result_plausibility({'p_value':0,'investigation_note':'checked','investigation_disposition':'unresolved'}),0)

    def test_empty_replay_and_empty_check_contract_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.json'
            write_json(path,{'original':{},'replay':{}})
            self.assertNotEqual(g.verify_reproducibility(path),0)
            write_json(path,{'checks':[]})
            self.assertNotEqual(g.check_contract(path),0)

    def test_exactly_flat_sensitivity_is_valid_and_scale_invariant(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.json'
            for scale in (1e-20,1,1e20):
                write_json(path,{'sweeps':[{'parameter':'a','levels':[1,2,3],'metrics':[scale]*3}]})
                self.assertEqual(g.verify_sensitivity_analysis(path),0)

    def test_statistical_protocol_requires_actual_numeric_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.json'
            protocol={'primary_metric':'loss','sampling_unit':'declared_fixture_unit','test':'t','alpha':.05,
                      'effect_size':True,'confidence_interval':[0,1],'multiplicity_correction':'Holm'}
            write_json(path,protocol)
            self.assertNotEqual(g.verify_statistical_protocol(path),0)

    def test_one_actual_failure_category_does_not_need_two_invented_categories(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'fixture.json'
            write_json(path,{'failures':[{'category':'fixture','candidate_ids':['fixture-id'],'prevalence':.1,'severity':'SEV-2'}]})
            self.assertEqual(g.verify_failure_taxonomy(path),0)


class ReauditLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.plan=fixture(self.root)
        self.keyenv=patch.dict(os.environ,{'FACTORY_SUPERVISOR_KEY':str(self.root/'keys/supervisor.key')})
        self.keyenv.start()
        self.quiet=contextlib.redirect_stdout(io.StringIO());self.quiet.__enter__()

    def tearDown(self):
        self.quiet.__exit__(None,None,None);self.keyenv.stop();self.temp.cleanup()

    def execute(self):
        g.freeze(self.root);self.assertEqual(g.run_exp(self.root,'known'),0)
        return g.active(self.root)[1]/'runs/known/attempt0001'

    def test_missing_signature_blocks_evaluation(self):
        attempt=self.execute();record=read_json(attempt/'execution.json')
        record.pop('supervisor_receipt');write_json(attempt/'execution.json',record)
        self.assertTrue(any('missing signed' in e['detail'] for e in evaluate(self.root)['errors']))

    def test_rehashing_outputs_does_not_repair_signature(self):
        attempt=self.execute();(attempt/'method.txt').write_text('Modified fixture method')
        forged_output_rehash(self.root)
        self.assertTrue(any('signed receipt binding' in e['detail'] for e in evaluate(self.root)['errors']))

    def test_nonce_replay_is_rejected(self):
        attempt=self.execute();record=read_json(attempt/'execution.json')
        record['run_nonce']='replacement nonce fixture';write_json(attempt/'execution.json',record)
        self.assertTrue(evaluate(self.root)['errors'])

    def test_missing_attempt_slot_is_rejected(self):
        attempt=self.execute();attempt.rename(attempt.with_name('attempt0002'))
        self.assertTrue(any('noncontiguous' in e['detail'] for e in evaluate(self.root)['errors']))

    def test_unmeasured_resources_are_null_and_legacy_runtime_disclosed(self):
        attempt=self.execute();r=read_json(attempt/'execution.json')['supervisor_receipt']
        self.assertIsNone(r['resource_observations']['cpu_time_seconds'])
        self.assertIsNone(r['resource_observations']['memory_peak_bytes'])
        self.assertIsNone(r['interpreter_hash'])
        self.assertEqual(r['runtime_id'],'legacy-command-unattested')

    def test_actual_typed_launch_and_audit_agree(self):
        self.plan['experiments'][0]['execution_contract']={
            'runtime_id':'python-cpu-v1','entrypoint':'source/run.py','network':'allowed',
            'arguments':{'a':'supervisor_bound','b':'plan_seed','c':'plan_id'}}
        write_json(self.root/g.ROOT_PLAN,self.plan)
        self.execute();self.assertEqual(evaluate(self.root)['errors'],[])

    def test_disabled_network_cannot_claim_unimplemented_isolation(self):
        self.plan['experiments'][0]['execution_contract']={
            'runtime_id':'python-cpu-v1','entrypoint':'source/run.py','network':'disabled'}
        write_json(self.root/g.ROOT_PLAN,self.plan);g.freeze(self.root)
        with self.assertRaisesRegex(EvidenceError,'cannot enforce network isolation'):g.run_exp(self.root,'known')

    def test_deterministic_method_does_not_need_fake_epochs(self):
        method=self.root/'method.txt';method.write_text('Disclosed analytic algorithm fixture')
        manifest=self.root/'method.json'
        write_json(manifest,{'mode':'deterministic','rationale':'Analytic fixture evaluates an explicitly fixed algorithm with no learned parameters.',
                             'method_evidence':{'path':'method.txt','sha256':sha(method)}})
        self.assertEqual(g.verify_training_sufficiency(manifest),0)
        method.write_text('Altered fixture');self.assertNotEqual(g.verify_training_sufficiency(manifest),0)

    def test_explicit_three_epoch_budget_is_not_rejected_by_ten_epoch_floor(self):
        history=self.root/'history.csv';history.write_text('epoch,validation_loss\n1,1\n2,.5\n3,.3\n')
        manifest=self.root/'training.json'
        write_json(manifest,{'epochs_trained':3,'min_epochs':1,'max_epochs':3,'stopping_rule':'fixed_budget',
                            'history_evidence':{'path':'history.csv','sha256':sha(history)}})
        self.assertEqual(g.verify_training_sufficiency(manifest),0)

    def test_hmac_fallback_never_exports_signing_secret(self):
        with patch.object(supervisor,'_try_ed25519',return_value=False):
            private,public,scheme=supervisor.init_supervisor_keys(force=True)
            data=base64.b64decode(public.read_text().splitlines()[1])
            self.assertNotEqual(data,private.read_bytes())
            receipt=supervisor.sign_receipt({'experiment_id':'known'})
            self.assertTrue(supervisor.verify_receipt_signature(receipt))
            ok,_=_verify_receipt_sig(receipt,data,scheme);self.assertFalse(ok)
            self.assertEqual(receipt['signature_scheme'],'hmac-sha256')

    def test_public_ed25519_key_cannot_be_used_for_hmac_downgrade(self):
        if not supervisor._try_ed25519():self.skipTest('cryptography unavailable')
        _,public,_=supervisor.init_supervisor_keys(force=True)
        receipt=supervisor.sign_receipt({'experiment_id':'known'})
        payload=canonical({k:v for k,v in receipt.items() if k not in ('signature_scheme','supervisor_signature','public_key_id')})
        receipt['signature_scheme']='hmac-sha256'
        public_bytes=base64.b64decode(public.read_text().splitlines()[1])
        receipt['supervisor_signature']=base64.b64encode(hmac.new(public_bytes,payload,hashlib.sha256).digest()).decode()
        with self.assertRaisesRegex(EvidenceError,'scheme differs'):supervisor.verify_receipt_signature(receipt)

    def test_offline_verifier_reads_actual_nested_receipts_and_binds_outputs(self):
        if not supervisor._try_ed25519():self.skipTest('Ed25519 public verification unavailable')
        attempt=self.execute()
        files={str(p.relative_to(self.root)):p for p in attempt.rglob('*') if p.is_file()}
        archive=self.root/'bundle.zip'
        create_bundle(archive,files,{'factory_version':'3.3.0'})
        public=self.root/'keys/supervisor.pub'
        result=verify_bundle(archive,public)
        self.assertEqual(result['status'],'PASS',result['errors'])
        self.assertEqual(result['signatures_verified'],1)
        (attempt/'method.txt').write_text('Offline mutation fixture')
        create_bundle(archive,files,{'factory_version':'3.3.0'})
        result=verify_bundle(archive,public)
        self.assertEqual(result['status'],'FAIL')
        self.assertTrue(any('signed output' in e for e in result['errors']))

    def test_cached_bytecode_is_not_omitted_from_freeze_checks(self):
        cache=self.root/'source/__pycache__';cache.mkdir()
        (cache/'run.cpython-312.pyc').write_bytes(b'test-only bytecode placeholder')
        with self.assertRaises(EvidenceError):inventory(self.root,['source'])
        paths=inventory(self.root,['source'],reject_dangerous_ext=False)
        self.assertIn('source/__pycache__/run.cpython-312.pyc',paths)

    def test_verification_does_not_generate_missing_keys(self):
        key=self.root/'keys/supervisor.key'
        with self.assertRaises(EvidenceError):supervisor.verify_receipt_signature({'supervisor_signature':'AA==','signature_scheme':'ed25519','public_key_id':'test'})
        self.assertFalse(key.exists())
