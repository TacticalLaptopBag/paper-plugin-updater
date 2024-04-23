#!/bin/python3
import json
import argparse
import requests
import urllib.request
import os
import traceback

parser = argparse.ArgumentParser(prog="papermc-updater", description="Updates plugins and Paper version", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("mc_version", type=str, nargs="?", help="Specify a new Minecraft version to upgrade to.")
args = vars(parser.parse_args())

# Helpful web functions
def api_GET(endpoint: str) -> dict:
    return requests.get("https://api.papermc.io/v2/projects/paper" + endpoint).json()


def api_DOWNLOAD(endpoint: str, fileName: str) -> str:
    """
    # Dear heavens, this takes farrrrr too long to download
    # https://stackoverflow.com/a/10744565
    response = requests.get("https://api.papermc.io/v2/projects/paper" + endpoint, stream=True)
    with open(fileName, "wb") as handle:
        for data in tqdm(response.iter_content()):
            handle.write(data)
    """
    print(f"Downloading {fileName}...")
    response = urllib.request.urlretrieve("https://api.papermc.io/v2/projects/paper" + endpoint, fileName)
    return fileName


# Update paper.jar
def paper_get_current_version() -> (int, str):
    paperBuild = None
    paperMCVersion = None
    with open("version_history.json", "r") as versionFile:
        versionData = json.loads(versionFile.readline())
        print(f"Current PaperMC version: {versionData['currentVersion']}")
        # git-Paper-493 (MC: 1.20.4)
        versionDataSplitSpace = versionData["currentVersion"].split(" ")
        paperBuildSplitDash = versionDataSplitSpace[0].split("-")
        paperBuild = paperBuildSplitDash[-1]
        paperMCVersion = versionDataSplitSpace[-1][:-1]

    print(f"Current PaperMC build: {paperBuild}")
    print(f"Current Minecraft version: {paperMCVersion}")
    
    return (int(paperBuild), paperMCVersion)


def paper_get_latest_version(mcVersion: str) -> int:
    print("Checking latest PaperMC build...")
    response = api_GET("/versions/" + mcVersion)
    paperBuild = int(response["builds"][-1])
    print(f"Latest PaperMC build: {paperBuild}")

    return paperBuild


def paper_get_build_download_name(mcVersion: str, build: int) -> str:
    response = api_GET("/versions/" + mcVersion + "/builds/" + str(build))
    downloadName = response["downloads"]["application"]["name"]
    print(f"Download name: {downloadName}")
    return downloadName


def paper_download_build(mcVersion: str, build: int) -> str:
    downloadName = paper_get_build_download_name(mcVersion, build)
    newPaperPath = api_DOWNLOAD("/versions/" + mcVersion + "/builds/" + str(build) + "/downloads/" + downloadName, downloadName)
    return newPaperPath


def paper_symlink(newPaperPath: str):
    os.remove("paper.jar")
    os.symlink(newPaperPath, "paper.jar")


def paper_update(upgradeVersion: str) -> str:
    (paperBuild, paperMCVersion) = paper_get_current_version() 
    print("")

    if not upgradeVersion:
        print("mc_version not specified, using current MC version")
        upgradeVersion = paperMCVersion

    latestPaperBuild = paper_get_latest_version(upgradeVersion)
    if latestPaperBuild <= paperBuild and paperMCVersion == upgradeVersion:
        print("Paper is already at latest build!")
        return upgradeVersion
    
    print("Update available!")

    latestPath = paper_download_build(upgradeVersion, latestPaperBuild)
    paper_symlink(latestPath)

    versionFormat = "({mc}) {build}"
    if paperMCVersion == upgradeVersion:
        versionFormat = "{build}"

    oldVersion = versionFormat.format(mc=paperMCVersion, build=paperBuild)
    newVersion = versionFormat.format(mc=upgradeVersion, build=latestPaperBuild)
    print(f"Successfully updated paper: {oldVersion} -> {newVersion}")

    return upgradeVersion


def run_plugin_updaters(updatersDir: str, upgradeVersion: str) -> (int, int, list[str]):
    if not os.path.isdir(updatersDir):
        return (0, 0)

    successCounter = 0
    updaterTotal = 0

    plugins_accounted_for: list[str] = []

    for updaterFileName in os.listdir(updatersDir):
        (updaterFileName, updaterFileExt) = os.path.splitext(updaterFileName)
        if updaterFileExt != ".py":
            continue

        updaterTotal = updaterTotal + 1
        updaterFilePath = os.path.join(updatersDir, updaterFileName)
        updaterModulePath = updaterFilePath.replace(os.sep, ".")
        updater = __import__(updaterModulePath, fromlist=[None])
        try:
            os.chdir("plugins")
            files = updater.update(upgradeVersion)
            plugins_accounted_for.extend(files)
            successCounter = successCounter + 1
        except:
            print(f"Unexpected error when running the updater found in {updaterFilePath}!")
            traceback.print_exc() 
        finally:
            os.chdir("..")
        print("")

    return (successCounter, updaterTotal, plugins_accounted_for)


def report_updater_coverage(plugins_accounted_for_list: list[str]):
    plugins_accounted_for: set[str] = set(plugins_accounted_for_list)
    unaccounted_plugins: set[str] = set()
    os.chdir("plugins")
    for file in os.listdir("."):
        if not os.path.isfile(file):
            continue
        if not file.endswith(".jar"):
            continue

        if file not in plugins_accounted_for:
            unaccounted_plugins.add(file)
    os.chdir("..")

    unaccounted_plugins_len = len(unaccounted_plugins)
    if unaccounted_plugins_len == 0:
        return

    print("")
    print(f"{unaccounted_plugins_len} plugins not updated due to a missing updater script:")
    for unaccounted_plugin in unaccounted_plugins:
        print(f" - {unaccounted_plugin}")


def main():
    global args
    upgradeVersion = paper_update(args["mc_version"])
    print("")

    print(f"Updating plugins using update scripts in 'plugins/updaters'...")
    print("")
    (updatesCompleted, totalUpdaters, plugins_accounted_for) = run_plugin_updaters("plugins/updaters", upgradeVersion)
    if updatesCompleted == totalUpdaters:
        print(f"Successfully updated {updatesCompleted}/{totalUpdaters} plugins!")
        report_updater_coverage(plugins_accounted_for)
    else:
        print(f"Failed to update some plugins. {updatesCompleted}/{totalUpdaters} plugins were updated.")
        print("Unable to give updater coverage due to update failures")


if __name__ == "__main__":
    main()

