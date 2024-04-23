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
    paper_build = None
    paper_mc_version = None
    with open("version_history.json", "r") as versionFile:
        versionData = json.loads(versionFile.readline())
        print(f"Current PaperMC version: {versionData['currentVersion']}")
        # git-Paper-493 (MC: 1.20.4)
        versionDataSplitSpace = versionData["currentVersion"].split(" ")
        paper_build_split_dash = versionDataSplitSpace[0].split("-")
        paper_build = paper_build_split_dash[-1]
        paper_mc_version = versionDataSplitSpace[-1][:-1]

    print(f"Current PaperMC build: {paper_build}")
    print(f"Current Minecraft version: {paper_mc_version}")
    
    return (int(paper_build), paper_mc_version)


def paper_get_latest_version(mc_version: str) -> int:
    print("Checking latest PaperMC build...")
    response = api_GET("/versions/" + mc_version)
    paper_build = int(response["builds"][-1])
    print(f"Latest PaperMC build: {paper_build}")

    return paper_build


def paper_get_build_download_name(mc_version: str, build: int) -> str:
    response = api_GET("/versions/" + mc_version + "/builds/" + str(build))
    download_name = response["downloads"]["application"]["name"]
    print(f"Download name: {download_name}")
    return download_name


def paper_download_build(mc_version: str, build: int) -> str:
    download_name = paper_get_build_download_name(mc_version, build)
    new_paper_path = api_DOWNLOAD("/versions/" + mc_version + "/builds/" + str(build) + "/downloads/" + download_name, download_name)
    return new_paper_path


def paper_symlink(new_paper_path: str):
    os.remove("paper.jar")
    os.symlink(new_paper_path, "paper.jar")


def paper_update(upgrade_version: str) -> str:
    (paper_build, paper_mc_version) = paper_get_current_version() 
    print("")

    if not upgrade_version:
        print("mc_version not specified, using current MC version")
        upgrade_version = paper_mc_version

    latest_paper_build = paper_get_latest_version(upgrade_version)
    if latest_paper_build <= paper_build and paper_mc_version == upgrade_version:
        print("Paper is already at latest build!")
        return upgrade_version
    
    print("Update available!")

    latest_path = paper_download_build(upgrade_version, latest_paper_build)
    paper_symlink(latest_path)

    version_format = "({mc}) {build}"
    if paper_mc_version == upgrade_version:
        version_format = "{build}"

    old_version = version_format.format(mc=paper_mc_version, build=paper_build)
    new_version = version_format.format(mc=upgrade_version, build=latest_paper_build)
    print(f"Successfully updated paper: {old_version} -> {new_version}")

    return upgrade_version


def run_plugin_updaters(updaters_dir: str, upgrade_version: str) -> (int, int, list[str]):
    if not os.path.isdir(updaters_dir):
        return (0, 0)

    success_counter = 0
    updater_total = 0

    plugins_accounted_for: list[str] = []

    for updater_file_name in os.listdir(updaters_dir):
        (updater_file_name, updater_file_ext) = os.path.splitext(updater_file_name)
        if updater_file_ext != ".py":
            continue

        updater_total = updater_total + 1
        updater_file_path = os.path.join(updaters_dir, updater_file_name)
        updater_module_path = updater_file_path.replace(os.sep, ".")
        updater = __import__(updater_module_path, fromlist=[None])
        did_attempt = False
        try:
            os.chdir("plugins")
            files = updater.update(upgrade_version)
            did_attempt = len(files) > 0
            if did_attempt:
                plugins_accounted_for.extend(files)
                success_counter = success_counter + 1
            else:
                updater_total = updater_total - 1
        except:
            print(f"Unexpected error when running the updater found in {updater_file_path}!")
            traceback.print_exc() 
        finally:
            os.chdir("..")

        if did_attempt:
            print("")

    return (success_counter, updater_total, plugins_accounted_for)


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
    upgrade_version = paper_update(args["mc_version"])
    print("")

    print(f"Updating plugins using update scripts in 'plugins/updaters'...")
    print("")
    (updates_completed, total_updaters, plugins_accounted_for) = run_plugin_updaters("plugins/updaters", upgrade_version)
    if updates_completed == total_updaters:
        print(f"Successfully updated {updates_completed}/{total_updaters} plugins!")
        report_updater_coverage(plugins_accounted_for)
    else:
        print(f"Failed to update some plugins. {updatesCompleted}/{totalUpdaters} plugins were updated.")
        print("Unable to give updater coverage due to update failures")


if __name__ == "__main__":
    main()

