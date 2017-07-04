#!/usr/bin/env bash

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo "Usage: realize_ui_files.sh -h|--help:  Shows this help"
    echo "                           --clean:    Forcibly removes all python files before generating new ones."
    echo "                           --autopep8: Make sure the generated python files are compliant with PEP-8."
    exit 0
fi

current_dir=$(pwd)
ui_files="$(pwd)/ui"
pyui_files="$(pwd)/src/ui"
mkdir -p "${pyui_files}"

# Remove previous created Python files
if [[ "$1" == "--clean" ]]; then
    rm -rf ${ui_files}
fi

cd "${ui_files}"
files=$(ls *.ui)
for file in ${files}; do
    filename="${file%.*}"
    pyuic5 ${filename}.ui --output="${pyui_files}/${filename}_ui.py"
done

# If autopep8 is "installed", clean up the files
if [[ "$1" == "--autopep8" ]];then
    if type autopep8 > /dev/null; then
        autopep8 ${pyui_files} --recursive --in-place --pep8-passes 5000
    else
        echo "autopep8 is not installed."
    fi
fi
cd ${current_dir}
