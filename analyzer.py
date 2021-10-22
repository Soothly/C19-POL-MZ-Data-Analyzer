from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from lib.downloader import download_current_data, extract_data, remove_downloaded_archive
from lib.territory_codes import admin_div_types
from datetime import date, datetime
import os
import matplotlib.pyplot as plt
import pandas as pd

columns_to_plot = [
    ['przypadki_srednia_7dni'],
    ['zgony_srednia_7dni'],
    ['procent_poz_testow_7dni', 'liczba_wykonanych_testow_srednia_7dni'],
    ['liczba_osob_objetych_kwarantanna'],
    ['liczba_na_10_tys_mieszkancow_7dni']
]

columns_to_int = [
    ("liczba_przypadkow_int", "liczba_przypadkow"),
    ("zgony_int", "zgony"),
    ("liczba_osob_objetych_kwarantanna", "liczba_osob_objetych_kwarantanna")
]
columns_to_str = [
    ("stan_rekordu_na_str", "stan_rekordu_na")
]
columns_to_average = [
    ("przypadki_srednia_7dni", "liczba_przypadkow_int"),
    ('zgony_srednia_7dni', "zgony_int"),
    ('procent_poz_testow_7dni', 'procent_poz_testow'),
    ("liczba_wykonanych_testow_srednia_7dni", 'liczba_wykonanych_testow'),
    ('liczba_na_10_tys_mieszkancow_7dni', "liczba_na_10_tys_mieszkancow")
]
columns_to_date_type = [
    ("stan_rekordu_na_str", "stan_rekordu_na_str")
]

columns_to_percentage = [
    ('procent_poz_testow', ('liczba_testow_z_wynikiem_pozytywnym', 'liczba_wykonanych_testow'))
]

index_column = "stan_rekordu_na_str"

operation_order = [
    "convert_to_int", "convert_to_str", "convert_to_date",
    "calculate_percentage", "calculate_avg"
]

columns = {
    "index": index_column,
    "convert_to_int": columns_to_int,
    "convert_to_str": columns_to_str,
    "convert_to_date": columns_to_date_type,
    "calculate_avg": columns_to_average,
    "calculate_percentage": columns_to_percentage,
    "plot": columns_to_plot,
    "operation_order": operation_order
}


def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("admin_div", choices=["wojewodztwo", "powiat"], 
        default="powiat", help="Input administrative division type")
    parser.add_argument("territory",
        help="Input territory name for which you want graphs generated")
    parser.add_argument("--delimiter", default=";", 
        help="Set delimiter used in CSV files")
    parser.add_argument("--data-dir", dest="data_dir", default="./data", 
        help="Set path for the directory to download data to")
    return parser.parse_args()

def plot_columns(dataset, columns):
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(16, 9))
    plt.xlabel("Daty")
    plt.ylabel("Wartości")
    title = ",".join(columns)
    plt.title(title)
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    for column in columns:
        plt.plot(dataset[column])
    plt.show()

def load_and_concatenate_data(data_path, delimiter):
    files = os.listdir(data_path)
    for file in files:
        if("csv" not in file):
            continue
        filepath = data_path + "/" + file
        try:
            data_from_file = pd.read_csv(
                filepath, delimiter=delimiter, encoding='utf-8'
            )
        except UnicodeDecodeError:
            data_from_file = pd.read_csv(
                filepath, delimiter=delimiter, encoding='cp1250'
            )
        data.append(data_from_file)
    
    concatenated_data = pd.concat(data)
    return concatenated_data

def get_single_area_data(data, territory_code):
    territory_id = codes[territory_code]
    placeholder = data.loc[data['teryt'] == territory_id]
    single_area_data = placeholder.copy()
    return single_area_data

def convert_to_int(data, source_column_name, result_column_name):
    data[result_column_name] = data[source_column_name].astype(int)
    return data

def convert_to_str(data, source_column_name, result_column_name):
    data[result_column_name] = data[source_column_name].astype(str)
    return data

def convert_to_date(data, source_column_name, result_column_name):
    data[result_column_name] = data[source_column_name].astype("datetime64")
    return data

def calculate_percentage(data, source_column_names, result_column_name):
    numerator = source_column_names[0]
    denominator = source_column_names[1]
    data[result_column_name] = (
        data[numerator] / data[denominator] * 100
    ).astype(float)
    return data

def calculate_7_day_rolling_average(data, source_column_name, result_column_name):
    data[result_column_name] = (
            data[source_column_name].rolling(window=7).mean()
        )
    return data


def get_operation_function(operation):
    operations = {
        "convert_to_int": convert_to_int,
        "convert_to_str": convert_to_str,
        "convert_to_date": convert_to_date,
        "calculate_percentage": calculate_percentage,
        "calculate_avg": calculate_7_day_rolling_average
    }
    return operations.get(operation, None)

def generate_additional_metrics(data, columns_config):
    data.dropna(axis=0, how='any', inplace=True)

    for operation in columns_config['operation_order']:
        for column in columns_config[operation]:
            operation_function = get_operation_function(operation)
            if(not operation_function):
                raise ValueError(f"Unable to match operation processor method \
                    for operation: {operation}")
            result_column_name = column[0]
            source_column_names = column[1]
            data = operation_function(data, source_column_names, result_column_name)

    data.set_index(columns_config["index"], inplace=True)
    return data

if(__name__ == "__main__"):
    print("Parsing command-line arguments")
    args = parse_args()
    date = datetime.now()
    date_code = date.strftime("%Y%m%d")
    data = []
    data_path = args.data_dir + "/" + args.admin_div
    zip_path = "."
    zip_name = "data.zip"
    archive_path = "./" + zip_name
    delimiter = args.delimiter
    codes = admin_div_types.get(args.admin_div)

    print("Finding out if fresh data needs to be downloaded")
    files = os.listdir(data_path)
    file_name_contains_current_date = [date_code in file for file in files]
    if(not any(file_name_contains_current_date)):
        print("Downloading data")
        download_current_data(zip_path, zip_name, args.admin_div)
        print("Extracting archive")
        extract_data(archive_path, data_path)
        print("Attempting to remove archive")
        remove_downloaded_archive(archive_path)
    else:
        print("Data is current")

    print("Loading data")
    data = load_and_concatenate_data(data_path, delimiter)
    single_area_data = get_single_area_data(data, args.territory)

    print("Processing data")
    single_area_data = generate_additional_metrics(single_area_data, columns)

    print("Plotting selected columns")
    for column in columns_to_plot:
        plot_columns(single_area_data, column)
    print("Done!")
