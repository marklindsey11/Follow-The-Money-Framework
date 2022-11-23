from typing import Dict, Any
from pathlib import Path

from nomenklatura.dataset import DataCatalog, Dataset


def test_donations_base(catalog_data: Dict[str, Any]):
    catalog = DataCatalog.from_dict(catalog_data)
    assert len(catalog.datasets) == 3, catalog.datasets
    ds = catalog.get("donations")
    assert ds is not None, ds
    assert ds.name == "donations"
    assert ds.publisher is None
    assert "publisher" not in ds.to_dict()
    assert len(ds.resources) == 2, ds.resources
    for res in ds.resources:
        assert res.name is not None
        if res.mime_type is None:
            assert res.mime_type_label is None


def test_company_dataset(catalog_data: Dict[str, Any]):
    catalog = DataCatalog.from_dict(catalog_data)
    assert len(catalog.datasets) == 3, catalog.datasets
    ds = catalog.get("company_data")
    assert ds is not None, ds
    assert ds.name == "company_data"
    assert ds.publisher is not None
    assert ds.publisher.country == "us"
    assert ds.publisher.country_label == "United States"
    assert ds.coverage is not None
    assert "coverage" in ds.to_dict()
    assert ds.coverage.start == "2005"
    assert ds.coverage.end == "2010-01"
    assert "us" in ds.coverage.countries

    assert "company_data" in repr(ds)

    other = Dataset(name="company_data", title="Company data")
    assert other == ds, other


def test_from_path(catalog_path: Path):
    catalog = DataCatalog.from_path(catalog_path)
    assert len(catalog.datasets) == 3, catalog.datasets
