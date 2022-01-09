from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import logging
from lib.dataset import DataSet
from lib.file_handler import FileHandler
from lib.territory import Territory
from datetime import date, datetime
import os
import sys


def parse_args():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "admin_div",
        choices=["wojewodztwo", "powiat", "province", "county"],
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


def configure_logger(name=None):
    handlers_list = []
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    date_format = "%Y-%m-%d %H:%M:%S"
    file_handler = logging.FileHandler(filename="./logs/analyzer.log", mode="w")
    file_handler.setLevel(logging.DEBUG)
    handlers_list.append(stream_handler)
    handlers_list.append(file_handler)
    logging.basicConfig(
        format="%(asctime)s | %(name)s |  %(levelname)s: %(message)s",
        datefmt=date_format,
        level=logging.DEBUG,
        handlers=handlers_list,
    )
    logger_name = name if name else __name__
    return logging.getLogger(logger_name)


def analyze(
    territory_type,
    territory,
    config="./config/dataset_config.json",
    delimiter=";",
    data_dir="./data",
):
    logger = configure_logger("Analyzer")
    logger.info("Parsing command-line arguments")
    date = datetime.now()
    date_code = date.strftime("%Y%m%d")
    data_path = data_dir + "/" + territory_type
    zip_path = "."
    zip_name = "data.zip"
    territory = Territory(territory_type, territory)
    file_handler = FileHandler(zip_name, zip_path, data_path)

    logger.info("Finding out if fresh data needs to be downloaded")
    files = os.listdir(data_path)
    file_name_contains_current_date = [date_code in file for file in files]
    if not any(file_name_contains_current_date):
        logger.info("Downloading data")
        file_handler.download_current_data(territory)
        logger.info("Extracting archive")
        file_handler.extract_data()
        logger.info("Attempting to remove archive")
        file_handler.remove_downloaded_archive()
    else:
        logger.info("Data is current")

    logger.info("Loading data")
    dataset = DataSet(data_path, delimiter, territory, config)

    logger.info("Processing data")
    dataset.generate_additional_metrics()

    logger.info("Plotting selected columns")
    dataset.plot()
    logger.info("Done!")


def get_data_dir_from_admin_div_type(admin_div_type):
    admin_div_types = {
        "wojewodztwo": "province",
        "province": "province",
        "powiat": "county",
        "county": "county",
    }
    data_dir = admin_div_types.get(admin_div_type, None)
    if data_dir is None:
        raise NotImplementedError(
            f"Administrative division'{admin_div_type}' is not supported"
        )
    return data_dir


if __name__ == "__main__":
    logger = configure_logger(name="Analyzer")
    logger.info("Parsing command-line arguments")
    args = parse_args()
    logger.debug(f"Args: {args}")
    date = datetime.now()
    logger.debug(f"Current time: {date}")
    date_code = date.strftime("%Y%m%d")
    logger.debug(f"Date code: {date_code}")
    admin_div_dir = get_data_dir_from_admin_div_type(args.admin_div)
    data_path = args.data_dir + "/" + admin_div_dir
    zip_path = "."
    zip_name = "data.zip"
    archive_path = "./" + zip_name
    territory = Territory(args.admin_div, args.territory)
    file_handler = FileHandler(zip_name, zip_path, data_path)

    logger.info("Finding out if fresh data needs to be downloaded")
    files = os.listdir(data_path)
    file_name_contains_current_date = [date_code in file for file in files]
    if not any(file_name_contains_current_date):
        logger.info("Downloading data")
        file_handler.download_current_data(territory)
        logger.info("Extracting archive")
        file_handler.extract_data()
        logger.info("Attempting to remove archive")
        file_handler.remove_downloaded_archive()
    else:
        logger.info("Data is current")

    logger.info("Loading data")
    dataset = DataSet(data_path, args.delimiter, territory, args.config)

    logger.info("Processing data")
    dataset.generate_additional_metrics()

    logger.info("Plotting selected columns")
    dataset.plot()
    logger.info("Done!")
