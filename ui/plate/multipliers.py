from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox

from immuno_calculator import cutoff_multiplier_accuracies
from logic.plate import Plate as PlateData


class Multipliers(QWidget):
    def __init__(self, parent, data: PlateData):
        super().__init__(parent)

        self.data = data

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add fake group name to fit the same layout with samples
        self.layout.addWidget(QLabel(self, text=''))

        # add dilution coefficient
        self.dilution_coefficient = DilutionCoefficient(self, data)
        self.layout.addWidget(self.dilution_coefficient)

        # add cutoff multiplier
        self.cutoff_multiplier = CutoffMultiplier(self, data)
        self.layout.addWidget(self.cutoff_multiplier)

        self.setLayout(self.layout)


class DilutionCoefficient(QWidget):
    def __init__(self, parent, data: PlateData):
        super().__init__(parent)

        self.data = data

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add header
        self.header = QLabel(self, text='Dilution\ncoefficient')
        self.layout.addWidget(self.header)

        # add a text box for the coefficient
        coefficient_text = '' if data is None else f'{data.dilution_coefficient}'
        self.coefficient = QLineEdit(self, text=coefficient_text)
        self.coefficient.textEdited.connect(self.dilution_coefficient_changed)
        self.layout.addWidget(self.coefficient)

        self.setLayout(self.layout)

    @Slot(str)
    def dilution_coefficient_changed(self, text: str):
        # if new text is a valid value, update the plate data
        try:
            coefficient = float(text)
            self.data.recalculate_dilutions(coefficient=coefficient)
            self.parent().parent().update_dilutions()
        except:
            # simply ignore invalid input
            pass


class CutoffMultiplier(QWidget):
    def __init__(self, parent, data: PlateData):
        super().__init__(parent)

        self.data = data

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.setLayout(self.layout)
