#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 new-version" >&2
    exit 1
fi

sed "s/__version__\s=\s'[^']*'/__version__ = '$1'/" -i flickrapi/__init__.py

git diff
echo
echo "Don't forget to commit and tag:"
echo git commit -m \'Bumped version to $1\' flickrapi/__init__.py
echo git tag -a version-$1 -m \'Tagged version $1\'
