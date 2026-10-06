from financial_analytics.config import Company, MetricDefinition
from financial_analytics.demo import make_demo_sec_payload
from financial_analytics.transform.sec import transform_company_facts


def metric(code: str, key: int, concept: str, period_type: str) -> MetricDefinition:
    return MetricDefinition(
        metric_key=key,
        metric_code=code,
        metric_name=code.replace("_", " ").title(),
        category="Test",
        unit="USD",
        period_type=period_type,
        concepts=(concept,),
    )


def test_sec_transform_selects_annual_facts():
    company = Company(1, "0000320193", "TEST", "Test Company", "Technology")
    metrics = [
        metric("revenue", 1, "RevenueFromContractWithCustomerExcludingAssessedTax", "duration"),
        metric("assets", 2, "Assets", "instant"),
    ]
    payload = make_demo_sec_payload(company, metrics, 2023, 2025)

    frame = transform_company_facts(payload, company, metrics, 2023, 2025)

    assert len(frame) == 6
    assert set(frame["fiscal_year"]) == {2023, 2024, 2025}
    assert set(frame["metric_key"]) == {1, 2}
    assert frame["value"].gt(0).all()


def test_sec_transform_prefers_higher_priority_concept():
    company = Company(1, "0000000001", "TEST", "Test Company", "Technology")
    revenue = MetricDefinition(
        metric_key=1,
        metric_code="revenue",
        metric_name="Revenue",
        category="Income Statement",
        unit="USD",
        period_type="duration",
        concepts=("PreferredRevenue", "FallbackRevenue"),
    )
    common = {
        "start": "2024-01-01",
        "end": "2024-12-31",
        "fy": 2024,
        "fp": "FY",
        "form": "10-K",
        "filed": "2025-02-01",
        "accn": "x",
    }
    payload = {
        "facts": {
            "us-gaap": {
                "PreferredRevenue": {"units": {"USD": [{**common, "val": 100.0}]}},
                "FallbackRevenue": {"units": {"USD": [{**common, "val": 999.0}]}},
            }
        }
    }

    frame = transform_company_facts(payload, company, [revenue], 2024, 2024)

    assert len(frame) == 1
    assert frame.loc[0, "value"] == 100.0
    assert frame.loc[0, "source_concept"] == "PreferredRevenue"
