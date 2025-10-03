import sys
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication(sys.argv)
label = QLabel("Привет из WSL!")
label.show()
label.raise_()
label.activateWindow()
app.exec_()