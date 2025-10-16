import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel

DB_NAME = "warehouse.db"

# === ЗАПРОСЫ К БД ===
def get_all_items():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.sku, i.name, c.name AS category, l.name AS location, i.quantity, i.notes
        FROM item i
        JOIN category c ON i.category_id = c.id
        JOIN location l ON i.location_id = l.id
        ORDER BY i.id
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_persons():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM person ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_categories():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM category ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_locations():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM location ORDER BY name")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_item(sku, name, category_id, location_id, quantity, notes):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sku, name, category_id, location_id, quantity, notes))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return False
    finally:
        conn.close()

def delete_item(item_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM item WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def add_checkout(item_id, person_id, issued_by_id, quantity, due_at, is_disposable=False):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO checkout (item_id, person_id, issued_by_id, quantity, checked_out_at, due_at, is_disposable)
            VALUES (?, ?, ?, ?, datetime('now'), ?, ?)
        """, (item_id, person_id, issued_by_id, quantity, due_at, is_disposable))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))
        return False
    finally:
        conn.close()

# === ГЛАВНОЕ ОКНО ===
class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт материальных ценностей (кафедра)")
        self.root.geometry("900x600")

        # Таблица товаров
        columns = ("ID", "SKU", "Наименование", "Категория", "Локация", "Кол-во", "Примечания")
        self.tree = ttk.Treeview(root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="Добавить товар", command=self.add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Выдать товар", command=self.checkout_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить товар", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=5)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in get_all_items():
            self.tree.insert("", "end", values=row)

    def add_item(self):
        sku = simpledialog.askstring("Добавить товар", "SKU:")
        if not sku: return
        name = simpledialog.askstring("Добавить товар", "Наименование:")
        if not name: return

        categories = get_all_categories()
        if not categories:
            messagebox.showwarning("Внимание", "Нет категорий. Создайте хотя бы одну.")
            return
        cat_names = [c[1] for c in categories]
        cat_choice = simpledialog.askinteger("Категория", f"Выберите категорию:\n{chr(10).join(f'{i+1}. {n}' for i, n in enumerate(cat_names))}")
        if not cat_choice or cat_choice < 1 or cat_choice > len(categories):
            return
        category_id = categories[cat_choice-1][0]

        locations = get_all_locations()
        if not locations:
            messagebox.showwarning("Внимание", "Нет локаций. Создайте хотя бы одну.")
            return
        loc_names = [l[1] for l in locations]
        loc_choice = simpledialog.askinteger("Локация", f"Выберите локацию:\n{chr(10).join(f'{i+1}. {n}' for i, n in enumerate(loc_names))}")
        if not loc_choice or loc_choice < 1 or loc_choice > len(locations):
            return
        location_id = locations[loc_choice-1][0]

        quantity = simpledialog.askinteger("Добавить товар", "Количество:", minvalue=1)
        if not quantity: return

        notes = simpledialog.askstring("Добавить товар", "Примечания (опционально):")

        if add_item(sku, name, category_id, location_id, quantity, notes):
            self.load_data()
            messagebox.showinfo("Успех", "Товар добавлен!")

    def delete_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return
        item = self.tree.item(selected[0])
        asset_id = item["values"][0]
        if messagebox.askyesno("Подтверждение", f"Удалить товар ID={asset_id}?"):
            delete_item(asset_id)
            self.load_data()

    def checkout_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для выдачи")
            return
        item = self.tree.item(selected[0])
        item_id = item["values"][0]
        item_name = item["values"][2]

        persons = get_all_persons()
        if not persons:
            messagebox.showwarning("Внимание", "Нет людей. Создайте хотя бы одного.")
            return
        person_names = [p[1] for p in persons]
        person_choice = simpledialog.askinteger("Кому выдать", f"Выберите получателя:\n{chr(10).join(f'{i+1}. {n}' for i, n in enumerate(person_names))}")
        if not person_choice or person_choice < 1 or person_choice > len(persons):
            return
        person_id = persons[person_choice-1][0]

        issued_by_choice = simpledialog.askinteger("Кто выдал", f"Выберите выдавшего:\n{chr(10).join(f'{i+1}. {n}' for i, n in enumerate(person_names))}")
        if not issued_by_choice or issued_by_choice < 1 or issued_by_choice > len(persons):
            return
        issued_by_id = persons[issued_by_choice-1][0]

        quantity = simpledialog.askinteger("Выдать", "Количество:", minvalue=1)
        if not quantity: return

        due_at = simpledialog.askstring("Срок возврата", "Дата возврата (YYYY-MM-DD):")
        if not due_at: return

        is_disposable = messagebox.askyesno("Расходный?", "Это расходный материал?")

        if add_checkout(item_id, person_id, issued_by_id, quantity, due_at, is_disposable):
            messagebox.showinfo("Успех", f"Товар '{item_name}' выдан!")
        else:
            messagebox.showerror("Ошибка", "Не удалось выдать товар.")

# === ЗАПУСК ===
if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()