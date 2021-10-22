
import pandas as pd
import os

class DataSet(object):
    def __init__(self, data_path, delimiter, territory) -> None:
        self.data_path = data_path
        self.delimiter = delimiter
        self.full_data = self.load_and_concatenate_data()
        self.territory = territory
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
    
    def convert_to_int(self, source_column_name, result_column_name):
        self.data[result_column_name] = self.data[source_column_name].astype(int)

    def convert_to_str(self, source_column_name, result_column_name):
        self.data[result_column_name] = self.data[source_column_name].astype(str)

    def convert_to_date(self, source_column_name, result_column_name):
        self.data[result_column_name] = self.data[source_column_name].astype("datetime64")

    def calculate_percentage(self, source_column_names, result_column_name):
        numerator = source_column_names[0]
        denominator = source_column_names[1]
        self.data[result_column_name] = (
            self.data[numerator] / self.data[denominator] * 100
        ).astype(float)

    def calculate_7_day_rolling_average(self, source_column_name, result_column_name):
        self.data[result_column_name] = (
                self.data[source_column_name].rolling(window=7).mean()
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
    
    def generate_additional_metrics(self, columns_config):
        self.data.dropna(axis=0, how='any', inplace=True)

        for operation in columns_config['operation_order']:
            for column in columns_config[operation]:
                operation_function = self.get_operation_function(operation)
                if(not operation_function):
                    raise ValueError(f"Unable to match operation processor method \
                        for operation: {operation}")
                result_column_name = column[0]
                source_column_names = column[1]
                data = operation_function(source_column_names, result_column_name)

        self.data.set_index(columns_config["index"], inplace=True)
        return data