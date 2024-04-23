import os
import requests
import urllib.request
import re

BASE_NAME = "ViaBackwards"
REPO = "ViaVersion/ViaBackwards"

def api_GET(endpoint: str) -> dict:
    return requests.get(endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    print(f"Downloading {fileName}...")
    response = urllib.request.urlretrieve(endpoint, fileName)
    return fileName


def get_file() -> str:
    for file in os.listdir("."):
        if file.startswith(BASE_NAME) and file.endswith(".jar"):
            return file

    return None


def get_current_version() -> str:
    file_name = get_file()
    if file_name is None:
        return "???"

    file_name = os.path.splitext(file_name)[0]
    file_name_split = file_name.split("-")
    if len(file_name_split) <= 1:
        return "???"

    return file_name_split[1]


def get_latest_version(metadata: dict) -> str:
    return metadata["tag_name"]


def update(mcVersion: str) -> list[str]:
    if get_file() == None:
        # Plugin not installed, skip
        return []

    print(f"Updating {BASE_NAME}...")
    latest_metadata_url = "https://api.github.com/repos/"+REPO+"/releases/latest"
    latest_metadata = api_GET(latest_metadata_url)

    latest_version = get_latest_version(latest_metadata)
    current_version = get_current_version()

    if current_version == latest_version:
        print(f"{BASE_NAME} already at latest version.")
        return [get_file()]

    if current_version == "???":
        print(f"{BASE_NAME} is at an unknown version! Will update anyway.")

    old_file = get_file() or ""

    url = latest_metadata["assets"][0]["browser_download_url"]
    api_DOWNLOAD(url, BASE_NAME+"-"+latest_version+".jar")

    if os.path.isfile(old_file):
        print(f"Removing old {BASE_NAME} version: {old_file}")
        os.remove(old_file)

    print(f"Updated {BASE_NAME} from {current_version} -> {latest_version}")
    return [get_file()]

