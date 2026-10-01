"""Independent mathematical oracles and disclosed failure fixtures.

All constants and mocked requests here are test inputs, never empirical data.
"""
import copy
import io
import json
import math
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import pytest
from scipy.stats import t
from flowgate.filters import EMA, KAMA, AdaptiveAlpha, frozen_ema_cutoff_radians
from flowgate.scoring import CausalResidualScore
from flowgate.shedding import EMAPipeline
from flowgate.metrics import event_metrics,point_metrics
from flowgate.queue import fcfs_schedule
from flowgate.statistics import paired_t_summary
from flowgate.manifest import read_acquisition_manifest
from flowgate.download import reconstruct
from flowgate.acquisition import sha256_file


def test_smallest_positive_float_has_positive_frozen_cutoff():
    a = math.nextafter(0, 1)
    assert frozen_ema_cutoff_radians(a) == a


def test_nyquist_crossing_classification_uses_exact_supplied_float():
    boundary=2*(math.sqrt(2)-1)
    for a in [math.nextafter(boundary,0),boundary,math.nextafter(boundary,1)]:
        q=Fraction.from_float(a)
        exists=q*q<=4*(1-q)
        w=frozen_ema_cutoff_radians(a)
        assert (w is not None)==exists
        if exists:assert 0<w<=math.pi


def test_large_kama_efficiency_ratio_uses_exact_integer_oracle():
    k = KAMA(period=3, fast_period=2, slow_period=30, initialization='first')
    values = [-10**308, 10**308, 0, 10**308]
    er = Fraction(abs(values[-1]-values[0]),sum(abs(b-a) for a,b in zip(values,values[1:])))
    expected = (er*(Fraction(2,3)-Fraction(2,31))+Fraction(2,31))**2
    for x in values:k.step(float(x))
    assert k.alpha == pytest.approx(float(expected),rel=2e-15)
    assert k.history[-1] == 1e308


def test_bad_batch_cannot_leave_an_unreturned_prefix_in_filter_state():
    f = EMA(.3, initialization='zero')
    with pytest.raises(ValueError):f.process([1,math.nan])
    assert f.value == 0 and f.updates == 0
    p = EMAPipeline(alpha=AdaptiveAlpha(.1,.8,max_delta=.2),initialization='first',max_skip=2)
    with pytest.raises(ValueError):p.process([1,2],[0,math.nan])
    assert p.events == 0 and p.filter.value is None and p.controller.value is None


def test_single_event_failure_rolls_back_every_state():
    p = EMAPipeline(alpha=AdaptiveAlpha(.1,.8,max_delta=.2),initialization='first',max_skip=2)
    before = (p.controller.value,p.shedder.since,p.filter.value,p.filter.updates,p.events)
    with patch.object(p.filter,'step',side_effect=ArithmeticError('disclosed fault fixture')):
        with pytest.raises(ArithmeticError):p.step(3,1)
    assert (p.controller.value,p.shedder.since,p.filter.value,p.filter.updates,p.events) == before
    assert p.step(3,1).output == 3


def test_effective_recurrence_weight_distinguishes_startup_hold_and_update():
    p=EMAPipeline(alpha=.25,initialization='first',max_skip=2)
    rows=p.process([4,8,12,16],[1]*4)
    assert [r.effective_beta for r in rows]==[1,0,0,.25]
    assert [r.alpha for r in rows]==[.25]*4
    previous=0
    for x,r in zip([4,8,12,16],rows):
        previous=(1-r.effective_beta)*previous+r.effective_beta*x
        assert r.output==previous


def test_batch_derived_failure_rolls_back_a_successful_prefix():
    k=KAMA(period=2,fast_period=2,slow_period=30,initialization='first')
    original=k.filter.step
    calls=0
    def fail_second(x,**kwargs):
        nonlocal calls
        calls+=1
        if calls==2:raise ArithmeticError('disclosed fault fixture')
        return original(x,**kwargs)
    with patch.object(k.filter,'step',side_effect=fail_second):
        with pytest.raises(ArithmeticError):k.process([1,2])
    assert k.filter.value is None and k.filter.updates==0 and not k.history and k.alpha is None


def test_mad_even_median_does_not_overflow_on_identical_residuals():
    s = CausalResidualScore(window=2,min_history=2,scale_floor=.1,estimator='mad')
    s.step(1e308);s.step(1e308)
    assert s.step(1e308) == 0


def test_event_censoring_has_separate_denominators():
    m = event_metrics([(1,2),(8,10)],[1],horizon_s=2,evaluation_start_s=0,evaluation_end_s=10)
    assert m['event_recall'] == .5 and m['event_recall_fully_observed'] == 1
    assert m['right_censored_unmatched_count'] == 1 and m['misses'] == 1
    assert m['fully_observed_misses'] == 0
    with pytest.raises(ArithmeticError):
        event_metrics([],[0],horizon_s=0,evaluation_start_s=0,evaluation_end_s=1e-320)


def test_no_alerts_exposes_undefined_precision_and_actual_misses():
    m=point_metrics([0,1],[0,0],threshold=1)
    assert m['precision'] is None and m['precision_status']=='undefined_no_positive_predictions'
    assert m['fn']==1 and m['f1']==0 and m['recall']==0


