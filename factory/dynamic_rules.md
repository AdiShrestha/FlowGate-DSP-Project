> FlowGate local audit revision (1 October 2026): read [LOCAL_AUDIT_POLICY.md](LOCAL_AUDIT_POLICY.md) before applying this supplied v3.3 policy. It narrows unsupported assurance and replaces outcome-biasing diagnostic rules. The root plan.md and the user’s research-integrity requirements govern this project.

# Active dynamic rules — v3.3.0

**DR-001 Evidence before status:** output schemas, hashes, and exit codes establish integrity only; predictions and observations must be recomputed.

**DR-002 Every attempt remains:** a failed, interrupted, or evidence-rejected attempt remains under its epoch; a second favorable attempt needs a new frozen design.

**DR-003 Correct metric names:** `average_precision` is not threshold precision; AUROC score direction is tested with known vectors; aliases are rejected.

**DR-004 Denominator integrity:** IDs, source records, labels, groups, entities, and splits are joined before calculating error or failure prevalence. Empty or phantom denominators block.

**DR-005 Convergence is a measured protocol:** validation checkpoint selection, patience/tolerance, raw history, and budget are checked. “10 epochs” alone is not convergence and “not significant” is not equivalence.

**DR-006 Interactions need design:** ≤5 ablation components require full factorial coverage and repeated units; sensitivity curves need registered levels and repeats; flat curves are diagnostic findings.

**DR-007 Measure resources:** device, synchronization, warmups, raw timings, memory scopes, energy readings, and sustained interval are observations. Estimates are not observations.

**DR-008 Review binds evidence:** semantic review must reference current file hashes and resolve every diagnostic; same-session review is useful but disclosed as such.

Each rule is enforced only where `gatekeeper_spec.md` says it is. The remainder belongs in the review and is printed as a limit. New rules require a reproducing regression test and an explicit false-positive analysis.

## v3.2.0–v3.3.0 verification rules

### D-074 (Category: Scientific sufficiency, Status: ACTIVE)
Training convergence evidence is required for comparative claims. Evidence: one incident, this project. Implementation: `Audit.training` and `Audit.training_sufficiency` check epochs, loss slope, criterion, and justification. Verification: regression fixtures cover short, declining, and converged traces.

### D-075 (Category: Sensitivity, Status: ACTIVE)
A sensitivity sweep with a degenerate flat response is surfaced for investigation unless explicitly expected. Evidence: one incident, this project. Implementation: `Audit.analyses` and audit diagnostics. Verification: flat-curve fixture.

### D-076 (Category: Provenance, Status: ACTIVE)
Unused real-data inputs paired with literal-heavy result sinks are a hard provenance failure. Evidence: one incident, this project. Implementation: `_acquisition_findings` via `acquisition_audit` AST scan. Verification: phantom-input fixture.

### D-077 (Category: Sampling, Status: ACTIVE)
Comparative claims require minimum total and per-class sample support and an explicit imbalance treatment. Evidence: one incident, this project. Implementation: `Audit.cohort`. Verification: small-N and 100:1 imbalance fixtures.

### D-078 (Category: Provenance, Status: ACTIVE)
Undisclosed synthetic fallbacks are blocked; disclosed test-only fallbacks remain visible warnings. Evidence: one incident, this project. Implementation: `acquisition_audit`. Verification: fallback fixtures.

### D-079 (Category: Results, Status: ACTIVE)
Valid adverse/null outcomes must be retained. Only malformed numeric evidence is invalid; outcome diagnostics require disclosed review. Implementation: `verify_result_plausibility`. Verification: numeric-validity and adverse-result fixtures.

### D-080 (Category: Results, Status: ACTIVE)
Exact zero p values and zero-width intervals trigger investigation; no universal minimum CI width or .5 F1/precision/recall baseline is imposed. Implementation: `verify_result_plausibility`. Verification: scale-invariance and malformed-value fixtures.

### D-081 (Category: Traceability, Status: ACTIVE)
Cross-artifact identifiers must resolve to declared source records. Evidence: one incident, this project. Implementation: `Audit.analyses_traceability`. Verification: missing-ID fixture.

### D-082 (Category: Governance, Status: ACTIVE)
Every Mandatory Constitution principle is represented in the machine-checked coverage matrix. Evidence: one incident, this project. Implementation: `verify_coverage_liveness`. Verification: drift and null-mechanism fixtures.

### D-083 (Category: Statistics, Status: ACTIVE)
Statistical and pre-submission checks inspect cited artifact values rather than keyword proximity. Evidence: one incident, this project. Implementation: `_result_findings`, `verify_statistical_protocol`, and `pre_submission_audit` inspect value-level plausibility. Verification: value-level fixtures.

### D-084 (Category: Tier inference, Status: ACTIVE)
Tier inference recognizes plural and paraphrased verdict vocabulary and ships paraphrase tests. Evidence: one incident, this project. Implementation: `tier_check` and `_detects_verdict_enum`. Verification: comma-separated verdict fixture.

