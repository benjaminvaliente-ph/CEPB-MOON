import sqlite3

# conn = sqlite3.connect("db_CEPBMOON.db")
# conn.row_factory = sqlite3.Row
# cursor = conn.cursor()

# cursor.execute("""SELECT idPais FROM tabdelegaciones""")
# paises = cursor.fetchall()
# i = 0
# for pais in paises:
#     i += 1
#     cursor.execute("""INSERT INTO tabdelegados VALUES (NULL, NULL, ?, ?)""",(pais["idPais"], i))
#     i += 1
#     cursor.execute("""INSERT INTO tabdelegados VALUES (NULL, NULL, ?, ?)""",(pais["idPais"], i))
#     conn.commit()
# print("a")

conn = sqlite3.connect("db_CEPBMOON.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("""SELECT idDelegacion, nomDelegacion FROM tabDelegaciones WHERE enforo = 2""")
paisesEnForo=cursor.fetchall()
for pais in paisesEnForo:
    print(pais["nomDelegacion"], pais["idDelegacion"])

# txt = "Nara Diaz Rojas"
# print(txt.split(" ", 1))