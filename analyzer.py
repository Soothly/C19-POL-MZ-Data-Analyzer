from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, SUPPRESS
import csv
import datetime
import os
import matplotlib.pyplot as plt
import pandas as pd

columns_to_plot = [
    'przypadki_srednia_7dni',
    'zgony_srednia_7dni',
    'procent_poz_testow_7dni',
    'liczba_osob_objetych_kwarantanna',
    'liczba_na_10_tys_mieszkancow'
]

def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog="")
    parser.add_argument("territory", help="")
    return parser.parse_args()

def get_date_from_filename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year, month, day).strftime("%Y-%m-%d")

def plot_column(dataset, column):
    plt.style.use("fivethirtyeight")
    plt.figure(figsize=(16, 9), )
    plt.xlabel("Daty")
    plt.ylabel("Wartości")
    plt.title(column)
    plt.plot(dataset[column])
    plt.show()

def read_csv(file, greater_area, minor_area):
    data = {}    
    with open(file, "r", encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        try:
            for row in csv_reader:
                if(row[0] != greater_area or row[1] != minor_area):
                    continue
                else:
                    data['cases'] = int(row[2])
                    data['deaths'] = int(float(row[4]))
                    data['deaths_covid_only'] = int(float(row[5]))
                    data['deaths_covid_contrib'] = int(float(row[6]))
                    data['poz_tests'] = int(row[7])
                    data['recovered'] = int(row[8])
                    data['quarantined'] = int(row[9])
                    data['all_tests'] = int(row[10])
                    data['positive_tests'] = int(row[11])
                    data['negative_tests'] = int(row[12])
        except UnicodeDecodeError:
            pass
    if(not data):
        with open(file, "r", encoding='cp1250') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if(row[0] != greater_area or row[1] != minor_area):
                    continue
                else:
                    try:
                        data['cases'] = int(row[2])
                        data['deaths'] = int(float(row[4])) if(row[4] != '') else 0
                        data['deaths_covid_only'] = int(float(row[5])) if(row[5] != '') else 0
                        data['deaths_covid_contrib'] = int(float(row[6])) if(row[6] != '') else 0
                        data['poz_tests'] = int(row[7])
                        data['recovered'] = int(row[8])
                        data['quarantined'] = int(row[9])
                        data['all_tests'] = int(row[10])
                        data['positive_tests'] = int(row[11])
                        data['negative_tests'] = int(row[12])
                    except ValueError:
                        data['poz_tests'] = ''
                        data['recovered'] = ''
                        data['quarantined'] = ''
                        data['all_tests'] = ''
                        data['positive_tests'] = ''
                        data['negative_tests'] = ''
    return data

def export_to_csv(data):
    with open("data.csv", 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';')
        csv_writer.writerow(['Data', 'Przypadki', 'Zgony', 'Kwarantanna', 'Pozytywne Testy', 'Testy', 'Procent pozytywnych'])
        for day in data:
            try:
                positivity_rate = data[day]['positive_tests']/data[day]['all_tests']
            except TypeError:
                positivity_rate = 0
            csv_writer.writerow(
                [
                    day, 
                    data[day]['cases'],
                    data[day]['deaths'],
                    data[day]['quarantined'],
                    data[day]['positive_tests'],
                    data[day]['all_tests'],
                    positivity_rate
                ])

if(__name__ == "__main__"):
    args = parse_args()
    data = []
    data_path = "./data"
    delimiter = ";"
    files = os.listdir(data_path)
    for file in files:
        if("csv" not in file):
            continue
        filepath = data_path + "/" + file
        date = get_date_from_filename(file)
        try:
            data_from_file = pd.read_csv(filepath, delimiter=delimiter, encoding='utf-8')
        except UnicodeDecodeError:
            data_from_file = pd.read_csv(filepath, delimiter=delimiter, encoding='cp1250')
        data.append(data_from_file)
    
    output = pd.concat(data)
    print(output)

    placeholder = output.loc[output['teryt'] == args.territory]
    single_area = placeholder.copy()

    print(single_area.columns)
    single_area.dropna(axis=0, how='any', inplace=True)
    single_area['liczba_przypadkow_int'] = single_area['liczba_przypadkow'].astype(int)
    single_area['zgony_int'] = single_area['zgony'].astype(int)
    single_area['przypadki_srednia_7dni'] = single_area['liczba_przypadkow_int'].rolling(window=7).mean()
    single_area['zgony_srednia_7dni'] = single_area['zgony_int'].rolling(window=7).mean()
    single_area['stan_rekordu_na_str'] = single_area['stan_rekordu_na'].astype(str)
    single_area['procent_poz_testow'] = (single_area['liczba_testow_z_wynikiem_pozytywnym'] / single_area['liczba_wykonanych_testow'] * 100).astype(float)
    single_area['procent_poz_testow_7dni'] = single_area['procent_poz_testow'].rolling(window=7).mean()
    single_area.to_csv('output.csv', sep=delimiter)
    single_area['liczba_osob_objetych_kwarantanna'] = single_area['liczba_osob_objetych_kwarantanna'].astype(int)
    single_area['stan_rekordu_na_str'] = single_area['stan_rekordu_na_str'].astype("datetime64")
    single_area.set_index('stan_rekordu_na_str', inplace=True)

    for column in columns_to_plot:
        plot_column(single_area, column)
