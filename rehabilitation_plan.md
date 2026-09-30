# FlowGate DSP Project Rehabilitation Plan

**Factory target:** Software Factory v2.2.0  
**Starting point:** the existing `DSP Mini Project` repository, not a greenfield rewrite  
**First execution unit:** Chunk 01 (there is deliberately no rehabilitation “Chunk 00”)  
**Primary deliverable:** a publication-ready, independently reproducible project whose empirical evidence comes only from authentic observed data and measured runtime behavior  
**Plan status:** planning and audit artifact; no rehabilitation work has been executed by this document

---

## 1. Purpose and authority of this plan

This document is the rehabilitation program for the existing FlowGate/load-adaptive-IIR project. It is intentionally more conservative than a normal refactor plan because the repository currently mixes potentially useful DSP implementation work with generated research inputs, simulated load, injected anomalies, stale narrative claims, generated artifacts, dependency environments, and uncommitted user work. A cosmetic reorganization would make the repository look cleaner while preserving the underlying scientific problems. That is not an acceptable outcome.

The rehabilitation has four simultaneous objectives:

1. **Factory adoption:** make the project’s current and future work follow Software Factory v2.2.0 from Project Initialization through release certification.
2. **Scientific rehabilitation:** remove fabricated, synthetic, simulated, injected, or silently substituted empirical evidence; repair the experimental design; and narrow claims whenever authentic data cannot support them.
3. **Repository rehabilitation:** produce a deliberate, comprehensible source tree; keep transient and machine-local material out of Git; preserve meaningful history; and avoid losing any current user work.
4. **Publication rehabilitation:** make every reported number traceable to immutable inputs, code, configuration, environment, and a run identifier, while keeping the manuscript, figures, tables, and machine-readable evidence mutually consistent.

This plan authorizes **planning only**. It does not authorize deleting files, rewriting Git history, force-pushing, downloading data, accepting data licenses, publishing artifacts, or changing the scientific claim. Those are later contract actions with explicit stop conditions and, where appropriate, Human approval.

The existing repository is evidence. Even files that should not survive into the finished project must first be inventoried, hashed where useful, and classified. “Make it look as if it came from the Factory” therefore means that the finished working tree and all new work will be Factory-native. It does **not** mean falsifying the migration history or pretending that the legacy phase never happened.

---

## 2. Executive rehabilitation decision

The correct approach is a **controlled in-place rehabilitation with a new Factory-native publishable surface**, not an ad hoc cleanup and not an immediate rewrite.

The repository should become an outer product repository with these responsibilities:

- `source/` is the only authoritative implementation and publishable project surface.
- `factory/` contains the pinned v2.2.0 Factory infrastructure and is ignored by the outer repository.
- `project/` is the Factory’s independent nested Git repository containing project plans, contracts, evidence reports, decisions, and evolution telemetry; it is ignored by the outer repository.
- `DROP_HERE/` and `TAKE_THIS/` retain their Factory-defined mailbox roles and are ignored.
- raw data, processed caches, experiment workspaces, virtual environments, frontend dependencies, interpreter caches, and uncurated results remain local or in an external artifact store and are ignored.
- a small, curated release-evidence set may be tracked only after independent verification and only when every file has an artifact manifest entry.

The existing implementation is not accepted as scientifically valid merely because much of it will be migrated. Every module is treated as one of four things:

1. **Reusable implementation candidate** — retain after semantic tests and review.
2. **Reference-only legacy material** — preserve privately for audit, but do not ship or cite.
3. **Invalid empirical machinery** — replace before it can generate release evidence.
4. **Transient or generated material** — untrack and ignore after preservation checks.

The working scientific direction should be narrowed initially to:

> **Load-driven time-varying single-pole IIR filtering under measured stream backpressure.**

That wording is a provisional scope, not a final title. It avoids claiming that financial anomalies are detected correctly before authentic labels exist, and it avoids claiming a causal compute advantage before resource behavior is measured. The phrase “anomaly detection” may return to the title only if a real, legally usable, sufficiently powered labeled-event dataset passes the data-feasibility contract and the pre-registered evaluation passes. If that gate fails, the project will publish a filtering/runtime study rather than manufacturing labels or treating arbitrary price moves as ground truth.

---

## 3. Non-negotiable rehabilitation principles

These principles become project invariants during Project Initialization and are enforced mechanically wherever possible.

### 3.1 No fabricated empirical evidence

No publication result, calibration value, benchmark, demonstration presented as evidence, or manuscript conclusion may be derived from:

- generated random walks;
- generated sine/noise mixtures;
- injected spikes, level shifts, variance changes, or other artificial anomalies;
- simulated queue depth, simulated consumer lag, or artificial backpressure traces;
- bootstrapped pseudo-observations manufactured from aggregate scores;
- duplicated real observations presented as independent observations;
- arbitrary labels created from the method under evaluation;
- a fallback dataset used after an authentic source fails;
- a placeholder result copied forward because a new run is unavailable;
- hand-edited CSV rows, figure values, or narrative numbers.

An inaccessible real source causes a fail-closed result:

> `BLOCKED — HUMAN ACTION REQUIRED`

It never causes a synthetic substitute.

### 3.2 Mathematical test vectors are not empirical datasets

Some deterministic constructed inputs are necessary to prove elementary DSP semantics: a short Kronecker impulse, a constant step, a fixed hand-calculated sequence, or a boundary-case queue event sequence. These are permitted only under all of the following restrictions:

- they live under a clearly named test-vector area such as `tests/fixtures/canonical/`;
- they contain no randomness;
- expected outputs are derived analytically or by an independent reference calculation;
- they are labeled “canonical mathematical test vector — non-empirical” in code and reports;
- they cannot be loaded by experiment or manuscript-result entry points;
- no chart based on them is described as market evidence, detector performance, runtime performance, or validation on real data.

If the Human intends “no constructed inputs anywhere, including unit tests,” Chunk 04 can replace even those fixtures with inline algebraic assertions. The default in this plan is the scientifically conventional distinction above: deterministic semantic vectors are allowed for software correctness, while fabricated research data is forbidden.

### 3.3 No silent substitution and no partial-success ambiguity

Acquisition and experiment commands must use typed outcomes. A missing day, checksum mismatch, schema mismatch, unavailable service, incomplete asset set, or failed run must make the contract fail or explicitly become a pre-declared incomplete case. Broad exception handlers that print and continue are forbidden in evidence-producing paths.

### 3.4 Claims follow evidence, never the reverse

The title, abstract, README, report, UI, and conclusion may use only claims recorded in a claim ledger. Each claim points to a verified artifact, experimental unit definition, statistical method, uncertainty interval, and contract report. Failed or underpowered results narrow the claim; they do not trigger a search for more favorable artificial data.

### 3.5 Historical truth is preserved

The repository will openly record that it was migrated into the Factory. Legacy results will be quarantined and marked non-authoritative. History rewriting, if ever necessary to remove large binaries from the public clone, is an optional, separately approved release-engineering action with a preservation bundle and a migration record—not a way to conceal the project’s origin.

### 3.6 Reproducibility means a clean-room rebuild

A result is not reproducible merely because it reruns inside the current 4.8 GB working directory. Release readiness requires a clean clone, locked dependencies, declared data retrieval or artifact access, checksum verification, headless execution, independent result recomputation, and no dependence on ignored local files.

---

## 4. Audited baseline: what exists today

The following facts were observed directly from the two supplied folders on 2026-08-31. They are the baseline that Chunk 01 must preserve in a machine-readable intake report before changing the tree.

### 4.1 Repository and worktree state

| Item | Observed state | Rehabilitation consequence |
|---|---:|---|
| Outer branch | `main` | Do not begin migration on an unrecorded working state. |
| Current commit | `f73dc1e` | Record this as the legacy baseline commit. |
| Remote | `git@github.com:AdiShrestha/FlowGate-DSP-Project.git` | No force-push or remote mutation is implied by this plan. |
| Visible commit count | 33 | Preserve normal history; assess binary history separately. |
| Working tree | dirty | Snapshot and classify before any cleanup. |
| Deleted tracked files | 1 notebook | Do not restore or finalize deletion without Human disposition. |
| Modified tracked paths | 10 | Preserve diffs; several include result files and bytecode. |
| Untracked paths reported | 319 | Most are data, but four tests and documents may be valuable. |
| Approximate workspace size | 4.8 GB | Local environments and data dominate; a clean clone must be much smaller. |
| Approximate `.git/` size | 1.7 GB | Diagnose refs/objects before any history-cleaning proposal. |

The deleted tracked notebook is `load-adaptive-iir/notebooks/01_full_pipeline.ipynb`. The current uncommitted state also includes modified `.DS_Store`, `.gitignore`, result CSV/figure artifacts, cached bytecode, and source/test changes. A cleanup contract must not assume that an untracked file is disposable or that a tracked modification is accidental.

### 4.2 File composition and repository hygiene

The current checkout has approximately 125 tracked files totaling 9.2 MB, excluding Git history. At least 85 tracked files are repository-hygiene problems rather than durable source:

- 2 `.DS_Store` files;
- 39 Python cache/bytecode files;
- 42 generated result files;
- 2 tracked data files, including a raw archive and a processed Parquet file.

The current `.gitignore` is an uncommitted, narrow list. It ignores the entire `React-Frontend/` and `Isolated-Backend/` directories, specific local documents, one virtual environment, one pytest cache, and one test cache. It does not define a coherent policy for Python environments, Node dependencies, cache directories, raw/processed data, run artifacts, notebooks, operating-system files, or publication evidence. Ignoring both applications wholesale also means potentially important source can disappear from review.

Approximate directory costs observed during the audit:

- `load-adaptive-iir/`: 2.5 GB;
- `load-adaptive-iir/data/`: 1.9 GB;
- `load-adaptive-iir/env/`: 623 MB;
- `Isolated-Backend/`: 486 MB, almost entirely its virtual environment;
- `React-Frontend/`: 119 MB, almost entirely `node_modules/`;
- current generated results: about 3.4 MB.

These sizes are not evidence that source should be deleted. They are evidence that source, dependencies, data, and artifacts have not yet been separated.

### 4.3 Authentic data currently present

The workspace contains 155 Binance-style daily ZIP archives and 155 processed Parquet files across five symbols and 31 days in January 2024. The processed set contains approximately 73,830,561 rows and only two retained columns: `timestamp` and `price`.

Samples are structurally consistent with Binance public aggregate/trade downloads, but the current project has no authoritative acquisition manifest establishing, for every file:

- canonical source URL;
- acquisition timestamp;
- official checksum URL and expected checksum;
- locally computed checksum;
- HTTP status and byte count;
- symbol, date, market, and source schema version;
- applicable terms/license review;
- transformation code version;
- full raw-to-processed column mapping;
- exclusion and duplicate rules.

