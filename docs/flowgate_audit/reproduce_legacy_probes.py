"""Standalone forensic counterexamples, not active methods or research trials.

Only two inspected, SHA-bound quarantined modules are executed. The injection
is explicitly artificial; no generated price is saved or supplied to the new
engine. This CLI requires the audit dependency group and one real raw archive.
"""
import collections
import hashlib
import io
import itertools
import json
import math
import sys
import types
import zipfile
from pathlib import Path


def main():
    import numpy as np
    import pandas as pd
    root = Path(__file__).resolve().parents[2]
    audit = root / 'docs/flowgate_audit'
    sys.path.insert(0, str(root / 'source'))
    from flowgate.acquisition import iter_binance_trades
    inventory = json.loads((audit / 'file_inventory.json').read_text())
    expected = {r['path']: r['sha256'] for r in inventory['legacy']}
    def load(archive, name):
        content = archive.read(name)
        assert hashlib.sha256(content).hexdigest() == expected[name]
        module = types.ModuleType('forensic_' + Path(name).stem)
        exec(compile(content, name, 'exec'), module.__dict__)
        return module
    with zipfile.ZipFile(audit / 'legacy_snapshot.zip') as archive:
        evaluator = load(archive, 'load-adaptive-iir/src/evaluate.py')
        injector = load(archive, 'load-adaptive-iir/src/anomaly_injection.py')
        table = pd.read_csv(io.BytesIO(archive.read('load-adaptive-iir/results/tables/multi_seed_roc_auc.csv')))
    mask = np.zeros(1000, dtype=bool); mask[500] = True
    alert = np.zeros(1000, dtype=bool); alert[499] = True
    info = [{'type': 'point', 'start': 500, 'end': 500}]
    metrics = evaluator.evaluate_predictions(mask, alert, info)
    area = evaluator.compute_auc(alert.astype(float), info, mask)[:2]
    all_rows = table[table.anomaly_type == 'all']
    record = next(r for r in json.loads((root / 'data/acquisition_manifest.json').read_text())['records']
                  if r['symbol'] == 'BTCUSDT' and r['utc_date'] == '2024-01-01')
    iterator = iter_binance_trades(root / record['path'], symbol=record['symbol'], utc_date=record['utc_date'],
                                   timestamp_unit=record['timestamp_unit'], expected_sha256=record['sha256'])
    try:
        prices = [float(r.price_text) for r in itertools.islice(iterator, 50_000)]
    finally:
        iterator.close()
    assert len(prices) == 50_000
    rng_state = np.random.get_state()
    try:
        _, _, actual_events = injector.inject_anomalies(pd.Series(prices), n_each=100, window_std=100, seed=0)
    finally:
        np.random.set_state(rng_state)
    counts = collections.Counter(e['type'] for e in actual_events)
    output = {
        'scope': 'Forensic legacy defects and historical table counts; not new empirical efficacy evidence',
        'counterexample': {
            'description': 'Only alert at 499; true label at 500. Nearby alert is not a point true positive. Missing legacy detected latency is serialized as null, not zero.',
            'legacy_precision_recall_f1_latency_fp_per_1k': [float(v) if math.isfinite(v) else None for v in metrics],
            'legacy_roc_auc_pr_auc': [float(v) for v in area],
            'correct_point_tp': int(np.sum(alert & mask)), 'correct_point_fp': int(np.sum(alert & ~mask))},
        'multiseed': {'rows': len(table), 'types': table.anomaly_type.value_counts().to_dict(),
                     'unique_days': len(all_rows[['symbol', 'date']].drop_duplicates()),
                     'unique_seed_labels': int(all_rows.seed.nunique()),
                     'duplicate_seed_config_rows': int(all_rows.duplicated(['seed', 'config']).sum()),
                     'independence_status': 'not_established'},
        'injection_feasibility_probe': {'source_sha256': record['sha256'], 'source_id': record['source_id'],
                                      'observations': len(prices), 'seed': 0, 'requested_each_type': 100,
                                      'actual_events': len(actual_events),
                                      'actual_by_type': {k: counts[k] for k in ['point', 'level_shift', 'volatility_burst']},
                                      'generated_series_saved': False,
                                      'limitations': 'Real background, deliberate legacy perturbation; no natural labels or task-quality conclusion'}
    }
    (audit / 'targeted_probes.json').write_text(json.dumps(output, indent=2, allow_nan=False) + '\n')
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
