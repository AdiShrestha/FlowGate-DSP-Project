"""Real-data integration smoke. No statistical or performance evidence is emitted."""
import itertools
import json
from pathlib import Path
from flowgate.acquisition import iter_binance_trades
from flowgate.filters import EMA


def test_real_provider_archive_and_filter_are_connected():
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((root/'data/acquisition_manifest.json').read_text())
    row=manifest['records'][0]
    # This smoke must fail when data are absent; it has no generated substitute.
    iterator=iter_binance_trades(root/row['path'],symbol=row['symbol'],utc_date=row['utc_date'],
                                timestamp_unit=row['timestamp_unit'],expected_sha256=row['sha256'])
    try:
        records=list(itertools.islice(iterator,1000))
    finally:
        iterator.close()
    assert len(records)==1000 and len({r.sample_id for r in records})==1000
    # Explicit test parameter; this is neither tuned nor claimed as optimal.
    f=EMA(.25,initialization='first')
    observed=[f.step(float(r.price_text)) for r in records]
    assert f.updates==1000 and observed[0]==float(records[0].price_text)
    assert min(float(r.price_text) for r in records) <= observed[-1] <= max(float(r.price_text) for r in records)
