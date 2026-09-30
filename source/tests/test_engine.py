"""Mathematical/operator fixtures, never empirical research evidence."""
import math
import itertools
import numpy as np
import pytest
from scipy import signal
from sklearn.metrics import roc_auc_score, average_precision_score

from flowgate import (EMA, AdaptiveAlpha, KAMA, ButterworthSOS, EMAPipeline,
                      StrideShedder, CausalResidualScore, point_metrics,
                      event_metrics, pareto_mask, fcfs_schedule)
from flowgate.filters import frozen_ema_cutoff_radians, frozen_ema_dc_delay
from flowgate.statistics import paired_t_summary, holm_adjust


@pytest.mark.parametrize("alpha", [.02, .06, .3, 1.0])
def test_zero_state_impulse_matches_closed_form(alpha):
    x = [1.0] + [0.0] * 30
    y = EMA(alpha, initialization="zero").process(x)
    np.testing.assert_allclose(y, [alpha * (1-alpha)**n for n in range(len(x))], atol=1e-15)


def test_step_startup_and_empty_input_are_explicit():
    cold = EMA(.25, initialization="zero")
    assert cold.process([]) == [] and cold.updates == 0
    np.testing.assert_allclose(cold.process([1.0]*10), [1-.75**(n+1) for n in range(10)])
    assert EMA(.25, initialization="first").process([1.0]*10) == [1.0]*10


def test_fixed_ema_matches_independent_scipy():
    x = np.sin(np.arange(200)*.37)
    np.testing.assert_allclose(EMA(.3, initialization="zero").process(x),
                               signal.lfilter([.3], [1, -.7], x), atol=1e-14)


def test_event_chunking_preserves_filter_and_controller_state():
    x = [math.sin(i*.4) for i in range(120)]
    load = [(i%7)/6 for i in range(120)]
    def pipeline():
        return EMAPipeline(alpha=AdaptiveAlpha(.03, .4, max_delta=.02), initialization="zero", max_skip=4)
    a, b = pipeline(), pipeline()
    expected = a.process(x, load)
    observed = b.process(x[:19], load[:19]) + b.process(x[19:], load[19:])
    assert observed == expected
    assert b.filter.updates == sum(row.processed for row in observed)
    assert all(row.output == observed[i-1].output for i, row in enumerate(observed) if not row.processed)


@pytest.mark.parametrize("skip", [0, 1, 4, 8])
def test_stride_bounds_and_exact_constant_load(skip):
    s = StrideShedder(max_skip=skip)
    kept = [i for i in range(100) if s.step(1)]
    assert kept == list(range(0, 100, skip+1))
    s = StrideShedder(max_skip=skip)
    assert all(s.step(0) for _ in range(20))


def test_adaptive_bounds_and_slew_have_no_hidden_alpha_clip():
    a = AdaptiveAlpha(.001, .7, max_delta=.015)
    values = [a.step(x) for x in [0, 1]*100]
    assert all(.001 <= x <= .7 for x in values)
    assert max(abs(y-x) for x, y in zip(values, values[1:])) <= .015 + 1e-15
    assert AdaptiveAlpha(1e-7, .3, max_delta=.1).step(1) == pytest.approx(1e-7)


@pytest.mark.parametrize("bad", [float('nan'), float('inf'), -.01, 1.01, True])
def test_invalid_load_rejected(bad):
    with pytest.raises(ValueError):
        AdaptiveAlpha(.02, .3, max_delta=.01).step(bad)


@pytest.mark.parametrize("bad", [0, -1, 1.01, True, float('nan')])
def test_invalid_alpha_rejected(bad):
    with pytest.raises(ValueError):
        EMA(bad, initialization="zero")


def test_bounded_ltv_convexity_and_loss_of_initial_condition():
    a = AdaptiveAlpha(.05, .8, max_delta=.4)
    f = EMA(.1, initialization="zero")
    for i in range(300):
        assert abs(f.step(math.sin(i), alpha=a.step(i%2))) <= 1 + 1e-15
    first, second = EMA(.1, initialization="zero"), EMA(.1, initialization="zero")
    second.value = 1
    for n in range(20):
        alpha = .1 if n%2 else .2
        first.step(0, alpha=alpha)
        second.step(0, alpha=alpha)
    assert second.value == pytest.approx(.9**10 * .8**10)


