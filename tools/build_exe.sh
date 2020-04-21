#!/usr/bin/bash

set -e

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

python build_exe.py build

echo "Successfully built standalone executable"
