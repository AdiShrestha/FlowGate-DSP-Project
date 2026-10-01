# FlowGate DSP — research rehabilitation

Read [plan.md](plan.md) before changing the methodology or running experiments.
This repository contains a corrected numerical foundation and the supplied
software factory v3.3.0 with a disclosed local audit patch. Read
[the re-audit](docs/re_audit/REPORT.md) and
[local factory policy](factory/LOCAL_AUDIT_POLICY.md). It does **not** yet contain a validated research study,
measured streaming runtime, or submission certificate.

The new engine in `source/flowgate/` provides stateful EMA/adaptive-alpha/KAMA,
uniform-grid Butterworth SOS filtering, explicit stride admission, causal
residual scoring, exact point metrics, event misses, paired unit-key statistics,
and an FCFS scheduling **model**. All algorithm parameters are explicit. It has
no synthetic acquisition fallback, bundled result table, or automatic experiment.

Run the core verification from the repository root:

```sh
python3 -m pip install --require-hashes -r source/requirements-test-macos-arm64.lock
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q source/tests
PYTHONDONTWRITEBYTECODE=1 python3 factory/run_self_tests.py
```

The real-archive smoke test needs `data/raw/`. The migration copied 155 original
archives after verifying every digest against Binance's official checksums.
The full semantic audit also checked all 119,611,063 raw observations.
Bulk raw data are ignored by Git. A fresh clone can reconstruct them with:

```sh
python3 source/acquire_archives.py --manifest data/acquisition_manifest.json --destination data/raw
```

Acquisition requires verified HTTPS and fails on changed/missing input. Do not
disable TLS verification to make it pass. `data/acquisition_manifest.json`
records input hashes and locations; market prices have **no natural anomaly
labels**. All January 2024 inputs were inspected previously and are exploratory.
If the Python installation lacks a working default trust store, supply a trusted
CA bundle with `--ca-file /absolute/path/to/ca-bundle.pem`.

`docs/flowgate_audit/` contains the file inventory, structural data audit,
provider checksums, targeted counterexamples, verification logs, and an explicitly
non-authoritative legacy snapshot ZIP. Never import that snapshot into the engine
or reuse its generated tables as research evidence.

`project/research_plan.json` is the supplied unpopulated factory template. It
must remain unfrozen until the Architect completes the domain adapter and
methodology described in `plan.md`. A binary-classification gate cannot certify
queueing, DSP fidelity, or physical latency by relabelling their outputs.

The existing proprietary `LICENSE` is preserved. No additional open-source
license or data-redistribution permission is inferred by this migration.

The hash locks above target CPython 3.12 on macOS arm64. Other platforms need
separately regenerated and tested locks. For portable public receipt verification,
install the optional hash-locked Ed25519 dependencies from
`factory/requirements-ed25519-macos-arm64.lock`. HMAC fallback is local-only.

The full engine suite requires raw archives; on a fresh clone run the acquisition
command before testing. Failed acquisition receipts and partial bytes remain
under `data/raw/.acquisition_attempts/`. The October re-audit and retained initial
failed checks are in `docs/re_audit/`; original migration checks remain historical.
