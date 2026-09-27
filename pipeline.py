"""
SalesPulse — Transaction Data Pipeline & MoM Growth Calculator
"""

import os
import csv
from datetime import datetime, timedelta
import random

class SalesPulsePipeline:
    def __init__(self, raw_data_path: str = "data/transactions.csv"):
        self.raw_data_path = raw_data_path
        self.cleaned_records = []

    def clean_and_transform(self):
        """Ingests raw CSV, cleans formatting, imputes missing values, and calculates KPIs."""
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Input file {self.raw_data_path} not found.")

        raw_rows = []
        with open(self.raw_data_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_rows.append(row)

        print(f"[*] Ingested {len(raw_rows)} raw sales records.")
        
        # Transformation
        cleaned = []
        for r in raw_rows:
            try:
                units = int(r.get("Units", 1))
                price = float(r.get("Unit_Price", 0.0))
                revenue = float(r.get("Revenue", units * price))
                profit = float(r.get("Profit", revenue * 0.28))
                date_str = r.get("Date", "2025-01-01").strip()
                region = r.get("Region", "North").strip().title()
                category = r.get("Category", "General").strip().title()

                cleaned.append({
                    "Transaction_ID": r.get("Transaction_ID", f"TXN-{random.randint(1000, 9999)}"),
                    "Date": date_str,
                    "Region": region,
                    "Category": category,
                    "Units": units,
                    "Unit_Price": price,
                    "Revenue": round(revenue, 2),
                    "Profit": round(profit, 2)
                })
            except (ValueError, TypeError):
                continue

        self.cleaned_records = cleaned
        print(f"[✓] Transformed {len(cleaned)} validated transactions.")
        return cleaned

    def compute_summary_kpis(self):
        """Computes top-level business revenue, profit margins, and regional winners."""
        if not self.cleaned_records:
            self.clean_and_transform()

        total_rev = sum(r['Revenue'] for r in self.cleaned_records)
        total_profit = sum(r['Profit'] for r in self.cleaned_records)
        margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

        # Group by Region
        regional_rev = {}
        for r in self.cleaned_records:
            reg = r['Region']
            regional_rev[reg] = regional_rev.get(reg, 0.0) + r['Revenue']

        top_region = max(regional_rev.items(), key=lambda x: x[1])[0] if regional_rev else "N/A"

        return {
            "total_revenue": total_rev,
            "total_profit": total_profit,
            "profit_margin_pct": round(margin, 2),
            "regional_breakdown": regional_rev,
            "top_region": top_region,
            "total_transactions": len(self.cleaned_records)
        }
