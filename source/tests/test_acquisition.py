"""Test-only archives. They never enter data/, runs, or an empirical claim."""
import zipfile
import hashlib
from unittest.mock import patch
import pytest
from flowgate.acquisition import iter_binance_trades, sha256_file


def archive(tmp_path, rows, *, member='BTCUSDT-trades-2024-01-01.csv'):
    path = tmp_path/'fixture.zip'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(member, '\n'.join(rows)+'\n')
    return path


def read(path, **overrides):
    kwargs = dict(symbol='BTCUSDT', utc_date='2024-01-01', timestamp_unit='ms',
                  expected_sha256=sha256_file(path))
    return list(iter_binance_trades(path, **{**kwargs, **overrides}))


def test_equal_price_and_timestamp_trades_are_not_dropped(tmp_path):
    path = archive(tmp_path, ['1,42000,1,42000,1704067200000,True,True',
                              '2,42000,1,42000,1704067200000,False,True'])
    rows = read(path)
    assert len(rows) == 2
    assert rows[0].timestamp_ns == 1704067200000000000
    assert rows[0].sample_id != rows[1].sample_id


def test_checksum_mismatch_and_wrong_unit_fail(tmp_path):
    path = archive(tmp_path, ['1,42000,1,42000,1704067200000,True,True'])
    with pytest.raises(ValueError, match='SHA-256'): read(path, expected_sha256='0'*64)
    with pytest.raises(ValueError, match='timestamp_unit'): read(path, timestamp_unit='us')


@pytest.mark.parametrize('row', ['1,nan,1,1,1704067200000,True,True',
                                  '1,1,1,1,1704153600000,True,True',
                                  '1,1,1,1,1704067200000,invalid,True',
                                  '1,1,1,1,1704067200000,True',
                                  '1,1,1,1,1704067200000.5,True,True'])
def test_invalid_rows_fail(tmp_path, row):
    with pytest.raises(ValueError): read(archive(tmp_path, [row]))


def test_duplicate_id_and_unsafe_member_fail(tmp_path):
    row='1,1,1,1,1704067200000,True,True'
    with pytest.raises(ValueError): read(archive(tmp_path, [row, row]))
    with pytest.raises(ValueError): read(archive(tmp_path, [row], member='../escape.csv'))


def test_2025_microseconds_and_empty_archive(tmp_path):
    path=archive(tmp_path,['1,1,1,1,1735689600000001,True,True'],member='BTCUSDT-trades-2025-01-01.csv')
    rows=read(path,utc_date='2025-01-01',timestamp_unit='us')
    assert rows[0].timestamp_ns == 1735689600000001000
    with pytest.raises(ValueError): read(archive(tmp_path, []))


def test_hash_and_parser_use_same_file_when_path_is_replaced(tmp_path):
    path=archive(tmp_path,['1,1,1,1,1704067200000,True,True'])
    expected=sha256_file(path)
    replacement=tmp_path/'other.zip'
    with zipfile.ZipFile(replacement,'w') as z:
        z.writestr('BTCUSDT-trades-2024-01-01.csv','1,2,1,2,1704067200000,True,True\n')
    make_hash=hashlib.sha256
    class Hasher:
        def __init__(self):self.hash=make_hash()
        def update(self,data):self.hash.update(data)
        def hexdigest(self):
            digest=self.hash.hexdigest();replacement.replace(path);return digest
    with patch('flowgate.acquisition.hashlib.sha256',Hasher):
        rows=list(iter_binance_trades(path,symbol='BTCUSDT',utc_date='2024-01-01',timestamp_unit='ms',expected_sha256=expected))
    assert rows[0].price_text=='1' and rows[0].source_sha256==expected
    assert sha256_file(path)!=expected
