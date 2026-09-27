"""
SalesPulse — Transaction Data Pipeline & Financial Analytics Engine
Performs ETL, schema inference, IQR outlier detection, MoM growth calculations,
and multidimensional cohort breakdowns.
"""

import os
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

class SalesPulsePipeline:
    def __init__(self, raw_data_path: str = "data/transactions.csv"):
        self.raw_data_path = raw_data_path
        self.records: List[Dict[str, Any]] = []
        self.outliers: List[Dict[str, Any]] = []
        self.profile: Dict[str, Any] = {}

    def _detect_outliers_iqr(self, values: List[float]) -> tuple[float, float]:
        """Calculates Q1, Q3, and IQR bounds for anomaly detection."""
        if len(values) < 4:
            return 0.0, 999999999.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        q1 = sorted_vals[int(n * 0.25)]
        q3 = sorted_vals[int(n * 0.75)]
        iqr = q3 - q1
        lower_bound = max(0.0, q1 - 1.5 * iqr)
        upper_bound = q3 + 1.5 * iqr
        return lower_bound, upper_bound

    def ingest_data(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """Ingests raw CSV records, standardizes schema, and calculates true values."""
        target_path = file_path or self.raw_data_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Input file {target_path} not found.")

        raw_rows = []
        with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_rows.append(row)

        processed = []
        revenues = []

        for r in raw_rows:
            try:
                txn_id = r.get("Transaction_ID") or f"TXN-{len(processed)+1:05d}"
                date_str = r.get("Date", "").strip() or datetime.now().strftime("%Y-%m-%d")
                
                # Standardize Date
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d")
                    month_key = dt.strftime("%Y-%m")
                except ValueError:
                    month_key = "2025-01"

                region = (r.get("Region") or "North").strip().title()
                category = (r.get("Category") or "General").strip().title()
                
                units = max(1, int(float(r.get("Units", 1))))
                unit_price = max(0.0, float(r.get("Unit_Price", 0.0)))
                
                # If Revenue is missing or 0, compute from Units * Unit_Price
                rev = float(r.get("Revenue", 0.0))
                if rev <= 0.0:
                    rev = units * unit_price

                # Profit: check if explicit Profit or Cost is provided, else use category margin model
                if "Profit" in r and float(r.get("Profit", 0.0)) != 0.0:
                    profit = float(r.get("Profit", 0.0))
                elif "Cost" in r:
                    profit = rev - float(r.get("Cost", 0.0))
                else:
                    # Category-based cost modeling (realistic margins by industry)
                    category_margins = {
                        "Software": 0.78,
                        "Services": 0.45,
                        "Hardware": 0.22,
                        "Accessories": 0.35,
                        "Cloud": 0.65
                    }
                    margin_pct = category_margins.get(category, 0.30)
                    profit = round(rev * margin_pct, 2)

                revenues.append(rev)
                processed.append({
                    "Transaction_ID": txn_id,
                    "Date": date_str,
                    "Month": month_key,
                    "Region": region,
                    "Category": category,
                    "Units": units,
                    "Unit_Price": round(unit_price, 2),
                    "Revenue": round(rev, 2),
                    "Profit": round(profit, 2),
                    "Margin_Pct": round((profit / rev * 100) if rev > 0 else 0.0, 2),
                    "Is_Outlier": False
                })
            except (ValueError, TypeError):
                continue

        # IQR Anomaly Detection on Revenue
        if revenues:
            low_b, high_b = self._detect_outliers_iqr(revenues)
            for p in processed:
                if p["Revenue"] > high_b or p["Revenue"] < low_b:
                    p["Is_Outlier"] = True

        self.records = processed
        self.outliers = [p for p in processed if p["Is_Outlier"]]
        return processed

    def get_filtered_analytics(self, region: Optional[str] = None, category: Optional[str] = None,
                               start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Applies dynamic multidimensional filters and computes KPI aggregations."""
        if not self.records:
            self.ingest_data()

        filtered = self.records
        if region and region.lower() != "all":
            filtered = [r for r in filtered if r["Region"].lower() == region.lower()]
        if category and category.lower() != "all":
            filtered = [r for r in filtered if r["Category"].lower() == category.lower()]
        if start_date:
            filtered = [r for r in filtered if r["Date"] >= start_date]
        if end_date:
            filtered = [r for r in filtered if r["Date"] <= end_date]

        if not filtered:
            return {
                "total_revenue": 0.0,
                "total_profit": 0.0,
                "total_transactions": 0,
                "average_order_value": 0.0,
                "profit_margin_pct": 0.0,
                "mom_growth_pct": 0.0,
                "top_region": "None",
                "top_category": "None",
                "monthly_trend": {},
                "regional_breakdown": {},
                "category_breakdown": {},
                "outlier_count": 0
            }

        total_rev = round(sum(r["Revenue"] for r in filtered), 2)
        total_profit = round(sum(r["Profit"] for r in filtered), 2)
        total_txns = len(filtered)
        aov = round(total_rev / total_txns, 2) if total_txns > 0 else 0.0
        avg_margin = round((total_profit / total_rev * 100), 2) if total_rev > 0 else 0.0

        # Monthly Trend (for MoM growth)
        monthly_map: Dict[str, Dict[str, float]] = {}
        for r in filtered:
            m = r["Month"]
            if m not in monthly_map:
                monthly_map[m] = {"revenue": 0.0, "profit": 0.0, "transactions": 0}
            monthly_map[m]["revenue"] += r["Revenue"]
            monthly_map[m]["profit"] += r["Profit"]
            monthly_map[m]["transactions"] += 1

        sorted_months = sorted(monthly_map.keys())
        mom_growth = 0.0
        if len(sorted_months) >= 2:
            prev_rev = monthly_map[sorted_months[-2]]["revenue"]
            curr_rev = monthly_map[sorted_months[-1]]["revenue"]
            if prev_rev > 0:
                mom_growth = round(((curr_rev - prev_rev) / prev_rev) * 100, 2)

        # Regional Breakdown
        regional_map: Dict[str, float] = {}
        for r in filtered:
            reg = r["Region"]
            regional_map[reg] = round(regional_map.get(reg, 0.0) + r["Revenue"], 2)
        top_region = max(regional_map.items(), key=lambda x: x[1])[0] if regional_map else "N/A"

        # Category Breakdown
        category_map: Dict[str, float] = {}
        for r in filtered:
            cat = r["Category"]
            category_map[cat] = round(category_map.get(cat, 0.0) + r["Revenue"], 2)
        top_category = max(category_map.items(), key=lambda x: x[1])[0] if category_map else "N/A"

        return {
            "total_revenue": total_rev,
            "total_profit": total_profit,
            "total_transactions": total_txns,
            "average_order_value": aov,
            "profit_margin_pct": avg_margin,
            "mom_growth_pct": mom_growth,
            "top_region": top_region,
            "top_category": top_category,
            "monthly_trend": monthly_map,
            "regional_breakdown": regional_map,
            "category_breakdown": category_map,
            "outlier_count": sum(1 for r in filtered if r["Is_Outlier"])
        }
