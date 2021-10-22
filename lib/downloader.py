import urllib.request
import zipfile
import os

data_types = {
    "powiat": "https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data",
    "wojewodztwo": "https://arcgis.com/sharing/rest/content/items/a8c562ead9c54e13a135b02e0d875ffb/data"
}

def download_current_data(path, filename, data_type):
    link = data_types.get(data_type,None)
    if not link:
        raise ValueError(
            "Unable to find link for '{}' data type".format(data_type))
    urllib.request.urlretrieve(link, f"{path}/{filename}")

def extract_data(zip_path, data_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)

def remove_downloaded_archive(file_path):
    try:
        os.remove(file_path)
        print("File - {} - removed".format(file_path))
    except FileNotFoundError:
        print("Could not remove - {}".format(file_path))
        print("File does not exist!")
    except IsADirectoryError:
        print("Could not remove - {}".format(file_path))
        print("Target is a directory")
    except Exception:
        print("Could not remove - {}".format(file_path))
        print("File is likely in use")
