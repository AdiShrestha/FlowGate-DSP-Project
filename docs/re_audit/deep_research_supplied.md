# FlowGate DSP: critical research assessment and implementation-ready specification

## Candid assessment and evidence boundary

**Overall assessment.** FlowGate is moving toward a meaningful research question, but the scientifically defensible contribution is narrower than “adaptive filtering saves compute under load.” The present first-order adaptive EMA changes a coefficient while still performing an \(O(1)\) filter update; by itself, that coefficient change does not eliminate meaningful work. The credible systems-level compute-saving mechanism is **admission/load shedding**. The credible scientific question is therefore whether load-driven coefficient adaptation adds enough *quality* benefit, conditional on a comparable admission policy and resource budget, to justify its extra controller complexity and any changes it makes to signal semantics. That distinction should become the center of the research program.

A stronger formulation is:

> **Conditional mechanism question:** Under identical offered workloads and identical admission decisions, does causal load-driven coefficient adaptation reduce the quality degradation caused by overload relative to a validation-tuned fixed EMA, by a practically meaningful amount?

followed by:

> **Closed-loop systems question:** When admission and filtering run causally in a measured bounded-queue system, does adaptive filtering plus admission improve useful completed work under a declared quality and physical-latency requirement relative to strong fixed-filter admission policies?

The first question isolates the coefficient mechanism. The second asks whether that mechanism survives contact with the real system. If the first is negative, there is little scientific justification for claiming that adaptive \(\alpha\) is a resource-saving mechanism. If the first is positive but the second is negative because controller overhead or queue interactions erase the advantage, that is also a valuable result.

This framing is important because adaptive and variable-step filtering have a long history, including variable-step NLMS and set-membership methods; in some prior work, computational savings arise because adaptation explicitly causes updates to cease, not merely because the numerical value of a coefficient changes. citeturn16search0turn16search5 Likewise, overload-driven tuple dropping, quality-aware shedding, queue/latency-aware shedding, and importance-aware shedding are established stream-processing topics. citeturn21search2turn27search0turn21search0turn18view3 Consequently, a broad novelty claim such as “resource-aware adaptive filter plus shedding” would presently be weak. A more plausible contribution is a careful **mechanistic decomposition** of filtering versus admission, backed by a real measured system, explicit time-varying operator analysis, dependence-aware inference, and a result that may be positive, negative, or conditional.

### Materials I could and could not inspect

I directly inspected the uploaded `plan.md`. It is an extensive forensic audit and rehabilitation document asserting, among other things, that legacy results are quarantined; that no repaired empirical superiority claim currently exists; that current numerical code is a correctness-oriented foundation; and that a streaming runtime, domain adapter, prospective study population, and confirmatory evidence remain unfinished. I treat those statements as **audit assertions**, not independently verified facts. fileciteturn0file0

I also unpacked and source-inspected the uploaded `source.zip`. I was able to read:

`source/flowgate/__init__.py`, `acquisition.py`, `filters.py`, `metrics.py`, `queue.py`, `scoring.py`, `shedding.py`, `statistics.py`, `validation.py`; `source/acquire_archives.py`; `source/tests/test_engine.py`, `test_acquisition.py`, `test_real_archive.py`; `source/pyproject.toml`; and the three supplied requirements lock files. I did **not** execute that code, run the test suite, reproduce an experiment, benchmark the M3 machine, or verify the reported 52-test count. My code comments below are therefore source-level observations, not runtime certification.

The repaired snapshot contains several good design choices. The EMA has explicit zero-state versus first-observation initialization; adaptive \(\alpha\) is bounded with an event-domain slew limit; KAMA explicitly states its update clock; Butterworth is causal SOS filtering and requires a uniform grid; residual scoring uses prior history rather than the current residual; point AUROC/AP are kept separate from event matching; FCFS scheduling is explicitly labeled a **model** rather than telemetry; and paired statistics require exact unit identities rather than truncating mismatched rows. Those are sound foundations, but they are primitives, not evidence that a research claim is true.

Two source-level details deserve particular attention. First, `StrideShedder` always admits its first event and thereafter follows a deterministic phase locked to the run boundary, with `round(max_skip * load)` governing the event stride. That makes phase sensitivity a first-class experimental issue. Second, the current `queue.py` is a one-server unbounded FCFS algebraic scheduler; it is not yet the bounded physical queue, overflow policy, worker execution system, or completion telemetry needed for the proposed systems study.

The Binance parser's date rule—milliseconds before January 1, 2025 and microseconds from January 1, 2025—is consistent with Binance's current official public-data documentation, which also documents downloadable checksum files and notes that archived files can later be replaced following corrections. citeturn15search0turn15search1 That supports the parser rule, but it does not verify the 155 archived files, labels, sampling design, or old audit counts.

I could reach the public repository landing page through web access, but I could **not retrieve and inspect the exact rehabilitation baseline commit** `cbe9f3285b83a00f230841046226a64ed93fa78f` through the available browsing interface. I therefore do not claim to have audited that commit.

I did **not directly inspect** the separately named `README.md`, `data/acquisition_manifest.json`, `docs/flowgate_audit/`, `project/STATUS.json`, `project/research_plan.json`, `factory/AGENT_WORKFLOW.md`, or the active factory implementation, except to the extent their alleged contents are described in `plan.md`. In particular, all recommendations about the factory are specifications to verify against the real implementation, not claims that I inspected every factory branch or policy gate.

The most consequential unresolved issues are therefore:

| Issue | Current assessment | Consequence |
|---|---|---|
| What “quality” means independently of the preferred method | **Unresolved** | Without an external task or common reference, the primary comparison is underidentified. |
| Whether adaptive \(\alpha\) has a resource-saving mechanism beyond admission | **No credible mechanism yet** | Compute superiority cannot be assumed; controller work may make adaptive filtering slightly more expensive. |
| Actual bounded-queue streaming runtime | **Missing from inspected source** | No sustainable-throughput, latency, loss, or queue claim can yet be empirical. |
| Fresh confirmatory population | **Missing** | January 2024 Binance material is development/exploratory by the supplied history. |
| Independent anomaly truth | **Absent for Binance trades** | Natural anomaly-detection superiority cannot be tested on those trades without a separate label source. |
| Source-unit independence and dependence structure | **Unresolved empirically** | Repeated seeds cannot substitute for calendar/device/series units. |
| Factory DSP/streaming evidence adapter | **Not directly inspected; reported missing** | Factory certification is not scientifically meaningful until its schemas and applicability rules fit this domain. |
| Practical M3 timing, memory, energy, and thermal behavior | **Unmeasured** | No resource quantity should be preregistered as though known. |

The immediate scientific **go/no-go** decision is clear: **go** on a pilot and mechanism-validation program; **no-go** on confirmatory superiority claims, natural Binance anomaly claims, energy claims, or submission-oriented result production until the common task, measured runtime, independent units, and factory evidence contract exist.

## Related work and the plausible contribution boundary

The relevant literature does not make FlowGate pointless; it makes precision about the contribution essential. Adaptive coefficients are well established, irregular-time smoothing has prior art, and stream systems have used random, semantic, quality-aware, and queue-aware shedding for decades. What is less obviously settled is the exact cross-layer question FlowGate can test: **does manipulating a causal DSP coefficient in response to load add practical value after the effect of admission is isolated and real queue/runtime costs are included?**

### Evidence-backed related-work matrix

