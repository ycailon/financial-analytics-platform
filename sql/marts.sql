DROP VIEW IF EXISTS mart_company_yearly;
CREATE VIEW mart_company_yearly AS
WITH base AS (
    SELECT
        c.company_key,
        c.ticker,
        c.company_name,
        c.sector,
        f.fiscal_year,
        MAX(CASE WHEN m.metric_code = 'revenue' THEN f.value END) AS revenue,
        MAX(CASE WHEN m.metric_code = 'operating_income' THEN f.value END) AS operating_income,
        MAX(CASE WHEN m.metric_code = 'net_income' THEN f.value END) AS net_income,
        MAX(CASE WHEN m.metric_code = 'operating_cash_flow' THEN f.value END) AS operating_cash_flow,
        MAX(CASE WHEN m.metric_code = 'capex' THEN f.value END) AS capex,
        MAX(CASE WHEN m.metric_code = 'assets' THEN f.value END) AS assets,
        MAX(CASE WHEN m.metric_code = 'liabilities' THEN f.value END) AS liabilities,
        MAX(CASE WHEN m.metric_code = 'equity' THEN f.value END) AS equity
    FROM fact_financial_metric f
    JOIN dim_company c ON c.company_key = f.company_key
    JOIN dim_metric m ON m.metric_key = f.metric_key
    GROUP BY c.company_key, c.ticker, c.company_name, c.sector, f.fiscal_year
), calculated AS (
    SELECT
        *,
        CASE WHEN revenue <> 0 THEN net_income / revenue END AS profit_margin,
        CASE WHEN revenue <> 0 THEN operating_income / revenue END AS operating_margin,
        CASE WHEN assets <> 0 THEN liabilities / assets END AS debt_to_assets,
        CASE WHEN assets <> 0 THEN net_income / assets END AS return_on_assets,
        CASE WHEN equity <> 0 THEN net_income / equity END AS return_on_equity,
        CASE WHEN operating_cash_flow <> 0 THEN capex / operating_cash_flow END AS capex_to_operating_cash_flow
    FROM base
)
SELECT
    *,
    CASE
        WHEN LAG(revenue) OVER (PARTITION BY company_key ORDER BY fiscal_year) <> 0
        THEN revenue / LAG(revenue) OVER (PARTITION BY company_key ORDER BY fiscal_year) - 1
    END AS revenue_growth_yoy,
    CASE
        WHEN LAG(net_income) OVER (PARTITION BY company_key ORDER BY fiscal_year) <> 0
        THEN net_income / LAG(net_income) OVER (PARTITION BY company_key ORDER BY fiscal_year) - 1
    END AS net_income_growth_yoy
FROM calculated;

DROP VIEW IF EXISTS mart_macro_monthly;
CREATE VIEW mart_macro_monthly AS
WITH base AS (
    SELECT
        f.observation_date,
        MAX(CASE WHEN s.series_code = 'cpi_u' THEN f.value END) AS cpi_u,
        MAX(CASE WHEN s.series_code = 'unemployment_rate' THEN f.value END) AS unemployment_rate
    FROM fact_macro_indicator f
    JOIN dim_macro_series s ON s.series_key = f.series_key
    GROUP BY f.observation_date
)
SELECT
    *,
    CASE
        WHEN LAG(cpi_u, 12) OVER (ORDER BY observation_date) <> 0
        THEN cpi_u / LAG(cpi_u, 12) OVER (ORDER BY observation_date) - 1
    END AS inflation_yoy
FROM base;

DROP VIEW IF EXISTS mart_company_economic_context;
CREATE VIEW mart_company_economic_context AS
WITH macro_annual AS (
    SELECT
        CAST(substr(observation_date, 1, 4) AS INTEGER) AS calendar_year,
        AVG(cpi_u) AS avg_cpi_u,
        AVG(unemployment_rate) AS avg_unemployment_rate,
        AVG(inflation_yoy) AS avg_inflation_yoy
    FROM mart_macro_monthly
    GROUP BY CAST(substr(observation_date, 1, 4) AS INTEGER)
)
SELECT
    c.*,
    m.avg_cpi_u,
    m.avg_unemployment_rate,
    m.avg_inflation_yoy
FROM mart_company_yearly c
LEFT JOIN macro_annual m ON m.calendar_year = c.fiscal_year;
