#!/usr/bin/env bash

uv sync
yarn --cwd ./gui/ install

export PYTHONPATH="${PYTHONPATH}:/workspaces/aps-gui/"

sudo ln -sf /workspaces/aps-gui/conf.nginx /etc/nginx/conf.d/aps.conf
sudo service nginx start
