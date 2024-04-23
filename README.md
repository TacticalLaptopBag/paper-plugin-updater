# paper-plugin-updater

A collection of Python scripts I use to update PaperMC and all installed plugins.

## Why not pluGET?
Because my server runs Debian 11 and doesn't have Python 3.10 binaries, which are required.
I'm too lazy to install Python 3.10, but apparently not lazy enough to not do it myself.

## Install
- Git clone or download this repository as a ZIP (Green Code button -> Download ZIP)
- Run `./install.sh path/to/server/root`

The path should be where the `plugins` folder is contained.
e.g. my plugins folder is in `my-server/plugins`, so I would run `./install.sh my-server`

## Usage
Simply run `python3 update.py` or `./update.py` while in the server root directory.
