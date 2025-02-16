from mfrc522 import SimpleMFRC522

import sqlite3 as sql

if __name__ == "__main__":
    con = sql.connect("data.db")
    cur = con.cursor()

    reader = SimpleMFRC522()
    print('Awaiting input...')

    while True:
        event = reader.read()
        print(event)
        if event:
            cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER PRIMARY KEY, name VARCHAR, photo BLOB)')
            event = event[1].strip()
            print(event)
            cur.execute('SELECT photo FROM photos WHERE name = ?', [event])
            photos = cur.fetchall()

            if photos:
                for photo in photos:
                    with open(f"{event}.jpg", "wb") as file:
                        file.write(photo[0])