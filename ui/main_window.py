from PySide6.QtWidgets import QMainWindow

from logic import Logic
from ui import Ui


class MainWindow(QMainWindow):
    def __init__(self, logic: Logic):
        super().__init__()

        self.logic = logic
        self.ui = Ui(self, self.logic)

        self.logic.ui = self.ui

        self.setWindowTitle('Endpoint titer')
        self.setCentralWidget(self.ui)