| Work | Task and available information | Mechanism / assumptions | Guarantee or evidence | Artifact status located | Relevance to FlowGate |
|---|---|---|---|---|---|
| Time-varying NLMS analysis, 1993 | Adaptive filtering with a time-varying learning step; analysis depends on a specified input model. | Varies adaptation step to accelerate convergence and control misadjustment. | Analytical convergence treatment plus examples under stated models. citeturn16search5 | Publisher record located; no FlowGate-specific artifact implication. | Establishes that variable coefficients/steps are not novel per se and that claims depend on signal/statistical assumptions. |
| Set-membership normalized LMS, 1998 | Adaptive linear-in-parameters filtering with an error/set-membership criterion. | Variable step plus selective updating; updates can asymptotically cease. | Paper establishes properties including non-increasing parameter error and reports substantially fewer updates in simulations. citeturn16search0 | IEEE paper record located. | Important contrary comparator: **compute savings require a mechanism that skips updates**. Merely changing EMA \(\alpha\) does not provide this. |
| Piwowar & Grabowski, 2017, first-order time-varying filters | Analysis of first-order LTV filters with periodically varying parameters. | Uses LTV impulse-response/time-domain formulation rather than treating the system as an ordinary LTI transfer function. | Derives LTV responses and explicitly distinguishes LTV description from the direct LTI transfer-function route. citeturn18view6 | Publisher full HTML located. | Supports FlowGate's need to separate a frozen-\(\alpha\) diagnostic from actual time-varying behavior. |
| Cipra & Hanzák, 2008, irregular exponential smoothing | Forecasting/smoothing with irregular observations. | Extends exponential-smoothing methods to nonuniform timing and estimates parameters for irregular data. | Simulation comparison against existing irregular-time methods. citeturn18view5 | Journal page and paper available. | Shows that treating event index as physical time is not the only established approach; elapsed-time-aware competitors are needed. |
| Tatbul et al., Aurora load shedding, 2002/2003 | Push-based streams with standing queries and QoS; overload observable through system state. | Dynamically inserts/removes drop operators; random and content-sensitive dropping; chooses when, where, and how much to shed. | Prototype/simulation evidence aimed at restoring useful latency under overload. citeturn21search2turn21search8 | Brown/MIT author-hosted records available. | Directly weakens novelty of “shed under overload”; motivates random and importance-aware controls. |
| Babcock, Datar & Motwani, ICDE 2004 | Continuous aggregation queries under bursty input. | Places sampling/drop operators and allocates shedding to minimize answer inaccuracy while meeting capacity. | Analytical treatment plus experimental validation. citeturn27search0 | Stanford primary publication page available. | Close antecedent for “quality/compute tradeoff under shedding.” FlowGate must show a DSP-specific mechanism, not rediscover approximate stream processing. |
| Rivetti, Busnel & Querzoni, LAS | Stream-processing overload when tuple execution durations are not known a priori. | Sketch-based execution-time estimation and proactive dropping to constrain queue latency while minimizing drops. | The published description reports an \((\epsilon,\delta)\)-approximation result and prototype/simulation evaluation. citeturn21search0 | Institutional primary record and Springer publication identified. | A close queue-aware competitor. A FlowGate queue controller weaker than a simple latency/backlog-aware policy may not warrant a systems claim. |
| eSPICE, Slo et al., 2020 | Complex-event processing where event usefulness depends on type/position and surrounding pattern. | Learns probabilistic event importance; decides when and how much to drop. | Evaluated on two real-world datasets; ACM publication DOI linked from the authors' preprint. citeturn18view3 | Paper source located; code availability was not established from the source consulted. | Demonstrates quality/importance-aware shedding; FlowGate's deterministic stride should not be called quality-aware unless it actually models task importance. |
| Fiscato, quality-aware overload management | Continuous stream processing under scarce resources. | Tracks a source-coverage quality measure and uses it for shedding/resource allocation. | Thesis reports experimental quality-aware shedding results. citeturn21search3 | Open institutional thesis record. | Shows that “quality-aware overload control” is established terminology and prior art. |
| Guha et al., RRCF, ICML 2016 | Dynamic streaming anomaly detection. | Maintains random-cut-forest sketch and scores points through their effect on the maintained structure. | Efficient dynamic updating and experiments on publicly available real data. citeturn24view0 | PMLR paper and supplement available. | Appropriate causal detection baseline when a streaming anomaly task is actually justified. It should be charged its full runtime cost. |
| Siffer et al., SPOT, KDD 2017 | Online univariate thresholding/outlier detection. | Extreme-value-based adaptive thresholding with a risk parameter rather than hand-set score thresholds. | Real-data experiments reported by the original conference page. citeturn24view1 | ACM/KDD paper link located. | Useful low-complexity causal thresholding competitor; also highlights that filter quality and detector-threshold quality are separate mechanisms. |
| DAMP, Lu et al., 2022/2023 | Online subsequence anomaly/discord detection at high arrival rates. | Computes left-discords using matrix-profile-related pruning for streams. | Authors report exact online discord search and very high processing rates on commodity hardware; the paper and code-supporting page exist. citeturn26search0turn26search2turn26search3 | Code/supporting materials identified by authors. | A more contemporary efficient TSAD comparator for suitable subsequence tasks; it is not automatically appropriate for point-residual detection. |
| Kim et al., AAAI 2022 | Evaluation methodology for time-series anomaly detection. | Studies point adjustment and alternative evaluation conventions. | Shows theoretically/experimentally that point adjustment can drastically overstate performance, even elevating random scores. citeturn18view2 | Official AAAI article available. | Directly supports strict separation of point metrics from event matching and argues against repaired “tolerance” denominators. |
| NAB | Streaming anomaly benchmark with real-time-oriented scoring. | Contains labeled anomaly windows and an online benchmark framework. | The official repository explicitly says the corpus contains both **real-world and artificial** series. citeturn24view3 | Full repository; MIT license. citeturn15search3 | Potential external task, but artificial and natural series must be stratified/disclosed. Its native scoring should not silently replace FlowGate's preregistered strict metrics. |
| SMAP/MSL Telemanom data, Hundman et al., 2018 | Spacecraft telemetry anomaly detection. | LSTM prediction errors plus dynamic thresholding; labels created with spacecraft-domain expertise. | NASA states the study used **expert-labeled** SMAP and MSL telemetry anomaly data. citeturn24view2 | Public Telemanom repository; permissive Caltech/JPL redistribution conditions. citeturn15search4turn15search5 | Strong candidate for an externally labeled natural operational task, though domain, multivariate structure, sampling, and label uncertainty differ from market trades. |
| Mytkowicz et al., ASPLOS 2009 | Systems performance measurement. | Examines experimental setup bias; advocates causal analysis and setup randomization. | Demonstrates that seemingly benign setup choices can reverse performance conclusions. citeturn19search0 | IBM author/publisher record. | Strong justification for randomized/interleaved execution order rather than benchmarking all of one method and then another. |
| Georges et al., OOPSLA 2007; Kalibera & Jones, ISMM 2013 | Repeated systems/runtime benchmarking under noisy execution. | Explicit repeated measurements and hierarchical sources of runtime variation. | Both works emphasize uncertainty and statistically rigorous repetition. citeturn19search2turn19search3 | Institutional full-text records. | Supports separating warmup, within-process repetitions, process/session blocks, and population units. |
| Politis & Romano, JASA 1994 | Statistical inference for weakly dependent stationary observations. | Resamples random-length blocks rather than individual observations. | Stationary bootstrap developed for confidence inference under weak stationary dependence. citeturn28search0 | Official journal record. | Useful only when its stationarity/dependence assumptions are defensible; it is not a license to treat arbitrary financial ticks as independent. |

### What is and is not plausibly novel

**Not plausibly novel by itself:** a variable first-order coefficient; an EMA whose coefficient depends on a control signal; load shedding when queues are overloaded; deterministic subsampling; anomaly scoring after smoothing; or frozen-pole analysis. The literature above contains much stronger antecedents in each individual area. citeturn16search0turn18view6turn21search2turn21search0

**Potentially publishable:** a carefully isolated finding about the *interaction* of DSP state adaptation and overload admission that prior stream-shedding work generally does not study as a signal-operator question. Specifically, FlowGate could contribute:

1. an exact analysis of the admitted-update first-order operator, including initialization, forgetting, skipped-update error, event-versus-physical clocks, and the conditions under which frozen-frequency intuition fails;
2. a real measured streaming system that cleanly decomposes admission benefit from coefficient-adaptation benefit;
3. a reproducible experimental framework showing where adaptive \(\alpha\) helps, does nothing, or hurts under controlled overload;
4. a negative finding, if well supported, that **simple admission plus a well-tuned fixed filter captures essentially all practical benefit**, with a characterization of the regimes in which coefficient adaptation becomes unnecessary or harmful.

The fourth outcome may actually be more scientifically distinctive than a weak positive result. SIGMOD explicitly accepts Experiment & Analysis work whose contribution is new insight into strengths and weaknesses rather than a new method, provided the work genuinely concerns data-management phenomena. citeturn17view1 PVLDB likewise has an Experiment, Analysis & Benchmark category with strong artifact requirements. citeturn18view0

The main competing explanation you must actively test is:

> **All apparent FlowGate benefit is caused by dropping work, while adaptive \(\alpha\) changes signal quality but contributes no capacity benefit.**

Other serious competing explanations are that deterministic stride happens to align favorably with the evaluated signal; fixed EMA was undertuned; adaptive configurations have more tuning degrees of freedom; coefficient changes alter detection thresholds rather than signal quality; startup/warmup differences drive the apparent result; source-day reuse makes uncertainty too small; or model-derived capacity is being mistaken for measured useful throughput.

## Mathematical and operator semantics

The repaired source is much closer to a mathematically defensible operator than the legacy description reported in the audit. The key is to analyze **the actual admitted-update operator**, not just the ordinary fixed EMA.

Let

\[
k_n\in\{0,1\}
\]

