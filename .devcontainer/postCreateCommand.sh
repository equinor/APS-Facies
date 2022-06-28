#!/usr/bin/env bash

# python -m venv venv
# source venv/bin/activate
# pip install --upgrade pip
# pip install poetry
# poetry install
export PYTHONPATH="${PYTHONPATH}:/workspaces/aps-gui/"

git lfs install
git lfs pull

sudo ln -sf /workspaces/aps-gui/conf.nginx /etc/nginx/conf.d/aps.conf
sudo service nginx start
