"""Saving revenue in Settings -> Revenues (audit #3, 30 Oct 2026).

Saving 2 or more companies at once used to crash (the Save button did nothing),
because the save loop replaced its own lists of values."""
import pandas as pd
import pytest

import trade.callbacks.settings.revenues as revenues
from trade.utils import market

YEARS = ["2022", "2023"]


def _write_existing(folder):
    """revenue.csv already holding CCC (not edited) and old AAA values."""
    data = pd.DataFrame(
        {("CCC", "2022-12-31 00:00:00"): ["EUR", 5, 50], ("AAA", "2022-12-31 00:00:00"): ["EUR", 1, 1]},
        index=["currencyCode", "NetIncome", "TotalRevenue"],
    )
    data.columns.names = ["symbol", "asOfDate"]
    data.to_csv(folder / "revenue.csv")
    market._revenues_cache[0] = None


def _save(companies, values):
    """Press Save with the boxes filled: values = {company: [(revenue, income) per year]}."""
    labels, revs, incomes = [], [], []
    for company in companies:
        for year, (revenue, income) in zip(YEARS, values[company]):
            labels.append({"type": "revenue", "company": company, "year": year})
            revs.append(revenue)
            incomes.append(income)
    income_labels = [dict(label, type="net_income") for label in labels]
    return revenues.export_revenues(1, companies, "manual", revs, labels, incomes, income_labels)


def _saved(folder):
    return pd.read_csv(folder / "revenue.csv", index_col=0, header=[0, 1])


@pytest.fixture
def folder(fake_data):
    _write_existing(fake_data)
    return fake_data


def test_two_companies_are_saved(folder):
    assert _save(["AAA", "BBB"], {"AAA": [(100, 10), (110, 11)], "BBB": [(200, 20), (220, 22)]}) is False
    df = _saved(folder)
    assert float(df[("BBB", "2023-12-31 00:00:00")]["TotalRevenue"]) == 220
    assert float(df[("AAA", "2022-12-31 00:00:00")]["NetIncome"]) == 10
    assert not df.columns.duplicated().any()
    assert sorted(df.columns.get_level_values(0).unique()) == ["AAA", "BBB", "CCC"]


def test_saving_again_replaces_the_values(folder):
    _save(["AAA", "BBB"], {"AAA": [(100, 10), (110, 11)], "BBB": [(200, 20), (220, 22)]})
    market._revenues_cache[0] = None
    _save(["AAA", "BBB"], {"AAA": [(300, 30), (330, 33)], "BBB": [(400, 40), (440, 44)]})
    df = _saved(folder)
    assert not df.columns.duplicated().any()
    assert len(df.columns) == 5                                  # 2 companies x 2 years + CCC
    assert float(df[("AAA", "2023-12-31 00:00:00")]["TotalRevenue"]) == 330


def test_a_company_not_edited_is_kept(folder):
    _save(["AAA", "BBB"], {"AAA": [(100, 10), (110, 11)], "BBB": [(200, 20), (220, 22)]})
    assert float(_saved(folder)[("CCC", "2022-12-31 00:00:00")]["TotalRevenue"]) == 50


def test_one_company_as_before(folder):
    _save(["AAA"], {"AAA": [(100, 10), (110, 11)]})
    df = _saved(folder)
    assert sorted(df.columns.get_level_values(0).unique()) == ["AAA", "CCC"]
    assert len(df.columns) == 3
    assert float(df[("AAA", "2022-12-31 00:00:00")]["TotalRevenue"]) == 100
