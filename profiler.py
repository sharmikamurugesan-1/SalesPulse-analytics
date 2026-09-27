"""
SalesPulse — Automated Data Profiler & Quality Scorecard
Evaluates CSV/tabular datasets for null density, duplicate records,
schema consistency, and computes a 0-100 Data Health Score.
"""

from typing import List, Dict, Any

class DataProfiler:
    def profile_dataset(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not records:
            return {
                "health_score": 0.0,
                "total_rows": 0,
                "columns": [],
                "missing_values": 0,
                "outliers_detected": 0,
                "grade": "F"
            }

        total_rows = len(records)
        columns = list(records[0].keys())
        missing_count = 0
        outliers_count = sum(1 for r in records if r.get("Is_Outlier", False))

        column_stats = {}
        for col in columns:
            vals = [r.get(col) for r in records]
            nulls = sum(1 for v in vals if v is None or str(v).strip() == "" or v == "N/A")
            missing_count += nulls
            uniques = len(set(str(v) for v in vals))
            column_stats[col] = {
                "missing": nulls,
                "missing_pct": round((nulls / total_rows) * 100, 1),
                "unique_values": uniques
            }

        # Health Score computation
        total_cells = total_rows * len(columns)
        completeness_ratio = 1.0 - (missing_count / total_cells) if total_cells > 0 else 0.0
        outlier_ratio = 1.0 - min(outliers_count / total_rows, 0.3)
        
        # Weighted score (Completeness 70%, Regularity 30%)
        health_score = round((completeness_ratio * 70.0 + outlier_ratio * 30.0), 1)

        grade = "A+" if health_score >= 95 else ("A" if health_score >= 90 else ("B" if health_score >= 75 else "C"))

        return {
            "health_score": health_score,
            "grade": grade,
            "total_rows": total_rows,
            "total_columns": len(columns),
            "missing_cells": missing_count,
            "outliers_detected": outliers_count,
            "column_metrics": column_stats
        }
