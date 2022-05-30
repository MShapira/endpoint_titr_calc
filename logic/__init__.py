import openpyxl
from PySide6.QtWidgets import QFileDialog
from numpy import float64

from immuno_calculator import AnalyticalGroup, build_common_plot, cutoff_multiplier_accuracies, write_data_to_csv, \
    letters, load_plate_data
from logic.plate import Plate


class Logic:
    def __init__(self):
        self.ui = None
        self.plates = list()
        self.groups = list()
        self.cutoff_multiplier_accuracy = cutoff_multiplier_accuracies[0]

    # deprecated - use load_plates() instead
    def load_plate(self, file_path: str):
        plate_data = load_plate_data(file_path)
        # for sample_index in range(1, 13):
        #     sample_ydata = list()
        #     for entry_index in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        #         sample_ydata.append(data[sample_index][entry_index])
        #
        #     self.samples.append(sample)
        rows = list()
        for entry_index in letters:
            current_row = list()
            for sample_index in range(1, 13):
                current_row.append(plate_data[sample_index][entry_index])
            rows.append(current_row)
        # for row_index in range(len(plate_data)):
        #     current_row = []
        #     for column_index in range(len(plate_data.columns)):
        #         if plate_data.values[row_index][column_index] is None:
        #             break
        #         else:
        #             current_row.append(plate_data.values[row_index][column_index])
        #     rows.append(current_row)
        plate = Plate(file_path, 'Plate', rows, [f'Sample {i}' for i in range(len(rows[0]))])
        self.plates.append(plate)

        self.ui.add_plate(plate)

    def load_plates(self, file_path: str):
        def row_is_empty(row) -> bool:
            # 0 cells or all cells are empty
            if len(row) == 0:
                return True
            for cell in row:
                if cell.value is not None:
                    return False
            return True
        def row_contains_plate_name(row) -> bool:
            # 2 or more cells, cell #1 contains text, all the rest are empty
            if len(row) < 2:
                return False
            if row[1].value is None:
                return False
            other_values = [row[i].value for i in range(len(row)) if i != 1]
            for other_value in other_values:
                if other_value is not None:
                    return False
            return True
        def get_plate_name(row) -> str:
            return row[1].value
        def row_contains_data(row) -> bool:
            # cell #0 contains a letter
            if len(row) == 0:
                return False
            return row[0].value in letters
        def get_row_data(row) -> list:
            # collect values starting from cell #1 until first empty cell
            values = list()
            for i in range(1, len(row)):
                if row[i].value is not None:
                    values.append(float64(row[i].value))
                else:
                    break
            return values
        def row_contains_sample_names(row) -> bool:
            # cell #0 is empty, all the rest are not (at least two)
            if row[0].value is not None:
                return False
            other_values = [row[i].value for i in range(1, len(row))]
            non_empty_value_count = 0
            for value in other_values:
                if value is not None:
                    non_empty_value_count += 1
            return non_empty_value_count >= 2
        def get_sample_names(row) -> list:
            # collect values starting from cell #1 until first empty cell
            names = list()
            for i in range(1, len(row)):
                if row[i].value is not None:
                    names.append(row[i].value)
                else:
                    break
            return names

        wb_obj = openpyxl.load_workbook(file_path)
        sheet = wb_obj.active

        new_plates = list()
        current_plate_name = None
        current_plate_rows = None
        current_plate_sample_names = None

        for row in sheet.iter_rows():
            if row_is_empty(row):
                continue
            if row_contains_plate_name(row):
                if current_plate_name is None:
                    current_plate_name = get_plate_name(row)
                continue
            if row_contains_data(row):
                if current_plate_rows is None:
                    current_plate_rows = list()
                current_plate_rows.append(get_row_data(row))
                continue
            if row_contains_sample_names(row) and current_plate_rows is not None:
                current_plate_sample_names = get_sample_names(row)

                new_plate = Plate(file_path, current_plate_name, current_plate_rows, current_plate_sample_names)
                new_plates.append(new_plate)
                current_plate_name = None
                current_plate_rows = None
                current_plate_sample_names = None

        for plate in new_plates:
            self.plates.append(plate)
            self.ui.add_plate(plate)

    def create_group(self, name: str, samples: list):
        group = AnalyticalGroup(name, samples)
        self.groups.append(group)

        # inform samples about group they now belong to
        for sample in samples:
            sample.group = group

        self.ui.on_group_added(group)

    def build_sigmoid(self):
        assert len(self.groups) != 0, "attempt to build sigmoid while not having any sample groups"

        for group in self.groups:
            for sample in group.samples:
                sample.get_popt_pcov()
                sample.get_R2()
            group.detect_outliers()
            group.plot_samples_data()

    def calculate_endpoint_titer(self):
        for group in self.groups:
            group.get_group_cutoff(self.cutoff_multiplier_accuracy)
            group.calculate_average_titer()

        build_common_plot(self.groups)

        # enable 'Save results' button
        self.ui.top_panel.right.save_results.setEnabled(True)

    def set_cutoff_multiplier_accuracy(self, accuracy: float):
        self.cutoff_multiplier_accuracy = accuracy

    def save_results(self):
        folder_name = QFileDialog.getExistingDirectory(self.ui, caption='Select folder for results')
        if folder_name != '':
            write_data_to_csv(self.groups, folder_name, self.cutoff_multiplier_accuracy)
