import random

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QInputDialog, QLineEdit

from logic import Logic
from logic.plate import Plate as PlateData
from ui.plate import Plate
from ui.top_panel import TopPanel
from immuno_calculator import AnalyticalGroup as GroupData

class Ui(QWidget):
    def __init__(self, parent, logic: Logic):
        super().__init__(parent)

        self.logic = logic

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add top panel
        self.top_panel = TopPanel(self, logic)
        self.layout.addWidget(self.top_panel)

        # add plate tabs
        self.plate_tabs = QTabWidget(self)
        self.plates = list()
        self.layout.addWidget(self.plate_tabs)

        self.setLayout(self.layout)

        # add a fake plate for a start
        self.add_plate(None)
        self.next_group_index = 1

        self.group_stylesheets = dict()

    def add_plate(self, plate_data: PlateData):
        # remove fake plate if any
        if len(self.plates) == 1 and self.plates[0].data is None:
            self.plate_tabs.removeTab(0)
            self.plates.clear()

        plate = Plate(self, self.logic, plate_data)
        self.plates.append(plate)
        self.plate_tabs.addTab(plate, plate.name)

    def group_samples(self):
        dialog = QInputDialog(self)
        group_name, is_set = dialog.getText(self, 'Create sample group', 'Group name: ',
                                            echo=QLineEdit.EchoMode.Normal, text=f'Group {self.next_group_index}')
        if is_set:
            selected_samples = list()

            # collect currently selected samples across all plates
            for plate in self.plates:
                for sample in plate.samples:
                    if sample.selected:
                        # set group for sample
                        sample.update_group_name(group_name)

                        selected_samples.append(sample.data)

                        # deselect
                        sample.selected = False
                        sample.update_selected_style()

            # inform logic to group samples
            self.logic.create_group(group_name, selected_samples)

            # update next group index
            self.next_group_index += 1

    def remove_from_corresponding_groups(self):
        # go across all selected samples across all plates and remove them from corresponding groups
        for plate in self.plates:
            for sample in plate.samples:
                if sample.selected:
                    sample.remove_from_group()

                    # deselect
                    sample.selected = False
                    sample.update_selected_style()

    def on_group_added(self, group: GroupData):
        # create a new random stylesheet and populate it across samples
        self.group_stylesheets[group] = f'background-color:hsv({random.randint(0, 255)}, 20%, 100%);'
        for plate in self.plates:
            for sample in plate.samples:
                if sample.data.group == group:
                    sample.group_stylesheet = self.group_stylesheets[group]
                    sample.setStyleSheet(sample.group_stylesheet)

        # allow building sigmoid
        self.top_panel.right.build_sigmoid.setEnabled(True)

    def update_negative_controls(self):
        for plate in self.plates:
            for sample in plate.samples:
                sample.update_negative_controls()

        # allow endpoint titer
        self.top_panel.right.endpoint_titer.setEnabled(True)
