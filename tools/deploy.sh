#!/usr/bin/env bash

set -e

usage()
{
  echo "Usage: $0 [-h] [-d/--deploy] [-t/--test]"
  echo
  echo "arguments:"
  echo " -d, --deploy     deploy to PyPI"
  echo " -t, --test       deploy to the PyPI test server"
  echo " -h, --help       show this help message and exit"
  exit 2
}

if [ "$1" = "-h" ] || [ "$1" = "--help" ] || [ "$#" -ne 1 ] ; then
  usage
fi

if ! type twine &> /dev/null ; then
  echo "Error: twine is not installed."
  echo "Please run 'pip install twine'."
  exit 1
fi

WORKSPACE_DIR=$(git rev-parse --show-toplevel)
cd "$WORKSPACE_DIR"

PACKAGE_STR=$(ls dist/*.tar.gz | sed 's/dist\///;s/.tar.gz//')

if [ "$1" = "-d" ] || [ "$1" = "--deploy" ] ; then
  URL="https://upload.pypi.org/legacy/"
  MSG="Successfully deployed $PACKAGE_STR to PyPI"
elif [ "$1" = "-t" ] || [ "$1" = "--test" ] ; then
  URL="https://test.pypi.org/legacy/"
  MSG="Successfully deployed $PACKAGE_STR to the PyPI test server"
else
  usage
fi

twine upload --repository-url $URL dist/*
echo $MSG
