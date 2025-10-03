-- Таблица сотрудников / пользователей
CREATE TABLE person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Таблица категорий товаров
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Таблица мест хранения (склад, полка, ячейка)
CREATE TABLE location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

-- Таблица товаров
CREATE TABLE item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER,
    location_id INTEGER,
    quantity INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (category_id) REFERENCES category(id),
    FOREIGN KEY (location_id) REFERENCES location(id)
);

-- Таблица выдачи/возврата
CREATE TABLE checkout (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    checked_out_at TEXT NOT NULL,
    due_at TEXT,
    returned_at TEXT,
    is_disposable BOOLEAN NOT NULL DEFAULT 0,
    issued_by_id INTEGER,
    FOREIGN KEY (item_id) REFERENCES item(id),
    FOREIGN KEY (person_id) REFERENCES person(id),
    FOREIGN KEY (issued_by_id) REFERENCES person(id)
);
