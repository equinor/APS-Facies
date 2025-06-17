# syntax = docker/dockerfile:1
ARG RMS_IMAGE
FROM node:20.19.2-alpine3.22 AS node

ENV CODE=/code
ENV NODE_MODULES=$CODE/node_modules
ENV TRUNCATION_RULES=src/stores/truncation-rules/templates/truncationRules.json

FROM bitnami/nginx:1.27.3-debian-12-r5 AS nginx

FROM ${RMS_IMAGE} AS base
# RMS 12.0 and earlier uses Python 3.6.1, but it is so old that I was unable to update the CA certificates,
# and thus unable to download any packages
ENV XDG_CACHE_HOME=/var/cahce

WORKDIR /code
FROM base AS python
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
    roxenv uv sync --no-install-project

FROM python AS aps
ENV PYTHONPATH=/code

COPY aps/algorithms ./aps/algorithms
COPY aps/toolbox ./aps/toolbox
COPY aps/api ./aps/api
COPY aps/utils ./aps/utils
COPY aps/rms_jobs ./aps/rms_jobs
COPY aps/__init__.py ./aps/


FROM python AS truncation-rules
SHELL ["/bin/bash", "-euo", "pipefail", "-c"]
RUN curl https://mise.run | MISE_INSTALL_PATH=/usr/local/bin/mise sh

COPY --from=aps /code/aps/ aps/

COPY .mise-tasks .mise-tasks/
COPY mise.toml ./
COPY bin/parse-truncation-rule-templates.py ./bin/
COPY examples/truncation_settings.dat ./examples/

ENV MISE_AUTO_INSTALL=false
RUN <<EOF
mise trust
roxenv mise tasks run generate-truncation-rules
EOF

FROM node AS install

# Dependencies for building fibers (Required by vuetify)
RUN apk add \
        python3 \
        make \
        bash \
        g++

WORKDIR $CODE

COPY gui/package.json gui/yarn.lock ./

RUN yarn install

FROM node AS gui

ENV YARN_CACHE_FOLDER=/yarn
RUN yarn config set cache-folder $YARN_CACHE_FOLDER

WORKDIR $CODE
COPY --from=install $NODE_MODULES $NODE_MODULES

COPY gui/package.json .
COPY gui/yarn.lock .

# build / configuration files
COPY gui/tsconfig.json .
COPY gui/eslint.config.cjs .
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
USER 0
RUN rm -f /app/*.html
USER 1001
COPY ./nginx/local.nginx /opt/bitnami/nginx/conf/server_blocks/local.conf
