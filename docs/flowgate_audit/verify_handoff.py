"""Recheck the migration's bytes, not its scientific submission readiness.

Run from any directory. Bulk archives must have been copied/reconstructed.
The output excludes its own digest; a Git commit supplies the outer identity.
"""
import datetime
import hashlib
import json
import zipfile
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    root = Path(__file__).resolve().parents[2]
    audit = root / 'docs/flowgate_audit'
    inventory = json.loads((audit / 'file_inventory.json').read_text())
    acquisition = json.loads((root / 'data/acquisition_manifest.json').read_text())
    provider = json.loads((audit / 'provider_checksums.json').read_text())
    structural = json.loads((audit / 'data_structural_audit.json').read_text())
    provider_by_name = {r['filename']: r for r in provider['records']}
    assert len(provider_by_name) == len(provider['records']) == 155
    data_rows = []
    for record in acquisition['records']:
        path = root / record['path']
        actual = sha(path)
        official = provider_by_name[path.name]
        assert actual == record['sha256'] == official['provider_sha256'] == official['local_sha256']
        assert official['status'] == 'VERIFIED_MATCH'
        data_rows.append({'path': record['path'], 'sha256': actual, 'bytes': path.stat().st_size})
    assert len(data_rows) == 155 and len({r['path'] for r in data_rows}) == 155
    raw_paths = set((root / 'data/raw').glob('*.zip'))
    assert raw_paths == {root / r['path'] for r in data_rows}
    expected_snapshot = {r['path']: r['sha256'] for r in inventory['legacy']
                         if not r['path'].startswith('load-adaptive-iir/data/')}
    with zipfile.ZipFile(audit / 'legacy_snapshot.zip') as archive:
        assert len(archive.infolist()) == len(expected_snapshot) == 215
        assert set(archive.namelist()) == set(expected_snapshot)
        for name, digest in expected_snapshot.items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == digest, name
    factory_rows = []
    for record in inventory['factory']:
        actual = sha(root / record['path'])
        assert actual == record['sha256'], record['path']
        factory_rows.append({'path': record['path'], 'sha256': actual})
    assert len(factory_rows) == 90
    assert len(structural['raw']) == len(structural['processed']) == 155
    assert all(r['status'] == 'PASS' for r in structural['raw'] + structural['processed'])
    assert sum(r['rows'] for r in structural['processed']) == 73_830_561
    findings = []
    for line in (root / 'plan.md').read_text().splitlines():
        if line.startswith('| FG-'):
            fields = [p.strip() for p in line.strip('|').split('|')]
            assert len(fields) == 4
            findings.append(dict(zip(('id', 'priority_and_certainty', 'legacy_evidence', 'finding_and_disposition'), fields)))
    assert len(findings) == 44 and len({r['id'] for r in findings}) == 44
    finding_register = {'scope': 'Forensic findings; source of authority is root plan.md',
                        'plan_sha256': sha(root / 'plan.md'), 'findings': findings}
    (audit / 'findings.json').write_text(json.dumps(finding_register, indent=2) + '\n')
    source_rows = [{'path': str(p.relative_to(root)), 'sha256': sha(p)}
                   for p in sorted((root / 'source').rglob('*')) if p.is_file()
                   and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts]
    report = {
        'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'byte integrity and preservation checks; no empirical efficacy/certification claim',
        'plan_sha256': sha(root / 'plan.md'),
        'verification_script_sha256': sha(Path(__file__)),
        'engine_test_log_sha256': sha(audit / 'engine_tests.log'),
        'factory_test_log_sha256': sha(audit / 'factory_tests.log'),
        'legacy_test_log_sha256': sha(audit / 'legacy_tests.log'),
        'source_files': source_rows,
        'unchanged_supplied_factory_files': factory_rows,
        'copied_raw_archives': data_rows,
        'snapshot_file_count': len(expected_snapshot),
        'snapshot_sha256': sha(audit / 'legacy_snapshot.zip'),
        'findings_count': len(findings),
        'findings_sha256': sha(audit / 'findings.json'),
        'legacy_tags': json.loads((audit / 'git_migration.json').read_text()),
        'limitations': ['full raw CSV semantic parsing remains future C04 work',
                        'no fresh-environment installation attestation',
                        'no measured streaming runtime or confirmatory study',
                        'no guarantee that numerical tests prove absence of all defects']
    }
    (audit / 'handoff_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'raw_archives_verified': len(data_rows),
                      'snapshot_files_verified': len(expected_snapshot),
                      'supplied_factory_files_unchanged': len(factory_rows),
                      'forensic_findings': len(findings), 'status': 'PASS'}))


if __name__ == '__main__':
    main()
