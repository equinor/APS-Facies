#!/usr/bin/env bash

if [[ "${TRACE:-0}" == "1" ]]; then
    set -o xtrace
fi

function run_tests() {
    # The entrypoint as seen by Equinor's internal RMS testing framework
    install_dependencies

    pytest "$PROJECT_ROOT/tests"
}

function install_dependencies() {
    pushd "$PROJECT_ROOT" >/dev/null || exit 1
    pip install .
}
