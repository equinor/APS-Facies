#!/usr/bin/env bash
declare version
declare -a arr

if [[ $# == 1 ]]; then
    CODE_DIR="$1"
else
    CODE_DIR="."
fi

version=$(grep version "${CODE_DIR}/Dockerfile" | tr  -d "\\\\" | tr "=" " " | tr "\"" " ")
trimmed_version=$(echo "${version}" | sed -e 's/^[ \t]*//')
arr=(${trimmed_version})
[[ ${#arr[*]} == 3 ]] && echo ${arr[2]} || echo ${arr[1]}
