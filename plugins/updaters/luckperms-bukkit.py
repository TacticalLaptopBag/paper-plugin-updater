import os
import requests


def api_GET(endpoint: str) -> dict:
    return requests.get(endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    # Using urllib.request causes a 403 response.
    # Jenkins seems happy enough with the requests library, so we'll just use that...

    # Source: https://stackoverflow.com/a/16696317
    print(f"Downloading {fileName} from {endpoint}...")
    with requests.get(endpoint, stream=True) as r:
        r.raise_for_status()
        with open(fileName, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return fileName


def get_luckperms_file() -> str:
    for file in os.listdir("."):
        if file.startswith("LuckPerms-Bukkit-") and file.endswith(".jar"):
            return file

    return None


def get_current_version() -> str:
    luckperms_file = os.path.splitext(get_luckperms_file())[0]
    return luckperms_file[17:]


def get_artifact_path(latest_metadata: dict) -> dict:
    for artifact in latest_metadata["artifacts"]:
        relative_path = artifact["relativePath"]
        artifact_file_name = relative_path.split("/")[-1]
        if artifact_file_name.startswith("LuckPerms-Bukkit-"):
            return relative_path
        

def get_artifact_version(artifact_relative_path: str) -> str:
    return os.path.splitext(artifact_relative_path)[0].split("-")[-1]


def get_artifact_file_name(artifact_relative_path: str) -> str:
    return artifact_relative_path.split("/")[-1]


def update(mcVersion: str) -> list[str]:
    # Artifact base path: https://ci.lucko.me/job/LuckPerms/lastSuccessfulBuild/artifact/<artifact-relativePath>
    # Artifact relative path: bukkit/loader/build/libs/LuckPerms-Bukkit-5.4.122.jar
    # Latest build info: https://ci.lucko.me/job/LuckPerms/lastSuccessfulBuild/api/json/

    print("Updating LuckPerms...")
    latest_metadata_url = "https://ci.lucko.me/job/LuckPerms/lastSuccessfulBuild/api/json/"
    latest_metadata = api_GET(latest_metadata_url)
    artifact_path = get_artifact_path(latest_metadata)
    latest_version = get_artifact_version(artifact_path)
    current_version = get_current_version()

    if latest_version == current_version:
        print("LuckPerms already at latest version.")
        return [get_luckperms_file()]

    old_file = get_luckperms_file()

    artifact_url = "https://ci.lucko.me/job/LuckPerms/lastSuccessfulBuild/artifact/"+artifact_path
    print(artifact_url)
    artifact_name = get_artifact_file_name(artifact_path)
    api_DOWNLOAD(artifact_url, artifact_name)
    
    print(f"Removing old LuckPerms version: {old_file}")
    os.remove(old_file)

    print(f"Updated LuckPerms from {current_version} -> {latest_version}")

    return [artifact_name]

