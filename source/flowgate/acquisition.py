"""Strict, streaming reader for explicitly checksummed Binance trade archives.

No network calls, global TLS mutation, cache shortcut, missing-day skip,
timestamp-price deduplication, or synthetic replacement. Official checksum
retrieval is a separate audited acquisition operation. A digest proves byte
identity, not labels, independence, representativeness, or licensing rights.
"""
import calendar
import csv
import hashlib
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class TradeRecord:
    symbol: str
    trade_id: int
    timestamp_ns: int
    price_text: str
    quantity_text: str
    quote_quantity_text: str
    buyer_maker: bool
    best_match: bool
    source_sha256: str
    source_row: int

    @property
    def sample_id(self):
        return f"binance:spot:{self.symbol}:{self.trade_id}"


def _decimal(text, field):
    try:
        number = Decimal(text)
    except InvalidOperation as e:
        raise ValueError(f"invalid {field}: {text!r}") from e
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{field} must be finite and positive")
    return number


def _unsigned(text, field):
    if not re.fullmatch(r"[0-9]+", text):
        raise ValueError(f"invalid integer {field}: {text!r}")
    return int(text)


def iter_binance_trades(path, *, symbol, utc_date, timestamp_unit, expected_sha256):
    """Preserve every provider trade, including equal timestamp/price events.

    Fail if rows are malformed, IDs are non-increasing, timestamps decrease,
    or timestamps leave the declared UTC day. Equal timestamps are allowed.
    The explicit unit is milliseconds before 2025 and microseconds from 2025,
    according to the documented Spot schema, not a first-value heuristic.
    """
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Z0-9]{2,30}", symbol):
        raise ValueError("invalid symbol")
    day = date.fromisoformat(utc_date)
    if day.isoformat() != utc_date:
        raise ValueError('utc_date must be canonical YYYY-MM-DD')
    schema_unit = "us" if day >= date(2025, 1, 1) else "ms"
    if timestamp_unit != schema_unit:
        raise ValueError(f"timestamp_unit for this Spot date must be {schema_unit}")
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise ValueError("expected_sha256 must be an explicit lowercase SHA-256")
    factor = 1_000_000 if timestamp_unit == "ms" else 1_000
    day_start = calendar.timegm(day.timetuple()) * 1_000_000_000
    day_end = day_start + 86_400 * 1_000_000_000
    member = f"{symbol}-trades-{day.isoformat()}.csv"
    last_id = last_timestamp = None
    # Hash and parse one open file description. A pathname replacement between
    # separate opens must not attach the digest of A to observations from B.
    with Path(path).open('rb') as verified_stream:
        h = hashlib.sha256()
        for block in iter(lambda: verified_stream.read(1024 * 1024), b''):
            h.update(block)
        digest = h.hexdigest()
        if digest != expected_sha256:
            raise ValueError('archive SHA-256 mismatch')
        verified_stream.seek(0)
        yield from _read_verified(verified_stream, symbol, day_start, day_end, member, factor, digest)


def _read_verified(stream, symbol, day_start, day_end, member, factor, digest):
    last_id = last_timestamp = None
    with zipfile.ZipFile(stream) as archive:
        entries = archive.infolist()
        if len(entries) != 1 or entries[0].filename != member or entries[0].is_dir():
            raise ValueError("archive must contain exactly the expected trade CSV")
        with archive.open(member) as raw, io.TextIOWrapper(raw, encoding="utf-8", newline="") as text:
            reader = csv.reader(text)
            for row_index, row in enumerate(reader, 1):
                if len(row) != 7:
                    raise ValueError(f"row {row_index}: expected seven columns")
                if row_index == 1 and row == ["trade Id", "price", "qty", "quoteQty", "time", "isBuyerMaker", "isBestMatch"]:
                    continue
                trade_id = _unsigned(row[0], "trade_id")
                timestamp = _unsigned(row[4], "timestamp") * factor
                for raw_value, field in zip(row[1:4], ("price", "quantity", "quote_quantity")):
                    _decimal(raw_value, field)
                if row[5] not in {"True", "False"} or row[6] not in {"True", "False"}:
                    raise ValueError(f"row {row_index}: invalid boolean")
                if not day_start <= timestamp < day_end:
                    raise ValueError(f"row {row_index}: timestamp outside declared UTC day")
                if last_id is not None and (trade_id <= last_id or timestamp < last_timestamp):
                    raise ValueError(f"row {row_index}: trade IDs/timestamps out of order")
                last_id, last_timestamp = trade_id, timestamp
                yield TradeRecord(symbol, trade_id, timestamp, row[1], row[2], row[3],
                                  row[5] == "True", row[6] == "True", digest, row_index)
    if last_id is None:
        raise ValueError("archive contains no trade observations")