def test_positive_service_cannot_be_reported_as_zero_sojourn():
    with pytest.raises(ArithmeticError,match='relative times'):
        fcfs_schedule([1e20],[1])


def test_t_interval_near_one_confidence_uses_upper_tail():
    confidence = math.nextafter(1,0)
    m = paired_t_summary({'a':1,'b':3},{'a':0,'b':0},confidence=confidence)
    critical = t.isf((1-confidence)/2,1)
    assert m['ci'] == pytest.approx([2-critical,2+critical])
    assert all(math.isfinite(x) for x in m['ci'])


def test_paired_large_equal_means_and_invalid_identity():
    m = paired_t_summary({'a':1e308,'b':1e308},{'a':0,'b':0},confidence=.95)
    assert m['effect'] == 1e308 and m['status'] == 'degenerate_variance'
    with pytest.raises(ValueError):paired_t_summary({1:1,2:2},{1:0,2:0},confidence=.95)


def test_paired_standard_error_underflow_refuses_inference():
    # Nonzero representable dispersion can still underflow after sqrt(n).
    a = {'a':0.0,'b':0.0,'c':1e-323,'d':1e-323}
    with pytest.raises(ArithmeticError,match='standard error'):
        paired_t_summary(a,dict.fromkeys(a,0.0),confidence=.95)


def fixture_manifest(tmp_path):
    original = json.loads((Path(__file__).parents[2]/'data/acquisition_manifest.json').read_text())
    obj = copy.deepcopy(original)
    row = obj['records'][0]
    obj['records'] = [row]
    obj['expected_record_count'] = 1
    obj['selection'] = {'symbols':[row['symbol']], 'start_utc_date':row['utc_date'],'end_utc_date':row['utc_date']}
    path = tmp_path/'manifest.json'
    path.write_text(json.dumps(obj))
    return path,obj


@pytest.mark.parametrize('mutation',['empty','duplicate','wrong_unit','wrong_url','wrong_label','bad_checksum','missing_frame'])
def test_manifest_rejects_missing_or_inconsistent_units(tmp_path,mutation):
    path,obj = fixture_manifest(tmp_path)
    if mutation=='empty':obj['records']=[]
    if mutation=='duplicate':obj['records']*=2
    if mutation=='wrong_unit':obj['records'][0]['timestamp_unit']='us'
    if mutation=='wrong_url':obj['records'][0]['url']='http://invalid.example/source'
    if mutation=='wrong_label':obj['records'][0]['labels']='anomaly'
    if mutation=='bad_checksum':obj['records'][0]['provider_checksum_text']='0'*64+' wrong.zip'
    if mutation=='missing_frame':obj.pop('selection')
    path.write_text(json.dumps(obj))
    with pytest.raises(ValueError):read_acquisition_manifest(path)


def test_duplicate_json_key_and_infinite_number_are_rejected(tmp_path):
    path = tmp_path/'manifest.json'
    for text in ['{"schema_version":1,"schema_version":1}','{"v":1e999}']:
        path.write_text(text)
        with pytest.raises(ValueError):read_acquisition_manifest(path)


def test_failed_request_retains_attempt_even_before_response(tmp_path):
    path,_ = fixture_manifest(tmp_path)
    dest = tmp_path/'raw'
    with patch('urllib.request.urlopen',side_effect=OSError('disclosed offline fixture')):
        with pytest.raises(OSError):list(reconstruct(path,dest))
    receipts = list(dest.rglob('receipt.json'))
    assert len(receipts)==1
    assert json.loads(receipts[0].read_text())['status']=='FAILED_RETAINED'
    assert len(list(dest.rglob('archive.partial')))==1
    assert not list(dest.glob('*.zip'))


def test_atomic_publish_retains_raced_target(tmp_path):
    path,obj = fixture_manifest(tmp_path)
    payload = b'test bytes only; not an archive or scientific data'
    sample = tmp_path/'sample';sample.write_bytes(payload)
    digest = sha256_file(sample)
    obj['records'][0]['sha256']=digest
    name = Path(obj['records'][0]['path']).name
    obj['records'][0]['provider_checksum_text']=digest+' '+name
    path.write_text(json.dumps(obj))
    dest = tmp_path/'raw'
    def raced_link(source,target):
        Path(target).write_bytes(b'concurrent file fixture')
        raise FileExistsError('raced target fixture')
    with patch('urllib.request.urlopen',return_value=io.BytesIO(payload)),patch('os.link',side_effect=raced_link):
        with pytest.raises(FileExistsError):list(reconstruct(path,dest))
    assert (dest/name).read_bytes()==b'concurrent file fixture'
    assert list(dest.rglob('archive.partial'))[0].read_bytes()==payload


def test_invalid_manifest_fails_before_destination_or_network(tmp_path):
    path,_=fixture_manifest(tmp_path);path.write_text('{}')
    with patch('urllib.request.urlopen') as request:
        with pytest.raises(ValueError):list(reconstruct(path,tmp_path/'raw'))
        request.assert_not_called()
    assert not (tmp_path/'raw').exists()
