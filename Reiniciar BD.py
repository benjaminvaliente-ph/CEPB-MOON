import sqlite3

conn = sqlite3.connect("db_CEPBMOON.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""UPDATE tabdelegaciones SET enforo = 0""")
cursor.execute("""UPDATE tabdelegados SET Delegado = NULL""")

conn.commit()