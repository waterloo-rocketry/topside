#!/usr/bin/bash

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd $WORKSPACE_DIR

FILES=$(git diff --name-only master | grep '\.py')

if [ ! -z "$FILES" ]
then
    autopep8 -i $FILES
fi
