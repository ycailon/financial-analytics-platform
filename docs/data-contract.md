# Data contract

## Financial facts

A financial fact is uniquely identified by:

`company_key + fiscal_year + metric_key`

Expected rules:

- company and metric keys must exist in their dimensions;
- `value` cannot be null;
- annual duration metrics should come from roughly 300-400 day periods;
- only 10-K / 10-K/A facts are used in the current annual model;
- the original SEC concept, filing date and accession number stay attached for traceability.

## Macro facts

A macro fact is uniquely identified by:

`series_key + observation_date`

Only normal monthly BLS periods `M01` to `M12` are loaded. `M13` annual-average rows are excluded because the SQL layer calculates its own annual context.

## Quality status

- `PASS`: the rule is satisfied.
- `WARN`: usable data exists but expected coverage is incomplete.
- `FAIL`: a structural quality rule is broken, for example a duplicate fact key.
