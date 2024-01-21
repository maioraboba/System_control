import sqlite3 as sql

con = sql.connect("data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER, name VARCHAR, photo BLOB)')

for i in range(1):
    with open(f"{i}.jpg", "rb") as photo:
        h = photo.read()
        cur.execute("INSERT INTO photos VALUES(1, 'roman', ?)", [h])

con.commit()
cur.close()
con.close()