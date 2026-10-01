"""Validate an explicit complete provider acquisition frame before any I/O.

Metadata consistency is checked here; provider authenticity is not inferred
from a caller-supplied checksum string or a status label.
"""
import json
import math
import re
from datetime import date, datetime, timedelta
from pathlib import Path


def _unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_constant(value):
    raise ValueError(f"non-standard JSON constant: {value}")


def _finite_json_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("non-finite JSON number")
    return number


def _day(value):
    if not isinstance(value, str):
        raise ValueError("UTC dates must be ISO strings")
    day = date.fromisoformat(value)
    if day.isoformat() != value:
        raise ValueError("UTC dates must be canonical YYYY-MM-DD")
    return day


def read_acquisition_manifest(path):
    obj = json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=_unique,
                     parse_constant=_reject_constant, parse_float=_finite_json_float)
    if not isinstance(obj, dict) or type(obj.get('schema_version')) is not int or obj['schema_version'] != 1:
        raise ValueError("unsupported acquisition manifest schema")
    selection = obj.get('selection')
    if not isinstance(selection, dict):
        raise ValueError("explicit acquisition selection frame required")
    symbols = selection.get('symbols')
    if not isinstance(symbols, list) or not symbols or any(not isinstance(s, str) or not re.fullmatch(r'[A-Z0-9]{2,30}', s) for s in symbols):
        raise ValueError("selection requires valid symbols")
    if len(set(symbols)) != len(symbols):
        raise ValueError("duplicate selection symbol")
    start, stop = _day(selection.get('start_utc_date')), _day(selection.get('end_utc_date'))
    if start > stop:
        raise ValueError("selection dates reversed")
    dates = [start + timedelta(days=i) for i in range((stop - start).days + 1)]
    planned = {(s, d.isoformat()) for s in symbols for d in dates}
    count = obj.get('expected_record_count')
    records = obj.get('records')
    if type(count) is not int or count != len(planned) or not isinstance(records, list) or len(records) != count:
        raise ValueError("missing/extra records relative to acquisition selection")
    seen = set()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("source record must be an object")
        symbol = row.get('symbol')
        if not isinstance(symbol, str):
            raise ValueError("source symbol must be a string")
        day = _day(row.get('utc_date'))
        key = (symbol, day.isoformat())
        if key not in planned or key in seen:
            raise ValueError("duplicate or unplanned source unit")
        seen.add(key)
        name = f'{symbol}-trades-{day.isoformat()}.zip'
        url = f'https://data.binance.vision/data/spot/daily/trades/{symbol}/{name}'
        digest = row.get('sha256')
        if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise ValueError("invalid archive SHA-256")
        expected = {'source_id': f'binance:spot:{symbol}:{day.isoformat()}',
                    'origin': 'observational', 'labels': 'none',
                    'path': 'data/raw/' + name, 'url': url, 'checksum_url': url + '.CHECKSUM',
                    'timestamp_unit': 'us' if day >= date(2025, 1, 1) else 'ms',
                    'status': 'provider_checksum_verified'}
        if any(row.get(k) != v for k, v in expected.items()):
            raise ValueError(f"inconsistent provider source metadata: {name}")
        parts = str(row.get('provider_checksum_text', '')).split()
        if parts != [digest, name]:
            raise ValueError("checksum text and source identity disagree")
        try:
            verified = datetime.fromisoformat(row['verified_at'])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("valid checksum retrieval time required") from error
        if verified.tzinfo is None:
            raise ValueError("checksum retrieval time requires timezone")
    if seen != planned:
        raise ValueError("acquisition frame incomplete")
    return obj
