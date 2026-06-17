import sqlite3

conn = sqlite3.connect("db_CEPBMOON.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""UPDATE tabDelegaciones SET enforo = 0""")
cursor.execute("""UPDATE tabDelegados SET nomDelegado = NULL""")
cursor.execute("""DELETE FROM tabDelegados""")
cursor.execute("""UPDATE tabMesa SET Presidente = Moderador = Secretario = Evaluador = Foro = Año = NULL""")

conn.commit()