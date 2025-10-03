import sys
import os
import sqlite3
from PyQt5 import QtWidgets, QtCore

class WarehouseApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Складской учет")
        self.setGeometry(300, 200, 800, 500)

        # Подключение к БД
        self.conn = sqlite3.connect("warehouse.db")
        self.cursor = self.conn.cursor()

        # Центральный виджет — вкладки
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        # Вкладки
        self.items_tab = self.create_tab("item", ["ID", "SKU", "Название", "Категория", "Локация", "Кол-во", "Заметки"])
        self.persons_tab = self.create_tab("person", ["ID", "Имя"])
        self.checkout_tab = self.create_tab("checkout", ["ID", "Товар", "Кто получил", "Кол-во", "Дата выдачи", "Срок", "Возврат", "Одноразовый", "Выдал"])

        self.tabs.addTab(self.items_tab, "Товары")
        self.tabs.addTab(self.persons_tab, "Пользователи")
        self.tabs.addTab(self.checkout_tab, "Выдачи")

    def create_tab(self, table_name, headers):
        """Создание вкладки с таблицей и кнопкой обновления"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        table = QtWidgets.QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        refresh_btn = QtWidgets.QPushButton("Обновить")
        refresh_btn.clicked.connect(lambda: self.load_data(table_name, table))

        layout.addWidget(table)
        layout.addWidget(refresh_btn)
        widget.setLayout(layout)

        # Загружаем данные при старте
        self.load_data(table_name, table)

        return widget

    def load_data(self, table_name, table):
        """Загрузка данных из БД в таблицу"""
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            rows = self.cursor.fetchall()
        except sqlite3.OperationalError:
            # Если таблицы нет — создаем пустую
            rows = []

        table.setRowCount(len(rows))
        if rows:
            table.setColumnCount(len(rows[0]))

        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WarehouseApp()
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec_())
