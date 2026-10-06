-- Largest revenue growth by company/year.
SELECT ticker, fiscal_year, revenue, revenue_growth_yoy
FROM mart_company_yearly
WHERE revenue_growth_yoy IS NOT NULL
ORDER BY revenue_growth_yoy DESC;

-- Profitability comparison for the most recent fiscal year available per company.
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY company_key ORDER BY fiscal_year DESC) AS rn
    FROM mart_company_yearly
)
SELECT ticker, fiscal_year, revenue, net_income, profit_margin, return_on_assets, return_on_equity
FROM ranked
WHERE rn = 1
ORDER BY profit_margin DESC;

-- Financial performance beside calendar-year economic context.
SELECT ticker, fiscal_year, revenue_growth_yoy, profit_margin,
       avg_inflation_yoy, avg_unemployment_rate
FROM mart_company_economic_context
ORDER BY fiscal_year, ticker;
