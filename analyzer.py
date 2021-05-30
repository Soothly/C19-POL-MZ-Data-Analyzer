import csv
import datetime
import os
import matplotlib.pyplot as plt


def get_date_from_filename(filename):
    year = int(filename[0:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    return datetime.datetime(year, month, day).strftime("%Y-%m-%d")

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
    data = {}
    data_path = "./dane_historyczne"
    files = os.listdir(data_path)
    files.pop()
    for file in files:
        filepath = data_path + "/" + file
        date = get_date_from_filename(file)
        data[date] = read_csv(filepath, "pomorskie", "Gdańsk")
    
    export_to_csv(data)

    print(data)