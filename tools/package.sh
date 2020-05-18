#!/usr/bin/env bash

set -e

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

python setup.py sdist bdist_wheel

PACKAGE_STR=$(ls dist/*.tar.gz | sed 's/dist\///;s/.tar.gz//')
echo "Successfully packaged sdist and wheel for $PACKAGE_STR"