The official [Binance public data repository](https://github.com/binance/binance-public-data) documents an adjacent `.CHECKSUM` file for archives. The current loader does not retrieve or verify it. The repository’s MIT license covers that code repository; it must not be casually presented as the market data’s reuse license. Data terms and publication rights require a separate source-backed review.

The existing acquisition code also globally disables TLS certificate verification, swallows failures per day, and continues. During processing it discards fields such as trade identifiers and quantity before applying a duplicate rule on `timestamp` and `price`. That can collapse distinct trades that happen to share those retained values. Until a provenance contract re-acquires or verifies each archive and a schema contract reprocesses it, the local data is **quarantined authentic-looking input**, not certified publication evidence.

### 4.4 Test baseline

The current collected suite, including untracked tests visible in the working tree, was run in a headless/cache-isolated environment with Python bytecode and pytest caching disabled. The observed result was:

> `97 passed, 5 warnings in 168.38s`

The warnings include SciPy precision-loss/catastrophic-cancellation warnings in statistical tests. A prior invocation spent more than three minutes in import/cache initialization without reaching useful execution, and Matplotlib/font configuration attempted to use non-writable cache locations until redirected to `/private/tmp`.

This is a useful behavioral baseline, but it is not a scientific pass:

- many tests assert behavior around synthetic/random fixtures;
- passing tests do not validate the meaning of the statistical units;
- there is no clean-room dependency installation test;
- no CI configuration exists;
- there is no package/lock configuration that reproduces the audited environment;
- the tests do not prevent an experiment entry point from falling back to generated data.

The installed local environment is not a declared source of truth. The current `requirements.txt` is unpinned and omits `rrcf` even though the implementation imports it. Release dependencies need a supported-version policy and lock files generated from a reviewed `pyproject.toml`.

### 4.5 Static Factory audit baseline

The supplied Factory folder identifies itself as v2.2.0. Its built-in self-check found no declared implementation/specification drift in the implemented command and lifecycle checks. It also emitted nine heuristic warnings involving historical version references and unpadded identifiers in examples. Those warnings should be archived during bootstrap and assessed, but the rehabilitation must not modify the read-only Factory copy to silence them.

Factory auditing of the current DSP code found:

- **2 hard acquisition-audit failures:** `generate_synthetic_signal` and `simulate_backpressure`;
- **8 additional simulation/fabrication-language warnings** across the backend, anomaly injection, data expansion, experiments, and orchestration code;
- **15 hard lint-contract failures** for swallowed exceptions, including WebSocket handlers, a backend test, acquisition/expansion modules, experiments A/B/C, `fp_paradox.py`, multi-seed evaluation, and `run_all.py`.

These counts are baseline observations, not final scope. Chunk 01 must rerun the commands against the migrated source and drive hard failures in production/evidence paths to zero.

### 4.6 Missing project/release infrastructure

The audited repository has no authoritative root-level:

- `LICENSE`;
- `CITATION.cff`;
- contribution or security policy;
- CI workflow;
- `pyproject.toml` or equivalent complete build definition;
- dependency lock;
- pytest configuration;
- release manifest;
- data provenance/checksum manifest;
- artifact schema;
- automated claim-to-artifact check;
- clean-room reproduction command.

These absences do not all belong in Chunk 01. The roadmap below introduces them only when their governing decisions and evidence exist.

---

## 5. Audited scientific defects that the plan must resolve

The implementation is not merely incomplete. Several existing mechanisms make the current results unsuitable for publication. They are recorded here so no later cleanup accidentally preserves the conclusion while changing only the presentation.

### 5.1 Generated data and simulated-load contamination

The current top-level orchestration and experiments can:

- generate a synthetic DSP demonstration signal;
- substitute a random walk when authentic data loading fails;
- inject synthetic anomalies;
- simulate backpressure and bursts;
- generate synthetic multi-seed experiments;
- produce a dashboard stream that loops historical data, alters time semantics, injects anomalies, and presents it as “LIVE.”

The three main experiments and `fp_paradox.py` contain generated-data or simulated-load behavior. These paths must never be “disabled by default” and left available to release commands. They must be removed from the evidence package or isolated into non-release teaching material outside the authoritative experiment package. The safest publication configuration contains no such generators at all.

### 5.2 The current repetition count is not an independence count

The multi-seed evaluation reports 150 runs as 50 repetitions across three regimes, but asset-days are sampled with replacement, only about 96 unique asset-day combinations appear, and seed values are reused across regimes. Sorting a paired test by `seed` alone does not establish correct pairing by asset, day, regime, and run. These rows cannot be described as 150 independent trials.

The repaired study must define the experimental unit before execution, encode its identity in every row, and model repeated measurements explicitly. Resampling, if used, must resample real experimental units for uncertainty estimation rather than create pseudo-observations that are later counted as new data.

### 5.3 Current metric implementations are nonstandard

The prediction evaluator credits detections within a tolerance buffer as true positives while dividing recall by an unbuffered anomaly count and capping the result at one. The AUC implementation similarly mixes buffered labels with an unbuffered denominator, caps rates, and uses a nonstandard threshold approximation. Those values are not suitable for a conventional ROC-AUC/PR-AUC claim.

The replacement must use a pre-specified event-based or point-based definition, never a hybrid. If event tolerance is scientifically justified, it needs:

- a real event time and event interval definition;
- a matching policy that prevents one alarm from crediting multiple events;
- a false-alarm accounting window;
- an explicit detection-delay measure;
- a conventional implementation cross-checked against an independent library or reference script.

### 5.4 Evaluation leakage and calibration leakage

The rolling scale used by the adaptive detector includes the current observation. Fixed and RRCF thresholds are derived using the evaluation distribution, and no authoritative train/calibration/test temporal split exists. This attenuates or leaks the event being scored and makes comparative performance optimistic or uninterpretable.

All hyperparameters, thresholds, equivalence margins, buffer widths, and stopping rules must be frozen using training/calibration periods that precede the untouched evaluation period. Code must reject a configuration whose calibration range overlaps evaluation.

### 5.5 Statistical conclusions exceed the analysis

Current materials treat a non-significant difference near `p = .67` as “zero quality cost.” Failure to reject a difference is not evidence of equivalence. An equivalence or non-inferiority claim requires a justified practical margin, an appropriate test or confidence interval, power/sensitivity analysis, and a design that respects repeated measures and multiple comparisons.

Current files also disagree materially:

- one DeLong results file reports a result near `p = .003` while another narrative emphasizes a paired result near `p = .67`;
- one report cites an AUC deficit around `0.040`, while another generated summary shows a deficit around `0.0998`;
- throughput/resource improvements are reported with inconsistent values, including approximately `+92.6%` and `+76.1%`;
- `project_context.md` says the project is complete and pushed, even though the worktree and science are not release-ready.

No current result table or prose conclusion should be carried into the rehabilitated manuscript. They may be preserved only as legacy audit inputs.

### 5.6 DSP timebase and system-semantics problems

The market observations are irregularly timed trades, but current workflows apply fixed-rate DSP concepts using arbitrary sample-rate values such as 1 Hz or 100 Hz. Welch PSD estimates and ordinary discrete-time Butterworth/EMA comparisons require a meaningful sampling model. “One event equals one uniformly spaced sample” can be a valid event-time analysis, but it must not then be described as physical-frequency behavior in hertz or used to claim wall-clock response.

Chunk 04 must choose and document one of two valid strategies:

1. **Uniform-time representation:** aggregate authentic observations into declared, fixed, non-overlapping time bins with explicit empty-bin handling. Fabricated interpolation is not allowed. If a filter requires a value in an empty bin, the policy must be scientifically justified and sensitivity-tested; otherwise analyze only observed bins.
2. **Time-aware event representation:** use actual inter-arrival times, for example a continuous-time-constant mapping such as `alpha_i = 1 - exp(-Δt_i / τ_i)`, and use analysis appropriate to irregular samples rather than pretending the sequence has a fixed physical sample rate.

Additional semantic defects to resolve include:

- “adaptive pole” is sometimes used for `alpha`, although the pole is `1 - alpha`;
- an impulse demonstration uses warm-start behavior inconsistent with a zero-state impulse response;
- a constant-one step initialized at one produces no transition and therefore demonstrates little;
- KAMA’s first-step update and returned pole trace can disagree;
- a per-step frozen-time pole bound is not, by itself, a proof of global BIBO stability for the time-varying system;
- a fourth-order Butterworth is not automatically a fair comparator to a first-order EMA;
- changing `alpha` does not itself reduce arithmetic cost; the resource claim arises from shedding/skipping behavior and must be separated from filter adaptation.

### 5.7 Application truthfulness and security issues

The backend currently combines real historical rows with injected events and simulated load, loops the stream, and suppresses some exceptions. The frontend hardcodes a local WebSocket address and calls the stream “LIVE.” It retains template material and has no meaningful test coverage. CORS is broadly configured in a way that should not be released with credentials.

The application is optional. It should be rehabilitated only after the scientific pipeline is stable. If retained, it must say “historical replay,” show source and run provenance, distinguish observed fields from computed signals, use measured queue telemetry, and never show a generated anomaly as ground truth. If those conditions cannot be met within scope, the cleanest publication release omits the application.

---

## 6. Factory v2.2.0 operating model for this rehabilitation

The supplied Factory defines two primary roles and the Gatekeeper:

- **Architect:** converts evidence and project needs into project artifacts, chunks, contracts, invariant updates, reviews, and release decisions.
- **Implementor:** executes exactly one contract at a time within allowed files, runs declared verification, performs self-review, and writes the contract report.
- **Gatekeeper:** provides the implemented mechanical commands, but does not replace the Architect’s manual responsibilities where the specification declares an unimplemented gate.

The rehabilitation must use that model literally. A large informal “clean everything” implementation turn would bypass the exact controls this project needs.

### 6.1 Factory bootstrap policy

Use the exact supplied v2.2.0 snapshot as the reference. During execution, bootstrap from an immutable tag or reviewed commit, record its version/hash in `project/factory_info.*`, and archive the self-check output. Because `bootstrap.sh` is idempotent and gap-filling, it can safely create missing Factory structure after the legacy state is preserved. It must not be allowed to overwrite current project files by name without a disposition decision.

The Factory appends these outer ignore entries: `factory/`, `project/`, `bootstrap.sh`, `DROP_HERE/`, and `TAKE_THIS/`. The project-specific ignore policy in this plan extends that list.

### 6.2 Project Initialization occurs before Chunk 01

There is no rehabilitation Chunk 00. Factory Project Initialization is a lifecycle phase, not a chunk. It creates and freezes the project’s founding artifacts:

- `project/project_description.md`;
- `project/architecture.md`;
- `project/roadmap.md`;
- `project/project_knowledge.md`;
- `project/invariants.md`.

Because the intended result is an external release, initialization must also create:

- `project/venue_requirements.md`;
- `project/key_facts.md`;
- `project/methodology_adversarial_review.md`.

The target deliverable is presently ambiguous: there is an IEEE-style manuscript draft and a separate Kathmandu University format reference. Initialization must ask the Human to choose the primary target—for example, a KU project report plus public reproducibility repository, and optionally a later submission to a specifically named venue. The Factory requirement to study real venue rules and recent papers cannot be met by the label “IEEE” alone. Until a concrete venue is chosen, venue-specific claims and formatting remain blocked.

### 6.3 Proposed founding invariants

The final identifiers should be frozen in `project/invariants.md`; the following set is the minimum:

| ID | Invariant |
|---|---|
| `INV-DATA-001` | No fabricated, synthetic, simulated, injected, or silently substituted input may contribute to empirical evidence. |
| `INV-DATA-002` | External-source failure is fail-closed and produces a typed blocked state. |
| `INV-PROV-001` | Every input file is traceable to source, acquisition event, expected checksum, observed checksum, schema, and transformation. |
| `INV-PROV-002` | Every reported value is traceable to a run ID, input manifest, code commit, config hash, environment lock, and raw metric artifact. |
| `INV-TIME-001` | Every analysis declares whether its axis is event index or physical time; physical frequency claims require a valid timebase. |
| `INV-EVAL-001` | Calibration/training intervals never overlap evaluation intervals. |
| `INV-EVAL-002` | Experimental units and dependencies are explicit; duplicates/resamples are never counted as independent units. |
| `INV-STAT-001` | Non-significance is never reported as equivalence; multiplicity, uncertainty, and practical margins are pre-specified. |
| `INV-CLAIM-001` | No public claim exists without a claim-ledger row and verified supporting artifact. |
| `INV-ART-001` | Generated results are immutable per run; reruns receive new run IDs and never overwrite evidence. |
| `INV-REPRO-001` | The release reproduces from a clean clone using only tracked source plus declared authentic external artifacts. |
| `INV-DOC-001` | README, manuscript, tables, figures, UI labels, and machine-readable results cannot disagree on a metric or scope. |
| `INV-SEC-001` | Credentials, local paths, machine identity, and permissive development-only security settings do not enter the release. |
| `INV-HIST-001` | Legacy material is quarantined and labeled; migration history is not falsified. |

### 6.4 Scientific claim tiers

Factory contract tiers should be applied as follows:

- repository migration, packaging, and hygiene: claim tier `NONE`;
- authentic data inventory and descriptive coverage: `T-DESC`;
- detector/filter comparisons: at least `T-COMP`, requiring at least two defensible baselines and significance/uncertainty handling;
- a claim that adaptation *causes* compute, latency, or robustness improvement: `T-CAUSAL`, requiring at least three baselines, adversarial/ablation tests, and pre-registered stopping logic.

Contracts at `T-COMP` and `T-CAUSAL` must use the Factory’s mandatory mechanical gate: required verification commands, `verify-contract`, `lint-contract`, any independent `recompute` declaration, stamped reports, and `tier-check`. The Architect must manually perform the Reality Gate, Methodology Adversarial Review, allowed-file review, baseline completeness check, title-claim audit, and cross-contract supersession check where Gatekeeper v2.2.0 does not implement them.

---

## 7. Target repository architecture

The final outer repository should converge on the following structure. Exact file names may be refined by an Architecture Decision Record, but the separation of responsibilities is mandatory.

```text
DSP Mini Project/
├── .github/
│   └── workflows/
├── .gitignore
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── SECURITY.md
├── README.md
├── rehabilitation_plan.md
├── bootstrap.sh                     # local Factory helper; outer-gitignored
├── factory/                         # pinned Factory v2.2.0; outer-gitignored
├── project/                         # independent nested Git repo; outer-gitignored
│   ├── project_description.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── project_knowledge.md
│   ├── invariants.md
│   ├── venue_requirements.md
│   ├── key_facts.md
│   ├── methodology_adversarial_review.md
│   ├── legacy_intake/
│   ├── chunks/
│   └── evolution/
├── DROP_HERE/                       # outer-gitignored
├── TAKE_THIS/                       # outer-gitignored
└── source/                          # authoritative tracked product
    ├── pyproject.toml
    ├── uv.lock or equivalent lock
    ├── README.md
    ├── configs/
    │   ├── acquisition/
    │   ├── experiments/
    │   └── schemas/
    ├── src/
    │   └── load_adaptive_iir/
    │       ├── __init__.py
    │       ├── cli.py
    │       ├── core/
    │       ├── data/
    │       ├── runtime/
    │       ├── evaluation/
    │       └── reporting/
    ├── tests/
    │   ├── unit/
    │   ├── semantic/
    │   ├── integration/
    │   ├── scientific/
    │   └── fixtures/canonical/
    ├── scripts/
    │   ├── acquire/
    │   ├── verify/
    │   ├── reproduce/
    │   └── release/
    ├── artifacts/
    │   ├── README.md
    │   └── release/                  # only curated verified small evidence
    ├── docs/
    │   ├── manuscript/
    │   ├── ku_report/
    │   ├── reproducibility/
    │   └── decisions/
    └── app/                          # optional, only if Chunk 10 is approved
        ├── api/
        └── web/
```

### 7.1 Why retain the Python package name

The current package identity `load_adaptive_iir` should initially be retained inside `source/src/` to minimize import churn and preserve useful semantic history. “FlowGate DSP” can remain the project/product name. A package rename has little scientific value and creates unnecessary risk; it should happen only if Project Initialization identifies a naming conflict or publication requirement.

### 7.2 Data and artifact layout outside tracked source

Authentic datasets and run workspaces should use configurable paths outside `source/` or under ignored directories:

```text
data/
├── raw/                 # immutable downloaded bytes
├── staged/              # validated decompression/staging
└── processed/           # deterministic derivations

artifacts/runs/<run-id>/
├── run_manifest.json
├── input_manifest.json
├── environment.json
├── config.resolved.yaml
├── logs/
├── metrics/
├── traces/
└── figures/
```

The physical root is selected through a documented configuration/environment variable and recorded as a non-portable local path only in local logs, never in release artifacts. Release manifests reference checksums and portable logical identifiers. Large release inputs/results should be deposited in an appropriate archival service with a persistent identifier after licensing review; a README link is not a substitute for checksums and schema.

### 7.3 Product source versus Factory evidence

The outer repository must not contain Factory prompts, contract reports, raw deliberations, or mega-context files. Those belong in the nested `project/` repository. Conversely, implementation source, user documentation, packaging, tests, and selected release artifacts must not live only in `project/`; otherwise the public clone would be incomplete.

---

## 8. Pre-Chunk-01 Project Initialization procedure

This is a lifecycle prerequisite, not a hidden implementation chunk.

### 8.1 Preserve the legacy state before bootstrap

The Architect prepares a read-only intake package containing:

- `git status --short --branch` output;
- branch, HEAD, remote, tags, and worktree information;
- a list of tracked files and blob sizes;
- a list of modified/deleted/untracked paths without exposing secrets;
- hashes of modified tracked source and documents;
- directory-level counts and sizes for raw data, processed data, environments, results, backend, and frontend;
- the legacy test command, environment notes, result, duration, and warnings;
- Factory acquisition/lint audit outputs;
- a secret/local-path scan result;
- the precise disposition status `UNDECIDED` for every user-modified or deleted path.

This package belongs in `project/legacy_intake/` after bootstrap. Large data is not copied there; the package records paths, metadata, and hashes. Before creating a preservation commit or bundle, the Human must decide whether the current modifications are intended work, disposable generated changes, or partial experiments. Chunk 01 may not collapse that distinction.

### 8.2 Bootstrap and pin Factory v2.2.0

After the legacy state has been preserved:

1. Install/bootstrap Factory v2.2.0 idempotently into the existing outer repository.
2. Record the exact source snapshot, version, and bootstrap command.
3. Confirm `factory/`, `project/`, `source/`, `DROP_HERE/`, and `TAKE_THIS/` exist.
4. Confirm `project/` is an independent nested Git repository and the outer repo ignores it.
5. Run `python3 factory/gatekeeper.py self-check` and preserve complete output.
6. Classify each of the nine observed heuristic warnings as expected historical/example text or a real bootstrap concern; do not patch the Factory during project work.
7. Commit the completed initialization artifacts in the nested `project/` repository.

### 8.3 Founding-document reconciliation

The Architect must not copy `project_context.md`, the existing report, or a build prompt into the founding docs as if their claims were facts. Instead:

- `project_description.md` says the project is an incomplete legacy rehabilitation and names the no-synthetic objective.
- `architecture.md` records the target tree, evidence boundary, data flow, run manifest, and optional application boundary.
- `roadmap.md` contains the chunk sequence and dependencies from this plan.
- `project_knowledge.md` distinguishes verified knowledge, hypotheses, unresolved decisions, and invalid legacy claims.
- `invariants.md` freezes the invariants above.
- `key_facts.md` starts with only verified, source-backed facts; legacy performance values are excluded.
- `venue_requirements.md` uses a concrete target and current official requirements.
- `methodology_adversarial_review.md` must explicitly assess data authenticity, labels, baselines, statistical power, timebase, title/claim consistency, venue fit, assumptions, and the negative-result path.

Any FAIL in the Methodology Adversarial Review blocks scientific execution. It does not block Chunk 01’s preservation and repository rehabilitation if Chunk 01 is written so it cannot generate scientific evidence.

---

## 9. Chunk 01 — Forensic intake, Factory normalization, and truth firewall

**Chunk objective:** convert the dirty legacy repository into a losslessly preserved, Factory-native, buildable baseline in which authoritative source is separated from legacy material and no production/research path can generate or substitute empirical data.

**Scientific claim tier:** `NONE` for migration contracts; `T-DESC` only for the inventory report’s observed counts. No detector-performance, resource, robustness, or publication conclusion may be made in this chunk.

**Risk posture:** Medium overall, with High-risk review for any untracking, quarantine movement, acquisition behavior change, or code path whose accidental retention could contaminate later evidence.

**Explicit non-goals:** Chunk 01 does not validate the algorithm, preserve legacy metric values as authoritative, download/reprocess the full dataset, redesign the DSP equations, run final experiments, rehabilitate the UI, or write the final paper.

### 9.1 Required Chunk 01 artifacts

```text
project/chunks/chunk01/
├── chunk01.md
├── execution_manifest.yaml
├── contracts/
│   ├── C01-01_contract.md
│   ├── C01-02_contract.md
│   ├── C01-03_contract.md
│   ├── C01-04_contract.md
│   ├── C01-05_contract.md
│   ├── C01-06_contract.md
│   ├── C01-07_contract.md
│   └── C01-08_contract.md
├── reports/
│   └── C01-XX/
├── notes/
├── scripts/
├── data_manifest.json               # only if data is inspected as a contract input
├── reality_gate_report.md           # must say not yet passed for publication data
└── chunk_report.md
```

Every contract must declare allowed files, frozen files, exact verification commands, external service dependencies, owner, risk tier, scientific claim tier, trace-to requirements/invariants, and a fail-closed stop condition. Snapshot the chunk before Implementor work begins. Frozen verification machinery includes Factory-selected test and verifier paths.

### 9.2 C01-01 — Legacy state preservation and asset ledger

**Owner:** Architect for specification and final classification; Implementor may run read-only inventory scripts.  
**Risk:** Medium.  
**Claim tier:** `T-DESC` for literal observed counts only.

**Purpose:** create a trustworthy, lossless description of the starting state so later cleanup cannot erase user work or turn legacy outputs into unexplained artifacts.

**Implementation requirements:**

1. Capture the Git/worktree facts listed in §8.1.
2. Build `project/legacy_intake/asset_ledger.csv` with one row per meaningful path or homogeneous generated group and at least:
   - logical asset ID;
   - original path;
   - tracked/untracked/modified/deleted state;
   - type (`source`, `test`, `document`, `raw-data`, `processed-data`, `result`, `environment`, `cache`, `application`, `unknown`);
   - size and hash strategy;
   - authenticity state (`not-applicable`, `unverified-authentic`, `verified-authentic`, `generated`, `mixed`, `unknown`);
   - publication authority (`authoritative`, `candidate`, `legacy-only`, `forbidden-evidence`, `transient`);
   - proposed disposition;
   - Human decision required;
   - final migrated path, initially blank.
3. Store text diffs for modified tracked source/documents and metadata for binaries. Do not copy 1.9 GB of data into `project/`.
4. Record the current test result and all five warnings without interpreting them as scientific validation.
5. Record the two acquisition-audit failures, eight warnings, and fifteen lint failures.
6. Scan for secrets, tokens, personal local paths, email placeholders, and machine identity. The scan report may record locations but must redact secret values.
7. Request Human decisions for the deleted notebook and any ambiguous modified/untracked source.

**Stop conditions:** hash/read failure; evidence of secrets requiring containment; inability to distinguish user changes from generated changes; mismatch between path counts and captured ledger; any attempted deletion or automatic restoration.

**Verification evidence:** reproducible inventory script output, aggregate counts reconciling to Git/file-system observations, random spot-checks across every asset class, and an Architect sign-off that no cleanup occurred.

### 9.3 C01-02 — Factory bootstrap, repository isolation, and lifecycle baseline

**Owner:** Implementor; Architect reviews Factory consistency.  
**Risk:** Medium.  
**Claim tier:** `NONE`.

**Purpose:** establish the exact v2.2.0 structure without overwriting legacy content.

**Implementation requirements:**

1. Bootstrap from the pinned v2.2.0 snapshot using the Factory’s idempotent script.
2. Confirm all manifest-required files exist and record hashes/version.
3. Confirm `project/.git` is independent of the outer `.git` and that the outer ignore policy hides `project/`.
4. Initialize and commit the founding project artifacts in the nested repository.
5. Run Factory self-check and archive output in the contract report.
6. Run Gatekeeper status/next commands appropriate to the initialized state and verify Chunk 01 is the next planned chunk.
7. Create no implementation source beyond the empty/initial `source/` scaffold allowed by bootstrap.

**Stop conditions:** bootstrap proposes overwriting a non-empty current path; version is not exactly the reviewed snapshot; nested repository points at the outer Git directory; self-check reveals actual implementation/spec drift; current user files would be shadowed without a ledger decision.

**Verification evidence:** directory and Git-boundary assertions, self-check output, `git check-ignore` proof for Factory-private paths, and nested-repository log.

### 9.4 C01-03 — Legacy quarantine and file-by-file disposition

**Owner:** Architect specifies; Implementor moves only approved paths.  
**Risk:** High because user work and evidence classification are involved.  
**Claim tier:** `NONE`.

**Purpose:** separate what informs rehabilitation from what is allowed to ship.

**Implementation requirements:**

1. Apply the disposition matrix in §10 only after C01-01 decisions are complete.
2. Preserve legacy documents, result summaries, and build prompts under `project/legacy_intake/` when they are useful for audit. Mark every such copy `LEGACY — NON-AUTHORITATIVE` in an index.
3. Do not copy large raw/processed data or environments; retain ledger entries and hashes.
4. Move reusable source/tests into an explicit staging area for C01-04, preserving provenance from original path to destination.
5. Retain the frontend/backend only as quarantined candidates. Do not include them in the authoritative build yet.
6. Do not carry any legacy generated result into `source/artifacts/release/`.
7. Do not delete original paths in the same operation that creates the quarantine. First verify content/hash equivalence and receive Architect/Human approval.

**Stop conditions:** missing ledger row; hash mismatch; ambiguous source ownership; a mixed authentic/generated result that cannot be separated; attempt to label a legacy result authoritative; any deletion not explicitly allowed.

**Verification evidence:** source-to-destination manifest, checksums, absence of authoritative references to quarantined results, and a Human-reviewed list of paths still awaiting deletion/untracking.

### 9.5 C01-04 — Authoritative source scaffold and behavior-preserving migration

**Owner:** Implementor.  
**Risk:** Medium.  
**Claim tier:** `NONE`.

**Purpose:** create the clean `source/` product skeleton and migrate reusable code without silently changing scientific behavior.

**Implementation requirements:**

1. Create `source/pyproject.toml`, the `src/load_adaptive_iir/` package skeleton, categorized test directories, configuration/schema areas, artifact policy README, and command entry points.
2. Migrate core mathematical functions and tests in small, reviewable groups.
3. Preserve the legacy behavior baseline where it is not prohibited, but mark known semantic defects with failing/xfail specifications or quarantine them from authoritative entry points. Do not “fix” the timebase, metrics, or stability theory without Chunk 04/06 contracts.
4. Remove import-time plotting, acquisition, or experiment side effects.
5. Ensure all caches can be redirected outside the repository and package imports do not require data files.
6. Separate pure DSP code from data access, runtime control, evaluation, and reporting.
7. Introduce an explicit exception hierarchy and structured outcomes; no `except Exception: pass/continue` in authoritative paths.
8. Keep dependencies minimal. Add `rrcf` only if a later baseline decision retains it; do not preserve a dependency solely because legacy code imported it.

**Stop conditions:** a migration requires generated data to make tests pass; authoritative imports reach legacy folders; source behavior changes without an approved semantic requirement; dependency resolution is unrepeatable; test execution writes tracked files.

**Verification evidence:** build/install in a fresh temporary environment, import smoke tests, behavior comparison on permitted deterministic vectors, and proof that experiment commands cannot see legacy results/data implicitly.

### 9.6 C01-05 — Git hygiene and ignore policy

**Owner:** Implementor; Human approves untracking/destructive follow-up.  
**Risk:** High for untracking/history decisions, Medium for ignore edits.  
**Claim tier:** `NONE`.

**Purpose:** make Git contain durable product material and exclude machine-local/generated material without hiding source.

**Implementation requirements:**

1. Replace the ad hoc ignore list with the reviewed policy in §11.
2. Verify with `git check-ignore -v` that representative environments, caches, raw data, processed data, local run outputs, Factory-private paths, and frontend dependencies are ignored.
3. Verify tracked source, tests, configs, docs, application source, and curated release manifests are **not** ignored.
4. Produce—but do not automatically execute—a reviewed list for `git rm --cached` of tracked caches, `.DS_Store`, generated results, and data.
5. After Human approval, untrack without deleting local bytes. Verify the files still exist where retention is required.
6. Do not ignore `React-Frontend/` or `Isolated-Backend/` wholesale. Either migrate retained source to `source/app/` or keep the legacy directories quarantined until a later removal decision.
7. Measure new tracked file counts and clone size.
8. Diagnose `.git/` growth. Do not prune reflogs, delete refs, run `git gc --prune=now`, or rewrite history under this contract.

**Stop conditions:** an ignore pattern captures authoritative source/evidence; untracking would remove the only copy; unexpected Git object/ref behavior; command includes filesystem deletion; Human approval is absent.

**Verification evidence:** ignore matrix tests, tracked-ignored-path scan, clean status after approved commits, preserved local bytes for untracked data, and before/after size report.

### 9.7 C01-06 — Non-fabrication firewall and fail-closed interfaces

**Owner:** Architect for High-risk policy-critical implementation, or Implementor only after ambiguity is fully resolved in the contract.  
**Risk:** High.  
**Claim tier:** `NONE`.

**Purpose:** ensure later developers cannot accidentally revive synthetic evidence or silent fallback.

**Implementation requirements:**

1. Remove generated-data and simulated-backpressure functions from authoritative package and CLI reachability.
2. Delete fallback branches that replace missing authentic data with generated series.
3. Add a static verifier over authoritative source that rejects production/research references to prohibited concepts and APIs, with a narrow allowlist for explanatory text and deterministic canonical test vectors.
4. Add an import-boundary test proving `source/` does not import the legacy tree.
5. Add a release-boundary test proving experiment/report commands cannot load `tests/fixtures/canonical/`.
6. Define typed acquisition outcomes and a `BlockedExternalDependency`-style failure that maps to `BLOCKED — HUMAN ACTION REQUIRED`.
7. Define data-source and run-manifest schemas without claiming current data passes them.
8. Add test cases for unavailable network, missing archive, checksum mismatch, missing day, schema mismatch, partial decompression, and duplicate identity conflict. These tests use mocks/hand-built byte fixtures only to exercise failure control flow; they never become research inputs.
9. Run Factory `acquisition-audit` and `lint-contract` against authoritative source. Hard failures must be zero.
10. Record any terminology false positives and improve the verifier by explicit, reviewed rule—not by broad exclusion.

**Stop conditions:** any empirical command still has a generator/fallback; the verifier can be bypassed by a normal entry point; test fixtures can be loaded by experiments; external failure exits successfully; production catches an exception without structured propagation.

**Verification evidence:** negative tests for every prohibited path, static audit output, CLI exit-code tests, import graph, and Architect code review.

### 9.8 C01-07 — Deterministic build, test, and CI baseline

**Owner:** Implementor.  
**Risk:** Medium.  
**Claim tier:** `NONE`.

**Purpose:** make mechanical correctness repeatable before scientific changes begin.

**Implementation requirements:**

1. Select supported Python versions and OS scope.
2. Create a complete build definition and deterministic lock workflow.
3. Configure pytest markers for unit, semantic, integration, scientific, external-data, and slow tests.
4. Redirect Matplotlib, Numba, pytest, and other caches to CI/temp locations.
5. Disable accidental network access in ordinary unit tests.
6. Add lint, format-check, type-check, package-build, unit-test, static non-fabrication audit, and secret/local-path scan jobs.
7. Establish a migration baseline mapping each of the 97 observed legacy tests to `retained`, `rewritten`, `retired-invalid`, or `blocked`.
8. Do not require synthetic/random tests merely to preserve a count of 97. Coverage is semantic, not numerical.
9. Preserve statistical precision warnings as failing scientific-test issues or explicit, bounded expected warnings; do not blanket-suppress them.
10. Test installation and core execution from a clean checkout with no legacy directories present.

**Stop conditions:** lock cannot reproduce; tests depend on current virtual environments/data; package import writes into source; warnings are globally suppressed; a retired invalid test leaves a corresponding requirement untested.

**Verification evidence:** CI-equivalent local command log, clean temporary-environment install, test-disposition ledger, build artifact inspection, and no new workspace modifications after tests.

### 9.9 C01-08 — Chunk integration, review, and baseline certification

**Owner:** Architect.  
**Risk:** Medium.  
**Claim tier:** `NONE`.

**Purpose:** integrate the previous contracts and decide whether scientific rehabilitation may proceed.

**Review checklist:**

- compare the final tree to the target architecture;
- verify no user work was lost and every moved path is in the ledger;
- verify outer and nested repositories are both in understood, committed states;
- rerun Factory self-check, `release-check` as an early diagnostic, acquisition audit, contract lint, contract verification, stamp verification, and tier check as applicable;
- verify all eight contract reports against their artifacts;
- review allowed-file diffs manually because allowed-file enforcement is not fully implemented by Gatekeeper;
- confirm legacy results are unreachable and visibly non-authoritative;
- confirm the Reality Gate is still **not passed** for publication data and no text says otherwise;
- confirm no performance number from the old reports has entered `key_facts.md`;
- confirm Chunk 02’s open scientific decisions and stop conditions are explicit.

**Chunk 01 pass criteria:**

1. Factory v2.2.0 is pinned and operational.
2. Founding artifacts are committed in the nested `project/` repository.
3. `source/` is the only authoritative code surface.
4. The package builds and tests from a clean temporary environment.
5. Production/research source has zero synthetic generators, simulated-load evidence paths, silent fallbacks, or swallowed-exception hard failures.
6. Legacy data/results/documents are preserved but cannot be consumed implicitly.
7. Git ignores transient material without hiding product source.
8. The current dirty-state assets have a completed disposition; no user work was lost.
9. Every report is stamped/verified as required and the chunk report records limitations.
10. The next action is Chunk 02, not an experiment run.

If any criterion fails, the Architect writes a bounded fix package. No later chunk may work around a failed truth-firewall criterion.

---

## 10. Legacy file disposition matrix

This matrix is the default proposal for C01-03. “Quarantine” means preserve a copy or hash-backed record in the nested Factory project, clearly marked non-authoritative; it does not mean silently delete the original. A Human-approved ledger row controls the actual disposition.

| Current path or group | Current role/problem | Proposed destination | Final disposition |
|---|---|---|---|
| `.DS_Store` files | OS metadata, some tracked/modified | none | Untrack, delete from product tree after preservation is unnecessary, and ignore globally. |
| `.pytest_cache/`, `__pycache__/`, `*.pyc` | Machine-generated caches, many tracked | none | Untrack and ignore; CI proves they are recreated outside tracked source. |
| `.remote-code-express/` | Tool/machine-local state | none | Inspect for user data/secrets, then ignore or remove locally with approval. |
| Root `.gitignore` | Incomplete and currently modified | outer root | Replace through C01-05 only after its uncommitted diff is captured. |
| `build_mega_context.py` | One-off context assembly, not product functionality | `project/legacy_intake/tools/` if audit-useful | Remove from public source after hash/copy verification. |
| `dsp_project_build_prompt.md` | Legacy prompt/specification input | `project/legacy_intake/requirements/` | Preserve as historical input; do not present as current architecture. |
| `fix1.md` | Legacy repair instructions/notes | `project/legacy_intake/notes/` | Preserve only if it explains current changes; otherwise ledger and remove. |
| `mega_report_context.md` | Generated/assembled narrative context | `project/legacy_intake/documents/` | Mark non-authoritative; never use as a source of facts. |
| `project_context.md` | Stale “complete” claims and metric narrative | `project/legacy_intake/documents/` | Quarantine; do not migrate assertions into `key_facts.md`. |
| `study.md` | Valuable adversarial observations mixed with unverified proposals | `project/legacy_intake/reviews/` | Mine each issue into requirements/decisions; independently verify citations and facts. |
| `load_adaptive_iir_literature_review.md` | Literature summary of uncertain provenance/currentness | `project/legacy_intake/literature/` | Use as a search lead only; verify every cited primary source before reuse. |
| `report_v2.tex` | Legacy IEEE-style manuscript with placeholders and inconsistent results | `project/legacy_intake/manuscripts/` | Quarantine, never patch into the final paper line by line. Rebuild from claim ledger later. |
| `ku_format.md` | Possible institutional formatting requirement | `project/legacy_intake/venue_inputs/` and then verified venue requirements | Preserve; verify against current official KU guidance before treating it as binding. |
| `load-adaptive-iir/README.md` | Useful project intent mixed with simulated/synthetic claims | `project/legacy_intake/documents/` plus newly written `source/README.md` | Rewrite from verified scope; do not copy performance claims. |
| `load-adaptive-iir/requirements.txt` | Unpinned/incomplete dependency declaration | legacy intake; replaced by `source/pyproject.toml` and lock | Retire after clean install equivalence is demonstrated. |
| `load-adaptive-iir/src/filters.py` | Candidate core DSP logic with semantic issues | `source/src/load_adaptive_iir/core/` | Migrate, preserve behavior baseline, repair only under Chunk 04 contracts. |
| `numba_filters.py` | Candidate optimized implementation | `source/.../core/` or retire | Retain only if parity, supported versions, warm-up policy, and measured benefit pass. |
| `calibration.py` | Candidate calibration logic with leakage/fairness concerns | `source/.../evaluation/` | Quarantine APIs until temporal split and baseline protocol are frozen. |
| `detection.py`, `rrcf_detector.py` | Candidate detectors with threshold/leakage concerns | `source/.../evaluation/` | Retain only behind non-authoritative API until Chunk 06; RRCF inclusion is a baseline decision. |
| `load_shedding.py` | Candidate runtime policy | `source/.../runtime/` | Migrate core policy; validate against measured queue telemetry in Chunk 05. |
| `data_acquisition.py` | Authentic-source intent with TLS/checksum/silent-failure defects | reference for `source/.../data/` rewrite | Replace with fail-closed acquisition; do not perform a superficial migration. |
| `data_expansion.py` | Processing plus arbitrary regime definitions and swallowed failures | reference for data/evaluation rewrite | Split deterministic transforms from scientific classifications; remove arbitrary regimes until justified. |
| `downstream_cost_measurement.py` | Candidate measurement intent | `source/.../runtime/` | Retain only if it measures actual processes with controlled protocol; otherwise replace. |
| `evaluate.py` | Nonstandard metrics | legacy intake plus a new tested evaluation module | Do not preserve numeric compatibility; replace with pre-specified standard/event metrics. |
| `delong.py`, `statistical_tests.py` | Candidate statistics with conflicting artifacts/warnings | `source/.../evaluation/` after independent validation | Cross-check against trusted implementation and exact unit definitions before use. |
| `zdomain_analysis.py` | Candidate analytical material | `source/.../core/` or `source/docs/` | Retain after correcting frozen-time/global-stability and initial-condition claims. |
| `visualize.py` | Figure generation mixed with legacy outputs | `source/.../reporting/` | Rewrite as artifact-consuming pure reporting; figures never recompute hidden metrics. |
| `demo_signals.py`, `anomaly_injection.py` | Fabricated input generation | no authoritative destination | Remove from publication/research package. At most retain descriptions in legacy intake. |
| `queue_simulator.py` | Simulated runtime evidence | no authoritative destination | Remove from evidence package; replace with a real bounded-queue harness. |
| `experiment_a_compute_cost.py` | Generated fallback and weak cost attribution | legacy intake; new protocol in later chunks | Replace; no old numeric continuity requirement. |
| `experiment_b_throughput_stability.py` | Simulated queue/throughput model used as evidence | legacy intake; measured runtime experiment later | Replace completely for empirical claims. Analytical queue theory, if retained, must be labeled theory and checked separately. |
| `experiment_c_pareto.py` | Synthetic anomalies/load, mixed metrics | legacy intake; pre-registered real experiment later | Replace completely. |
| `fp_paradox.py` | Synthetic fallback/injection/simulation | legacy intake | Do not migrate to authoritative source. Reintroduce a hypothesis only if real evidence motivates it. |
| `multi_seed_evaluation.py` | Pseudo-replication and synthetic experiments | legacy intake | Replace with an explicit experimental-unit runner; “seed” is not the unit. |
| `run_all.py` | Orchestrates generated demo/fallbacks and overwrites results | legacy intake | Replace with typed CLI commands; no monolithic run that silently changes modes. |
| `isolate_timing.py` | One-off timing aid | `source/scripts/` only if protocol-compliant | Review; use a proper benchmark harness with metadata and repetitions. |
| `recompute_delong_subset.py` | Possible independent check but likely coupled to legacy artifacts | legacy intake | Rebuild independent recomputation from frozen raw predictions; enforce different implementation hash. |
| Current 14 test modules | Mixed useful semantics and synthetic assumptions | categorized `source/tests/` | Map one by one. Retire invalid premises; do not preserve the test count as a goal. |
| Deleted notebook `notebooks/01_full_pipeline.ipynb` | User-deleted tracked file, state ambiguous | pending Human decision | Preserve deletion intent/diff first. If retained, notebooks are exploratory and cannot be the only reproduction path. |
| Other notebooks | Exploratory, potentially output-heavy | `source/notebooks/` only if justified; outputs stripped | Prefer executable scripts/docs; no embedded result becomes authoritative. |
| `load-adaptive-iir/data/raw/` | Large local source archives, not provenance-certified | ignored external/local data root | Do not copy into Git. Verify/reacquire checksums in Chunk 03. |
| `load-adaptive-iir/data/processed/` | Large derived cache with lossy schema | ignored external/local data root | Rebuild deterministically after raw verification; old Parquet is quarantine-only. |
| `load-adaptive-iir/results/` | 42+ tracked/generated artifacts with contradictions | `project/legacy_intake/results_manifest/` plus local quarantine | Hash/index, mark invalid for citation, untrack, and regenerate later under immutable run IDs. |
| Local Python environments (`env/`, `.myenv/`, backend env) | Hundreds of MB of machine-local dependencies | none | Ignore and remove locally only after reproducible lock/install succeeds. |
| `Isolated-Backend/main.py` | Optional demo with injection/simulation/looping/security issues | quarantine; possibly `source/app/api/` in Chunk 10 | Do not migrate into authoritative release in Chunk 01. |
| `Isolated-Backend/test.py` | Weak backend test with swallowed exception | legacy intake | Replace if app retained. |
| `Isolated-Backend/requirements.txt` | Separate unpinned environment | legacy intake | Consolidate under reviewed workspace/dependency strategy if app retained. |
| `React-Frontend/src/` and config | Optional UI source, currently wholesale ignored | quarantine; possibly `source/app/web/` in Chunk 10 | Preserve source and lock file; exclude template cruft and generated dependencies. |
| `React-Frontend/node_modules/` | Recreated dependency tree | none | Ignore and remove locally after lock-based install proof. |
| Frontend template README/assets/styles | Boilerplate or dead assets | none or app docs if still used | Remove only after app-specific asset/reference audit. |

### 10.1 Rules for deleting legacy paths

A legacy path may be deleted from the working tree only when all of these are true:

1. its ledger row is complete;
2. the Human approved the class or exact path;
3. any required quarantine copy/hash is verified;
4. migrated behavior/source is independently confirmed where applicable;
5. no current Git modification would be lost;
6. a recovery mechanism is named;
7. the contract allowed files and command include that path explicitly.

Untracking is separate from deleting. For data/results/caches that should remain locally, use an approved index-only removal such as `git rm --cached` and verify local bytes remain. No broad recursive delete rooted at the workspace or an unresolved environment variable is acceptable.

---

## 11. Proposed `.gitignore` policy

The final file should be generated/reviewed in C01-05, not copied blindly from this plan. The important property is that it ignores categories, not product directories.

```gitignore
# Software Factory private/local infrastructure
factory/
project/
bootstrap.sh
DROP_HERE/
TAKE_THIS/

# Operating-system and editor metadata
.DS_Store
Thumbs.db
*.swp
*.swo
*~
.idea/
.vscode/
.remote-code-express/

# Secrets and machine-local configuration
.env
.env.*
!.env.example
*.pem
*.key

# Python bytecode, tooling, and environments
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/
.venv/
venv/
env/
.myenv/
build/
dist/
*.egg-info/
.ipynb_checkpoints/

# Native/accelerator/tool caches
.numba_cache/
.matplotlib/
.cache/

# JavaScript dependencies and build outputs
node_modules/
.vite/
coverage/
source/app/web/dist/

# Authentic local data and deterministic caches
data/raw/
data/staged/
data/processed/
source/data/raw/
source/data/staged/
source/data/processed/
*.parquet
*.feather

# Local experiment workspaces and uncurated outputs
artifacts/runs/
source/artifacts/runs/
source/artifacts/work/
*.prof

# Logs and local process state
*.log
*.pid
```

Important exceptions/policies:

- Do **not** ignore every `.zip` or `.csv` globally. Source/config fixtures, citation metadata, and curated release tables can legitimately use those extensions. Put large data under ignored data roots instead.
- Do **not** ignore all `results/` paths globally. The project should have an intentionally tracked `source/artifacts/release/` containing only verified small outputs and manifests. Ordinary outputs live under ignored `artifacts/runs/`.
- Do **not** ignore all notebooks globally. If a reviewed notebook is part of documentation, track its source with cleared outputs and a paired script where practical.
- Do **not** ignore `React-Frontend/` or `Isolated-Backend/` by name. Whole-directory ignores conceal source. Ignore their dependency/build/cache subdirectories or quarantine/remove the legacy directory explicitly.
- `.gitignore` does not remove already tracked files. Index cleanup requires an explicit reviewed contract.

### 11.1 Mechanical ignore verification

C01-05 should encode a table-driven test equivalent to:

- expected ignored: `.DS_Store`, `__pycache__/x.pyc`, `.venv/bin/python`, `node_modules/x`, `data/raw/sample.zip`, `data/processed/sample.parquet`, `artifacts/runs/test/metrics.json`, `factory/VERSION`, `project/invariants.md` from the outer repository;
- expected tracked/trackable: `source/src/load_adaptive_iir/core/filter.py`, `source/tests/unit/test_filter.py`, `source/configs/experiments/final.yaml`, `source/artifacts/release/README.md`, `source/docs/manuscript/main.tex`, `source/app/web/src/App.tsx` if the app is retained.

Also fail if `git ls-files -ci --exclude-standard` returns a path without an explicit migration ledger entry.

---

## 12. Chunk roadmap after Chunk 01

The sequence below is dependency-ordered. Chunks may be split when a plan becomes too large, but they must not be merged in a way that places data acquisition, semantic correction, experimental design, execution, and publication into one review boundary.

### Chunk 02 — Scientific scope, venue, literature, and feasibility freeze

**Objective:** turn the broad legacy concept into a defensible research question and a negative-result-safe plan before acquiring or analyzing evidence.

**Key contracts:**

1. **Venue and deliverable decision (`T-DESC`, Medium):** identify the exact KU/report requirements and, if intended, the exact external venue; archive current official author instructions, data/code policy, formatting, page limits, disclosure rules, and deadlines. Study at least three recent relevant papers from the actual venue using primary sources.
2. **Literature verification (`T-DESC`, Medium):** independently retrieve and verify every reference intended for the paper. Build a bibliography ledger containing DOI/URL, venue, year, exact proposition supported, and quotation/paraphrase notes. The legacy literature review is only a search seed.
3. **Research-question and title ladder (High):** define a conservative title, a stronger title available only after specified gates, and forbidden claims. Separate DSP behavior, runtime control, and anomaly-detection questions.
4. **Real-label feasibility (High, `T-DESC`):** evaluate legally usable sources of authentic event labels. Official LOBSTER documentation describes event type 7 as halt/resume events, and [LOBSTER’s sample-data page](https://data.lobsterdata.com/info/DataSamples.php) describes available sample formats, but access, license, symbol/date coverage, and event prevalence must be verified. Nasdaq’s [historical halt page](https://www.nasdaqtrader.com/trader.aspx?id=TradingHaltHistory) and [halt reason codes](https://beta.nasdaqtrader.com/Trader.aspx?id=TradeHaltCodes) are candidates, not assumed approvals.
5. **Data-rights review (High):** distinguish downloader code license, source terms, dataset redistribution rights, and publication citation duties.
6. **Adversarial methodology review refresh (Architect):** resolve or fail data authenticity, baseline sufficiency, statistical power, timebase, title/claim consistency, assumption stress, and negative-result contingency.

**Critical decision gate:**

- If a real labeled-event source has sufficient occurrences, timestamp alignment, negative periods, legal use, and acquisition reproducibility, the project may retain an anomaly-detection evaluation as a secondary or primary question.
- If it does not, anomaly ground-truth claims are removed. The project studies filter behavior and measured runtime/resource trade-offs on authentic streams. It does not inject events, label volatility heuristically, or substitute a different synthetic benchmark.

**Exit criteria:** exact venue chosen or external submission explicitly deferred; research questions frozen; claim ladder approved; real-label feasibility decided; bibliography ledger source-backed; MAR passes; Chunk 03 source list and rights constraints are explicit.

### Chunk 03 — Trusted acquisition, provenance, schema, and Reality Gate

**Objective:** create immutable, checksum-verified authentic input and deterministic processing without silent gaps.

**Scientific tier:** `T-DESC`; this chunk may describe source coverage but may not make performance claims.

**Key contracts:**

1. **Acquisition protocol:** HTTPS verification remains enabled; retrieve official archive/checksum pairs; store response metadata; use bounded retries that do not convert failure to success; use temporary files plus atomic finalize; reject redirects to unexpected hosts unless allowed.
2. **Provenance schema:** implement the Factory `data_manifest.json` and `acquisition_provenance.json` requirements, including request-level evidence and human spot-check fields.
3. **Raw validation:** verify expected checksum before decompression, archive structure, schema, date/symbol consistency, monotonic/valid timestamps, trade identity, numeric domains, record count, and duplicate identity.
4. **Full-fidelity staging:** retain raw source fields necessary for identity and later analysis. Do not reduce to timestamp/price before duplicate resolution and provenance checks.
5. **Deterministic transformation:** schema-versioned transform; content-addressed processed outputs; exact exclusion reasons; no in-place overwrite; input/output hashes and row-count accounting.
6. **Coverage report:** expected versus acquired days/assets/events, gaps, source errors, and rights status. An incomplete expected set is a failure unless the study design predeclares that exact partial set.
7. **Reality Gate:** Architect performs source/authenticity, schema/properties, coverage, and provenance checks and conducts Human spot checks against official URLs/checksums.

**Legacy-data treatment:** use local January 2024 files only as candidates. For each archive, verify against an official checksum and provenance URL or re-acquire it. If an old processed file cannot be reproduced byte-for-byte under the corrected schema, discard it as a cache and regenerate. Do not claim the current 73,830,561 processed rows are certified until row accounting passes.

**Exit criteria:** Reality Gate PASS for the exact dataset version, or blocked status with no downstream run. A signed dataset manifest becomes a frozen input to later chunks.

### Chunk 04 — DSP core semantic correction and analytical validation

**Objective:** make the filter definitions mathematically explicit, timebase-correct, and independently tested before comparative experiments.

**Scientific tier:** `T-DESC` for mathematical properties; any comparative bandwidth statement is at least `T-COMP`.

**Key contracts:**

1. **State/initial-condition specification:** define zero-state, warm-start, missing-observation, reset, and chunk-boundary behavior for every filter.
2. **Canonical semantic tests:** analytically derived impulse, step, constant, alternating, and short sequence tests; streaming versus batch parity; chunk-boundary parity; dtype/NaN/Inf policy; Numba/reference parity if Numba remains.
3. **Timebase decision:** implement either fixed-bin authentic aggregation or actual-`Δt` filtering. Ban arbitrary `fs=1`/`fs=100` defaults in evidence paths. Every output records unit semantics.
4. **Coefficient/pole terminology:** use `alpha` for smoothing coefficient and `p = 1 - alpha` for the pole; correct UI/docs/APIs.
5. **Stability analysis:** distinguish `0 < alpha_i ≤ 1` per-step contraction, bounded input/state behavior, rate constraints, and frozen-time response. Obtain an independent derivation/review for any global claim.
6. **KAMA trace correction:** make the first update and returned coefficient/pole trace agree; specify efficiency-ratio warm-up.
7. **Baseline matching:** define fair comparison criteria (equivalent cutoff, equivalent effective memory, order/latency constraints) before selecting EMA, KAMA, Butterworth, RRCF, or other baselines. A fourth-order filter is not a default fair comparator to a first-order filter.
8. **Independent reference verifier:** implement a small clear reference formulation separate from the optimized code and compare deterministic outputs/tolerances.

**Exit criteria:** semantic suite passes in clean room; no arbitrary physical sampling rate; analytical claims have bounded wording; optimized and reference implementations agree; baseline parameterization is frozen for pilot use.

### Chunk 05 — Real replay and measured backpressure/runtime harness

**Objective:** replace queue simulation with actual execution telemetry while keeping every input event authentic.

**Scientific tier:** initial harness validation `T-DESC`; comparative runtime hypotheses in later chunks are `T-COMP`/`T-CAUSAL`.

**Key contracts:**

1. **Bounded-queue pipeline:** real producer, bounded queue, consumer/filter, downstream computation, structured trace events, and clean termination. Queue depth and lag are read from the actual process, not calculated by a queue simulator.
2. **Replay schedule:** derive schedules only from authentic records. Time compression is allowed if declared as a deterministic transformation of observed timestamps. Concurrent replay may use distinct authentic shards; it must not duplicate one shard and count copies as new observations.
3. **Open-loop protocol:** replay an immutable recorded arrival schedule identically across methods for paired comparison.
4. **Closed-loop protocol:** run complete systems with randomized method order, declared warm-up/cooldown, resource isolation, repetition policy, and the same logical input coverage.
5. **Telemetry:** monotonic timestamps, enqueue/dequeue times, queue depth, consumer lag, processed/skipped records, CPU time, wall time, peak RSS, allocations if reliable, hardware/OS/runtime metadata, and process failures.
6. **Load policy semantics:** distinguish adaptive filtering from load shedding. Report compute savings from skipped/deferred work as a runtime-policy effect, not a consequence of changing a first-order coefficient.
7. **Integrity accounting:** every input record ends in exactly one declared state such as processed, shed by rule, rejected before run, or failed. No loss is implicit.

**Prohibited:** `simulate_backpressure`, generated burst intervals, sleeps chosen to manufacture queue instability, edited queue traces, and calling a replay “live.”

**Exit criteria:** known-small authentic replay passes full accounting; repeated harness runs emit valid manifests; telemetry is self-consistent; a no-op/reference consumer establishes overhead; no comparative conclusion is yet published.

### Chunk 06 — Pre-registered evaluation and statistical analysis protocol

**Objective:** freeze how experiments will answer the research questions before looking at final comparative results.

**Scientific tier:** the protocol governs `T-COMP` and possibly `T-CAUSAL` claims.

**Key contracts:**

1. **Experimental unit:** define asset-day, event episode, replay shard, machine-run, or another defensible unit; encode a globally unique unit ID. Document nesting/repeated measures.
2. **Temporal partitioning:** freeze training/calibration/pilot/final periods with non-overlap and leakage checks. If cross-validation is used, it must respect time and grouped units.
3. **Outcome definitions:** filtering fidelity, latency, compute/resource, shedding, false alarms, detection delay, and any AUC/event metric are specified mathematically with units and edge cases.
4. **Real-label alignment:** if labels passed Chunk 02/03, define timestamp timezone, event interval, symbol mapping, tolerance, matching, censored periods, and negative-window rules. Otherwise remove all label-dependent outcomes.
5. **Baseline set:** at least two baselines for `T-COMP`; at least three plus ablations/adversarial tests for `T-CAUSAL`. Include a no-adaptation/no-shedding reference and separate adaptation-only from shedding-only variants.
6. **Power/sensitivity:** estimate detectable effect based on real pilot variance and independent units. Do not generate a target sample by duplicating units. State what happens if power is inadequate.
7. **Equivalence/non-inferiority:** define a domain-justified margin before final results if “no quality cost” is desired. Otherwise use descriptive uncertainty and avoid equivalence wording.
8. **Multiplicity/model:** specify primary outcome, secondary outcomes, corrections, paired/grouped model, random effects or cluster-robust approach where necessary, diagnostics, missing-run handling, and exact confidence interval method.
9. **Stopping/retry policy:** predeclare infrastructure retry conditions, failed-run inclusion, no optional stopping, no post-hoc regime creation, and no cherry-picking.
10. **Metric verifier:** compare primary metric outputs to an independent implementation on frozen small real predictions/labels; reject degenerate all-equal/all-one behavior.

**Exit criteria:** protocol, analysis code interfaces, and configs are frozen and hash-stamped before final data is opened; title/claim audit passes; the negative-result and no-label paths are explicit.

### Chunk 07 — Pilot on authentic data and measured telemetry

**Objective:** prove the entire pipeline works on a small predesignated non-final subset and use only pilot evidence to finalize operational tolerances.

**Scientific tier:** `T-DESC`; pilot comparative numbers are not final claims.

**Key contracts:**

1. Execute acquisition-manifest selection, processing, filtering, replay, telemetry, evaluation, artifact writing, and report generation end to end.
2. Verify exact record accounting and run-manifest completeness.
3. Measure runtime variance and refine run counts only according to the predeclared power procedure.
4. Test every failure path: unavailable input, checksum mismatch, interrupted run, partial output, metric degeneracy, and report/artifact disagreement.
5. Perform ablation smoke tests that distinguish filter adaptation from shedding.
6. Run independent recomputation on pilot artifacts.
7. Freeze final configs and seal off pilot data from the final evaluation if the design requires it.

**Stop conditions:** unexplained record loss; unstable environment; pilot-dependent favorable metric redefinition; result overwrite; invalid real-label alignment; evidence checker/report mismatch; insufficient genuine units.

**Exit criteria:** full artifact lineage works; final run matrix is feasible and frozen; pilot limitations are recorded; no pilot result appears in abstract/conclusion.

### Chunk 08 — Final real-data experiment execution

**Objective:** run the frozen experiment matrix on authentic observations and real runtime telemetry without interactive result-driven changes.

**Scientific tier:** `T-COMP` for comparisons; `T-CAUSAL` only for the pre-registered causal/ablation question.

**Key contracts:**

1. Materialize immutable run configs and input manifests.
2. Execute randomized/paired run order with hardware/environment capture.
3. Write every attempt to a unique run ID; do not overwrite failed or unfavorable runs.
4. Apply only predeclared infrastructure retries and preserve original attempts.
5. Seal raw predictions, traces, labels, record-accounting output, and environment metadata before aggregate analysis.
6. Check expected-versus-observed unit coverage before any statistic.
7. Run Factory mandatory mechanical gates for each comparative contract.

**Exit criteria:** all planned units are present or handled exactly by the missingness rule; hashes and stamps verify; no config changed after seeing outcomes; raw run package is independently readable.

### Chunk 09 — Independent recomputation, statistics, and claim ledger

**Objective:** convert frozen raw run evidence into defensible results and prevent report/artifact contradictions.

**Key contracts:**

1. **Independent recomputation:** a separately implemented script reads sealed raw artifacts and recomputes each primary statistic. Factory `recompute` must confirm the verifier is not the same script/hash as the producer.
2. **Primary analysis:** execute the pre-registered grouped/paired model and uncertainty intervals; preserve diagnostics and exclusions.
3. **Multiplicity and secondary outcomes:** apply the frozen correction/hierarchy; label exploratory findings.
4. **Equivalence decision:** use the frozen margin/test. If not passed, remove “no quality cost,” even if the ordinary difference test is non-significant.
5. **Ablation/adversarial analysis:** distinguish coefficient adaptation, shedding, calibration, timebase choice, and baseline selection. Challenge the strongest causal interpretation.
6. **Claim ledger:** create one row per prospective public claim with artifact pointer, values, units, CI, test, population, limitations, wording ceiling, and status.
7. **Evidence consistency:** run `evidence-check`; apply cross-contract metric supersession rules; flag degenerate metrics; stamp reports.

**Possible valid outcomes:**

- adaptation plus shedding improves a predeclared resource metric within a supported fidelity margin;
- it improves resources but fails the fidelity margin, requiring a trade-off conclusion;
- adaptation does not improve resources after harness overhead;
- some baselines dominate;
- labels are too sparse for detector conclusions;
- the study is a negative result.

All are acceptable scientific outcomes. None authorizes fabricated augmentation.

**Exit criteria:** every candidate claim is supported, narrowed, or rejected; independent recomputation agrees; tables/figures are generated only from verified aggregates; the strongest surviving title is selected from the predeclared ladder.

### Chunk 10 — Optional historical-replay application rehabilitation

**Objective:** either build an honest, tested demonstration from verified artifacts or omit the app from the publication release.

**Entry gate:** Chunk 09 evidence and schemas are stable, and the Human confirms an app is worth the maintenance/release surface.

**If retained:**

- migrate API and web source under `source/app/`;
- serve only verified historical replay or an explicitly separate genuine live connector;
- label historical data as “historical replay,” never “LIVE”;
- show dataset/run IDs, symbol, observed time, replay speed, queue telemetry, and whether an output is observed, derived, or a model alarm;
- do not inject anomalies or fabricate load;
- do not loop a stream without a visible restart boundary;
- use configurable WebSocket/HTTP endpoints;
- define authentication/deployment scope and safe CORS;
- add API schema tests, WebSocket lifecycle tests, frontend tests, accessibility checks, disconnect/backpressure behavior, and dependency/security scans;
- ensure the app reads immutable artifacts or approved pipeline output and cannot mutate release evidence.

**If omitted:** remove legacy app source from the public release after preservation and explain that the project is a reproducible research package, not a live-monitoring product.

### Chunk 11 — Manuscript, KU report, documentation, and reproducibility package

**Objective:** write public material from the verified claim ledger rather than editing the legacy narrative into consistency.

**Key contracts:**

1. Draft methods from frozen protocol/config/schema artifacts.
2. Generate tables/figures from verified release aggregates with stable captions, units, sample/unit counts, and uncertainty.
3. Write results strictly from approved claim-ledger wording.
4. Include negative/null findings and limitations, including data coverage, label availability, generalizability, hardware scope, and timebase choice.
5. Rebuild the KU report and/or venue manuscript using the current official format. Remove all placeholders such as `Aditya [Surname]` and `yourname@ku.edu.np` only from verified Human-supplied facts.
6. Create README quick start, architecture/data flow, provenance, reproduction guide, artifact guide, data-rights statement, test guide, and troubleshooting.
7. Add license only after ownership/dependency/data compatibility review; add `CITATION.cff` with verified author/identifier fields.
8. Add an AI-use disclosure appropriate to the chosen venue. IEEE’s current [submission and peer-review policies](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/) require disclosure of AI-generated article content beyond ordinary editing; re-check the exact venue policy at submission time and describe the system, affected sections, and level of use accurately.
9. Run automated claim/document consistency checks and manual title-claim audit.

**Exit criteria:** no unsupported number/placeholders/local paths; every figure/table regenerates; bibliography sources verified; disclosure and rights statements complete; README reproduction works from a clean clone.

### Chunk 12 — Release hardening, archive, certification, and retrospective

**Objective:** produce the first publication-ready release and close the rehabilitation with auditable certification.

**Key contracts:**

1. Clean-room clone/install/reproduce on all supported environments.
2. CI matrix and release-build verification, including static non-fabrication audit and external-data fail-closed tests.
3. Secret, personal-path, machine-identity, license, dependency, and vulnerability scans.
4. Verify outer repository contains no Factory/private artifacts and nested `project/` has complete contract history.
5. Decide whether large historical Git objects require remediation. If yes, use a separately approved migration plan: signed tag/bundle/clone preservation, exact removal list, collaborator coordination, remote backup, documented old-to-new commit mapping, and explicit force-push approval. If no, leave history intact.
6. Deposit permitted large data/evidence in an archival service, verify upload checksums, mint persistent identifiers, and update manifests.
7. Run Gatekeeper `release-check`, acquisition audit, evidence checks, contract verification, lint, independent recomputation, stamp verification, tier check, and `release-certify`.
8. Inspect `project/RELEASE_CERTIFICATION.md`; use “certified” only after the command succeeds and the Architect’s manual gates pass.
9. Create versioned release notes stating scope, claims, limitations, data access, reproduction, and known non-goals.
10. Complete the Factory Retrospective from `project/evolution/telemetry.jsonl` and `decision_log.md`; propose Factory-rule changes only when this project provides repeated evidence.

**Exit criteria:** release tag/artifacts are reproducible, archived, checked, and claim-consistent; public clone contains no legacy synthetic evidence or private Factory material; recovery and maintenance ownership are documented.

---

## 13. Dependency graph and chunk ordering

```text
Project Initialization
        │
        ▼
Chunk 01  Repository + truth firewall
        │
        ▼
Chunk 02  Scope + venue + real-label feasibility
        │
        ▼
Chunk 03  Authentic acquisition + Reality Gate
        │
        ├───────────────┐
        ▼               ▼
Chunk 04 DSP semantics  Chunk 05 measured runtime harness
        └───────┬───────┘
                ▼
Chunk 06  Frozen evaluation/statistics protocol
                │
                ▼
Chunk 07  Authentic pilot
                │
                ▼
Chunk 08  Final experiments
                │
                ▼
Chunk 09  Independent analysis + claim ledger
                │
                ├──────────────► Chunk 10 optional app
                │                         │
                └──────────────┬──────────┘
                               ▼
Chunk 11  Manuscript/docs/reproduction
                               │
                               ▼
Chunk 12  Release certification + retrospective
```

No shortcut should move manuscript conclusions or dashboard work ahead of the claim ledger. Chunks 04 and 05 can be planned independently after authentic schema is known, but they must converge before the protocol is frozen.

---

## 14. Contract-level scientific evidence model

Every evidence-producing contract from Chunk 03 onward should write a manifest chain like:

```text
source URL + official checksum
          │
          ▼
acquisition_provenance.json
          │
          ▼
raw object hash + data_manifest.json
          │
          ▼
transformation manifest + processed object hash
          │
          ▼
experiment config hash + code commit + environment lock
          │
          ▼
run_manifest.json + raw predictions/telemetry/accounting
          │
          ▼
independent recomputation + verified aggregate metrics
          │
          ▼
claim_ledger.csv
          │
          ▼
table / figure / manuscript sentence / README statement
```

The link is broken if any node is absent. A pretty figure cannot repair missing raw provenance, and a checksum of a fabricated file does not make the content authentic.

### 14.1 Minimum run manifest

Each run should record at least:

- schema and project version;
- unique run ID and attempt ID;
- start/end timestamps in UTC;
- status and structured failure reason;
- outer source commit and dirty flag (final evidence requires clean);
- Factory contract/chunk ID;
- resolved configuration plus hash;
- input dataset manifest ID and object hashes;
- label manifest ID if applicable;
- method/baseline identifier and version;
- experimental unit identifiers;
- train/calibration/pilot/evaluation interval identifiers;
- seed only where an algorithm itself is stochastic, never as an independence identifier;
- hardware, OS, Python, dependency-lock hash, CPU affinity/process settings;
- replay schedule ID and replay factor;
- records expected, enqueued, processed, shed, rejected, and failed;
- output artifact paths/hashes;
- warning list;
- command and exit code.

### 14.2 Minimum claim-ledger row

Each public claim should include:

- claim ID;
- exact approved wording and prohibited stronger wording;
- research question/hypothesis;
- claim tier;
- population/data scope;
- independent unit and observed count;
- method and baselines;
- point estimate, units, interval, and statistical test;
- multiplicity status;
- practical margin if relevant;
- supporting run/artifact/report IDs;
- independent recomputation status;
- caveats and external-validity ceiling;
- destination locations (abstract, results, README, UI, caption);
- status (`approved`, `descriptive-only`, `exploratory`, `rejected`, `superseded`).

---

## 15. Authentic-data policy and enforcement design

The user’s requirement to remove fabricated and synthetic fake data must be expressed at four layers. Relying on a code search alone is too weak, because genuine files can still be mislabeled or duplicated, and a generator can be hidden behind neutral terminology.

### 15.1 Layer 1 — Source legitimacy

Every empirical source needs a source dossier in the Factory project containing:

- official provider identity and canonical documentation URL;
- exact dataset/product name and market/instrument meaning;
- access method and authentication needs;
- redistribution/publication terms and date checked;
- raw schema and source timezone;
- checksum/signature mechanism;
- documented corrections or source revisions;
- expected update/finality behavior;
- known gaps and biases;
- citation language required by the provider;
- Human acceptance of any terms that an automated agent cannot accept.

Search-engine results, mirrors, and a file name that resembles an official file are insufficient. Primary provider documentation must support the source.

### 15.2 Layer 2 — Acquisition provenance

Each request/response pair should be captured with enough evidence to distinguish an authentic acquisition from a locally produced file:

- request ID and timestamp;
- exact URL/parameters and resolved host;
- TLS verification status;
- response status, headers needed for provenance, byte count, and content hash;
- expected official checksum source and value;
- tool/version and retry history;
- temporary path/final content-addressed object ID;
- Human spot-check selection and result.

Credentials and session tokens must never enter the manifest. Where a provider does not publish checksums, the dossier must state that limitation and define a stronger spot-check/archival strategy. A local checksum proves later integrity; it does not prove original authenticity by itself.

### 15.3 Layer 3 — Transformation accountability

Every transform must conserve or explicitly account for records. For the current trade data, that means:

1. retain raw trade identifiers and quantity long enough to establish identity;
2. define duplicate identity from source semantics, not from an already lossy projection;
3. report counts before/after decompression, parse, validation, duplicate resolution, filtering, aggregation, and final output;
4. write a reason-coded exclusion table;
5. use deterministic sort/serialization settings;
6. include code/config/input hashes;
7. never overwrite a processed object under the same ID when code or configuration changes.

Regime classifications such as “low,” “medium,” and “high” may not be created from arbitrary thresholds and then treated as natural data labels. If regimes are needed, their definition must be grounded in a pre-specified observed measure, derived using calibration data, sensitivity-tested, and described as an analytical grouping—not an externally observed truth.

### 15.4 Layer 4 — Evidence-boundary enforcement

Authoritative experiment code accepts only a `VerifiedDatasetRef` (or equivalent typed handle) produced after the Reality Gate. It should reject:

- arbitrary filesystem glob input;
- a CSV/Parquet lacking a known manifest ID;
- data whose hash differs from the manifest;
- test fixtures;
- legacy result/data directories;
- an incomplete expected partition;
- an unverified label file;
- a dataset manifest with a non-PASS gate state.

The CLI should require explicit commands such as:

```text
flowgate data acquire --manifest <request.yaml>
flowgate data verify --dataset <dataset-id>
flowgate data transform --dataset <dataset-id> --config <transform.yaml>
flowgate run pilot --config <pilot.yaml>
flowgate run final --config <frozen-final.yaml>
flowgate report build --analysis <verified-analysis-id>
```

There should be no generic `run_all` that guesses which data to use, changes to a demonstration when files are missing, or overwrites a shared `results/` directory.

### 15.5 Prohibited terminology and code-pattern gate

The static gate should scan authoritative Python, JavaScript/TypeScript, shell scripts, notebooks, configuration, and manuscript-facing scripts for patterns such as:

- `synthetic`, `simulate`, `simulation`, `inject`, `dummy`, `fake`, `random_walk`, `generate_signal`;
- NumPy/random distribution calls feeding acquisition/evaluation/metric paths;
- broad exception handlers with success/continue behavior;
- TLS verification disablement;
- fallback assignments after acquisition exceptions;
- hardcoded “LIVE” UI strings for historical replay;
- results paths opened in write mode without a run ID/manifest.

This is a conservative alarm, not a semantic proof. A reviewed allowlist may permit phrases in documentation explaining that such methods are forbidden, and may permit deterministic canonical test-vector modules. The allowlist must use exact path/rule/reason entries and must not exclude entire source subtrees.

### 15.6 Randomness policy

Randomness is not automatically fabricated data. It may be legitimate for randomized execution order, stochastic algorithm internals, or resampling real experimental units for uncertainty. When permitted:

- the purpose is predeclared;
- a seed is recorded;
- random output is never treated as a new observed unit;
- no random value creates an empirical feature, label, arrival, event, or market record;
- results are robust to the algorithmic seed or the stochastic method is explicitly part of the claim.

The phrase “50 seeds” must disappear as a substitute for “50 independent real trials.”

---

## 16. Proposed scientific design after feasibility gates

This section gives the default design direction so later chunks do not drift back toward the legacy experiment. Chunk 02/06 may narrow it using verified literature, venue needs, real data availability, and power analysis.

### 16.1 Research questions

The initial question ladder should be:

**RQ1 — DSP semantics:** Under an explicit event-time or physical-time representation, how do the fixed and load-driven single-pole filters change smoothing, delay, and response as measured on authentic observations?

**RQ2 — Runtime:** In a real bounded streaming implementation, how do adaptation and load-shedding policies affect queue stability, end-to-end latency, throughput, CPU time, peak memory, and record retention under authentic replay schedules?

**RQ3 — Downstream fidelity:** Does any measured runtime benefit remain within a predeclared fidelity/non-inferiority margin on a downstream task with authentic labels or another independently defined authentic outcome?

**RQ4 — Attribution:** Which component—coefficient adaptation, shedding, calibration, or their interaction—explains any observed change?

RQ3 must be removed or reformulated if authentic labels/outcomes are unavailable. RQ4 is causal/ablation work and is the highest-tier claim.

### 16.2 Candidate method and baseline matrix

The exact methods depend on Chunk 04 matching rules, but a defensible matrix needs to separate components:

| ID | Filter behavior | Load-shedding behavior | Purpose |
|---|---|---|---|
| `B0` | Fixed single-pole coefficient | none | simplest no-adaptation/no-shedding reference |
| `B1` | Fairly matched conventional smoother selected from literature | none | alternative smoothing baseline |
| `B2` | Legacy-relevant adaptive smoother such as KAMA, if justified | none | adaptation baseline independent of queue load |
| `A0` | Proposed load-driven coefficient | none | isolates coefficient adaptation |
| `S0` | Fixed coefficient | proposed shedding policy | isolates shedding |
| `AS` | Proposed load-driven coefficient | proposed shedding policy | full system |

If an anomaly detector remains in scope, detector choice/calibration must be held constant across filtering/runtime policies unless detector variation is itself a declared factor. RRCF should not be both an unmatched detector and an unexplained baseline. At least three suitable baselines/ablations are required for the causal attribution claim.

### 16.3 Real workload construction

Workloads should be defined from complete authentic source partitions. Examples of permitted operations include:

- replaying original inter-arrival times;
- applying a fixed documented time-compression factor to the entire authentic interval;
- selecting predeclared high/medium/low observed-load intervals based on calibration-period quantiles;
- running distinct authentic asset/day shards concurrently to exercise capacity, while retaining every record’s source identity;
- sorting by authentic timestamp with a deterministic tie rule.

Examples of prohibited operations include:

- inventing burst start/end times;
- copying one busy interval multiple times and describing it as multiple observations;
- inserting generated trades/anomalies;
- resampling with replacement and calling the samples independent days;
- choosing favorable windows after viewing method outcomes;
- using the first 50,000 rows only because it is convenient.

If a capacity boundary requires load beyond the authentic observed schedule, concurrent replay of distinct real shards or higher fixed time compression can measure system capacity. The manipulation must be called a replay load factor, not natural market load, and causal conclusions must be limited to the runtime harness.

### 16.4 Experimental unit and pairing

There are two related but distinct units:

- **signal/evaluation unit:** a unique authentic asset-day, labeled event episode, or predeclared non-overlapping interval;
- **system-runtime unit:** a complete isolated process run of a frozen schedule/configuration on a defined machine state.

Within-unit method comparisons can be paired by the full logical key, for example:

```text
dataset_version / asset / date / interval / replay_factor / repetition_block
```

Method is then the within-block factor. Analyses must model repeated runtime runs and multiple intervals from the same asset/day. Neither a seed nor a table row alone establishes independence.

### 16.5 Outcome hierarchy

The protocol should declare one primary outcome per central question, with a restrained secondary set.

Candidate runtime outcomes:

- p95/p99 end-to-end latency;
- maximum or time-integrated queue occupancy;
- sustainable input rate under an operationally defined stability criterion;
- CPU time per accepted record;
- peak RSS;
- fraction and identity of records shed;
- downstream work avoided, measured rather than inferred.

Candidate filter/fidelity outcomes:

- predeclared lag/response statistic in the chosen timebase;
- deviation from a declared reference signal representation, if the reference is independently defined;
- task-specific event metric using authentic labels;
- false alarms per observed hour and event detection delay;
- conventional ROC-AUC/PR-AUC only when point labels and sampling interpretation make them valid.

The project should not combine incomparable outcomes into a convenient “Pareto” story without predefining dominance, uncertainty, and tie rules. A Pareto chart is descriptive unless the underlying comparisons and uncertainty support more.

### 16.6 Runtime measurement controls

Runtime claims are especially sensitive to noise and implementation bias. The harness should control or record:

- machine model, CPU topology, memory, power mode, thermal state where observable;
- OS version and competing-load policy;
- Python/runtime/compiler/dependency versions;
- CPU affinity/thread counts and BLAS/Numba settings;
- process warm-up and JIT compilation exclusion/inclusion policy;
- queue capacity and scheduling primitives;
- run order randomization/blocking;
- cooldown and repeated-run count;
- input bytes/records and output accounting;
- instrumentation overhead via a no-op/reference run.

Compute benefit should be measured in wall time, CPU time, downstream invocations, or energy only if a credible energy measure exists. It must not be inferred solely from a coefficient value or a queue-theory formula.

### 16.7 Authentic-label decision paths

**Path A — sufficient real labels:** align labels under a frozen mapping; use temporally separated calibration and test events; report event prevalence, symbol/date coverage, missing labels, event-delay/false-alarm metrics, and uncertainty at the event/cluster level.

**Path B — labels authentic but too sparse:** provide a descriptive case study only, clearly identify low power, and keep the main contribution on DSP/runtime behavior.

**Path C — no suitable labels/rights/alignment:** remove detector-accuracy conclusions, injected-anomaly figures, ROC/PR performance claims, and “true anomaly” UI language. Evaluate only outcomes that are genuinely observed or mathematically defined without pseudo-ground truth.

No fourth path manufactures labels.

---

## 17. Verification and test architecture

### 17.1 Test categories

| Category | Purpose | Input policy | Network policy | Release role |
|---|---|---|---|---|
| Unit | local branches/types/errors | deterministic scalar/small canonical vectors | forbidden | required on every change |
| Semantic | prove DSP/state/metric meaning | analytically derived canonical vectors or tiny verified captures | forbidden | required for core/evaluation changes |
| Integration | join acquisition/processing/runtime components | mocks for failure control flow; tiny checksum-pinned authentic fixture if redistribution permits | normally forbidden | required in CI |
| Scientific | assert protocol invariants, leakage, unit IDs, metric/reference parity | checksum-pinned authentic pilot artifacts or canonical metric examples | forbidden | required for experiment code |
| External-data | provider connectivity/checksum/schema spot test | real provider bytes | explicit/opt-in | scheduled/manual, fail-closed |
| Reproduction | clean clone to release artifacts | declared authentic dataset/artifact access | explicit | release gate |
| Application | API/UI truthfulness and lifecycle | verified historical replay fixture | forbidden in ordinary CI | required only if app retained |

### 17.2 Tests that must be added

At minimum, the rehabilitated suite should verify:

- TLS verification is not disabled;
- acquisition failure cannot return a dataset handle;
- checksum mismatch deletes/quarantines the temporary file and fails;
- partial expected coverage cannot pass Reality Gate;
- raw-to-processed record accounting balances;
- distinct trades are not collapsed after dropping identity fields;
- experiment code refuses unmanifested data and canonical test fixtures;
- calibration/evaluation intervals cannot overlap;
- pairing keys are complete and unique;
- resampled rows cannot increment the independent-unit count;
- run outputs are immutable and reruns get a new ID;
- report builders read verified aggregates only;
- evidence-check detects an intentionally contradictory verdict artifact;
- primary statistics recompute independently;
- all-equal/degenerate predictions are flagged;
- fixed/adaptive filter streaming and batch behavior agree;
- time-aware coefficient behavior is correct at zero/small/large `Δt` boundaries;
- initial-condition behavior is explicit;
- coefficient and pole traces agree;
- shedding record accounting is exact;
- runtime telemetry timestamps are monotonic and units declared;
- historical replay is never labeled live;
- static non-fabrication rules fail on representative prohibited code;
- local paths, credentials, and machine identity are absent from release files.

### 17.3 Legacy test disposition rules

Each existing test receives one of these statuses:

- `RETAIN-AS-IS` only if the requirement is valid and the input obeys the policy;
- `REWRITE-SAME-REQUIREMENT` if its premise is valid but it uses randomness/generated empirical framing;
- `REPLACE-INVALID-REQUIREMENT` if it encodes a wrong metric, arbitrary timebase, simulator behavior, or leakage;
- `RETIRE-NO-LONGER-IN-SCOPE` if the feature is removed;
- `BLOCKED-PENDING-DECISION` for timebase/labels/baselines.

Retirement requires a reason and any replacement requirement ID. The project should not boast of “97 tests” after migration; it should report which invariants and requirements are covered.

### 17.4 CI stages

A sensible fail-fast order is:

1. repository/manifest/ignore validation;
2. secret and local-path scan;
3. formatting and lint;
4. type/schema validation;
5. non-fabrication/acquisition audit;
6. package build and clean install;
7. unit and semantic tests;
8. integration/scientific invariant tests;
9. application tests if present;
10. release artifact/evidence checks on release branches.

Ordinary pull-request CI should not download the full dataset. It verifies code using permitted tiny fixtures and schemas. Scheduled/manual external checks confirm provider behavior. Release reproduction uses the full declared authentic dataset in an environment authorized for it.

### 17.5 Warning policy

Warnings that threaten validity are failures. In particular:

- statistical precision loss;
- invalid/empty slices;
- overflow/NaN production;
- schema coercion;
- timezone ambiguity;
- missing checksum/provenance;
- non-convergence;
- dependency deprecation that changes numerical behavior.

An expected-warning allowlist needs exact warning type, call site, reason, expiration/review date, and test. Global filters are forbidden.

---

## 18. Documentation, authorship, and publication integrity

### 18.1 Document sources of truth

| Public content | Authoritative input |
|---|---|
| Project scope and limitations | frozen project description, architecture, claim ledger |
| Data description | verified data manifest and source dossier |
| Methods | frozen protocol/configs and reviewed implementation |
| Sample/unit counts | sealed run coverage/accounting artifact |
| Numeric results | independently recomputed verified aggregates |
| Tables and figures | scripts consuming those aggregates only |
| Abstract/conclusion | approved claim-ledger wording |
| Installation | clean-room CI/reproduction steps |
| Data availability | rights review and archived artifact identifiers |
| AI disclosure | actual work log plus current target-venue policy |

Generated narrative files are not facts. A report builder may insert machine-readable verified numbers into templates, but an AI-written sentence does not promote a result to evidence.

### 18.2 Figure and table rules

Every release figure/table should carry or link to:

- artifact ID and generation script;
- input aggregate hashes;
- units and sample/experimental-unit counts;
- uncertainty definition;
- method/baseline labels matching configs;
- caption wording from approved scope;
- software version/commit;
- accessibility information where relevant.

Figures should never be manually edited to change data, labels, or values after generation. Layout-only editing must be reproducible or recorded. A “real data” filename is not proof that its contents are real.

### 18.3 Authorship and placeholders

Do not infer surname, email, institutional affiliation, supervisor, course code, dates, acknowledgments, or author order from placeholder text. The Human supplies these in a verified metadata file. Release checks fail on placeholder patterns and unverifiable identity strings.

### 18.4 AI-use record

The nested project repository should maintain a concise factual record of AI assistance by phase: planning, code migration, testing, analysis review, drafting, and editing. At submission, map that record to the chosen venue’s current policy. This plan was AI-assisted and should be part of that record if it materially guides the project.

### 18.5 Data/code licensing

The project must separately determine:

- copyright/license for new code;
- compatible licenses/attributions for Python/JS dependencies;
- use and redistribution terms for Binance and any label provider;
- whether tiny authentic fixtures may be redistributed;
- whether derived aggregates/figures may be archived;
- whether the KU report or venue requires specific statements.

Do not add an open-source license that purports to relicense third-party raw data or dependencies.

---

## 19. Git and release-history strategy

### 19.1 Normal rehabilitation history

The preferred history is transparent and incremental:

1. preserve/commit intended current source/doc changes or record them on a legacy-intake branch after Human review;
2. create the Factory initialization in the nested project repository;
3. implement one contract per reviewable commit or commit group;
4. keep outer product commits free of `project/`/Factory internals;
5. use messages that include contract IDs without pretending earlier commits were Factory-generated;
6. tag the pre-rehabilitation baseline and the first certified release if the Human approves.

### 19.2 Large-object diagnosis

The working `.git/` is much larger than the visible checkout. Before recommending history rewriting, C01-05/Chunk 12 must determine whether size comes from:

- objects reachable from normal branches/tags;
- local tool-created refs or turn-diff refs;
- reflogs;
- currently untracked data captured by local tooling;
- genuine large binaries in public history.

Local Codex/tool refs may explain local bloat without affecting the remote clone. The plan must not conflate those cases.

### 19.3 Optional history rewrite

History rewriting is justified only if public clone size/security/licensing materially requires it. The separate plan must:

- identify exact object IDs/paths and why ordinary untracking is insufficient;
- preserve a Git bundle or offline clone plus checksums;
- coordinate collaborators and CI/remotes;
- use a reviewed tool such as `git filter-repo` with explicit paths;
- verify source tags/branches and release build after rewrite;
- document old-to-new commit mapping;
- obtain explicit approval for force-push;
- provide recovery steps.

It is not part of Chunk 01 and cannot be used to erase the rehabilitation record.

---

## 20. Risk register

| ID | Risk | Likelihood/impact | Prevention/detection | Required response |
|---|---|---|---|---|
| `R-01` | User’s dirty work is lost during cleanup | High/High | C01-01 ledger, diffs, hashes, Human decisions | Stop; restore from preserved state; investigate contract breach. |
| `R-02` | Authentic-looking local data is assumed authentic | High/High | official URL/checksum/provenance and Reality Gate | Quarantine/reacquire; block experiments. |
| `R-03` | A fallback silently produces generated data | High/High | typed failures, static audit, negative tests | Fail contract; no downstream artifact accepted. |
| `R-04` | Test fixtures leak into experiments | Medium/High | package/import boundary and manifest-only dataset handles | Reject run; invalidate affected outputs. |
| `R-05` | Processed schema destroys identity | High/High | full raw schema, identity-based duplicate tests, accounting | Reprocess from verified raw; invalidate old processed data. |
| `R-06` | Irregular samples are analyzed as uniform physical time | High/High | INV-TIME-001, timebase contract/tests | Block frequency/time claims; repair design. |
| `R-07` | Pseudo-replication inflates sample size | High/High | unique unit IDs, grouped models, unit-count checks | Reanalyze; retract independence/significance claims. |
| `R-08` | Non-significance is presented as equivalence | High/High | claim ledger, predeclared margin, title audit | Replace wording or run valid equivalence design. |
| `R-09` | Queue simulation survives under renamed code | Medium/High | telemetry provenance, real process accounting, adversarial review | Invalidate runtime claims and replace harness. |
| `R-10` | Adaptation is credited for shedding benefit | High/High | factorial ablations `B0/A0/S0/AS` | Narrow attribution; causal claim blocked. |
| `R-11` | Reports disagree with artifacts | Existing/High | evidence-check, independent recompute, immutable runs | Fail report; supersede through documented protocol. |
| `R-12` | Legacy results leak into final manuscript | High/High | quarantine namespace, claim-only document build | Remove claim; rebuild and rescan. |
| `R-13` | Dependency environment cannot be reproduced | High/Medium | reviewed lock, clean install CI | Block release; resolve versions/platform scope. |
| `R-14` | Frontend presents replay as live/ground truth | Existing/High | UI truthfulness tests and optional-app gate | Correct labels or omit app. |
| `R-15` | Data redistribution violates provider terms | Medium/High | rights dossier and Human/legal review | Do not redistribute; publish acquisition procedure/allowed aggregates only. |
| `R-16` | Factory gate is assumed implemented when it is manual | Medium/High | gate implementation matrix in chunk review | Architect performs/manual-documents the gate. |
| `R-17` | `.gitignore` hides real source | Existing/High | positive and negative ignore tests | Fix before commit; inventory hidden paths. |
| `R-18` | History cleanup destroys recoverability | Low/High | separate approved plan and preservation bundle | Stop, recover from bundle, no force-push until verified. |
| `R-19` | Sparse labels tempt artificial augmentation | High/High | predeclared no-label path | Remove/narrow RQ; never inject. |
| `R-20` | Negative results trigger post-hoc metric/window selection | Medium/High | frozen protocol/configs and immutable attempts | Label exploratory or reject; do not alter primary result. |
| `R-21` | Personal/local paths enter release | Existing/Medium | release-check and clean-clone tests | Sanitize portable manifests/docs; rerun checks. |
| `R-22` | Factory-private artifacts leak into public repo | Medium/Medium | outer ignore and release tree audit | Remove from public index; verify clean clone. |

---

## 21. Human decision register

The Factory should track these decisions explicitly rather than letting implementation defaults decide them:

1. **Primary deliverable:** KU project report, named external venue paper, both in sequence, or repository-only rehabilitation.
2. **Provisional scientific scope:** runtime/filter study versus anomaly-detection study contingent on real labels.
3. **Legacy dirty state:** which modified/untracked source/tests/docs represent intended work.
4. **Deleted notebook:** preserve deletion, restore for quarantine, or migrate content after review.
5. **Application:** omit, defer, or rehabilitate after science.
6. **Data provider terms:** acceptance/authorization and redistribution constraints.
7. **Target Python/platform support:** minimum versions and operating systems.
8. **Performance hardware:** available machine(s) and whether claims are single-machine or multi-platform.
9. **Repository visibility and archival target:** private during rehab, eventual public release, persistent artifact repository.
10. **License/author metadata:** owner, contributors, affiliation, citation identity.
11. **History remediation:** whether remote clone size warrants a later rewrite.
12. **Literal test-vector interpretation:** whether deterministic mathematical vectors are permitted under the no-synthetic requirement.

The recommended defaults are: KU report plus public reproducibility repository first; external paper only after a named venue and successful evidence; anomaly detection conditional on real labels; defer the app; retain deterministic canonical vectors only for software correctness; preserve Git history unless remote-size evidence justifies otherwise.

---

## 22. Global stop conditions

The Architect must stop the active contract/chunk rather than improvise if any of the following occurs:

- a current uncommitted file would be overwritten, deleted, or semantically replaced without disposition;
- an external service/data license needs Human acceptance;
- official checksum/provenance cannot be established;
- expected data coverage is incomplete or schema accounting does not balance;
- only fabricated/injected labels can support the planned evaluation;
- calibration overlaps final evaluation;
- the independent-unit count or pairing cannot be reconstructed;
- metric/reference implementations disagree beyond declared tolerance;
- statistical warnings make primary output unreliable;
- a contract report’s verdict contradicts its backing artifact;
- source or verification machinery changes outside allowed files;
- a `T-COMP`/`T-CAUSAL` contract lacks mandatory baselines/mechanical gates;
- the title/abstract implies a stronger claim than the evidence tier permits;
- a release reproduction needs an ignored undeclared file;
- history rewriting, remote mutation, license choice, publication, or archive deposit lacks explicit authorization;
- a secret or personally sensitive file/value is discovered.

“Take more time,” “try a different window,” or “use synthetic data temporarily” are not valid resolutions to these stop conditions.

---

## 23. Definition of publication-ready completion

The project is rehabilitated only when all of the following are true.

### Repository and Factory

- outer repository has a clean, deliberate tracked tree;
- Factory v2.2.0 is pinned and passes recorded self-check;
- nested `project/` contains complete founding docs, chunk plans, contracts, reports, telemetry, decision log, and release certification;
- `source/` is the only authoritative product implementation;
- no product source is hidden by whole-directory ignore rules;
- environments, dependencies, raw/processed data, caches, and uncurated runs are untracked/ignored;
- legacy files are gone from the public surface or explicitly labeled historical where retention has real value.

### Data integrity

- every empirical byte is authentic-source traceable;
- official checksums are verified where available;
- acquisition and transformation accounting balance;
- Reality Gate passes for the exact release dataset;
- no generated/injected/simulated data or silent substitution contributes to evidence;
- no duplicated/resampled row is counted as a new independent observation;
- data rights and availability statements are accurate.

### DSP and software correctness

- timebase, coefficient, pole, initial conditions, and state semantics are explicit;
- reference and optimized implementations agree;
- statistical metrics match independent/reference calculations;
- build/install/tests pass from a clean clone;
- warnings that affect validity are resolved;
- CI prevents regression in the non-fabrication and provenance invariants.

### Experimental validity

- research questions and protocol were frozen before final results;
- authentic labels exist or label-dependent claims are removed;
- experimental units, pairing, missingness, and repetitions are correct;
- baselines and ablations satisfy the scientific tier;
- runtime behavior is measured on actual processes/queues;
- final runs/configs are immutable and all attempts are accounted for;
- independent recomputation agrees;
- negative or null outcomes are reported honestly.

### Publication integrity

- each claim has a verified claim-ledger row;
- manuscript/README/UI/table/figure values are consistent;
- title and abstract stay within the evidence ceiling;
- citations and venue requirements are verified from current primary sources;
- placeholders, local paths, secrets, and machine identity are absent;
- authorship, licenses, data availability, and AI disclosure are accurate;
- reproduction instructions work without the original 4.8 GB workspace.

### Release

- release checks, acquisition/evidence checks, independent recomputation, stamps, tiers, and Factory certification pass;
- large external artifacts have verified persistent identifiers where permitted;
- release tag/build is recoverable;
- limitations and maintenance scope are documented;
- retrospective is complete.

Until then, language such as “100% complete,” “publication-ready,” “zero quality cost,” “real-time live anomaly detection,” and “Factory-certified” is prohibited.

---

## 24. Recommended first execution sequence

When the Human authorizes rehabilitation work, the first working session should do only the following:

1. Re-read the exact supplied Factory v2.2.0 role/specification files and record their hashes.
2. Capture the dirty worktree and asset ledger without modifying any existing path.
3. Ask for the minimum ambiguous dispositions: deleted notebook, modified source/tests/docs, and whether deterministic canonical test vectors are permitted.
4. Create a recoverable preservation point for intended current work.
5. Bootstrap the Factory idempotently and verify outer/nested repository separation.
6. Complete and commit Project Initialization artifacts, including the no-fabrication invariants and provisional no-label contingency.
7. Write and snapshot `project/chunks/chunk01/chunk01.md`, its eight contracts, and execution manifest.
8. Execute only `C01-01`.
9. Review and stamp its report before proceeding to `C01-02`.

Do not start by moving directories, replacing `.gitignore`, running `git clean`, deleting environments, regenerating results, or “fixing” the paper. Those actions become safe only after the forensic and Factory boundaries exist.

---

## 25. Final rehabilitation stance

The project has a useful core idea and a meaningful amount of implementation/test work, but its present evidence pipeline cannot support publication claims. The fastest credible route is not to polish the current report or rerun the existing scripts. It is to preserve the legacy state, install the Factory discipline, remove every synthetic/simulated evidence path, certify authentic inputs, correct the DSP semantics, measure the actual runtime system, freeze a statistically valid protocol, and then let the real results determine the paper’s claim.

If authentic labels never become available, the rehabilitation still succeeds by producing a rigorous DSP/runtime project with an honest scope. If the adaptive method does not outperform its baselines, the rehabilitation still succeeds by producing a reproducible negative result. The only unacceptable success criterion is one that requires fabricated evidence, concealed history, or a conclusion stronger than the data.
