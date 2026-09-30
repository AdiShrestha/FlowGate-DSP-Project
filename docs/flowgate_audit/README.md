# FlowGate forensic evidence

The audit inventories and hashes every retained first-party project file and
every supplied factory file, excluding Git internals, installed environments,
node_modules, operating-system metadata, and generated Python/Numba caches.
`file_inventory.json` covers 525 legacy files and 90 supplied factory files.
`text_review_index.json` indexes 191 text files, 180 distinct contents, including
complete textual reads, Python function ranges, duplicate mappings, and suspect
constructs. A static index is not an assertion of equal-depth semantic review
for every historical policy or duplicated planning paragraph.

Every raw ZIP passed a complete decompression/CRC check; every processed
Parquet timestamp and price was checked for finite values, ordering, and positive
price. The 155 caches contain 73,830,561 rows. This structural audit neither
recovers discarded trade IDs nor proves that all transformations were valid.
Every raw ZIP also matches its official provider checksum.

`legacy_snapshot.zip` preserves all inventoried legacy artifacts except bulk raw
and processed market data. It includes historical code, figures, results,
manuscripts, and factory/planning records. It is quarantine material, never an
importable implementation or confirmatory evidence source. Raw archive hashes
are in the inventory and raw bytes were separately copied into the new data
folder. The deleted tracked notebook is preserved by the published legacy Git
tag, rather than silently restored into the current engine.

The core's tests and smoke outputs are software verification evidence only.
The old 97-test suite demonstrates preserved historical behavior; its passing
status does not validate its metrics, queue model, or trial independence.
`factory_tests_sandboxed.log` retains the original sandbox socket failure;
`factory_tests.log` records the complete 276-test pass outside that restriction.

Read root `plan.md` for the substantive findings, certainty levels, migration
decisions, contracts, mathematical analysis, and required research work.

`findings.json` mirrors the 44 finding rows and binds its source plan hash.
`handoff_verification.json` records copied raw-file hashes, the 215-file snapshot
verification, all 90 unchanged supplied factory files, and current source hashes.
Recheck with `python3 docs/flowgate_audit/verify_handoff.py`; this verifies bytes,
not research readiness. The verification manifest excludes its own digest.

`reproduce_legacy_probes.py` executes two inspected SHA-bound legacy modules in
a standalone forensic process. It reproduces the adjacent-alert metric defect,
historical trial counts, and the 100/23/0 realized injection counts on 50,000
real background trades. The deliberate generated perturbation is never saved
or treated as natural anomaly truth. `legacy_probes.log` retains its output.
`acquisition_existing_verification.log` records the new CLI's digest check of
all 155 existing local archives; it is not a fresh-download integration result.
