import os
import requests
import urllib.request


def api_GET(endpoint: str) -> dict:
    return requests.get(endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    print(f"Downloading {fileName}...")
    response = urllib.request.urlretrieve(endpoint, fileName)
    return fileName


def get_floodgate_file() -> str:
    # updated: floodgate-spigot-2.22.2.jar
    # orig: floodgate-spigot.jar
    for file in os.listdir("."):
        if file.startswith("floodgate-spigot") and file.endswith(".jar"):
            return file

    return None


def get_current_version() -> str:
    file_name = get_floodgate_file()
    if file_name is None:
        return "???"

    file_name = os.path.splitext(file_name)[0]
    file_name_split = file_name.split("-")
    if len(file_name_split) <= 2:
        return "???"

    return file_name_split[2]


def get_latest_version() -> str:
    response = api_GET("https://download.geysermc.org/v2/projects/floodgate")
    return response["versions"][-1]


def update(mcVersion: str) -> list[str]:
    print("Updating Floodgate...")
    current_version = get_current_version()
    latest_version = get_latest_version()

    if current_version == latest_version:
        print("Floodgate already at latest version.")
        return [get_floodgate_file()]

    if current_version == "???":
        print("Floodgate is at an unknown version! Will update anyway.")

    old_file = get_floodgate_file() or ""

    url = "https://download.geysermc.org/v2/projects/floodgate/versions/"+latest_version+"/builds/latest/downloads/spigot"
    api_DOWNLOAD(url, "floodgate-spigot-"+latest_version+".jar")

    if os.path.isfile(old_file):
        print(f"Removing old Floodgate version: {old_file}")
        os.remove(old_file)

    print(f"Updated Floodgate from {current_version} -> {latest_version}")
    return [get_floodgate_file()]

