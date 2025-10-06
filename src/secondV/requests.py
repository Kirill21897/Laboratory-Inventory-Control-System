import sqlite3

conn = sqlite3.connect('src/second variant/main.db')
cur = conn.cursor()

cur.execute('''CREATE TABLE IF NOT EXISTS item(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku INTEGER,
            name VARCHAR(30),
            category_id INTEGER,
            location_id INTEGER,
            quantity INTEGER,
            notes VARCHAR(100)
);''')

def sItem(itemName):
    cur.execute('SELECT id,sku,name,category_id,location_id,quantity,notes FROM item WHERE name = (?)',itemName)
    return cur.fetchone() # возвращает список