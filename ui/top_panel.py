from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox

from immuno_calculator import cutoff_multiplier_accuracies
from logic import Logic


class TopPanel(QWidget):
    """
    Top panel consists of two halves:
    - left half contains 'Load plate' button and is left-aligned
    - right half contains 'Build sigmoid' and 'Endpoint titer' buttons and is right-aligned
    """

    def __init__(self, parent, logic: Logic):
        super().__init__(parent)

        self.logic = logic

        self.layout = QHBoxLayout()

        self.left = LeftHalf(self)
        self.layout.addWidget(self.left)

        self.right = RightHalf(self)
        self.layout.addWidget(self.right)

        self.setLayout(self.layout)

    @Slot()
    def load_plate_released(self):
        file_path, _ = QFileDialog.getOpenFileName(self, caption='Load plate data from file',
                                                   filter='Excel sheets (*.xlsx)')
        if file_path != '':
            self.logic.load_plates(file_path)


class LeftHalf(QWidget):
    def __init__(self, parent: TopPanel):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add 'Load plate' button
        self.load_plate = QPushButton(self, text='Load plate(s)')
        self.load_plate.setFixedWidth(100)
        self.load_plate.released.connect(parent.load_plate_released)
        self.layout.addWidget(self.load_plate)

        self.setLayout(self.layout)


class RightHalf(QWidget):
    def __init__(self, parent: TopPanel):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignRight)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add title
        self.title = QLabel(self, text='Calculation precision')
        self.layout.addWidget(self.title)

        # add a combo box for the calculation precision
        self.precision = QComboBox(self)
        for accuracy in cutoff_multiplier_accuracies:
            self.precision.addItem(f'{accuracy}')
        self.precision.currentIndexChanged.connect(self.precision_changed)
        self.layout.addWidget(self.precision)

        # add 'Build sigmoid' button
        self.build_sigmoid = QPushButton(self, text='Build sigmoid')
        self.build_sigmoid.setFixedWidth(100)
        self.build_sigmoid.setEnabled(False)
        self.build_sigmoid.released.connect(parent.logic.build_sigmoid)
        self.layout.addWidget(self.build_sigmoid)

        # add 'Endpoint titer' button
        self.endpoint_titer = QPushButton(self, text='Endpoint titer')
        self.endpoint_titer.setFixedWidth(100)
        self.endpoint_titer.setEnabled(False)
        self.endpoint_titer.released.connect(parent.logic.calculate_endpoint_titer)
        self.layout.addWidget(self.endpoint_titer)

        # add 'Save results' button
        self.save_results = QPushButton(self, text='Save results')
        self.save_results.setFixedWidth(100)
        self.save_results.setEnabled(False)
        self.save_results.released.connect(parent.logic.save_results)
        self.layout.addWidget(self.save_results)

        self.setLayout(self.layout)

    @Slot()
    def precision_changed(self, index: int):
        self.parent().logic.set_cutoff_multiplier_accuracy(cutoff_multiplier_accuracies[index])