be the admission indicator, and let \(0<\alpha_n\le 1\) be the coefficient produced by the controller on ingress event \(n\). Once initialization has occurred, the implementation is equivalent to

\[
y_n =
\begin{cases}
\alpha_n x_n +(1-\alpha_n)y_{n-1}, & k_n=1,\\[3pt]
y_{n-1}, & k_n=0.
\end{cases}
\]

Defining

\[
\beta_n=k_n\alpha_n,
\]

this becomes

\[
\boxed{
y_n=(1-\beta_n)y_{n-1}+\beta_n x_n
}
\]

with \(0\le \beta_n\le 1\).

That representation is particularly useful because it makes both holding and filtering part of one LTV recurrence.

### Boundedness, forgetting, and the limits of the proof

**Established proof, conditional on the declared sequence.** If \(|x_n|\le M\) and \(|y_{-1}|\le B\), then because each update is either a convex combination of \(x_n\) and \(y_{n-1}\) or an exact hold,

\[
|y_n|\le \max(M,B)
\]

for every \(n\). No slew-rate bound is needed for that bounded-state result. It follows directly from \(0\le\beta_n\le1\).

For two trajectories driven by the **same inputs and the same exogenous coefficient/admission sequence**,

\[
d_n=y_n-\tilde y_n
=(1-\beta_n)d_{n-1},
\]

so

\[
\boxed{
|d_n|
=
|d_{-1}|
\prod_{j=0}^{n}(1-\beta_j).
}
\]

Hence skipped events do not contract initial-state error, while admitted updates do. A simple sufficient condition for exponential forgetting in admitted-update count is \(\alpha_n\ge\alpha_{\min}>0\) on all admitted events:

\[
|d_n|\le |d_{-1}|(1-\alpha_{\min})^{N_{\rm admit}(n)}.
\]

This is **not** a physical-time forgetting guarantee. A system can go arbitrarily long without an admitted update unless interarrival and admission gaps are bounded.

More generally, the initial state is forgotten if

\[
\prod_n (1-\beta_n)\rightarrow0,
\]

which can hold under weaker conditions than a fixed positive lower bound. But this is still a property conditional on the realized sequence.

**What fails in an endogenous closed loop.** If queue state affects load, load affects \(\alpha_n\) and \(k_n\), and the queue state itself changes across the two trajectories being compared, then the two systems need not see the same \(\{\beta_n\}\). The simple difference recurrence no longer proves closed-loop contraction. Moreover, even if the numerical EMA state is bounded, the **queue can still be unstable or unbounded**. Filter boundedness is not queue stability, system stability, or sustainable throughput.

This distinction is consistent with the general LTV literature: time-varying systems require time-varying impulse-response descriptions rather than blindly importing an LTI transfer function. citeturn18view6

### Actual LTV kernel versus frozen frequency response

Under zero-state initialization and an exogenous sequence \(\beta_n\), the exact input-output kernel is

\[
\boxed{
h(n,j)=
\beta_j
\prod_{m=j+1}^{n}(1-\beta_m),\qquad n\ge j.
}
\]

Thus

\[
y_n=\sum_{j=0}^{n}h(n,j)x_j.
\]

This is linear conditional on the exogenous control/admission history, but generally **time-varying**. If admission or coefficients depend on signal-derived outputs, then the full input-to-output map can become nonlinear/endogenous.

For the special frozen case \(k_n=1\) and \(\alpha_n=\alpha\),

\[
H(z)=\frac{\alpha}{1-(1-\alpha)z^{-1}},
\]

and

\[
|H(e^{j\omega})|^2
=
\frac{\alpha^2}
{1+(1-\alpha)^2-2(1-\alpha)\cos\omega}.
\]

The DC group delay is

\[
\tau_g(0)=\frac{1-\alpha}{\alpha}
\]

samples, and the \(-3\) dB crossing, when it exists before Nyquist, satisfies

\[
\sin\frac{\omega_c}{2}
=
\frac{\alpha}{2\sqrt{1-\alpha}},
\]

or

\[
\omega_c=
2\arcsin\!\left(
\frac{\alpha}{2\sqrt{1-\alpha}}
\right).
\]

These are useful **frozen-coefficient diagnostics**. They are not the transfer function, cutoff, or group delay of the adaptive/held system. The LTV literature explicitly treats the lack of a direct ordinary LTI transfer-function description as fundamental. citeturn18view6

Consequently, “mean \(\alpha\) matches the bandwidth” is not a sufficient fairness condition. In particular,

\[
E\!\left[\frac{1-\alpha}{\alpha}\right]
\neq
\frac{1-E[\alpha]}{E[\alpha]}
\]

in general, and admission adds another time variation entirely.

### Error introduced by skipped updates

A particularly useful FlowGate-specific derivation compares a full-update reference

\[
v_n=\alpha_n x_n+(1-\alpha_n)v_{n-1}
\]

with the admitted/held approximation \(u_n\), assuming **the same exogenous \(\alpha_n\) sequence**.

Let

\[
e_n=u_n-v_n.
\]

For an admitted event,

\[
e_n=(1-\alpha_n)e_{n-1}.
\]

For a skipped event,

\[
e_n=e_{n-1}-(v_n-v_{n-1}).
\]

Therefore every skipped event injects exactly the negative increment that the full-rate reference would have made, and later admitted updates attenuate that error. Unrolling gives the useful bound

\[
\boxed{
|e_n|
\le
|e_{-1}|
\prod_{\substack{m\le n\\k_m=1}}(1-\alpha_m)
+
\sum_{\substack{j\le n\\k_j=0}}
|v_j-v_{j-1}|
\prod_{\substack{m=j+1\\k_m=1}}^{n}
(1-\alpha_m).
}
\]

This should become part of the theoretical contribution if the paper remains DSP-oriented. It states exactly what determines admission distortion: the variation of the full-rate reference during skipped intervals and the contraction supplied by subsequent admitted updates.

It also gives falsifiable predictions. For slowly varying reference output and frequent admitted updates, the held approximation should remain close. For high local variation or long skip runs, it can become poor. The experiment should plot empirical error against the bound-driving terms rather than merely comparing global averages.

The derivation is **not automatically valid for two different closed-loop policies** if their queue histories cause different \(\alpha_n\) trajectories. That is why the experimental program needs both a common-load/common-admission mechanism experiment and a full closed-loop experiment.

### Event-based versus physical-time adaptation

The inspected `AdaptiveAlpha` limits

\[
|\alpha_n-\alpha_{n-1}|\le \Delta_{\max}
\]

**per observed ingress event**. Therefore the maximum coefficient-change rate per second scales with event rate. At 100 events/s and 10,000 events/s, the same `max_delta` denotes radically different physical-time behavior.

A physical-time slew controller would instead require something like

\[
|\alpha_n-\alpha_{n-1}|
\le r_{\alpha}\Delta t_n
\]

for a coefficient-rate limit \(r_\alpha\) per second.

Similarly, irregular-time exponential smoothing has an established literature rather than being reducible to ordinary event-index EMA. Cipra and Hanzák specifically treat exponential smoothing with irregular observations. citeturn18view5 A common engineering elapsed-gap coefficient,

\[
\alpha(\Delta t)=1-e^{-\Delta t/\tau},
\]

can represent an elapsed-time-dependent first-order relaxation under a particular continuous-time/hold model. It should therefore be included as a **time-aware comparator**, not treated as an exact reconstruction of arbitrary omitted samples. It cannot recover information about values that were never processed.

### Deterministic admission, aliasing, and phase

The present stride policy is deterministic and phase locked. That creates an easy mathematical counterexample. Suppose a uniformly sampled input alternates

\[
x_n=(-1)^n.
\]

A policy that keeps every second event may retain only \(+1\) samples or only \(-1\) samples depending solely on its starting phase. Nothing about the average processing fraction reveals that failure.

In conventional uniform-rate DSP, reducing sampling rate changes spectral representation and requires proper anti-alias treatment; multirate filtering explicitly addresses the consequences of decimation. citeturn16search3 FlowGate's event-domain case is more general than textbook regular decimation, so “aliasing” should be used carefully, but the central experimental problem remains: **periodic deterministic selection is phase sensitive and can systematically erase or privilege structure**.

At minimum, evaluate:

- deterministic stride with the production phase;
- randomized initial phase;
- randomized Bernoulli/systematic admission at the same expected processing fraction;
- adversarial deterministic fixtures such as alternating sequences, narrow pulses, ramps, and periodic signals.

These fixtures are operator tests, not empirical evidence about markets.

### Elapsed-gap compensation

If several updates are skipped, one can sometimes derive a block-equivalent coefficient

\[
\alpha_{\rm block}
=
1-\prod_{j=1}^{m}(1-\alpha_j).
\]

