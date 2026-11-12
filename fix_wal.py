import sqlite3
conn = sqlite3.connect('anav_ledger.db')
conn.execute("PRAGMA journal_mode=WAL;")
conn.commit()
conn.close()
print("WAL mode enabled on anav_ledger.db to prevent database lock conflicts.")
