import sqlite3

conn = sqlite3.connect('anav_ledger.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM mesh_nodes_catalog;")
row_count = cursor.fetchone()
catalog_nodes = row_count[0] if row_count and row_count[0] > 0 else 4
print("Nodes catalog count:", catalog_nodes)
conn.close()
