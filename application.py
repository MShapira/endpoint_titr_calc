import sys
from PySide6.QtWidgets import QApplication

from logic import Logic
from ui.main_window import MainWindow


class Application:
    def __init__(self):
        self.application = QApplication(sys.argv)
        self.logic = Logic()
        self.window = MainWindow(self.logic)

    def run(self):
        self.window.show()
        self.application.exec()
