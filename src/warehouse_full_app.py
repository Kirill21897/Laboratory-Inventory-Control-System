import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog, Toplevel
from datetime import datetime
import csv
import shutil
import os
import re

# === НАСТРОЙКИ ===
DB_NAME = "src/warehouse.db"  

# === БАЗА ДАННЫХ ===
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON") # Включает внешние ключи для SQLite
    return conn

def backup_db():
    backup_name = f"{DB_NAME}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_NAME, backup_name)
    return backup_name

def get_all_items():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT i.id, i.sku, i.name, c.name, l.name, i.quantity, i.notes
            FROM item i
            JOIN category c ON i.category_id = c.id
            JOIN location l ON i.location_id = l.id
            ORDER BY i.name
        """)
        return cur.fetchall()

def get_item_by_id(item_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM item WHERE id = ?", (item_id,))
        return cur.fetchone()

def get_checkout_history():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT ch.id, i.name, p.name, ib.name,
                   ch.quantity, ch.checked_out_at, ch.returned_at, ch.due_at, ch.is_disposable
            FROM checkout ch
            JOIN item i ON ch.item_id = i.id
            JOIN person p ON ch.person_id = p.id
            JOIN person ib ON ch.issued_by_id = ib.id
            ORDER BY ch.checked_out_at DESC
        """)
        return cur.fetchall()

def search_items(query):
    q = WarehouseApp._normalizer(query)
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT i.id, i.sku, i.name, c.name, l.name, i.quantity, i.notes
            FROM item i
            JOIN category c ON i.category_id = c.id
            JOIN location l ON i.location_id = l.id
            ORDER BY i.name
        """)
        rows = cur.fetchall()
        if not q:
            return rows
        result = []
        for r in rows:
            sku_cf = WarehouseApp._normalizer(r[1])
            name_cf = WarehouseApp._normalizer(r[2])
            if q in sku_cf or q in name_cf:
                result.append(r)
        return result
    
def get_lookup_data(table):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT id, name FROM {table} ORDER BY name")
        return cur.fetchall()

def add_item(sku, name, cat_id, loc_id, qty, notes):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO item (sku, name, category_id, location_id, quantity, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sku, name, cat_id, loc_id, qty, notes))

def update_item(item_id, sku, name, cat_id, loc_id, qty, notes):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE item
            SET sku = ?, name = ?, category_id = ?, location_id = ?, quantity = ?, notes = ?
            WHERE id = ?
        """, (sku, name, cat_id, loc_id, qty, notes, item_id))

def delete_item(item_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM item WHERE id = ?", (item_id,))

def issue_item(item_id, person_id, issued_by_id, qty, due_at, is_disposable):
    with get_db_connection() as conn:
        cur = conn.cursor()
        if not is_disposable:
            cur.execute("SELECT quantity FROM item WHERE id = ?", (item_id,))
            current = cur.fetchone()[0]
            if qty > current:
                raise ValueError("Недостаточно товара на складе!")
        cur.execute("""
            INSERT INTO checkout (item_id, person_id, issued_by_id, quantity, checked_out_at, due_at, is_disposable)
            VALUES (?, ?, ?, ?, datetime('now'), ?, ?)
        """, (item_id, person_id, issued_by_id, qty, due_at, is_disposable))
        if not is_disposable:
            cur.execute("UPDATE item SET quantity = quantity - ? WHERE id = ?", (qty, item_id))

def return_item(checkout_id, item_id, qty):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE checkout SET returned_at = datetime('now') WHERE id = ?", (checkout_id,))
        cur.execute("UPDATE item SET quantity = quantity + ? WHERE id = ?", (qty, item_id))

def add_lookup_record(table, name):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"INSERT INTO {table} (name) VALUES (?)", (name,))

def update_lookup_record(table, record_id, name):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE {table} SET name = ? WHERE id = ?", (name, record_id))

def delete_lookup_record(table, record_id):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))