def test_kama_warmup_and_efficiency_coefficient():
    k = KAMA(period=3, fast_period=2, slow_period=30, initialization="zero")
    assert k.step(2) == pytest.approx(2*(2/31)**2)
    assert k.alpha == pytest.approx((2/31)**2)
    k.step(3); k.step(4); k.step(5)
    assert k.alpha == pytest.approx((2/3)**2)


def test_butterworth_matches_reference_and_chunks():
    x = np.cos(np.arange(101)*.3)
    kwargs = dict(order=4, cutoff_hz=10, fs_hz=100, initialization="zero")
    f = ButterworthSOS(**kwargs)
    y = np.r_[f.process(x[:7]), f.process(x[7:])]
    expected = signal.sosfilt(signal.butter(4, 10, fs=100, output='sos'), x)
    np.testing.assert_allclose(y, expected, atol=1e-14)
    _, h = signal.sosfreqz(f.sos, worN=[10], fs=100)
    assert abs(h[0]) == pytest.approx(1/math.sqrt(2), rel=1e-12)
    warm = ButterworthSOS(**{**kwargs, 'initialization':'first'})
    np.testing.assert_allclose(warm.process([40000.0]*50), [40000.0]*50, rtol=1e-12)
    assert len(warm.process([])) == 0


def test_frozen_cutoff_and_delay_match_scipy():
    a = .3
    w = frozen_ema_cutoff_radians(a)
    _, h = signal.freqz([a], [1, -(1-a)], worN=[w])
    assert abs(h[0]) == pytest.approx(1/math.sqrt(2))
    _, d = signal.group_delay(([a], [1, -(1-a)]), w=[0])
    assert frozen_ema_dc_delay(a) == pytest.approx(d[0])
    assert frozen_ema_cutoff_radians(1) is None
    assert frozen_ema_cutoff_radians(.99) is None


@pytest.mark.parametrize("estimator", ['std', 'mad'])
def test_score_is_causal_and_warmup_is_missing(estimator):
    kwargs = dict(window=4, min_history=3, scale_floor=.1, estimator=estimator)
    a, b = CausalResidualScore(**kwargs), CausalResidualScore(**kwargs)
    prefix = [1., 2., 1., 2., 1.]
    scores = [a.step(x) for x in prefix]
    assert scores[:3] == [None]*3
    other = [b.step(x) for x in prefix]
    b.step(1e9)
    assert other == scores
    assert a.step(100) > 100
    with pytest.raises(ValueError):
        CausalResidualScore(**{**kwargs, 'estimator':'unknown'})


def test_rank_metrics_exhaustive_ties_against_distinct_library_path():
    y = [0, 0, 1, 1]
    for scores in itertools.product([0., 1., 2.], repeat=4):
        m = point_metrics(y, scores, threshold=1)
        assert m['auroc'] == pytest.approx(roc_auc_score(y, scores), abs=1e-14)
        assert m['average_precision'] == pytest.approx(average_precision_score(y, scores), abs=1e-14)


def test_nearby_false_alert_does_not_become_point_true_positive():
    y, scores = [0, 1, 0], [10., 0., 0.]
    m = point_metrics(y, scores, threshold=5)
    assert m['tp'] == 0 and m['fp'] == 1 and m['recall'] == 0
    assert m['auroc'] == .25


def test_event_misses_false_alerts_and_censoring_are_visible():
    m = event_metrics([(1, 1), (4, 5), (9, 10)], [0, 1.2, 1.3, 6.1],
                      horizon_s=1, evaluation_start_s=0, evaluation_end_s=10)
    assert m['hits'] == 1 and m['misses'] == 2 and m['false_alerts'] == 3
    assert m['events'][1]['latency_s'] is None
    assert m['events'][2]['window_right_censored']
    assert m['mean_latency_detected_s'] == pytest.approx(.2)
    assert m['event_recall'] == pytest.approx(1/3)


def test_one_alert_cannot_match_two_overlapping_events():
    m = event_metrics([(1, 2), (1.5, 2.5)], [1.7], horizon_s=0,
                      evaluation_start_s=0, evaluation_end_s=3)
    assert m['hits'] == 1 and m['misses'] == 1