### D-085 (Category: Release, Status: ACTIVE)
Release certification aggregates project-wide scientific findings and Constitution coverage. Evidence: one incident, this project. Implementation: `certify`. Verification: aggregate blocking fixture.

### D-086 (Category: Mechanical gate, Status: ACTIVE)
Comparative and causal contracts require scientific sufficiency, split, and plausibility gates. Evidence: one incident, this project. Implementation: Mandatory Mechanical Gate in `check`/certification. Verification: missing-gate fixture.

### D-087 (Category: Evidence parsing, Status: ACTIVE)
Evidence parsing rejects duplicate keys, non-finite constants, and symlink/path escapes at every component. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `engine.io.read_json` and shared readers. Verification: parser and path fixtures.

### D-088 (Category: Attempts, Status: ACTIVE)
Every execution attempt is retained and only the latest successful attempt can certify. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: epoch attempt records and audit. Verification: failed-then-success fixture.

### D-089 (Category: Reproducibility, Status: ACTIVE)
Benchmark-critical nondeterministic results require fresh-process replay within tolerance. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `Audit.claims`. Verification: mismatch fixture.

### D-090 (Category: Permutation inference, Status: ACTIVE)
Monte Carlo p-values use add-one correction; exact enumeration is used when tractable. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `engine.metrics.paired_inference`. Verification: finite-draw fixture.

### D-091 (Category: Independent arithmetic, Status: ACTIVE)
Gatekeeper-owned metric implementations are used for verification. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `engine.metrics.binary_metrics`. Verification: known direction and AP vectors.

### D-092 (Category: Temporal leakage, Status: ACTIVE)
Temporal splits enforce train < validation < test ordering. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `Audit.cohort`. Verification: temporal-order fixture.

### D-093 (Category: Ablations, Status: ACTIVE)
Ablations above five components require a disclosed fractional-factorial alias structure. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `Audit.analyses_ablation`. Verification: large-design fixture.

### D-094 (Category: Execution safety, Status: ACTIVE)
Experiment commands execute as argv lists with allowlisted experiment IDs. Evidence: observed undocumented mechanism in a noncompliant build. Implementation: `engine.plan.validate` and `safe_args`. Verification: shell metacharacter fixture.

## v3.3.0 trust-boundary rules

### D-095 (Category: Execution contract, Status: ACTIVE)
Experiment execution uses typed contracts; the supervisor constructs the launch command from `runtime_id` and `entrypoint`. Shell wrappers, inline-code flags, and free-form interpreter flags are rejected. Evidence: trust-boundary analysis. Implementation: `validate_contract` and `resolve_contract`. Verification: ATK-001, ATK-002, ATK-018 fixtures.

### D-096 (Category: Content addressing, Status: ACTIVE)
Inventories bind sorted paths/digests in the compatibility snapshot_merkle_root field; it is not a Merkle tree. Symlinks, special files and importable binary/cache bytes are rejected. Implementation: `engine.io.merkle_root` and `inventory`. Verification: bytecode and special-file fixtures.

### D-097 (Category: Receipt signing, Status: ACTIVE)
All retained completed attempts require verified signature and identity/input/output/launch bindings. Ed25519 permits public verification; HMAC is local-only. Same-user key isolation is not enforced. Missing CPU/memory measurements are null. Implementation: `build_receipt` and `verify_receipt_signature`. Verification: receipt mutation and offline binding fixtures.

### D-098 (Category: Schema validation, Status: ACTIVE)
All evidence validators use strict typed schemas that reject boolean/string/integer confusion, empty structures satisfying vacuous checks, and justification strings bypassing numeric requirements. Evidence: trust-boundary analysis. Implementation: `expect_str` and `engine.schema`. Verification: ATK-012 fixtures.

### D-099 (Category: Recursive plausibility, Status: ACTIVE)
Recursive diagnostics expose exact-zero p and zero-width intervals, plus adverse AUROC or an explicitly supplied baseline. Numeric validity remains separate; legitimate negative results are admissible. Implementation: `_deep_result_findings`. Verification: nested diagnostic fixtures.

### D-100 (Category: Reproduction identity, Status: ACTIVE)
Fresh-process replay must bind model, config, training mode, producer paths and typed/legacy runtime identity. Implementation: `engine.audit.Audit.reproduction_identity` and `engine.audit.Audit.claims`. Verification: reproduction identity fixtures.

### D-101 (Category: Assurance level, Status: ACTIVE)
Local audit assurance is at most SUPERVISOR_ATTESTED with verified receipts. A review boolean cannot establish independence; stronger unsupported levels are rejected. Implementation: `_assurance_with_review`. Verification: assurance level fixtures.

### D-102 (Category: Attack registry, Status: ACTIVE)
The 18-entry attack registry is checked for structure only in release audit. Actual regression execution is a separate version/environment-bound record; fixture success is not exhaustive hostile-worker or scientific validation. Implementation: `verify_attack_registry`. Verification: registry structure tests and separately recorded full suite.
