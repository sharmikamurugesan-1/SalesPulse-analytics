"""
SalesPulse — End-to-End Execution Pipeline
"""

import os
import time
from data.generate_dataset import generate_sales_data
from pipeline import SalesPulsePipeline
from db_loader import SalesPulseDatabase
from visualizer import SalesVisualizer

def run_salespulse():
    print("=" * 60)
    print("📊 SalesPulse — Sales Analytics & ETL Pipeline")
    print("=" * 60)
    
    data_file = "data/transactions.csv"
    if not os.path.exists(data_file):
        print("[*] Transactions dataset not found. Generating sample data...")
        generate_sales_data(data_file, num_rows=400)

    start = time.time()
    
    # 1. ETL Pipeline
    pipe = SalesPulsePipeline(raw_data_path=data_file)
    cleaned = pipe.clean_and_transform()
    kpis = pipe.compute_summary_kpis()

    # 2. Database Load
    db = SalesPulseDatabase("salespulse.db")
    loaded_count = db.load_transactions(cleaned)
    print(f"[✓] Loaded {loaded_count} rows into SQLite database 'salespulse.db'.")

    # 3. Visuals
    vis = SalesVisualizer("output")
    chart_file = vis.generate_summary_chart(kpis)
    print(f"[✓] Generated executive chart: {chart_file}")

    elapsed = time.time() - start
    
    print("-" * 60)
    print(f"💰 Total Revenue:     ${kpis['total_revenue']:,.2f}")
    print(f"📈 Total Profit:      ${kpis['total_profit']:,.2f} ({kpis['profit_margin_pct']}%)")
    print(f"🌍 Top Region:        {kpis['top_region']}")
    print(f"⏱️  Pipeline Runtime:  {elapsed:.2f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    run_salespulse()
