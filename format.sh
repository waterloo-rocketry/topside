#!/usr/bin/bash

if ! type autopep8 &> /dev/null
then
    echo "Error: autopep8 is not installed."
    echo "Please run 'pip install autopep8'."
    exit 1
fi

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

FILES=$(git diff --name-only master | grep '\.py')

if [ ! -z "$FILES" ]
then
    autopep8 -i $FILES
fi
