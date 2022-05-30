from PySide6.QtWidgets import QWidget, QHBoxLayout, QInputDialog, QLineEdit

from logic import Logic
from logic.plate import Plate as PlateData
from ui.plate.dilutions import Dilutions
from ui.plate.multipliers import Multipliers
from ui.plate.sample_column import SampleColumn


class Plate(QWidget):
    def __init__(self, parent, logic: Logic, data: PlateData = None):
        super().__init__(parent)

        self.logic = logic
        self.data = data
        self.name = '' if data is None else data.name

        self.layout = QHBoxLayout()

        # add multipliers column
        self.multipliers = Multipliers(self, self.data)
        self.layout.addWidget(self.multipliers)

        # add dilutions column
        self.dilutions = Dilutions(self, self.data)
        self.dilutions.setMinimumWidth(100)
        self.layout.addWidget(self.dilutions)

        # add sample columns
        self.samples = list()
        if self.data is None:
            # plate does not have valid data, show dummy values
            for i in range(12):
                sample = SampleColumn(self, dummy_name=f'Sample {i+1}')
                self.samples.append(sample)
                self.layout.addWidget(self.samples[-1])
        else:
            # plate has valid data, show valid values then
            for sample_data in self.data.samples:
                sample = SampleColumn(self, data=sample_data)
                self.samples.append(sample)
                self.layout.addWidget(self.samples[-1])

        self.setLayout(self.layout)

        if self.data is None:
            self.setEnabled(False)

    def update_dilutions(self, skip_index: int | None = None):
        self.dilutions.update_values(skip_index)
