"""Bind the current audit's files/checks; never issue a research certificate.

Historical migration manifests remain untouched. Every repository file is
hashed/classified, with coverage descriptions that do not pretend generated
metadata or every test scaffold received independent mathematical proof.
"""
import ast
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/re_audit'
sys.path.insert(0,str(ROOT/'source'))
from flowgate.manifest import read_acquisition_manifest
from flowgate.acquisition import sha256_file


def need(condition, message):
    if not condition:raise ValueError(message)


def main():
    manifest=read_acquisition_manifest(ROOT/'data/acquisition_manifest.json')
    semantic=json.loads((OUT/'raw_semantic_audit.json').read_text())
    need(semantic['status']=='PASS','current full raw semantic audit incomplete/failed')
    need(semantic['parser_sha256']==sha256_file(ROOT/'source/flowgate/acquisition.py'),'semantic audit binds different parser bytes')
    planned={r['source_id']:r for r in manifest['records']}
    parsed={r['source_id']:r for r in semantic['records']}
    need(len(parsed)==len(semantic['records'])==len(planned) and set(parsed)==set(planned),'missing/duplicate semantic source unit')
    need(semantic['rows']==sum(r['rows'] for r in parsed.values()),'raw row aggregate mismatch')
    for sid,row in planned.items():
        need(parsed[sid]['status']=='PASS' and parsed[sid]['sha256']==row['sha256'],'failed/inconsistent parsed source')
        need(sha256_file(ROOT/row['path'])==row['sha256'],'raw bytes changed since semantic audit')
    gap_rows=[]
    for symbol in manifest['selection']['symbols']:
        days=sorted([r for sid,r in parsed.items() if sid.split(':')[2]==symbol],key=lambda r:r['source_id'])
        for a,b in zip(days,days[1:]):
            gap_rows.append({'first_source_id':a['source_id'],'next_source_id':b['source_id'],
                             'gap_slots':b['first_trade_id']-a['last_trade_id']-1})
    need(all(r['gap_slots']==0 for r in gap_rows),'gap/overlap at an adjacent daily source boundary')
    loss=json.loads((OUT/'cache_loss_comparison.json').read_text())
    need(loss['status']=='PASS' and loss['units']==len(planned),'cache-count comparison failed')
    need(loss['raw_rows']==semantic['rows'] and loss['lost_rows']==loss['raw_rows']-loss['legacy_cache_rows'],'cache-loss denominator mismatch')
    installed={}
    normalize=lambda name:re.sub(r'[-_.]+','-',name).lower()
    for name in ('fresh_install_report.json','fresh_crypto_install_report.json'):
        for row in json.loads((OUT/name).read_text())['install']:
            installed[normalize(row['metadata']['name'])]=(row['metadata']['version'],row['download_info']['archive_info']['hashes']['sha256'])
    locked_artifacts={}
    for name in ('source/requirements-macos-arm64.lock','source/requirements-test-macos-arm64.lock','factory/requirements-ed25519-macos-arm64.lock'):
        artifacts=[]
        for line in (ROOT/name).read_text().splitlines():
            if not line.strip() or line.startswith('#'):continue
            match=re.fullmatch(r'([\w.-]+)==([^\s]+) --hash=sha256:([0-9a-f]{64})',line)
            need(match is not None,'unsupported artifact-lock entry')
            package,version,digest=match.groups()
            need(installed.get(normalize(package))==(version,digest),'install report differs from artifact lock: '+package)
            artifacts.append({'package':package,'version':version,'sha256':digest})
        locked_artifacts[name]=artifacts
    need('No broken requirements found.' in (OUT/'fresh_pip_check.log').read_text(),'fresh dependency consistency check incomplete')
    scope={
        'source/flowgate/':'Active numerical/acquisition source: semantic audit against mathematical/causal/provenance contracts and regression oracles.',
        'source/tests/':'Disclosed test inputs: full execution plus targeted contract/failure review; never empirical observations.',
        'factory/engine/':'Active factory implementation: source-level integrity/statistical/applicability audit; remaining domain/trust limits documented.',
        'factory/tests/':'Full regression execution and targeted guard/fixture review; not independent scientific proof of every possible path.',
        'factory/legacy/':'Retained historical factory: inactive; preservation/line classification only, no new research authority.',
        'docs/flowgate_audit/':'Initial migration evidence/tools: historical byte identity; do not attribute old validation to current source.',
        'docs/re_audit/':'Current report, observed audit records and scripts: provenance/structure/hash review; supplied report remains untrusted context.'}
    paths=subprocess.run(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT,check=True,capture_output=True).stdout.split(b'\0')
    excluded={'docs/re_audit/file_review_inventory.json','docs/re_audit/verification.json'}
    rows=[]
    for raw in sorted(set(paths)):
        if not raw:continue
        relative=raw.decode()
        if relative in excluded:continue
        path=ROOT/relative
        need(path.is_file() and not path.is_symlink(),'missing/nonregular repository file '+relative)
        data=path.read_bytes()
        try:text=data.decode('utf-8');lines=len(text.splitlines());kind='text'
        except UnicodeDecodeError:text=None;lines=None;kind='binary'
        if relative.endswith('.py') and text is not None:ast.parse(text,filename=relative)
        description=next((value for prefix,value in scope.items() if relative.startswith(prefix)),
                         'Plan/policy/schema/lock/scaffold: checked applicability, history, references or declared structure; scope is described in the current report.')
        rows.append({'path':relative,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
                     'text_lines':lines,'kind':kind,'review_scope':description})
    (OUT/'file_review_inventory.json').write_text(json.dumps({'scope':'all current repository files, excluding self-referential output records and Git-ignored bulk/caches; coverage descriptions distinguish review depth','files':rows},indent=2)+'\n')
    tests={}
    for label,name in [('core','core_tests.log'),('factory_unittest','factory_tests.log'),('factory_pytest','factory_pytest.log'),('fresh_core','fresh_core_tests.log'),('fresh_factory','fresh_factory_tests.log')]:
        text=(OUT/name).read_text()
        if label=='factory_unittest':
            match=re.search(r'Ran (\d+) tests',text);need(match is not None and re.search(r'^OK$',text,re.M),'unittest failure/incomplete log')
            count=int(match.group(1))
        else:
            match=re.search(r'(\d+) passed',text);need(match is not None and not re.search(r'\d+ failed|\d+ errors?',text),'pytest failure/incomplete log')
            count=int(match.group(1))
        tests[label]={'passed':count,'log':name,'sha256':sha256_file(OUT/name)}
    status=json.loads((ROOT/'project/STATUS.json').read_text())
    need(status['methodology_frozen'] is False and status['research_certified'] is False,'unexpected research status')
    plan=json.loads((ROOT/'project/research_plan.json').read_text())
    need(not plan['experiments'],'incomplete template unexpectedly populated')
    need(not (ROOT/'project/.factory/current.json').exists(),'unreviewed project freeze exists')
    report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS',
            'scope':'byte identity, complete raw acquisition semantics, source syntax, retained executed verification and honest unfrozen status; no scientific-result certificate',
            'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),
            'file_count':len(rows),'inventory_sha256':sha256_file(OUT/'file_review_inventory.json'),
            'verifier_sha256':sha256_file(Path(__file__)),'plan_sha256':sha256_file(ROOT/'plan.md'),
            'raw_source_count':len(parsed),'raw_rows':semantic['rows'],'raw_audit_sha256':sha256_file(OUT/'raw_semantic_audit.json'),
            'cross_day_id_gap_slots':sum(r['gap_slots'] for r in gap_rows),'cross_day_boundaries':gap_rows,
            'cache_loss_rows':loss['lost_rows'],'cache_loss_comparison_sha256':sha256_file(OUT/'cache_loss_comparison.json'),
            'lock_artifact_checks':locked_artifacts,
            'lock_check_scope':'pip installation-report artifact identity and dependency consistency, not sealed installed-runtime attestation',
            'tests':tests,'research_certified':False,'limitations':[
                'mathematical tests and line-level review cannot guarantee absence of every scientific defect',
                'inactive legacy packages/snapshots and repetitive generated records have preservation/structural scope, not equal-depth semantic review',
                'no DSP/streaming domain profile, actual bounded runtime or confirmatory study',
                'no independently justified primary quality target, margin, population or source-unit independence',
                'same-user execution/signing is not sealed evaluation or independent peer review']}
    (OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k in ('status','file_count','raw_source_count','raw_rows','cache_loss_rows','research_certified','tests')},indent=2))


if __name__=='__main__':main()
