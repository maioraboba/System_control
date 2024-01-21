import sqlite3 as sql
import sys

from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


class WriteSql(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface_for_write_sql.ui', self)
        self.con = sql.connect("data.db")
        cur = self.con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS photos(id INTEGER, name VARCHAR, photo BLOB)')
        self.take_photo.clicked.connect(self.take_photo_from_folder)
        self.add_student.clicked.connect(self.add_student_to_table)
        self.table_of_students.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)  # !!!
        self.fname = ""
        self.student_name = ""
        self.titles = ['ID', 'ФИО']
        self.update_table()

    def take_photo_from_folder(self):
        self.fname = QFileDialog.getOpenFileName(self, 'Выберите фото ученика', '',
                                                 'Картинка (*.jpg);;Картинка (*.png)')[0]
        self.label.setText("Выбрано")

    def add_student_to_table(self):
        cur = self.con.cursor()
        try:
            item_id = cur.execute("SELECT COALESCE(max(id), 0) FROM photos").fetchone()[0] + 1
            self.student_name = self.name_student.text()
            if self.fname and self.student_name:
                # запись в базу данных, если получено фото
                with open(self.fname, "rb") as photo:
                    h = photo.read()
                    print(3)
                    cur.execute("INSERT INTO photos VALUES(?, ?, ?)", [item_id, self.student_name, h])
        except ValueError:
            self.statusBar().showMessage("Неверно заполнена форма")
        else:
            self.con.commit()
            self.update_table()

    def update_table(self):
        cur = self.con.cursor()
        req = f"SELECT photos.id, photos.name FROM photos"
        result = cur.execute(req).fetchall()
        self.table_of_students.setRowCount(len(result))
        if result:
            self.table_of_students.setColumnCount(len(result[0]))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.table_of_students.setItem(i, j, QTableWidgetItem(str(val)))
        self.table_of_students.setHorizontalHeaderLabels(self.titles)
        self.label.setText("Не выбрано")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = WriteSql()
    ex.show()
    sys.exit(app.exec())
