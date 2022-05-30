import math
from immuno_calculator import load_plate_data
from immuno_calculator import Sample as SampleData


class Plate:
    def __init__(self, file_path: str, name: str, rows: list, sample_names: list):
        self.name = f'{file_path}:{name}'
        self.samples = list()
        self.dilution_coefficient = 1.
        self.dilutions = [1.] * 8
        self.log_dilutions = [1.] * 8
        self.cutoff_multiplier = 0.99

        for sample_index in range(len(sample_names)):
            sample_ydata = list()
            for row in rows:
                sample_ydata.append(row[sample_index])

            sample = SampleData(sample_names[sample_index], xdata=self.log_dilutions, ydata=sample_ydata)
            sample.plate = self

            self.samples.append(sample)

    def recalculate_dilutions(self, coefficient: float | None = None, base_dilution: float | None = None):
        if base_dilution is not None:
            self.dilutions[0] = base_dilution
            self.log_dilutions[0] = math.log10(self.dilutions[0])
        if coefficient is not None:
            self.dilution_coefficient = coefficient
        for i in range(1, len(self.dilutions)):
            self.dilutions[i] = self.dilutions[i - 1] * self.dilution_coefficient
            self.log_dilutions[i] = math.log10(self.dilutions[i])
