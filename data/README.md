# Data provenance

`acquisition_manifest.json` names 155 real Binance Spot trade archives across
BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, and BNBUSDT for January 2024. Each archive
matched the provider's official SHA-256 checksum on the audit date. Raw files
are copied locally under `raw/` and excluded from Git; acquisition from the
recorded URLs is reproducible with `source/acquire_archives.py`.

The old caches are not migrated. They kept only floating-point timestamp and
price, deduplicated legitimate equal-time/equal-price trades, and discarded
provider trade IDs. The inventory records their hashes for forensic reference.
They are not an authoritative cohort or split manifest.

Provider byte identity is separate from label validity, dataset rights, sampling
design, and independence. These prices are unlabeled. None of the January 2024
corpus is an untouched confirmatory holdout. Do not invent a `label` column to
fit the factory's binary schema.