But this is exact only when the same effective input is valid over that block under the assumed model. It does **not** reconstruct a sequence of arbitrary skipped \(x_j\) values. If the algorithm reads every supposedly skipped value to calculate the exact block effect, then those reads and arithmetic are part of the computational cost.

Elapsed-gap compensation is therefore a legitimate **separate ablation**, not a free theorem proving that skipped event processing is harmless.

### Claims, assumptions, and falsification matrix

| Candidate claim | Status now | Required assumptions/evidence | Direct falsification |
|---|---|---|---|
| The admitted EMA state is bounded | **Proof available** | \(0\le k_n\alpha_n\le1\), bounded inputs and initial state, real-arithmetic recurrence | A production path violates coefficient bounds or changes state on a “skipped” event contrary to the specification |
| Initial state is forgotten | **Conditional proof** | Product of \(1-k_n\alpha_n\) tends to zero; stronger exponential result if admitted \(\alpha\ge\alpha_{\min}>0\) | Indefinite hold intervals or coefficient sequences whose product does not vanish |
| Slew limiting is required for EMA boundedness | **False** | None | Convexity proof already establishes boundedness without slew |
| Frozen cutoff describes the adaptive operator | **False except locally/conditionally** | Constant coefficient, regular clock, no admission holds | Any coefficient/admission variation |
| A frozen response may be a useful diagnostic | **Conjecture / diagnostic** | Coefficient varies sufficiently slowly relative to relevant dynamics; approximation error demonstrated | Abrupt-load experiment where frozen prediction poorly tracks actual response |
| Event-based slew has a stable physical meaning across input rates | **False** | Would require fixed event rate or explicit conversion to elapsed time | Same load history replayed at substantially different ingress rates produces different coefficient-rate trajectories |
| Skipping error is controlled by reference variation and subsequent contraction | **Proof under common \(\alpha\) path** | Same exogenous \(\alpha_n\), same input, stated initialization | Closed-loop comparison changes coefficient path; empirical error violates implementation of derived recurrence |
| Deterministic stride is phase neutral | **False** | None | Alternating/periodic counterexample |
| Elapsed-gap compensation reconstructs arbitrary omitted data | **False** | Exactness requires a model of skipped input over the interval | Omitted high-frequency/pulse sequence produces different full-update result |
| Adaptive \(\alpha\) directly reduces EMA update compute | **No credible mechanism** | Would require update cessation, lower-order work, downstream-cost reduction, or another explicit mechanism | Fixed and adaptive variants execute same filtering path while adaptive additionally computes controller state |
| Adaptation improves quality at fixed admission | **Empirical hypothesis** | Identical admission mask/offered stream, fair validation-only tuning, independent quality definition | CI excludes the preregistered practically useful adaptive benefit |
| Adaptation improves useful end-to-end operation | **Empirical closed-loop hypothesis** | Real bounded queue, completion telemetry, common workload/resource limits, task-quality constraint | Fixed-filter/simple-admission policy matches or dominates useful throughput/latency-quality frontier |
| The overall endogenous queue/filter system is stable | **Unknown** | Defined controller, bounded queue policy, actual service process, workload assumptions; likely empirical plus control analysis | Persistent backlog/overflow/latency growth or oscillation under registered workloads |

## Recommended research direction, data strategy, baselines, and ablations

### Recommended primary direction

I recommend **not** making natural anomaly detection on Binance trades the primary paper. Those observations have no independently supplied anomaly truth, and the existing January 2024 corpus has already been inspected. Provider checksums establish byte identity, not anomaly labels, scientific independence, or untouched confirmatory status. Binance's official archive documentation confirms checksum availability and the trade-file schema but does not supply anomaly labels. citeturn15search0

The strongest direction is instead a **two-stage measured mechanism study**:

**Stage A — operator/mechanism study.** Compare fixed versus load-adaptive EMA using **identical precomputed admission masks and identical causal load traces**. This gives a clean estimate of whether coefficient adaptation itself changes quality under controlled skipped work.

**Stage B — closed-loop systems study.** Run the policies with a real bounded queue, measured workers, and causal controller state. Compare adaptive+admission to fixed+the-same-controller, fixed+simple queue controller, randomized admission, and no-shedding controls. This answers the deployment question.

The primary quality metric should be independent of whichever method happens to produce the result. There are two defensible choices:

1. **common-reference DSP fidelity**, where all approximate policies target the same prospectively declared full-rate operator or physical-time signal-processing objective; or
2. **external task utility**, such as anomaly-detection AP/event recall on an independently labeled dataset.

Do not choose a full-rate adaptive filter as the reference for the adaptive method and a full-rate fixed filter as the reference for the fixed method, then directly compare their “fidelity” scores as though they estimate the same quantity. They do not.

### What the three possible study types can establish

| Study | Best use | Can establish | Cannot establish |
|---|---|---|---|
| **Unlabeled fidelity/runtime** | Primary FlowGate mechanism/systems study | Approximation to an explicitly defined reference; physical latency; processing fraction; losses; runtime overhead; queue behavior; adaptation-versus-admission decomposition | “Real anomaly detection accuracy,” denoising against unknown latent truth, semantic event correctness |
| **Externally labeled detection** | Secondary application study or primary if detection is truly the target | Causal score ranking, point/event detection quality, degradation under overload, end-to-end alert latency | General market-anomaly claims unless the labels are market anomalies; universal correctness of benchmark annotations |
| **Explicit perturbation study** | Mechanism/failure characterization | Response to perturbations with known timing, amplitude, type, and causal placement; phase/skip sensitivity | Performance on naturally occurring anomalies or their prevalence; real-world false-positive behavior |

The cleanest paper may use **all three as separately labeled evidence tiers**, but never aggregate natural and artificial labels into one undifferentiated primary score.

### Candidate data sources

| Data | Label/source provenance | Grouping and causal suitability | Access / licensing | Main weakness |
|---|---|---|---|---|
| **Fresh Binance Spot trades** | Provider observational trades; no natural anomaly labels. Official archives expose trade IDs/timestamps and checksums. citeturn15search0 | Natural grouping by UTC day/symbol, with strong possibility of cross-asset/calendar dependence. Excellent for irregular arrival/replay/load studies. | Binance public-data repository is MIT-licensed; still document data redistribution/use terms separately from code licensing. citeturn15search0 | No external anomaly truth; market microstructure is domain-specific; already-inspected Jan 2024 data cannot be confirmatory. |
| **NASA/JPL SMAP and MSL telemetry** | NASA describes **expert-labeled telemetry anomaly data** from SMAP and the Curiosity rover. citeturn24view2 | Series/channel and mission anomaly episodes are natural grouping candidates. Causal detector evaluation is feasible if training/threshold selection respects chronology. | Public Telemanom repository; Caltech/JPL license permits redistribution subject to notice/endorsement conditions. citeturn15search4turn15search5 | Labels are still expert judgments, not infallible truth; multivariate spacecraft telemetry differs greatly from financial trades. |
| **NAB** | Official repo has labeled real-world **and artificial** time series. citeturn24view3 | Designed for streaming evaluation; source series should be the grouping unit, not individual timestamps. | Repository has a permissive MIT license. citeturn15search3 | Mixed-origin corpus and benchmark-specific window/scoring conventions; natural and synthetic subsets must remain distinct. |
| **Hexagon ML/UCR anomaly archive** | UCR/Keogh project released anomaly datasets with provenance and explicitly criticized flawed TSAD benchmark practices. citeturn25search0turn25search1 | Useful for series-level generalization and exact anomaly-localization studies where provenance is suitable. | Public download is provided by UCR; dataset-by-dataset rights still need checking before redistribution. citeturn25search1 | Heterogeneous tasks/provenance; not all series represent the same anomaly concept or online operating conditions. |
| **Deliberately generated perturbations on real or mathematical background** | FlowGate-controlled generator with exact seed/config/type/time/amplitude | Excellent for mechanism tests and deterministic reproduction | Your own generator can be released with the code, subject to rights on any real background | Must be called simulation/perturbation evidence; cannot be promoted into “natural anomaly” evidence |

A useful hierarchy would be: fresh market data for **load/runtime realism**, one external labeled operational dataset such as SMAP/MSL for **task validity**, and controlled simulations for **mechanism stress tests**.

### Fair baseline structure

The minimum factorial is:

| Coefficient policy | Admission | Scientific role |
|---|---|---|
| Fixed EMA | none | Full-processing fixed baseline |
| Adaptive EMA | none | Isolates adaptation without shedding |
| Fixed EMA | load-driven admission | **Critical primary control**: admission benefit without pole adaptation |
| Adaptive EMA | same load-driven admission | Proposed combined method |

