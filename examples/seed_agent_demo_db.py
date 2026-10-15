import sqlite3
from pathlib import Path


db_path = Path(__file__).resolve().parents[1] / "example.db"

orders = [
    (1, "2026-10-01", "completed", 120.0),
    (2, "2026-10-02", "completed", 85.5),
    (3, "2026-10-03", "pending", 200.0),
    (4, "2026-10-04", "completed", 49.9),
    (5, "2026-10-05", "cancelled", 35.0),
]

with sqlite3.connect(db_path) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            amount REAL NOT NULL
        )
    """)
    conn.executemany(
        """
        INSERT OR REPLACE INTO orders (order_id, order_date, status, amount)
        VALUES (?, ?, ?, ?)
        """,
        orders,
    )

print(f"已写入演示订单数据：{db_path}")