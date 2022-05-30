from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit

from logic.plate import Plate as PlateData


class Dilutions(QWidget):
    def __init__(self, parent, data: PlateData):
        super().__init__(parent)

        self.data = data

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add fake group name to fit the same layout with samples
        self.layout.addWidget(QLabel(self, text=''))

        # add header
        self.header = QLabel(self, text='Dilutions')
        self.layout.addWidget(self.header)

        # add 8 dilution values
        self.dilutions = list()
        if self.data is None:
            # no valid data, add dummy values
            for i in range(8):
                dilution = QLineEdit(self, text='')
                self.dilutions.append(dilution)
                self.layout.addWidget(self.dilutions[-1])
        else:
            # there is valid data, show actual values

            for index in range(len(self.data.dilutions)):
                dilution_data = self.data.dilutions[index]
                dilution = QLineEdit(self, text=f'{dilution_data:.2f}')
                dilution.textEdited.connect(partial(self.dilution_changed, index))
                self.dilutions.append(dilution)
                self.layout.addWidget(self.dilutions[-1])

        self.setLayout(self.layout)

    def update_values(self, skip_index: int | None):
        for i in range(len(self.data.dilutions)):
            if i != skip_index:
                self.dilutions[i].setText(f'{self.data.dilutions[i]:.2f}')

    def dilution_changed(self, index: int, text: str):
        # if new text is a valid value, update the plate data
        try:
            value = float(text)

            # if the base dilution changed (index=0), the whole set of dilutions should be recalculated
            if index == 0:
                self.data.recalculate_dilutions(base_dilution=value)
            else:
                # some specific dilution was changed, update only that value
                self.data.dilutions[index] = value
            self.parent().update_dilutions(skip_index=index)
        except:
            # simply ignore invalid input
            pass