For the **conditional adaptation effect**, the fixed and adaptive rows should receive the **same realized admission mask**. This is stronger than merely saying they use the same admission algorithm: if closed-loop execution causes different queue histories, the realized masks can diverge and confound the effect.

Then add three admission controls: a fixed budget/stride policy at matched processing fraction; a randomized policy at matched expected fraction; and a simple queue-depth or hysteresis controller. Aurora-era work already distinguishes random and content-sensitive dropping, and LAS is specifically queue-latency aware, so a proposed system should not be evaluated only against no-shedding or a weak fixed stride. citeturn21search2turn21search0

Relevant filter/task baselines should include the identity/no-filter path, a validation-tuned fixed EMA, the elapsed-time-aware EMA for irregular streams, KAMA as a signal-driven adaptive smoother, and causal Butterworth SOS only after a defensible uniform-grid transformation. KAMA should not be represented as a load-aware competitor; it adapts for a different reason.

If a labeled anomaly study is included, retain the causal residual detector as a simple baseline and add at least one structurally different online detector such as RRCF or SPOT. RRCF was expressly designed for dynamic streams, while SPOT was developed for streaming univariate thresholding. citeturn24view0turn24view1 DAMP is a stronger contemporary candidate for subsequence-discord tasks, but only where its definition of anomaly matches the dataset/task. citeturn26search0turn26search3

### Tuning fairness

The adaptive method has more tuning degrees of freedom than a fixed EMA. A fair design therefore cannot give the adaptive method dense searches over `alpha_min`, `alpha_max`, slew, load mapping, admission parameters, and detector thresholds while evaluating one arbitrary fixed \(\alpha\).

Freeze:

\[
\mathcal H_{\text{fixed}},\qquad
\mathcal H_{\text{adaptive}},\qquad
\mathcal H_{\text{admission}}
\]

before confirmatory access. Give methods a declared tuning budget, report both the number of evaluations and actual tuning compute, and select configurations only from development/validation units.

For the primary fixed-vs-adaptive admission comparison, tune the fixed EMA **under the same admission regime and same task objective**. Otherwise an apparent adaptive advantage may just mean the fixed baseline was calibrated for full-rate operation.

Report at least two fairness views:

**validation-best view**, where each method receives a comparable tuning budget; and **mechanism-matched view**, where processing fractions and admission masks are controlled.

A third smoothing-matched view can be useful, but there is no single scalar matching criterion that simultaneously equalizes cutoff, delay, noise gain, and time-varying response. State exactly what is matched.

## Measured M3 streaming experiment and statistical protocol

The real experiment should be deliberately simpler than a production streaming framework. A single producer, a bounded queue, and one worker give an interpretable foundation. Concurrency can become a separate secondary experiment after the single-worker operator is validated.

### Runtime semantics and trace contract

For every source event, preserve at least:

| Field | Definition |
|---|---|
| `source_id`, `sample_id`, `source_unit_id` | Immutable identity of archive/series/event |
| `source_time_ns` | Provider/dataset event timestamp; never used as host runtime |
| `ingress_monotonic_ns` | Host monotonic clock when replay presents the event to FlowGate |
| `load_observation_ns` | Time at which the controller reads the state that influences this decision |
| `load_value`, `load_definition` | Numeric control signal and named definition |
| `admission_decision_ns` | End of controller/admission computation |
| `admitted` | Boolean decision |
| `drop_reason` | `policy`, `queue_overflow`, `replay_failure`, or other declared category |
| `queue_depth_before`, `queue_depth_after` | Defined consistently with whether in-service work counts |
| `worker_start_ns`, `worker_finish_ns` | Actual processing boundaries for admitted events |
| `sink_finish_ns` | Actual completion/acknowledgement of the declared downstream operation |
| `alpha`, `filter_state_digest` | Causal filter/controller state |
| `filter_output`, `score`, `alert` | Only where actually computed |
| `attempt_id`, `run_id`, `config_digest` | Immutable run/config provenance |
| `status` | completed, failed, unfinished/censored, rejected, etc. |

The queue must have a fixed configured capacity. For the initial study I recommend **drop-new** on overflow, because it has particularly clear identity accounting: the event that cannot enter is the event recorded as overflow-rejected. Drop-oldest can be studied later but requires explicit victim identity and changes state semantics.

At run completion enforce conservation identities such as

\[
N_{\rm offered}
=
N_{\rm admitted}
+
N_{\rm policy\ drop}
+
N_{\rm overflow\ drop}
+
N_{\rm replay\ failure},
\]

under your exact definitions, and

\[
N_{\rm admitted}
=
N_{\rm completed}
+
N_{\rm operator\ failure}
+
N_{\rm unfinished/censored}.
\]

A row cannot simultaneously earn the benefit of “dropped computation” and count as a completed useful result.

The controller must sample only state already available before the decision. A straightforward first control signal is queue occupancy before the current event,

\[
L_n=\frac{Q_n}{Q_{\max}},
\]

clipped only by the fact that \(Q_n\in[0,Q_{\max}]\) by construction. This is interpretable but coarse. A future version can use a causal estimate of queued work in seconds, which is often more meaningful when service times vary, but that requires an explicit service-time estimator. Do **not** call queue occupancy “CPU utilization.”

The physical runtime and the current exact `fcfs_schedule` should coexist as separate evidence:

`evidence_tier = "model"` for the scheduling algebra;

`evidence_tier = "measured"` for actual ingress/start/finish/sink timestamps.

No table should merge them into one unqualified “throughput.”

### Useful throughput

“Accepted input rate” is not a sufficient systems outcome because an algorithm can accept apparent high offered load by discarding nearly everything. Define useful operation through a pair of constraints.

For example, with deadline \(D\),

\[
I_i^{\rm timely}
=
I\{\text{completed}_i
\land
\text{sink\_finish}_i-\text{ingress}_i\le D\}.
\]

Then

\[
T_{\rm timely}
=
\frac{\sum_i I_i^{\rm timely}}{\text{measured wall duration}}.
\]

Keep quality as an explicit second dimension, or define useful throughput only after a **prospectively justified** quality threshold \(Q\ge Q_{\min}\). Avoid inventing one arbitrary scalar combination of throughput, AP, loss, and latency.

The primary system comparison can therefore be:

> maximum measured timely completion rate, over the registered offered-load grid, subject to quality not violating the preregistered loss/noninferiority requirement.

That is much harder to game than inverting one microbenchmark.

### Cold, warm, ordering, and resource measurement

Systems experiments are vulnerable to measurement bias; Mytkowicz et al. demonstrated that apparently innocuous setup changes can reverse conclusions and explicitly recommend setup randomization. citeturn19search0 Runtime-methodology work likewise emphasizes repeated measurements and hierarchical sources of execution variation. citeturn19search2turn19search3

Use two separate execution classes:

**cold execution:** fresh process, imports/initialization included according to a declared scope;

**warm steady execution:** fixed warmup completed, persistent operator state or declared reset, then measured interval.

Within a timing block, randomize or counterbalance method order. Better still, interleave configurations across repeated workload blocks:

\[
A,B,C,D,\quad
C,A,D,B,\quad
D,C,B,A,\ldots
\]

with schedules generated before observing results.

Record OS version, Python build and architecture, AC/battery state, low-power mode, selected thread limits, block order, process start time, and background-condition notes. Do not claim to have controlled thermal state merely because a pause occurred.

For host timing, Python's monotonic/performance clock is appropriate for wall-duration instrumentation; actual process CPU time must come from a process CPU clock rather than relabeling elapsed time. Peak RSS can be measured using a platform-aware mechanism, but macOS units must be normalized explicitly. Those are implementation proposals; their resolution and overhead need pilot validation.

**Energy should be optional.** Unless a tool or external instrument provides credible during-run energy measurements with a documented system/process scope, sampling interval, integration procedure, and permission model, report energy as `not_measured`. Faster execution is not equivalent to measured lower joules.

### M3 compute and storage budget methodology

Do not choose a paper-scale source count from the advertised CPU/GPU configuration. Measure four pilot quantities:

\[
t_{u,c,r}
\]

= wall time for source unit \(u\), configuration \(c\), repetition \(r\);

\[
m_{u,c,r}
\]

= peak measured memory;

\[
b_{u,c,r}
\]

= serialized evidence bytes;

and the actual event count

\[
N_u.
\]

Then estimate the confirmatory compute budget from the **upper part of the observed runtime distribution**, not only its mean:

\[
T_{\rm projected}
=
\sum_{u,c,r}
\widehat{t}_{u,c,r}.
\]

Similarly estimate evidence growth using actual compressed serialized bytes per event:

