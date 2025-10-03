-- ======================
-- СБРОС (если база была)
-- ======================
DROP TABLE IF EXISTS checkout;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS location;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS person;

-- ======================
-- ТАБЛИЦЫ
-- ======================

CREATE TABLE person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE location (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

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

-- ======================
-- ДАННЫЕ
-- ======================

-- Люди
INSERT INTO person (name) VALUES ('Иван Петров');
INSERT INTO person (name) VALUES ('Анна Смирнова');
INSERT INTO person (name) VALUES ('Сергей Иванов');

-- Категории
INSERT INTO category (name) VALUES ('Инструменты');
INSERT INTO category (name) VALUES ('Расходные материалы');
INSERT INTO category (name) VALUES ('Оборудование');

-- Локации
INSERT INTO location (name) VALUES ('Склад №1');
INSERT INTO location (name) VALUES ('Склад №2');
INSERT INTO location (name) VALUES ('Цех');

-- Товары
INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
VALUES ('HMR-001', 'Молоток', 1, 1, 15, 'Стандартный молоток');

INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
VALUES ('SCW-010', 'Саморезы 4x40 (упаковка)', 2, 1, 200, 'В коробке по 100 шт.');

INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
VALUES ('DRL-100', 'Дрель электрическая', 3, 2, 5, 'Makita, 220V');

-- Выдачи (пример)
INSERT INTO checkout (item_id, person_id, quantity, checked_out_at, due_at, is_disposable, issued_by_id)
VALUES (1, 2, 1, '2025-10-03 09:00:00', '2025-10-10 18:00:00', 0, 1);

INSERT INTO checkout (item_id, person_id, quantity, checked_out_at, is_disposable, issued_by_id)
VALUES (2, 3, 50, '2025-10-02 14:30:00', 1, 1);
