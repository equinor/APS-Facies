# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.236.0/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.8-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="14"
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
ARG POETRY_VERSION="1.1.15"
# Install poetry
RUN pip install --upgrade pip \
  && curl -sSL https://install.python-poetry.org | python3 - --version="$POETRY_VERSION"

# Install dependencies
WORKDIR /workspaces/aps-gui/
COPY --chown="vscode:vscode" pyproject.toml poetry.lock ./
# Install dependencies
RUN poetry install

COPY --chown="vscode:vscode" gui/package.json gui/yarn.lock ./gui/

RUN yarn --cwd ./gui/ install

# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1