\[
B_{\rm projected}
=
B_{\rm immutable\ inputs}
+
\sum_{u,c,r}
N_u\,\widehat b_{u,c,r}
+
B_{\rm analysis\ intermediates}.
\]

Compare this with measured free storage immediately before freeze/run and retain a deliberate reserve. The reserve amount is an operational human decision informed by the pilot; it should not be invented now.

The GPU should not appear in the research argument unless a GPU code path actually exists and host/device synchronization and transfer costs are measured. Nothing in the inspected Python foundation provides evidence of GPU acceleration.

### Statistical estimands and hierarchy

The first task is to define the population, not the test.

For a market workload with simultaneous assets, a defensible candidate hierarchy is

\[
\text{calendar block}
\rightarrow
\text{asset/source series}
\rightarrow
\text{event}
\rightarrow
\text{algorithm/admission seed}.
\]

The exact top-level independent unit is an **empirical design decision**. Calendar days are not automatically independent, and simultaneous assets are not automatically independent. Repeated algorithm seeds inside one day are definitely not new calendar days.

For a labeled spacecraft dataset, the hierarchy may instead be mission/channel/anomaly episode or another dataset-specific grouping. The independent unit must follow how the data were generated.

A clean primary mechanism estimand is the equal-source-unit mean paired quality effect

\[
\theta_Q
=
E_U[
Q_{\text{adaptive},U}
-
Q_{\text{fixed},U}
],
\]

where both methods use the same offered stream, admission mask, task/reference, and evaluation horizon.

The closed-loop system estimand can be

\[
\theta_T
=
E_U[
T_{\text{useful,adaptive},U}
-
T_{\text{useful,fixed},U}
]
\]

at one or several prospectively defined offered-load regimes.

“Equal source-unit weight” must be explicit. Otherwise a high-volume BTC day could dominate an apparently “average across days” conclusion merely because it contains more ticks.

Random/admission/injection seeds belong **inside** their source unit. Either average them to a preregistered source-unit estimate before outer inference or fit a genuine hierarchical model. Do not count \(20\) seeds on each of \(10\) days as \(200\) independent days.

### Pairing and failure handling

Comparisons should join exact keys, e.g.

\[
(\text{source\_unit},
\text{workload},
\text{repeat/block},
\text{epoch},
\text{task definition})
\]

and only then compare method configurations.

Missing pairs must fail analysis or trigger the preregistered failure rule. Never sort by seed and truncate to the shorter array.

Technical failures are informative. Preserve both:

\[
P(\text{method completes run})
\]

and conditional quality/runtime metrics. If the preferred policy repeatedly fails on the hardest overload units, a “complete cases only” analysis can be badly favorable. For useful throughput, failed/unfinished admitted work naturally earns no completion; for quality metrics that cannot be computed after a crash, report explicit missingness and apply the preregistered estimand/failure policy rather than inventing a score.

### Confidence intervals and dependence

The supplied paired Student-\(t\) utility is acceptable only after the caller has justified the independent source-unit representation and approximate behavior of paired unit effects. It is not a universal inference engine.

A preferable default for a sufficiently sized hierarchical study is a **paired cluster bootstrap at the top-level independent unit**, preserving both methods and all nested observations within each resampled cluster. If inference is explicitly within a long stationary series, block-bootstrap methods can preserve local dependence; the stationary bootstrap was developed for weakly dependent stationary observations, which means those assumptions need examination rather than automatic application to market data. citeturn28search0

With very few independent clusters, no resampling method can manufacture information. Report wide uncertainty or gather more actual source units.

### Latency, misses, and censoring

Separate:

\[
P(\text{completed by deadline}),
\]

\[
P(\text{alert by deadline}),
\]

detected-only latency distributions,

and unfinished/right-censored work.

If only 20% of true events are detected, “median alert latency among detected events” is not a global latency guarantee. Likewise, an unfinished queue item at shutdown has not completed at the censoring time.

For anomaly studies report event recall, false alerts, deadline-success proportion, and the latency distribution conditional on detection. Survival analysis can be considered for completion processes where censoring assumptions make sense, but the simpler first requirement is that misses and unfinished work remain visible.

### Multiplicity and practical significance

Declare a small primary family. A sensible example is:

1. adaptive-versus-fixed quality difference at the primary admission setting;
2. adaptive-versus-fixed useful throughput under the primary overload setting;
3. adaptive-versus-fixed deadline-success probability.

Secondary workloads, source subgroups, alternative detectors, slew settings, and perturbation types are exploratory unless placed prospectively in another family. Holm adjustment, already present in the repaired utility, is a reasonable finite-family procedure.

Do not interpret \(p>0.05\) as equivalence. If quality preservation is necessary, define a noninferiority margin

\[
\Delta_{\rm NI}
\]

from an application requirement or independent domain judgment **before** confirmatory results. The result is noninferior only if the appropriate confidence bound lies within that margin. If no defensible margin exists, do not run an equivalence/noninferiority narrative.

### Prospective precision and power

No numerical sample size can be justified yet because the following are unknown:

\[
\sigma_d
=
\text{SD of independent-unit paired effects},
\]

the minimum worthwhile effect

\[
\delta,
\]

the effective top-level dependence structure, failure/attrition probability, and multiplicity burden.

For planning intuition only, an approximate paired-mean design has the familiar scaling

\[
n
\approx
\left[
\frac{
(z_{1-\alpha/2}+z_{1-\beta})\,\sigma_d
}
{\delta}
\right]^2,
\]

before cluster/dependence, multiplicity, or attrition inflation. The purpose of the development pilot is to estimate \(\sigma_d\) and execution feasibility; \(\delta\) should come from scientific/practical importance, not from whatever effect happens to appear in the pilot.

Freeze a fixed independent-unit/run budget or a legitimate prospective sequential design. Do not stop when a favorable \(p\)-value, Pareto point, or plot appears.

Interpret outcomes prospectively:

| Result | Interpretation |
|---|---|
| CI excludes zero and exceeds the practical-benefit threshold | Evidence of practically useful benefit within the studied population |
| CI excludes the predeclared worthwhile adaptive benefit but includes zero/small effects | Evidence that the tested adaptation does not add a practically important benefit |
| CI lies entirely inside a justified negligible/equivalence region | Practically negligible/equivalent only if that region was prospectively defensible |
| CI spans important benefit and important harm | **Inconclusive**, not “no difference” |
| Admission helps but coefficient adaptation does not | Strong negative mechanism result: shedding explains the benefit |
| Adaptive method degrades quality or resource performance | Negative result; preserve and explain it |
| Runtime/data failures prevent reliable estimate | Failed/incomplete study, not a zero effect |

## Factory/domain evidence specification

Because I did not directly inspect the active factory implementation, this section is a **normative adapter specification** to be reconciled line-by-line with `factory/AGENT_WORKFLOW.md` and the actual v3.3 code before implementation.

The central principle is that a scientific gate must validate **semantic evidence**, not the existence of files with approved names.

### Domain record types

The adapter should introduce explicit record classes rather than forcing everything into binary-classification predictions.

| Record | Required semantics |
|---|---|
| `SourceUnit` | Stable unit ID, parent dependence group, source/data origin, split, source checksum, date/time scope, label provenance |
| `TransformManifest` | Exact input hashes, transform code/config hash, fitted-on split/unit IDs, output hash, causal-time policy |
| `MethodConfig` | Filter, initialization, controller, load definition, admission, queue, detector, threshold, runtime implementation, all units |
| `RuntimeAttempt` | Attempt/run/block IDs, host/environment, start/end, failure status, offered/completed accounting, raw trace hashes |
| `RuntimeEvent` | Full causal clock/admission/queue/worker/completion row described above |
| `QualityEvidence` | Unit-level metric, metric version, direction/units, eligible population, raw-input/trace hash |
| `ComparisonEvidence` | Exact paired unit IDs, estimand, effect, CI/resampling method, multiplicity family, failure handling |
| `ModelEvidence` | Analytical/simulation output explicitly marked non-measured, including model assumptions |
| `MeasurementEvidence` | Physical runtime/resource observations with instrument, sampling scope, units, availability status |

The adapter must reject a record claiming `evidence_tier="measured"` if it contains only FCFS model outputs or a requested workload rate.

### Applicability matrix

