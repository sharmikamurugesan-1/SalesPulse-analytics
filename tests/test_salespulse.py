"""
Unit & Integration Tests for SalesPulse-analytics
Validates ETL transformation, IQR outlier detection, KPI calculations, and data profiling.
"""

import os
import pytest
from pipeline import SalesPulsePipeline
from profiler import DataProfiler
from db_loader import init_db, load_transactions_to_db, query_sales_summary

TEST_DB = "test_salespulse.db"

@pytest.fixture(autouse=True)
def setup_teardown():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_pipeline_ingestion_and_kpis(tmp_path):
    csv_file = tmp_path / "test_sales.csv"
    csv_file.write_text(
        "Transaction_ID,Date,Region,Category,Units,Unit_Price,Revenue,Profit\n"
        "TXN-01,2025-01-10,North,Software,2,100.0,200.0,150.0\n"
        "TXN-02,2025-01-15,South,Services,1,50.0,50.0,20.0\n"
        "TXN-03,2025-02-05,North,Software,4,100.0,400.0,300.0\n"
        "TXN-04,2025-02-12,East,Hardware,1,10.0,10.0,2.0\n"
    )

    pipeline = SalesPulsePipeline(raw_data_path=str(csv_file))
    records = pipeline.ingest_data()

    assert len(records) == 4
    analytics = pipeline.get_filtered_analytics()
    
    assert analytics["total_revenue"] == 660.0
    assert analytics["total_profit"] == 472.0
    assert analytics["total_transactions"] == 4
    assert analytics["top_region"] == "North"
    assert analytics["top_category"] == "Software"
    assert analytics["average_order_value"] == 165.0

def test_iqr_outlier_detection(tmp_path):
    # Dataset with 1 extreme outlier
    csv_file = tmp_path / "outlier_sales.csv"
    csv_file.write_text(
        "Transaction_ID,Date,Region,Category,Units,Unit_Price,Revenue,Profit\n"
        "TXN-01,2025-01-10,North,Software,1,100.0,100.0,70.0\n"
        "TXN-02,2025-01-11,North,Software,1,105.0,105.0,72.0\n"
        "TXN-03,2025-01-12,North,Software,1,98.0,98.0,68.0\n"
        "TXN-04,2025-01-13,North,Software,1,102.0,102.0,71.0\n"
        "TXN-05,2025-01-14,North,Software,1,5000.0,5000.0,3500.0\n"  # Clear outlier
    )

    pipeline = SalesPulsePipeline(raw_data_path=str(csv_file))
    records = pipeline.ingest_data()

    outliers = [r for r in records if r["Is_Outlier"]]
    assert len(outliers) == 1
    assert outliers[0]["Transaction_ID"] == "TXN-05"

def test_data_profiler(tmp_path):
    profiler = DataProfiler()
    sample_records = [
        {"Transaction_ID": "T1", "Revenue": 100.0, "Region": "North", "Is_Outlier": False},
        {"Transaction_ID": "T2", "Revenue": 200.0, "Region": None, "Is_Outlier": False},
    ]
    report = profiler.profile_dataset(sample_records)
    
    assert report["total_rows"] == 2
    assert report["missing_cells"] == 1
    assert report["health_score"] > 80.0

def test_sqlite_loader_and_summary():
    records = [
        {"Transaction_ID": "T1", "Date": "2025-01-01", "Month": "2025-01", "Region": "North",
         "Category": "Software", "Units": 2, "Unit_Price": 50.0, "Revenue": 100.0, "Profit": 70.0,
         "Margin_Pct": 70.0, "Is_Outlier": 0}
    ]
    load_transactions_to_db(records, db_path=TEST_DB)
    summary = query_sales_summary(db_path=TEST_DB)
    
    assert summary["count"] == 1
    assert summary["revenue"] == 100.0
    assert summary["profit"] == 70.0
