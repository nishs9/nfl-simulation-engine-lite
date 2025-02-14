import sqlite3
import os

def get_db_conn() -> sqlite3.Connection:
    db_conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "nfl_stats.db"))
    return db_conn