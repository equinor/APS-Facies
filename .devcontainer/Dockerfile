# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.236.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.11-trixie"
FROM mcr.microsoft.com/devcontainers/python:${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="20"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

RUN apt-get update \
 && apt-get -y install \
      # For connecting to the dev container from other IDEs
      openssh-server \
      # The server for APS
      nginx

## Install Nginx
#RUN apt install nginx

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.

USER vscode
ENV PATH="/home/vscode/.local/bin:$PATH"
WORKDIR /workspaces/aps-gui/

COPY .tool-versions ./
RUN <<EOF
#!/usr/bin/env bash
UV_VERSION="$(cat .tool-versions|grep uv | grep -o -E '([0-9]+\.?)+')"
pip install --no-cache-dir --user "uv==$UV_VERSION"
EOF
