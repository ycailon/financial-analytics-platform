# Data sources

## SEC EDGAR Company Facts API

Source documentation:

- https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

The SEC Company Facts endpoint returns standardized XBRL facts for one filer in JSON. The API does not require an API key. Automated access should identify the client through a declared User-Agent and stay within the SEC fair-access guidance.

This project keeps the SEC CIK and source US-GAAP concept attached to each selected financial fact so the transformation is auditable.

## BLS Public Data API

Source documentation:

- https://www.bls.gov/developers/home.htm
- https://www.bls.gov/developers/api_faqs.htm
- https://www.bls.gov/developers/api_signature_v2.htm

The default macro series are:

- `CUUR0000SA0` — CPI-U, U.S. city average, all items, not seasonally adjusted.
- `LNS14000000` — seasonally adjusted civilian unemployment rate.

The project uses the unregistered/public request path and intentionally keeps the request inside the lower public limits. No registration key is needed for the default configuration.

## Source-data assumptions

SEC XBRL tags are standardized, but companies can still use different valid tags for comparable concepts or change tags over time. `config/sec_metrics.yaml` therefore lists candidate concepts in priority order instead of assuming one tag works for every company forever.

The macro indicators are used as economic context only. The project does not claim CPI or unemployment caused a company's revenue, margin or earnings movement.
