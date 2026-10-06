# Sample data

The repository does not commit real SEC or BLS payloads.

`financial-analytics demo` generates deterministic, synthetic payloads that follow the source schemas closely enough to exercise the full transformation, warehouse, quality-check and Power BI export path without internet access.

`financial-analytics refresh` uses the real public SEC and BLS endpoints and writes raw responses under `data/raw/`, which is excluded from Git.
