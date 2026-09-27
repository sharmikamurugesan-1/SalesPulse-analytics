import os
import csv
import random
from datetime import datetime, timedelta

def generate_sales_data(filepath: str = "data/transactions.csv", num_rows: int = 500):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]
    categories = {
        "Cloud Software": (299.0, 1200.0),
        "Hardware Systems": (450.0, 2400.0),
        "Consulting Services": (150.0, 800.0),
        "Support & SLA": (99.0, 450.0)
    }

    start_date = datetime(2025, 1, 1)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Transaction_ID", "Date", "Region", "Category", "Units", "Unit_Price", "Revenue", "Profit"])
        
        for i in range(1, num_rows + 1):
            txn_id = f"TXN-2025-{i:04d}"
            random_days = random.randint(0, 180)
            date_val = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
            region = random.choice(regions)
            cat = random.choice(list(categories.keys()))
            min_p, max_p = categories[cat]
            price = round(random.uniform(min_p, max_p), 2)
            units = random.randint(1, 12)
            rev = round(units * price, 2)
            profit_margin = random.uniform(0.22, 0.42)
            profit = round(rev * profit_margin, 2)
            
            writer.writerow([txn_id, date_val, region, cat, units, price, rev, profit])

    print(f"[✓] Generated {num_rows} transactions in {filepath}")

if __name__ == "__main__":
    generate_sales_data()
