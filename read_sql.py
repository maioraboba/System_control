import sqlite3 as sql

con = sql.connect("data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
event = ("roman", )
cur.execute('SELECT photo FROM photos WHERE name = ?', event)
photos = cur.fetchall()

sc = 0
for photo in photos:
    with open(f'{sc}.jpg', 'wb') as file:
        file.write(photo[0])
        sc += 1

con.commit()
cur.close()
con.close()