def test_exact_fcfs_waiting_times_and_idle_periods():
    rows = fcfs_schedule([0, .5, 1, 4], [1, 1, 1, 1])
    assert [r.start_s for r in rows] == [0, 1, 2, 4]
    assert [r.wait_s for r in rows] == [0, .5, 1, 0]
    assert [r.sojourn_s for r in rows] == [1, 1.5, 2, 1]
    light = fcfs_schedule(range(20), [.1]*20)
    assert all(r.wait_s == 0 for r in light)
    overload = fcfs_schedule([i*.1 for i in range(20)], [1]*20)
    assert overload[-1].wait_s > overload[0].wait_s


def test_drops_keep_identity_and_never_count_as_completions():
    rows = fcfs_schedule([0, 0, .1], [1, 1, 1], admitted=[True, False, True])
    assert rows[1].finish_s is None and rows[2].start_s == 1
    assert [r.event_index for r in rows] == [0, 1, 2]
    with pytest.raises(ValueError): fcfs_schedule([1, 0], [1, 1])
    with pytest.raises(ValueError): fcfs_schedule([0], [-1])


def test_pairing_missing_unit_fails_and_degenerate_is_not_significant():
    with pytest.raises(ValueError):
        paired_t_summary({'a':.1, 'b':.2}, {'a':.1, 'c':.2}, confidence=.95)
    m = paired_t_summary({'a':.1, 'b':.2}, {'a':.1, 'b':.2}, confidence=.95)
    assert m['status'] == 'degenerate_variance' and m['p_two_sided'] is None
    m = paired_t_summary({'a':.1, 'b':.4, 'c':.9}, {'a':.2, 'b':.3, 'c':.8}, confidence=.95)
    assert m['ci'][0] < m['effect'] < m['ci'][1]
    assert holm_adjust([.01, .04, .03]) == pytest.approx([.03, .06, .06])


def test_pareto_ties_incomparable_and_identical():
    assert pareto_mask([[1, 2], [1, 1], [2, 1], [1, 2]]) == [True, False, True, True]
    with pytest.raises(ValueError): pareto_mask([[float('nan'), 1]])


def test_tiny_frozen_cutoff_does_not_round_to_zero():
    assert frozen_ema_cutoff_radians(1e-12) == pytest.approx(1e-12, rel=1e-10, abs=0)
    with pytest.raises(ArithmeticError): frozen_ema_dc_delay(5e-324)


def test_numpy_integer_labels_retain_exact_point_semantics():
    m = point_metrics(np.array([0, 1], dtype=np.int64), [0., 1.], threshold=.5)
    assert m['auroc'] == 1 and m['tp'] == 1
    with pytest.raises(ValueError): point_metrics([False, True], [0., 1.], threshold=.5)


def test_scale_overflow_cannot_become_a_zero_anomaly_score():
    score = CausalResidualScore(window=2, min_history=2, scale_floor=.1, estimator='mad')
    score.step(-1.7e308); score.step(1.7e308)
    with pytest.raises(ArithmeticError): score.step(0.)
    # Large equal finite values need not overflow a valid sample mean.
    score = CausalResidualScore(window=2, min_history=2, scale_floor=.1, estimator='std')
    score.step(1e308); score.step(1e308)
    assert score.step(1e308) == 0


def test_queue_and_statistics_reject_overflowed_derived_values():
    with pytest.raises(ArithmeticError):
        fcfs_schedule([-1.7e308, -1e308], [1.7e308, 1.7e308])
    with pytest.raises(ArithmeticError):
        paired_t_summary({'a':1.7e308,'b':1.7e308}, {'a':-1.7e308,'b':0.}, confidence=.95)


def test_numerically_unresolvable_confidence_is_not_an_infinite_interval():
    with pytest.raises(ArithmeticError):
        paired_t_summary({'a':1.,'b':3.}, {'a':0.,'b':0.}, confidence=np.nextafter(1.,0.))


def test_full_load_preserves_an_extremely_small_positive_alpha_min():
    controller = AdaptiveAlpha(1e-20, .3, max_delta=.1)
    assert controller.step(1) == 1e-20
    assert controller.step(0) == pytest.approx(.1)
