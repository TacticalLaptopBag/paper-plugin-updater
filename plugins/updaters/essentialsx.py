import os
import requests
import urllib.request


def api_GET(endpoint: str) -> dict:
    return requests.get(endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    print(f"Downloading {fileName}...")
    response = urllib.request.urlretrieve(endpoint, fileName)
    return fileName


def get_essentialsx_file() -> str:
    for file in os.listdir("."):
        if file.startswith("EssentialsX-") and file.endswith(".jar"):
            return file

    return None


def get_installed_components() -> set[str]:
    components: set[str] = set()
    for file in os.listdir("."):
        if file.startswith("EssentialsX") and file.endswith(".jar"):
            component_name = file.split("-")[0]
            components.add(component_name)

    return components


def get_installed_files() -> list[str]:
    files: list[str] = []
    for file in os.listdir("."):
        if file.startswith("EssentialsX") and file.endswith(".jar"):
            files.append(file)

    return files


def get_current_version() -> str:
    essentialsx_file = os.path.splitext(get_essentialsx_file())[0]
    return essentialsx_file[12:]


def get_component_name(metadata_asset: dict) -> str:
    name = metadata_asset["name"]
    # EssentialsX-1.20.1.jar
    return name.split("-")[0]


def download_asset(metadata_asset: dict):
    download_url = metadata_asset["browser_download_url"]
    api_DOWNLOAD(download_url, metadata_asset["name"])


def update(mcVersion: str) -> list[str]:
    if len(get_installed_files()) == 0:
        # Plugin not installed, skip
        return []

    print("Updating EssentialsX...")
    latest_metadata_url = "https://api.github.com/repos/EssentialsX/Essentials/releases/latest"
    latest_metadata = api_GET(latest_metadata_url)
    latest_version = latest_metadata["tag_name"]
    current_version = get_current_version()

    if current_version == latest_version:
        print("EssentialsX already at latest version.")
        return get_installed_files()

    installed_components = get_installed_components()
    old_files: set[str] = set()
    for asset in latest_metadata["assets"]:
        asset_name = get_component_name(asset)
        if asset_name in installed_components:
            download_asset(asset)
            old_version = asset_name+"-"+current_version+".jar"
            old_files.add(asset_name+"-"+current_version+".jar")

    for old_file in old_files:
        print(f"Removing old EssentialsX component: {old_file}")
        os.remove(old_file)

    print(f"Updated EssentialsX from {current_version} -> {latest_version}")
    return get_installed_files()

