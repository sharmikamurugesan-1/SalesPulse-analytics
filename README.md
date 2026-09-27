# 📊 SalesPulse — Business Sales Analytics & ETL Pipeline

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Power BI Ready](https://img.shields.io/badge/Power%20BI-Integrated-yellow.svg)]()

> **Impact:** ⚡ Turns raw CSV exports into actionable business insights in seconds.

**SalesPulse** is an end-to-end sales analytics pipeline that ingests messy transaction CSVs, cleans and transforms data using Pandas, stores normalized records in SQLite, and generates interactive executive charts and Power BI-ready datasets.

---

## 📌 Architecture & ETL Workflow

```
[Raw POS / Transaction CSVs]
             │
             ▼
[Pandas Cleaning Pipeline] ──► Imputes nulls, parses dates, calculates margins
             │
             ▼
[SQLite Storage & Modeling] ──► Structured relational transactions table
             │
             ▼
[Visualizer & BI Models]   ──► Regional heatmaps, revenue trends & Power BI output
```

---

## ✨ Features

- **Automated Data Cleaning:** Normalizes transaction timestamps, handles missing postal codes, and calculates profit margins.
- **SQLite Database Ingestion:** Upserts transactions into structured relational storage for SQL queries.
- **Executive Visualizations:** Produces automated charts showing revenue by region and product category breakdowns.
- **Power BI Compatibility:** Structured schema ready for instant import into Microsoft Power BI or Tableau.

---

## 🚀 Quickstart

### 1. Installation
```bash
git clone https://github.com/sharmika-murugesan/SalesPulse-analytics.git
cd SalesPulse-analytics
pip install -r requirements.txt
```

### 2. Run the Analytics Pipeline
```bash
python main.py
```

### 3. Check Outputs
- Cleaned SQLite Database: `salespulse.db`
- Executive Revenue Chart: `output/regional_revenue_breakdown.png`

---

## 🛠️ Tech Stack

- **Data Processing:** Python 3.10+, Pandas, NumPy
- **Database:** SQLite
- **Visualization:** Matplotlib, Seaborn, Power BI

---

## 📄 License
MIT License. Developed by **Sharmika Murugesan** — Available for freelance data analytics projects.
