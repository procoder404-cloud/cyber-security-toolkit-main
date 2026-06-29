
import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

# ==========================
# Users Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    email TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL

)
""")

# ==========================
# Scan History Table
# ==========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS scan_history(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT,

    tool_name TEXT,

    result TEXT,

    scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()

conn.close()

print("Database Created Successfully!")