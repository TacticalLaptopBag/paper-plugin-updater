#!/bin/bash
set -e

if [[ $# -lt 1 ]]; then
    echo "Not enough args. Need install directory (server root directory)"
    exit 1
fi

INSTALL_DIR=$1

if [[ -d $INSTALL_DIR ]]; then
    echo "Installing updater to $INSTALL_DIR..."
else
    echo "$INSTALL_DIR is not a directory."
    exit 1
fi

cp -v update.py ${INSTALL_DIR}
cp -rfv plugins ${INSTALL_DIR}

echo "Successfully installed updater to $INSTALL_DIR"

