"""Full provider-row audit; no filtering/detection/throughput experiment.

Every manifest source receives a retained PASS/ERROR record. Failures do not
become omitted days or generated observations. IDs are not gap-filled.
"""
import argparse
import concurrent.futures
import datetime
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'source'))
from flowgate.acquisition import iter_binance_trades
from flowgate.manifest import read_acquisition_manifest


def scan(record):
    result = {'source_id': record['source_id'], 'path': record['path'],
              'sha256': record['sha256'], 'rows': 0, 'id_gap_count': 0,
              'id_gap_slots': 0, 'equal_timestamp_price_distinct_trades': 0,
              'status': 'ERROR'}
    previous_id = previous_time = None
    prices_at_time = set()
    try:
        for trade in iter_binance_trades(ROOT / record['path'], symbol=record['symbol'],
                                        utc_date=record['utc_date'], timestamp_unit=record['timestamp_unit'],
                                        expected_sha256=record['sha256']):
            if previous_id is None:
                result['first_trade_id'] = trade.trade_id
                result['first_timestamp_ns'] = trade.timestamp_ns
            elif trade.trade_id > previous_id + 1:
                result['id_gap_count'] += 1
                result['id_gap_slots'] += trade.trade_id - previous_id - 1
            if trade.timestamp_ns != previous_time:
                prices_at_time = set()
            if trade.price_text in prices_at_time:
                result['equal_timestamp_price_distinct_trades'] += 1
            prices_at_time.add(trade.price_text)
            previous_id, previous_time = trade.trade_id, trade.timestamp_ns
            result['rows'] += 1
        result.update(last_trade_id=previous_id, last_timestamp_ns=previous_time, status='PASS')
    except Exception as error:
        result.update(error_type=type(error).__name__, error=str(error))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError('audit workers must lie in [1,4]')
    records = read_acquisition_manifest(ROOT / 'data/acquisition_manifest.json')['records']
    output = ROOT / 'docs/re_audit/raw_semantic_audit.json'
    results = []
    report = {'scope': 'Full raw CSV semantic validation and ID/order counts; no natural anomaly labels, no efficacy claim',
              'started_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'expected_sources': len(records), 'completed_sources': 0,
              'parser_sha256': __import__('hashlib').sha256((ROOT / 'source/flowgate/acquisition.py').read_bytes()).hexdigest(),
              'records': results, 'status': 'RUNNING'}
    output.write_text(json.dumps(report, indent=2) + '\n')
    with concurrent.futures.ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(scan, r): r['source_id'] for r in records}
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as error:
                result = {'source_id': futures[future], 'status': 'ERROR',
                          'error_type': type(error).__name__, 'error': str(error)}
            results.append(result)
            report['completed_sources'] = len(results)
            results.sort(key=lambda r: r['source_id'])
            output.write_text(json.dumps(report, indent=2) + '\n')
            print(f"{len(results)}/{len(records)} {result['source_id']} {result['status']} rows={result.get('rows',0)}", flush=True)
    report.update(finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  status='PASS' if len(results) == len(records) and all(r['status'] == 'PASS' for r in results) else 'FAIL',
                  rows=sum(r.get('rows', 0) for r in results),
                  id_gap_slots=sum(r.get('id_gap_slots', 0) for r in results),
                  equal_timestamp_price_distinct_trades=sum(r.get('equal_timestamp_price_distinct_trades', 0) for r in results))
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'records'}, indent=2), flush=True)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
