import sqlite3

conn = sqlite3.connect('instance/database.db')

cursor = conn.cursor()


cursor.execute(f"DROP TABLE IF EXISTS elements")

conn.commit()
conn.close()