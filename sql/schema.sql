PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_company (
    company_key INTEGER PRIMARY KEY,
    cik TEXT NOT NULL UNIQUE,
    ticker TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    sector TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_metric (
    metric_key INTEGER PRIMARY KEY,
    metric_code TEXT NOT NULL UNIQUE,
    metric_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit TEXT NOT NULL,
    period_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_macro_series (
    series_key INTEGER PRIMARY KEY,
    series_id TEXT NOT NULL UNIQUE,
    series_code TEXT NOT NULL UNIQUE,
    series_name TEXT NOT NULL,
    unit TEXT NOT NULL,
    frequency TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_financial_metric (
    company_key INTEGER NOT NULL,
    fiscal_year INTEGER NOT NULL,
    period_start TEXT,
    period_end TEXT NOT NULL,
    metric_key INTEGER NOT NULL,
    value REAL NOT NULL,
    form TEXT,
    filed_date TEXT,
    accession_number TEXT,
    source_concept TEXT NOT NULL,
    PRIMARY KEY (company_key, fiscal_year, metric_key),
    FOREIGN KEY (company_key) REFERENCES dim_company(company_key),
    FOREIGN KEY (metric_key) REFERENCES dim_metric(metric_key)
);

CREATE TABLE IF NOT EXISTS fact_macro_indicator (
    series_key INTEGER NOT NULL,
    observation_date TEXT NOT NULL,
    value REAL NOT NULL,
    PRIMARY KEY (series_key, observation_date),
    FOREIGN KEY (series_key) REFERENCES dim_macro_series(series_key)
);

CREATE INDEX IF NOT EXISTS idx_financial_year ON fact_financial_metric(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_financial_metric ON fact_financial_metric(metric_key);
CREATE INDEX IF NOT EXISTS idx_macro_date ON fact_macro_indicator(observation_date);
