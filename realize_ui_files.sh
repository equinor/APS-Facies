#!/usr/bin/env bash

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: realize_ui_files.sh -h|--help: Shows this help"
    echo "Usage: realize_ui_files.sh --clean: Forcibly removes all python files before generating new ones."
    exit 0
fi

# Remove previous created Python files
if [[ "$1" == "--clean" ]]; then
    rm *.py
fi

files=$(ls *.ui)
for file in ${files}; do
    filename="${file%.*}"
    pyuic5 ${filename}.ui --output=${filename}.py
done