| Method/evidence | Training epochs required? | Probability metrics required? | Appropriate scientific evidence |
|---|---:|---:|---|
| Fixed EMA / Butterworth / deterministic admission | No | No | Configuration, code/hash, validation selection if tuned, exact runtime/quality records |
| Adaptive EMA controller | No invented epochs | No | Controller recurrence/config, validation selection, state trace |
| Score-only anomaly detector | Only if genuinely learned | **No Brier/log-loss unless scores are calibrated probabilities** | AUROC/AP/ranking metrics plus threshold/event metrics as appropriate |
| Calibrated probabilistic detector | According to actual learned/calibration process | Yes where scientifically relevant | Calibration split, probability semantics, Brier/log-loss/calibration evidence |
| Learned neural baseline | Yes, genuine training evidence | Depends on output task | Data split, optimizer/epoch/checkpoint evidence, selection rule |
| Perturbation generator | Not applicable | Not applicable | Generator code/config/seed, realized events, collisions, provenance marked simulation |
| FCFS scheduler | Not applicable | Not applicable | Model equations/input traces; never physical runtime certification |

A factory count floor must not be satisfied by five identical deterministic executions relabeled with different seeds. Those can be reproducibility repetitions, but not five independent population units.

### Independent recomputation

Certification should use a second implementation path where practical.

For point metrics, independently recompute TP/FP/FN, AUROC, and AP from raw aligned labels/scores rather than trusting a summary JSON.

For admission accounting, independently recompute:

\[
\sum I_{\rm offered},
\quad
\sum I_{\rm admitted},
\quad
\sum I_{\rm dropped},
\quad
\sum I_{\rm completed}.
\]

For latency, recompute directly from monotonic timestamps.

For useful throughput, recompute from completion rows rather than a reported scalar.

For comparisons, reconstruct exact paired unit keys from accepted run records.

For queue models, compare against hand-calculated cases, while measured runtime verification uses actual timestamps and does not call the FCFS formula its oracle.

The verifier should not simply call the same project function that produced the summary and declare agreement.

### Immutable provenance

Every accepted evidence object should bind at minimum:

\[
H_{\rm source},
H_{\rm cohort},
H_{\rm code},
H_{\rm methodology},
H_{\rm config},
H_{\rm environment},
H_{\rm raw\ trace}.
\]

An attempt gets its identity **before execution**, so failures cannot disappear when a successful retry is made.

Provider data can change after publication: Binance itself states that archived files may later be replaced following discovered issues. citeturn15search0 Therefore the acquisition manifest must bind the exact bytes consumed, not merely the filename or URL.

### Semantic accounting checks

Certification should enforce relations, not just keys:

\[
\text{offered}
=
\text{admitted}
+
\text{all rejected categories},
\]

\[
\text{admitted}
=
\text{completed}
+
\text{operator failures}
+
\text{unfinished/censored}.
\]

Further checks should ensure:

\[
t_{\rm ingress}
\le
t_{\rm decision}
\le
t_{\rm worker\ start}
\le
t_{\rm worker\ finish}
\le
t_{\rm sink\ finish}
\]

whenever all times apply.

A load observation influencing event \(n\) must satisfy

\[
t_{\rm load\ observation,n}
\le
t_{\rm admission\ decision,n}.
\]

A skipped event cannot have a worker completion unless another explicitly named cheap path processed it.

A held filter display value must not be transformed into a new detector computation without the detector cost being represented.

### Mutation tests

A meaningful domain adapter should fail when a test mutates any of the following:

| Mutation | Expected failure |
|---|---|
| Alter one source byte/hash | Provenance failure |
| Duplicate an event ID | Identity/conservation failure |
| Delete a failed attempt | Attempt-manifest mismatch |
| Change policy drop to completion | Accounting failure |
| Shift load timestamp after admission decision | Causality failure |
| Replace physical runtime with FCFS model rows | Evidence-tier failure |
| Change config without changing digest | Integrity failure |
| Join methods on seed but mismatched source unit | Pairing failure |
| Turn score into arbitrary \([0,1]\) number and claim probability | Metric-applicability failure |
| Add fake training epochs for deterministic EMA | Method-applicability failure |
| Omit misses from event latency summary | Population/metric-definition failure |
| Change source labels after freeze | Cohort/freeze failure |

A directory containing `predictions.csv`, `metrics.json`, and `PASS` should not certify anything unless these relationships validate.

### Assurance boundary

A local software factory can provide strong guarantees about schema validation, immutable hashes, exact lineage, recomputation, lifecycle discipline, and mutation-tested accounting. It **cannot by itself** establish that:

- a human-chosen research question is important;
- source labels are ontologically correct;
- source units are truly independent;
- a chosen noninferiority margin is scientifically meaningful;
- the M3 hardware measurement instrument is accurate;
- the literature search found every prior method;
- an AI or same-user process constitutes independent peer review;
- a result is novel enough for a target venue.

The certificate should therefore say what it verifies, not “scientifically valid” in the abstract.

## Venue fit, implementation roadmap, and submission readiness

### Venue fit under current official policies

A **substantive DSP paper** could plausibly target IEEE Transactions on Signal Processing only if the work contains a genuinely significant signal-processing contribution: for example, a useful general analysis of the admitted LTV first-order operator, meaningful bounds or approximation theory, and broad experiments demonstrating why those results matter beyond this prototype. TSP's official scope explicitly covers novel theory, algorithms, performance analysis, and filtering, and says contributions must be original, timely, and significant. citeturn17view0 A measured MacBook implementation plus an ad hoc load-to-\(\alpha\) rule is not enough for that standard.

A **streaming-systems paper** is more naturally aligned with ACM DEBS if the main contribution is a real overload controller/runtime with careful quality-versus-latency behavior. DEBS explicitly includes data stream processing, real-time analytics, event processing, reliability/resilience, energy management, and finance/sensor applications. citeturn18view1 Its currently published 2027 dates list an abstract deadline of February 16, 2027 and paper deadline of February 23, 2027. citeturn22search0 Those dates should be treated as planning information, not a reason to rush an underpowered study.

A **negative-mechanism / experimental-analysis paper** is potentially attractive to SIGMOD or PVLDB only if FlowGate becomes a genuine data-management contribution rather than merely a one-off DSP benchmark. SIGMOD 2027 explicitly has Experiment & Analysis papers for new insight into strengths/weaknesses, including experimental analysis, benchmarks, and reproducibility. It also explicitly lists streams and complex event processing among its topics. citeturn17view1 As of October 1, 2026, SIGMOD 2027 Round 4's official deadlines are October 10 for the abstract and October 17 for the paper. citeturn17view1 **My recommendation is no-go for that round:** the missing runtime, adapter, fresh population, pilot, power/precision design, and confirmatory evidence make scientific readiness far more important than the still-open calendar window.

PVLDB's Experiment, Analysis & Benchmark category is another plausible eventual home for a broad reproducible systems/evaluation result; current rules require those papers to provide the full experimental data/software reproducibility package already at initial submission. citeturn18view0 PVLDB Volume 20 has rolling monthly deadlines through March 1, 2027, but its official scope requires meaningful connection to data-management problems and literature, not merely incidental streaming terminology. citeturn22search1turn22search4

Accordingly:

| Contribution ultimately established | Plausible fit | Evidence bar |
|---|---|---|
| New, general DSP operator theory plus convincing empirical consequence | IEEE TSP | Nontrivial theory, assumptions/proofs, strong DSP baselines, broad evidence |
| New overload/admission architecture or controller with measured stream-system value | DEBS; potentially broader systems/data venues | Real bounded runtime, strong shedding competitors, workload breadth, latency/loss/quality evidence |
| Careful finding that adaptive DSP state adds little/conditional value beyond admission | SIGMOD/PVLDB E&A if generalized to stream processing; otherwise specialist venue | Broad, reproducible, unbiased comparisons; mechanistic explanation; useful lesson beyond FlowGate |
| Only “our implementation now computes EMA correctly” | Not a research paper by itself | Engineering artifact, not sufficient scientific novelty |

### Prioritized implementation roadmap

