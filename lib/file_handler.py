import logging
import urllib.request
import zipfile
import os


class FileHandler(object):
    def __init__(self, filename, file_path, data_dir) -> None:
        self.links_by_territory_type = {
            "powiat": "https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data",
            "county": "https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data",
            "wojewodztwo": "https://arcgis.com/sharing/rest/content/items/a8c562ead9c54e13a135b02e0d875ffb/data",
            "province": "https://arcgis.com/sharing/rest/content/items/a8c562ead9c54e13a135b02e0d875ffb/data",
        }
        self.filename = filename
        self.file_path = file_path
        self.data_dir = data_dir
        self.zip_path = self.file_path + "/" + filename
        self.logger = logging.getLogger("File Handler")

    def download_current_data(self, territory):
        link = self.links_by_territory_type.get(territory.type, None)
        if not link:
            raise ValueError(f"Unable to find link for '{territory.type}' data type")
        urllib.request.urlretrieve(link, f"{self.file_path}/{self.filename}")

    def extract_data(self):
        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            zip_ref.extractall(self.data_dir)

    def remove_downloaded_archive(self):
        try:
            os.remove(self.zip_path)
            self.logger.info(f"File - {self.zip_path} - removed")
        except FileNotFoundError:
            self.logger.error(f"Could not remove - {self.zip_path}")
            self.logger.error(f"File does not exist!")
        except IsADirectoryError:
            self.logger.error(f"Could not remove - {self.zip_path}")
            self.logger.error(f"Target is a directory")
        except Exception:
            self.logger.error(f"Could not remove - {self.zip_path}")
            self.logger.error(f"File is likely in use")
