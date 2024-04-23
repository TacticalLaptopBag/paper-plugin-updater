import os
import requests
import urllib.request
import re


def api_GET(endpoint: str) -> dict:
    return requests.get(endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    print(f"Downloading {fileName}...")
    response = urllib.request.urlretrieve(endpoint, fileName)
    return fileName


def get_vivecraft_file() -> str:
    # updated: Vivecraft_Spigot_Extensions-1.20.4r1.jar
    # orig: Vivecraft_Spigot_Extensions.jar
    for file in os.listdir("."):
        if file.startswith("Vivecraft_Spigot_Extensions") and file.endswith(".jar"):
            return file

    return None


def get_current_version() -> str:
    file_name = get_vivecraft_file()
    if file_name is None:
        return "???"

    file_name = os.path.splitext(file_name)[0]
    file_name_split = file_name.split("-")
    if len(file_name_split) <= 1:
        return "???"

    return file_name_split[1]


def get_asset_for_mcversion(mcVersion: str, latest_metadata: dict) -> dict:
    for asset in latest_metadata["assets"]:
        name = asset["name"]
        match = re.search(r"\d+\.\d+\.\d+", name)
        if match.group() == mcVersion:
            return asset


def get_latest_version(asset: dict) -> str:
    name = os.path.splitext(asset["name"])[0]
    match = re.search(r"\d+\.\d+\.\d+", name)
    return name[match.start():]


def update(mcVersion: str) -> list[str]:
    if get_vivecraft_file() == None:
        # Plugin not installed, skip
        return []

    print("Updating Vivecraft...")
    latest_metadata_url = "https://api.github.com/repos/jrbudda/Vivecraft_Spigot_Extensions/releases/latest"
    latest_metadata = api_GET(latest_metadata_url)
    latest_asset = get_asset_for_mcversion(mcVersion, latest_metadata)
    if latest_asset is None:
        print(f"Vivecraft FATAL: No (modern) version found for {mcVersion}!")
        raise Exception("Unable to retrieve latest version")
    latest_version = get_latest_version(latest_asset)
    current_version = get_current_version()

    # Use "created_at" property to determine latest version for current mcVersion

    if current_version == latest_version:
        print("Vivecraft already at latest version.")
        return [get_vivecraft_file()]

    if current_version == "???":
        print("Vivecraft is at an unknown version! Will update anyway.")

    old_file = get_vivecraft_file() or ""

    api_DOWNLOAD(latest_asset["browser_download_url"], "Vivecraft_Spigot_Extensions-"+latest_version+".jar")

    if os.path.isfile(old_file):
        print(f"Removing old Vivecraft version: {old_file}")
        os.remove(old_file)

    print(f"Updated Vivecraft from {current_version} -> {latest_version}")
    return [get_vivecraft_file()]

