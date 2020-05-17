#!/usr/bin/bash

set -e

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

python build_cxfreeze.py build

echo "Successfully built standalone executable with cx_Freeze"
