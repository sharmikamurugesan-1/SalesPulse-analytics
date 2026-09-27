"""
SalesPulse — SQLite Database Loader
"""

import sqlite3
import os
from typing import List, Dict, Any

class SalesPulseDatabase:
    def __init__(self, db_path: str = "salespulse.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT UNIQUE,
                date TEXT,
                region TEXT,
                category TEXT,
                units INTEGER,
                unit_price REAL,
                revenue REAL,
                profit REAL
            )
        """)
        conn.commit()
        conn.close()

    def load_transactions(self, records: List[Dict[str, Any]]) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted = 0
        for r in records:
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO sales_transactions 
                    (transaction_id, date, region, category, units, unit_price, revenue, profit)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    r['Transaction_ID'], r['Date'], r['Region'], r['Category'],
                    r['Units'], r['Unit_Price'], r['Revenue'], r['Profit']
                ))
                inserted += 1
            except Exception as e:
                continue

        conn.commit()
        conn.close()
        return inserted
