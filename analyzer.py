from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from downloader import download_current_data, extract_data, remove_downloaded_archive
from territory_codes import codes
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

def parse_args():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("territory",
        help="Input territory name for which you want graphs generated")
    return parser.parse_args()

def plot_columns(dataset, columns):
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(16, 9))
    plt.xlabel("Daty")
    plt.ylabel("Wartości")
    title = ",".join(columns)
    plt.title(title)
    for column in columns:
        plt.plot(dataset[column])
    plt.show()


if(__name__ == "__main__"):
    args = parse_args()
    data = []
    data_path = "./data"
    zip_path = "."
    zip_name = "data.zip"
    archive_path = zip_path + "/" + zip_name
    delimiter = ";"

    files = os.listdir(data_path)
    file_name_contains_current_date = [date_code in file for file in files]
    if(not any(file_name_contains_current_date)):
    download_current_data(zip_path, zip_name)
    extract_data(archive_path, data_path)
        remove_downloaded_archive(archive_path)

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
    
    output = pd.concat(data)

    territory_id = codes[args.territory]
    placeholder = output.loc[output['teryt'] == territory_id]
    single_area = placeholder.copy()

    single_area.dropna(axis=0, how='any', inplace=True)
    single_area['liczba_przypadkow_int'] = (
        single_area['liczba_przypadkow'].astype(int)
    )
    single_area['zgony_int'] = single_area['zgony'].astype(int)
    single_area['przypadki_srednia_7dni'] = (
        single_area['liczba_przypadkow_int'].rolling(window=7).mean()
    )
    single_area['zgony_srednia_7dni'] = (
        single_area['zgony_int'].rolling(window=7).mean()
    )
    single_area['liczba_wykonanych_testow_srednia_7dni'] = (
        single_area['liczba_wykonanych_testow'].rolling(window=7).mean()
    )
    single_area['stan_rekordu_na_str'] = (
        single_area['stan_rekordu_na'].astype(str)
    )
    single_area['procent_poz_testow'] = (
        (single_area['liczba_testow_z_wynikiem_pozytywnym'] / 
         single_area['liczba_wykonanych_testow'] * 100).astype(float)
    )
    single_area['procent_poz_testow_7dni'] = (
        single_area['procent_poz_testow'].rolling(window=7).mean()
    )
    single_area['liczba_osob_objetych_kwarantanna'] = (
        single_area['liczba_osob_objetych_kwarantanna'].astype(int)
    )
    single_area['stan_rekordu_na_str'] = (
        single_area['stan_rekordu_na_str'].astype("datetime64")
    )
    single_area['liczba_na_10_tys_mieszkancow_7dni'] = (
        single_area['liczba_na_10_tys_mieszkancow'].rolling(window=7).mean())
    single_area.set_index('stan_rekordu_na_str', inplace=True)

    for column in columns_to_plot:
        plot_columns(single_area, column)
