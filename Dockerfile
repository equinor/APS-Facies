# syntax = docker/dockerfile:1
ARG RMS_IMAGE
FROM node:20.19.2-alpine3.22 AS node

ENV CODE=/code
ENV NODE_MODULES=$CODE/node_modules
ENV TRUNCATION_RULES=src/stores/truncation-rules/templates/truncationRules.json

FROM nginx:1.29.1-bookworm AS nginx

FROM ${RMS_IMAGE} AS base
# RMS 12.0 and earlier uses Python 3.6.1, but it is so old that I was unable to update the CA certificates,
# and thus unable to download any packages
ENV XDG_CACHE_HOME=/var/cahce

WORKDIR /code
FROM base AS python
RUN dnf install -y git
ENV PATH="/root/.local/bin:$PATH"

COPY .tool-versions ./
RUN <<EOF
#!/usr/bin/env bash
UV_VERSION="$(cat .tool-versions|grep uv | grep -o -E '([0-9]+\.?)+')"
roxenv pip install --user "uv==$UV_VERSION"
EOF

ENV UV_PYTHON_PREFERENCE="only-system"

COPY pyproject.toml uv.lock ./
# Necessary for placing the auto-generated _version.py file
RUN --mount=type=cache,target=$XDG_CACHE_HOME/uv \
    roxenv uv venv --system-site-packages && \
    roxenv uv sync --all-extras --no-install-project

FROM python AS aps
ENV PYTHONPATH=/code

COPY src/aps ./src/aps/


FROM python AS truncation-rules
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
RUN curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh

COPY --from=aps /code/src/aps/ src/aps/

COPY .mise-tasks .mise-tasks/
COPY mise.toml ./
COPY examples/truncation_settings.dat ./examples/

ENV MISE_AUTO_INSTALL=false
RUN mise trust
RUN --mount=type=bind,source=.git,target=/code/.git,readonly \
    roxenv mise tasks run generate-truncation-rules

FROM node AS install

WORKDIR $CODE

COPY gui/package.json gui/yarn.lock ./

RUN yarn install --frozen-lockfile

FROM node AS gui

ENV YARN_CACHE_FOLDER=/yarn
RUN yarn config set cache-folder $YARN_CACHE_FOLDER

WORKDIR $CODE
COPY --from=install $NODE_MODULES $NODE_MODULES

COPY gui/package.json .
COPY gui/yarn.lock .

# build / configuration files
COPY gui/tsconfig.json .
COPY gui/.oxlintrc.json .
COPY gui/.postcssrc.js .
COPY gui/vite.config.ts .
COPY gui/vue.config.js .
COPY gui/index.html .

# Static files
COPY gui/public public
COPY --from=truncation-rules $CODE/gui/$TRUNCATION_RULES $CODE/$TRUNCATION_RULES
COPY --from=truncation-rules $CODE/gui/public/truncation-rules $CODE/public/truncation-rules

COPY gui/src src

CMD ["yarn", "run", "serve:gui"]

FROM nginx AS server
RUN <<EOF
#!/usr/bin/env sh
set -eu

# Ensure that the nginx-user has a uid >= 1000
# that way, it is not a privileged user, and radix will be happy
deluser "nginx"
adduser \
    --disabled-password \
    --no-create-home \
    --gecos "" \
    --uid 1001 \
    "nginx"

# Create log directory if not present, set permissions
mkdir -p /var/log/nginx
chown -R "nginx:nginx" /var/log/nginx

# Create tmp directory if not present, set permissions
mkdir -p /tmp/nginx
chown -R "nginx:nginx" /tmp/nginx

# Create pidfile, set permissions
touch /var/run/nginx.pid
chown -R "nginx:nginx" /var/run/nginx.pid

# Allow writing to the cache
mkdir -p /var/cache/nginx
chown -R "nginx:nginx" /var/cache/nginx/
chmod -R +w /var/cache/nginx/
EOF

USER 1001
COPY ./nginx/local.nginx /etc/nginx/conf.d/local.conf
