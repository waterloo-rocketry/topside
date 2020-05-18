#!/usr/bin/env bash

if ! type pyinstaller &> /dev/null
then
    echo "Error: pyinstaller is not installed."
    echo "Please run 'pip install pyinstaller'."
    exit 1
fi

set -e

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

case "$OSTYPE" in
    darwin*) PATHSEP=":" ;;
    linux*)  PATHSEP=":" ;;
    msys*)   PATHSEP=";" ;;
esac

pyinstaller --name "Topside" \
            --add-data "application/resources"$PATHSEP"resources" \
            --windowed main.py

echo "Successfully built standalone executable with PyInstaller"
