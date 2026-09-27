"""
SalesPulse — Visualizer & Chart Generator
"""

import os
from typing import Dict, Any

class SalesVisualizer:
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_summary_chart(self, kpi_data: Dict[str, Any]) -> str:
        """Generates a regional revenue comparison report."""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt

            breakdown = kpi_data.get("regional_breakdown", {})
            regions = list(breakdown.keys())
            revenues = [breakdown[r] for r in regions]

            fig, ax = plt.subplots(figsize=(9, 5))
            bars = ax.bar(regions, revenues, color='#6366f1', edgecolor='#4338ca', alpha=0.9)
            
            ax.set_title("SalesPulse — Revenue by Region (2025)", fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel("Revenue ($ USD)", fontsize=11)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
            
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'${height:,.0f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=9, fontweight='bold')

            plt.xticks(rotation=15)
            plt.tight_layout()
            
            chart_path = os.path.join(self.output_dir, "regional_revenue_breakdown.png")
            plt.savefig(chart_path, dpi=200)
            plt.close()
            return chart_path
        except ImportError:
            # Fallback text summary
            text_path = os.path.join(self.output_dir, "summary_report.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(f"SalesPulse KPI Summary\nTotal Revenue: ${kpi_data['total_revenue']:,.2f}\n")
            return text_path
