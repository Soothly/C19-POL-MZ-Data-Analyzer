import urllib.request
import zipfile

def download_current_data(path, filename):
    urllib.request.urlretrieve(
        "https://arcgis.com/sharing/rest/content/items/e16df1fa98c2452783ec10b0aea4b341/data", 
        f"{path}/{filename}")

def extract_data(zip_path, data_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(data_dir)