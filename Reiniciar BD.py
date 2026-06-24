import sqlite3

conn = sqlite3.connect("db_CEPBMOON.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("UPDATE tabDelegaciones SET enforo = 0")
cursor.execute("UPDATE tabDelegados SET nomDelegado = NULL")
cursor.execute("DELETE FROM tabDelegados")
cursor.execute("DELETE FROM tabPuntaje")
cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'tabDelegados'")
cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'tabPuntaje'")
cursor.execute("UPDATE tabMesa SET Presidente = NULL")
cursor.execute("UPDATE tabMesa SET Moderador = NULL")
cursor.execute("UPDATE tabMesa SET Secretario = NULL")
cursor.execute("UPDATE tabMesa SET Evaluador = NULL")
cursor.execute("UPDATE tabMesa SET Foro = NULL")
cursor.execute("UPDATE tabMesa SET Año = ' ' ")

conn.commit()