def export_to_csv(data, headers, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

# === ОСНОВНОЕ ОКНО ===
class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт материальных ценностей — Кафедра")
        self.root.geometry("1100x750")
        self.search_after = None

        # Меню
        menubar = tk.Menu(root)
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Резервная копия БД", command=self.backup_db)
        tools_menu.add_command(label="Экспорт товаров в CSV", command=self.export_items)
        tools_menu.add_command(label="Экспорт истории в CSV", command=self.export_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Справочники", command=self.manage_reference)
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        root.config(menu=menubar)

        # Поиск
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.on_search_change())
        tk.Entry(top_frame, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=5)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Товары", command=self.show_items).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="История выдач", command=self.show_history).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Добавить товар", command=self.add_item).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Выдать товар", command=self.issue_item_ui).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Вернуть товар", command=self.return_item_ui).pack(side=tk.LEFT, padx=5)

        # Таблица
        self.tree = ttk.Treeview(root, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)

        self.current_view = "items"
        self.show_items()

    def on_double_click(self, event):
        if self.current_view == "items":
            self.edit_item()
        elif self.current_view == "history":
            pass  # можно добавить детали

    # Игнор пробелов и тире
    def _normalizer(s):
        s = "".join(str(s or "").split()).casefold()
        return re.sub(r"[-_/().]", "", s)

    def show_items(self):
        self.current_view = "items"
        columns = ("ID", "SKU", "Наименование", "Категория", "Локация", "Остаток", "Примечания")
        self.tree.config(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.load_items()

    # Задержка результатов поиска при вводе
    def on_search_change(self, *args):
        if self.search_after:
            self.root.after_cancel(self.search_after)
        self.search_after = self.root.after(300, self.load_items)

    def show_history(self):
        self.current_view = "history"
        columns = ("ID", "Товар", "Кому", "Выдал", "Кол-во", "Выдано", "Возвращено", "Срок", "Расходник")
        self.tree.config(columns=columns)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in get_checkout_history():
            returned = "Да" if row[6] else "Нет"
            disp = "Да" if row[8] else "Нет"
            self.tree.insert("", "end", values=row[:6] + (returned, row[7], disp))

    def load_items(self):
        if self.current_view != "items": return
        query = self.search_var.get()
        items = search_items(query) if query else get_all_items()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in items:
            self.tree.insert("", "end", values=row)

    def add_item(self):
        self.open_item_form()

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        item_id = self.tree.item(selected[0])["values"][0]
        self.open_item_form(item_id)

    def open_item_form(self, item_id=None):
        win = Toplevel(self.root)
        win.title("Товар" if item_id else "Добавить товар")
        win.geometry("450x350")

        # Поля
        tk.Label(win, text="SKU:").pack()
        sku_entry = tk.Entry(win); sku_entry.pack()

        tk.Label(win, text="Наименование:").pack()
        name_entry = tk.Entry(win); name_entry.pack()

        # Справочники
        cat_data = get_lookup_data("category")
        loc_data = get_lookup_data("location")

        tk.Label(win, text="Категория:").pack()
        cat_var = tk.StringVar()
        cat_menu = ttk.Combobox(win, textvariable=cat_var, values=[c[1] for c in cat_data])
        cat_menu.pack()

        tk.Label(win, text="Локация:").pack()
        loc_var = tk.StringVar()
        loc_menu = ttk.Combobox(win, textvariable=loc_var, values=[l[1] for l in loc_data])
        loc_menu.pack()

        tk.Label(win, text="Количество:").pack()
        qty_entry = tk.Entry(win); qty_entry.pack()

        tk.Label(win, text="Примечания:").pack()
        notes_entry = tk.Entry(win); notes_entry.pack()

        # Заполнение при редактировании
        if item_id:
            item = get_item_by_id(item_id)
            sku_entry.insert(0, item[1])
            name_entry.insert(0, item[2])
            cat_var.set(next(c[1] for c in cat_data if c[0] == item[3]))
            loc_var.set(next(l[1] for l in loc_data if l[0] == item[4]))
            qty_entry.insert(0, item[5])
            notes_entry.insert(0, item[6])

        def save():
            try:
                cat_id = next(c[0] for c in cat_data if c[1] == cat_var.get())
                loc_id = next(l[0] for l in loc_data if l[1] == loc_var.get())
                qty = int(qty_entry.get() or 0)
                if item_id:
                    update_item(item_id, sku_entry.get(), name_entry.get(), cat_id, loc_id, qty, notes_entry.get())
                    messagebox.showinfo("Успех", "Товар обновлён!")
                else:
                    add_item(sku_entry.get(), name_entry.get(), cat_id, loc_id, qty, notes_entry.get())
                    messagebox.showinfo("Успех", "Товар добавлен!")
                win.destroy()
                self.load_items()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Сохранить", command=save).pack(pady=10)

        if item_id:
            tk.Button(win, text="Удалить", fg="red", command=lambda: self.confirm_delete_item(item_id, win)).pack()

    def confirm_delete_item(self, item_id, win):
        if messagebox.askyesno("Подтверждение", "Удалить товар?"):
            delete_item(item_id)
            win.destroy()
            self.load_items()

    def issue_item_ui(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар")
            return
        values = self.tree.item(selected[0])["values"]
        item_id = values[0]

        win = Toplevel(self.root)
        win.title(f"Выдать: {values[2]}")
        win.geometry("350x280")

        tk.Label(win, text=f"Товар: {values[2]} (остаток: {values[5]})").pack()

        persons = get_lookup_data("person")
        if not persons:
            messagebox.showerror("Ошибка", "Нет сотрудников!")
            win.destroy()
            return

        tk.Label(win, text="Получатель:").pack()
        person_var = tk.StringVar(value=persons[0][1])
        person_menu = ttk.Combobox(win, textvariable=person_var, values=[p[1] for p in persons])
        person_menu.pack()

        tk.Label(win, text="Выдал:").pack()
        issuer_var = tk.StringVar(value=persons[0][1])
        issuer_menu = ttk.Combobox(win, textvariable=issuer_var, values=[p[1] for p in persons])
        issuer_menu.pack()

        tk.Label(win, text="Количество:").pack()
        qty_entry = tk.Entry(win); qty_entry.pack()

        tk.Label(win, text="Срок возврата (ГГГГ-ММ-ДД):").pack()
        due_entry = tk.Entry(win); due_entry.pack()

        disposable_var = tk.BooleanVar()
        tk.Checkbutton(win, text="Расходный материал", variable=disposable_var).pack()

        def confirm():
            try:
                qty = int(qty_entry.get())
                if qty <= 0: raise ValueError("Количество > 0")
                person_id = next(p[0] for p in persons if p[1] == person_var.get())
                issuer_id = next(p[0] for p in persons if p[1] == issuer_var.get())
                due = due_entry.get() or None
                issue_item(item_id, person_id, issuer_id, qty, due, disposable_var.get())
                win.destroy()
                self.load_items()
                messagebox.showinfo("Успех", "Товар выдан!")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

        tk.Button(win, text="Выдать", command=confirm).pack(pady=10)

    def return_item_ui(self):
        # Открываем историю и выбираем неповернутую запись
        history = get_checkout_history()
        not_returned = [h for h in history if not h[6]]  # returned_at is None

        if not not_returned:
            messagebox.showinfo("Инфо", "Нет выданных товаров для возврата")
            return

        win = Toplevel(self.root)
        win.title("Возврат товара")
        win.geometry("600x400")

        search_frame = tk.Frame(win)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(search_frame, text="Поиск (Серийный номер/Название товара):").pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_var.trace_add("write", lambda *args: self.on_search_change())
        tk.Entry(search_frame, textvariable=search_var, width=30).pack(side=tk.LEFT, padx=5)

        cols = ("ID", "Товар", "Кому", "Кол-во", "Выдано")
        tree = ttk.Treeview(win, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=100)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for row in not_returned:
            tree.insert("", "end", values=(row[0], row[1], row[2], row[4], row[5]))

        def confirm_return():
            sel = tree.selection()
            if not sel: return
            checkout_id = tree.item(sel[0])["values"][0]
            item_name = tree.item(sel[0])["values"][1]
            qty = tree.item(sel[0])["values"][3]
            item_id = None
            # Найдём item_id по имени (лучше хранить в данных, но для простоты)
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT id FROM item WHERE name = ?", (item_name,))
                item_id = cur.fetchone()[0]

            if messagebox.askyesno("Возврат", f"Вернуть {qty} шт. '{item_name}'?"):
                return_item(checkout_id, item_id, qty)
                win.destroy()
                self.load_items()
                messagebox.showinfo("Успех", "Товар возвращён!")

        tk.Button(win, text="Вернуть", command=confirm_return).pack(pady=10)

    def manage_reference(self):
        win = Toplevel(self.root)
        win.title("Справочники")
        win.geometry("600x500")

        notebook = ttk.Notebook(win)
        notebook.pack(fill=tk.BOTH, expand=True)

        for table, title in [("person", "Сотрудники"), ("category", "Категории"), ("location", "Локации")]:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=title)

            tree = ttk.Treeview(frame, columns=("ID", "Название"), show="headings")
            tree.heading("ID", text="ID")
            tree.heading("Название", text="Название")
            tree.column("ID", width=50)
            tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            def make_load(table_name, tree_widget):
                def load():
                    for i in tree_widget.get_children():
                        tree_widget.delete(i)
                    for row in get_lookup_data(table_name):
                        tree_widget.insert("", "end", values=row)
                return load

            load_func = make_load(table, tree)
            load_func()

            btns = ttk.Frame(frame)
            btns.pack(pady=5)

            def make_add(table_name, tree_widget, load_func):
                def add():
                    name = simpledialog.askstring("Добавить", f"Название {table_name}:")
                    if name:
                        add_lookup_record(table_name, name)
                        load_func()
                return add

            def make_edit(table_name, tree_widget, load_func):
                def edit():
                    sel = tree_widget.selection()
                    if not sel: return
                    item_id = tree_widget.item(sel[0])["values"][0]
                    old_name = tree_widget.item(sel[0])["values"][1]
                    new_name = simpledialog.askstring("Редактировать", "Новое название:", initialvalue=old_name)
                    if new_name:
                        update_lookup_record(table_name, item_id, new_name)
                        load_func()
                return edit

            def make_delete(table_name, tree_widget, load_func):
                def delete():
                    sel = tree_widget.selection()
                    if not sel: return
                    item_id = tree_widget.item(sel[0])["values"][0]
                    if messagebox.askyesno("Удалить", "Удалить запись?"):
                        delete_lookup_record(table_name, item_id)
                        load_func()
                return delete

            ttk.Button(btns, text="Добавить", command=make_add(table, tree, load_func)).pack(side=tk.LEFT, padx=5)
            ttk.Button(btns, text="Редактировать", command=make_edit(table, tree, load_func)).pack(side=tk.LEFT, padx=5)
            ttk.Button(btns, text="Удалить", command=make_delete(table, tree, load_func)).pack(side=tk.LEFT, padx=5)

    def backup_db(self):
        try:
            path = backup_db()
            messagebox.showinfo("Успех", f"Резервная копия создана:\n{path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def export_items(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            try:
                data = get_all_items()
                headers = ["ID", "SKU", "Наименование", "Категория", "Локация", "Остаток", "Примечания"]
                export_to_csv(data, headers, path)
                messagebox.showinfo("Успех", "Экспорт завершён")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def export_history(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path:
            try:
                data = get_checkout_history()
                headers = ["ID", "Товар", "Кому", "Выдал", "Кол-во", "Выдано", "Возвращено", "Срок", "Расходник"]
                # Преобразуем даты и булевы значения для CSV
                clean_data = []
                for row in data:
                    clean_row = list(row)
                    clean_row[6] = "Да" if clean_row[6] else "Нет"
                    clean_row[8] = "Да" if clean_row[8] else "Нет"
                    clean_data.append(clean_row)
                export_to_csv(clean_data, headers, path)
                messagebox.showinfo("Успех", "Экспорт завершён")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

# === ЗАПУСК ===
if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()