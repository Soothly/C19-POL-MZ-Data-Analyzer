
import pandas as pd
import matplotlib.pyplot as plt
import os
import json


class DataSet(object):
    def __init__(self, data_path, delimiter, territory, config_file_path) -> None:
        self.data_path = data_path
        self.delimiter = delimiter
        self.territory = territory
        self.config = DataSetConfig(self.territory.id, config_file_path)
        self.operations = DataSetOperations()
        self.full_data = self.load_and_concatenate_data()
        self.data = self.get_single_area_data()

    def load_and_concatenate_data(self):
        files = os.listdir(self.data_path)
        full_data = []
        for file in files:
            if("csv" not in file):
                continue
            filepath = self.data_path + "/" + file
            try:
                data_from_file = pd.read_csv(
                    filepath, delimiter=self.delimiter, encoding='utf-8'
                )
            except UnicodeDecodeError:
                data_from_file = pd.read_csv(
                    filepath, delimiter=self.delimiter, encoding='cp1250'
                )
            full_data.append(data_from_file)
        
        concatenated_data = pd.concat(full_data)
        return concatenated_data
    
    def get_single_area_data(self):
        territory_id = self.territory.code
        placeholder = self.full_data.loc[self.full_data['teryt'] == territory_id]
        single_area_data = placeholder.copy()
        return single_area_data
    
    def generate_additional_metrics(self):
        self.data.dropna(axis=0, how='any', inplace=True)

        for operation in self.config.operation_order:
            for operation_config in getattr(self.config, operation):
                operation_function = self.operations.get_operation_function(operation)
                if(not operation_function):
                    raise ValueError(f"Unable to match operation processor method \
                        for operation: {operation}")
                result_column_name = operation_config["result_column"]
                source_column_names = operation_config["source_column"]
                operation_function(self.data, source_column_names, result_column_name)

        self.data.set_index(self.config.index_column, inplace=True)
    
    def plot(self):
        for plot in self.config.plots:
            plot.draw(self.data)

class DataSetConfig(object):
    def __init__(self, dataset_name, config_file_path) -> None:
        self.dataset_name = dataset_name
        self.from_file = self._load_config_from_file(config_file_path)
        self.plots = self._build_plot_objects()


    def _load_config_from_file(self, file_path):
        with open(file_path, "r") as json_file:
            config = json.load(json_file)

        self.plots_data = config["plots"]
        self.convert_to_int = config["convert_to_int"]
        self.convert_to_str = config["convert_to_str"]
        self.calculate_avg = config["calculate_avg"]
        self.convert_to_date = config["convert_to_date"]
        self.calculate_percentage = config["calculate_percentage"]
        self.index_column = config["index_column"]
        self.operation_order = config["operation_order"]

    def _build_plot_objects(self):
        plots = []
        for plot in self.plots_data:
            title = self.dataset_name +" - "+ plot["name"]
            columns = plot["columns"]
            plots.append(Plot(title, columns))
        return plots


class Plot(object):
    def __init__(self, name, columns) -> None:
        self.name = name
        self.columns = columns
    
    def draw(self, data):
        plt.style.use("fivethirtyeight")
        plt.figure(figsize=(16, 9))
        plt.xlabel("Daty")
        plt.ylabel("Wartości")
        title = self.name
        plt.title(title)
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        for column in self.columns:
            plt.plot(data[column])
        plt.show()

    
class DataSetOperations(object):
    def __init__(self) -> None:
        super().__init__()
    
    def convert_to_int(self, data, source_column_name, result_column_name):
        data[result_column_name] = data[source_column_name].astype(int)

    def convert_to_str(self, data, source_column_name, result_column_name):
        data[result_column_name] = data[source_column_name].astype(str)

    def convert_to_date(self, data, source_column_name, result_column_name):
        data[result_column_name] = data[source_column_name].astype("datetime64")

    def calculate_percentage(self, data, source_column_names, result_column_name):
        numerator = source_column_names[0]
        denominator = source_column_names[1]
        data[result_column_name] = (
            data[numerator] / data[denominator] * 100
        ).astype(float)

    def calculate_7_day_rolling_average(self, data, source_column_name, result_column_name):
        data[result_column_name] = (
                data[source_column_name].rolling(window=7).mean()
            )

    def get_operation_function(self, operation):
        operations = {
            "convert_to_int": self.convert_to_int,
            "convert_to_str": self.convert_to_str,
            "convert_to_date": self.convert_to_date,
            "calculate_percentage": self.calculate_percentage,
            "calculate_avg": self.calculate_7_day_rolling_average
        }
        return operations.get(operation, None)
