from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from lib.dataset import DataSet
from lib.file_handler import FileHandler
from lib.territory import Territory
from datetime import date, datetime
import os


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "admin_div",
        choices=["wojewodztwo", "powiat"],
        default="powiat",
        help="Input administrative division type",
    )
    parser.add_argument(
        "territory", help="Input territory name for which you want graphs generated"
    )
    parser.add_argument("--config", default="./config/dataset_config.json")
    parser.add_argument(
        "--delimiter", default=";", help="Set delimiter used in CSV files"
    )
    parser.add_argument(
        "--data-dir",
        dest="data_dir",
        default="./data",
        help="Set path for the directory to download data to",
    )
    return parser.parse_args()



if __name__ == "__main__":
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
    if not any(file_name_contains_current_date):
        print("Downloading data")
        file_handler.download_current_data(territory)
        print("Extracting archive")
        file_handler.extract_data()
        print("Attempting to remove archive")
        file_handler.remove_downloaded_archive()
    else:
        print("Data is current")

    print("Loading data")
    dataset = DataSet(data_path, args.delimiter, territory, args.config)

    print("Processing data")
    dataset.generate_additional_metrics()

    print("Plotting selected columns")
    dataset.plot()
    print("Done!")