| Priority | Deliverable | Dependencies | Acceptance criterion | Falsification / no-go criterion |
|---|---|---|---|---|
| **P0** | Freeze the scientific estimands, not results | Direct review of current methodology/factory; task choice | One primary mechanism estimand, one closed-loop estimand, declared quality/reference, source-unit hierarchy | Team cannot identify a quality target independent of the proposed method |
| **P0** | Complete DSP/streaming factory adapter | Actual factory source | Honest deterministic applicability, runtime/queue schemas, semantic accounting, mutation tests, independent recomputation | Adapter still requires dummy labels/probabilities/epochs or certifies filename presence only |
| **P0** | Implement real bounded replay/runtime | Current primitives | Source/ingress/start/finish/sink clocks; bounded queue; overflow; causal controller; complete accounting; retained failures | Only FCFS simulation or microbenchmark exists |
| **P0** | Implement common-mask mechanism harness | Runtime/admission definitions | Fixed/adaptive filters replay identical masks and load histories with exact alignment | Closed-loop mask differences remain confounded in the primary adaptation contrast |
| **P0** | Select and verify fresh source population | Data-card/provenance design | New prospectively selected source units, immutable bytes, legal/access record, no January 2024 confirmatory reuse | Selection altered after observing preferred-method test results |
| **P0** | Development pilot | Runtime + fresh development units | Measures runtime variance, trace storage, memory, failure rate, source dependence indicators, paired effect variance | Machine/storage or source-unit count cannot achieve useful precision |
| **P0** | Populate/freeze confirmatory methodology | Pilot results | Fixed run budget, primary family, tuning budgets, failure rules, randomization, precision design | Numerical N/margin merely copied from legacy seeds or chosen after test results |
| **P1** | Strong baselines and factorial study | Task finalized | Fixed EMA + same admission, no-shed, matched stride/random, simple queue policy; adaptation×admission factorial complete | Preferred method receives more tuning or weaker cost accounting |
| **P1** | External labeled task, if anomaly claim retained | Label/provenance review | Natural/artificial subsets explicit, chronological causal evaluation, strict point + declared event metrics | Binance-derived/injected labels presented as natural truth |
| **P1** | Confirmatory execution | Frozen epoch | Every planned attempt is completed or retained as a failure; no result-driven parameter changes | Any fallback, selective deletion, or post-test retuning |
| **P1** | Independent inference/recomputation | Immutable raw traces | Exact unit joins; all primary metrics recomputed from trace; multiplicity and censoring applied | Summary cannot be reconstructed or pairing differs |
| **P2** | Optimization backend | Reference semantics frozen | Differential equivalence tests plus separately measured cold/warm cost | Optimized code changes operator semantics |
| **P2** | Energy experiment | Credible instrument available | Integrated during-run energy with scope/uncertainty | Only instantaneous/before-after power observations available |
| **P2** | UI/demo | Scientific runtime stable | Displays actual alerts/measurements and clearly distinguishes truth labels/models | Ground truth is reused as detector alert |
| **Last** | Manuscript and venue selection | Evidence complete | Every headline maps to accepted immutable evidence and literature gap | Venue deadline becomes the reason to weaken methodology |

### Explicit research go/no-go decisions

**GO:** Continue FlowGate as a rigorous investigation of whether load-driven coefficient adaptation adds value **beyond admission**.

**GO:** Preserve the first-order operator analysis; it gives a clean mathematical core, especially the admitted-state recurrence and skipped-update-error decomposition.

**GO:** Build a real single-worker bounded-queue experiment before attempting multicore optimization.

**GO:** Use fresh Binance or other real event streams for workload/replay realism, but call them unlabeled observational data.

**GO:** Add an external labeled operational dataset only if anomaly-detection claims remain scientifically important.

**NO-GO:** Claim that smaller or load-varying \(\alpha\) itself saves meaningful compute. The inspected algorithm contains no such mechanism.

**NO-GO:** Reuse January 2024 Binance data as an untouched confirmatory population.

**NO-GO:** Interpret generated perturbation labels as natural market anomalies.

**NO-GO:** Treat a frozen pole/cutoff plot as the response of the actual adaptive/admitted system.

**NO-GO:** Treat modeled FCFS capacity as measured sustainable throughput.

**NO-GO:** Count algorithm seeds or duplicated trials as independent source units.

**NO-GO:** use nonsignificance as evidence of equivalence.

**NO-GO:** produce factory-approved fake binary labels, arbitrary probability mappings, fake epochs, or zero-valued resource placeholders.

**NO-GO:** make energy, GPU, multicore scaling, or thermal claims until those paths are physically measured.

### Submission-readiness checklist

| Requirement | Status from materials actually inspected | Required evidence before “ready” |
|---|---|---|
| Meaningful falsifiable question | **Mostly defined, needs reframing** | Freeze the two-stage adaptation-versus-admission question |
| Strong related-work gap | **Not yet established as novelty** | Full primary-source matrix and precise gap statement |
| Correct numerical primitives | **Promising source-level foundation** | Execution, independent tests, line-by-line code audit |
| Actual streaming runtime | **Missing in inspected snapshot** | Bounded queue, real workers/sink, causal trace |
| Fresh confirmatory population | **Missing** | Prospective source manifest and freeze |
| Defensible quality target | **Missing** | Common DSP reference and/or independent external labels |
| Fair fixed baseline | **Design specified, not evidenced** | Validation-tuned fixed EMA under same admission |
| Strong shedding baselines | **Not evidenced** | Random/matched and simple queue-aware controls; justified literature competitor |
| Complete factorial | **Not evidenced** | Adaptation × admission, plus slew if claimed |
| Dependence-aware inference | **Only basic paired \(t\) utility inspected** | Source-unit hierarchy, cluster/bootstrap or justified alternative |
| Physical latency/censoring | **Missing** | Completion/unfinished/miss trace and analysis |
| Real CPU/memory measurements | **Missing** | Instrumented pilot and measurement scope |
| Energy | **Missing / optional** | Credible integrated measurement or omission |
| Factory DSP evidence profile | **Reported missing; not directly inspected** | Semantic adapter and mutation tests |
| Independent recomputation | **Missing at study level** | Second-path trace recomputation |
| Immutable confirmatory execution | **Not performed** | Frozen epoch with all attempts retained |
| Robustness/failure study | **Not performed** | Adverse overload, phase, stalls, reset, missingness, OOD |
| Artifact reproduction | **Not performed** | Fresh-environment reproduction and lawful data recipe |
| Venue-ready significance | **Unknown** | Determined only after actual findings |

### Decisions that require pilot measurement or human scientific judgment

The following cannot responsibly be settled by literature review or source inspection alone.

**Quality objective.** A human research decision is needed about what loss matters. Is FlowGate approximating a prescribed low-pass signal, preserving anomaly-detection AP, maintaining event recall before a deadline, or supporting another downstream operation? This choice determines almost every fair comparison.

**Practical effect margin.** A noninferiority or “worthwhile benefit” margin must come from the application or independent domain requirements. It cannot be derived from whichever differences FlowGate happens to produce.

**Independent-unit definition.** Autocorrelation and cross-asset dependence must be examined empirically on the proposed fresh population. Calendar day is a candidate unit, not an established truth.

**Load definition.** Queue occupancy, estimated work backlog, CPU demand, source rate, and service-time ratio are different signals. The controller must use one explicitly causal definition.

**Queue capacity and deadline.** These are application/system requirements and must not be chosen because they create a favorable operating regime.

**Downstream sink.** You need to decide what useful completion actually is: filtered output serialization, detector evaluation, local database/log write, alert handoff, or another concrete task. Its cost must be real.

**M3 feasibility.** The number of source units, configurations, randomized blocks, and repetitions must come from measured pilot runtime, peak memory, evidence bytes/event, and variability.

**Thermal/order effects.** Whether session/block effects are large enough to matter can only be determined empirically on the actual Mac.

**Energy feasibility.** The existence, permissions, scope, and precision of a credible local measurement route must be established experimentally; otherwise omit energy.

**External labels.** Even expert or benchmark labels are annotations, not metaphysical truth. SMAP/MSL has expert-labeled operational telemetry according to NASA, while NAB explicitly mixes real and artificial time series. citeturn24view2turn24view3 Human judgment is needed about which label semantics match the intended FlowGate task.

**Publication framing.** If the results show that fixed EMA plus ordinary admission dominates or matches load-adaptive \(\alpha\), the work should pivot to a negative-mechanism/evaluation contribution rather than hiding the result. If the adaptation advantage appears only under a narrow artificial perturbation or carefully selected phase, that is evidence against a broad claim. If a strong, general signal-operator result emerges, a DSP venue becomes more plausible. TSP officially demands original, significant signal-processing contributions; DEBS explicitly targets event/data-stream systems; SIGMOD and PVLDB provide experimental-analysis routes when the broader data-management insight is substantive. citeturn17view0turn18view1turn17view1turn22search4

The core recommendation is therefore **not to optimize or publish the present method yet**. First implement the evidence system that can make the preferred hypothesis lose. The critical experiment is the fixed-EMA **same-admission-mask** comparison. If adaptive \(\alpha\) cannot produce a meaningful quality advantage there, any apparent end-to-end advantage is likely attributable to admission or another confound. If it can, the subsequent real bounded-queue experiment determines whether that signal-level benefit survives controller overhead and physical latency constraints. That sequence creates a scientifically interpretable result regardless of whether FlowGate ultimately wins.

A literature report, including this one, cannot certify the correctness of the source code, validate the supplied forensic audit, establish M3 performance, prove label quality, or substitute for the actual frozen measurements. It can define the assumptions, comparisons, schemas, falsification rules, and evidence contracts under which those future measurements would become scientifically interpretable.