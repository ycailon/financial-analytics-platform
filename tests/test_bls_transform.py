from financial_analytics.config import MacroSeries
from financial_analytics.demo import make_demo_bls_payload
from financial_analytics.transform.bls import transform_bls_response


def test_bls_transform_builds_monthly_rows():
    series = [
        MacroSeries(1, "CUUR0000SA0", "cpi_u", "CPI", "Index", "Monthly"),
        MacroSeries(2, "LNS14000000", "unemployment_rate", "Unemployment", "Percent", "Monthly"),
    ]
    payload = make_demo_bls_payload(series, 2024, 2025)

    frame = transform_bls_response(payload, series)

    assert len(frame) == 48
    assert frame["observation_date"].min() == "2024-01-01"
    assert frame["observation_date"].max() == "2025-12-01"
    assert set(frame["series_key"]) == {1, 2}
