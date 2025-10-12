import sqlite3

# cur.execute("DROP TABLE IF EXISTS checkout;")
# cur.execute("DROP TABLE IF EXISTS item;")
# cur.execute("DROP TABLE IF EXISTS location;")
# cur.execute("DROP TABLE IF EXISTS category;")
# cur.execute("DROP TABLE IF EXISTS person;")

# cur.execute('''CREATE TABLE IF NOT EXISTS person (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL
# );''')

# cur.execute('''CREATE TABLE IF NOT EXISTS category (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL
# );''')

# cur.execute('''CREATE TABLE IF NOT EXISTS location (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     name TEXT NOT NULL
# );''')

# cur.execute('''CREATE TABLE IF NOT EXISTS item (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     sku TEXT UNIQUE NOT NULL,
#     name TEXT NOT NULL,
#     category_id INTEGER,
#     location_id INTEGER,
#     quantity INTEGER NOT NULL DEFAULT 0,
#     notes TEXT,
#     FOREIGN KEY (category_id) REFERENCES category(id),
#     FOREIGN KEY (location_id) REFERENCES location(id)
# );''')

# cur.execute('''CREATE TABLE IF NOT EXISTS checkout (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     item_id INTEGER NOT NULL,
#     person_id INTEGER NOT NULL,
#     quantity INTEGER NOT NULL,
#     checked_out_at TEXT NOT NULL,
#     due_at TEXT,
#     returned_at TEXT,
#     is_disposable BOOLEAN NOT NULL DEFAULT 0,
#     issued_by_id INTEGER,
#     FOREIGN KEY (item_id) REFERENCES item(id),
#     FOREIGN KEY (person_id) REFERENCES person(id),
#     FOREIGN KEY (issued_by_id) REFERENCES person(id)
# );''')

# cur.execute("INSERT INTO person (name) VALUES ('Иван Петров');")
# cur.execute("INSERT INTO person (name) VALUES ('Анна Смирнова');")
# cur.execute("INSERT INTO person (name) VALUES ('Сергей Иванов');")

# cur.execute("INSERT INTO category (name) VALUES ('Инструменты');")
# cur.execute("INSERT INTO category (name) VALUES ('Расходные материалы');")
# cur.execute("INSERT INTO category (name) VALUES ('Оборудование');")

# cur.execute("INSERT INTO location (name) VALUES ('Склад №1');")
# cur.execute("INSERT INTO location (name) VALUES ('Склад №2');")
# cur.execute("INSERT INTO location (name) VALUES ('Цех');")

# cur.execute('''INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
# VALUES ('HMR-001', 'Молоток', 1, 1, 15, 'Стандартный молоток');''')

# cur.execute('''INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
# VALUES ('SCW-010', 'Саморезы 4x40 (упаковка)', 2, 1, 200, 'В коробке по 100 шт.');''')

# cur.execute('''INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
# VALUES ('DRL-100', 'Дрель электрическая', 3, 2, 5, 'Makita, 220V');''')

# cur.execute('''INSERT INTO checkout (item_id, person_id, quantity, checked_out_at, due_at, is_disposable, issued_by_id)
# VALUES (1, 2, 1, '2025-10-03 09:00:00', '2025-10-10 18:00:00', 0, 1);''')

# cur.execute('''INSERT INTO checkout (item_id, person_id, quantity, checked_out_at, is_disposable, issued_by_id)
# VALUES (2, 3, 50, '2025-10-02 14:30:00', 1, 1);''')
# conn.commit()

# fetchall - [(),(),()] Список кортежей
# fetchone - () - кортеж(первая по условию строка)

class WareHouseSql:
    def __init__(self, db_path="warehouse.db"):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
    
    def info(self):
        self.cur.execute('SELECT * FROM person')
        return self.cur.fetchall()
    
    def selectInfo(self,tableName):
        self.cur.execute(f'SELECT * FROM {tableName}')
        return self.cur.fetchall()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
    
    def close(self):
        self.conn.close()

# Usage:
with WareHouseSql() as warehouse:
    data = warehouse.info()
    print(data)
    tableName = input()
    data = warehouse.selectInfo(tableName)
    print(data)

    
