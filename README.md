# FlowGate DSP — research rehabilitation

Read [plan.md](plan.md) before changing the methodology or running experiments.
This repository contains a corrected numerical foundation and the supplied
software factory v3.3.0. It does **not** yet contain a validated research study,
measured streaming runtime, or submission certificate.

The new engine in `source/flowgate/` provides stateful EMA/adaptive-alpha/KAMA,
uniform-grid Butterworth SOS filtering, explicit stride admission, causal
residual scoring, exact point metrics, event misses, paired unit-key statistics,
and an FCFS scheduling **model**. All algorithm parameters are explicit. It has
no synthetic acquisition fallback, bundled result table, or automatic experiment.

Run the core verification from the repository root:

```sh
python3 -m pip install -r source/requirements-test.lock
python3 -m pytest -q source/tests
python3 factory/run_self_tests.py
```

The real-archive smoke test needs `data/raw/`. The migration copied 155 original
archives after verifying every digest against Binance's official checksums.
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
