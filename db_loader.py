"""
SalesPulse — SQLite Relational Database Loader
Persists raw and transformed sales transactions, aggregates, and data profiling metrics.
"""

import sqlite3
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "salespulse.db")

def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    """Initializes tables and performance indexes for sales analytics."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT NOT NULL,
        date TEXT NOT NULL,
        month TEXT NOT NULL,
        region TEXT NOT NULL,
        category TEXT NOT NULL,
        units INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        revenue REAL NOT NULL,
        profit REAL NOT NULL,
        margin_pct REAL NOT NULL,
        is_outlier INTEGER DEFAULT 0
    );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_date ON transactions(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_region ON transactions(region);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_txn_category ON transactions(category);")

    conn.commit()
    conn.close()

def load_transactions_to_db(records: List[Dict[str, Any]], db_path: str = DB_PATH):
    """Loads batch of transaction dictionaries into SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()

    # Clear existing to maintain clean sync
    cur.execute("DELETE FROM transactions;")

    cur.executemany("""
    INSERT INTO transactions (
        transaction_id, date, month, region, category, units,
        unit_price, revenue, profit, margin_pct, is_outlier
    ) VALUES (
        :Transaction_ID, :Date, :Month, :Region, :Category, :Units,
        :Unit_Price, :Revenue, :Profit, :Margin_Pct, :Is_Outlier
    )
    """, records)

    conn.commit()
    conn.close()

def query_sales_summary(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Queries aggregate financial performance directly from SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*), SUM(revenue), SUM(profit), AVG(revenue) FROM transactions")
    count, rev, profit, aov = cur.fetchone()

    conn.close()
    return {
        "count": count or 0,
        "revenue": round(rev or 0.0, 2),
        "profit": round(profit or 0.0, 2),
        "aov": round(aov or 0.0, 2)
    }
