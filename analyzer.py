from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from lib.dataset import DataSet
from lib.file_handler import FileHandler
from lib.territory import Territory
from datetime import date, datetime
import os
import matplotlib.pyplot as plt

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

if(__name__ == "__main__"):
    print("Parsing command-line arguments")
    args = parse_args()
    date = datetime.now()
    date_code = date.strftime("%Y%m%d")
    data_path = args.data_dir + "/" + args.admin_div
    zip_path = "."
    zip_name = "data.zip"
    archive_path = "./" + zip_name
    territory = Territory(args.admin_div, args.territory)
    file_handler = FileHandler(zip_name, zip_path, data_path)

    print("Finding out if fresh data needs to be downloaded")
    files = os.listdir(data_path)
    file_name_contains_current_date = [date_code in file for file in files]
    if(not any(file_name_contains_current_date)):
        print("Downloading data")
        file_handler.download_current_data(territory)
        print("Extracting archive")
        file_handler.extract_data()
        print("Attempting to remove archive")
        file_handler.remove_downloaded_archive()
    else:
        print("Data is current")

    print("Loading data")
    dataset = DataSet(data_path, args.delimiter, territory)

    print("Processing data")
    dataset.generate_additional_metrics(columns)

    print("Plotting selected columns")
    for column in columns_to_plot:
        plot_columns(dataset.data, column)
    print("Done!")
