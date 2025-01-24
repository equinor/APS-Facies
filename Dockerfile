# syntax = docker/dockerfile:1
ARG RMS_IMAGE
FROM node:20.18.1-alpine3.21 AS node

ENV CODE=/code
ENV NODE_MODULES=$CODE/node_modules
ENV TRUNCATION_RULES=src/stores/truncation-rules/templates/truncationRules.json

FROM bitnami/nginx:1.27.3-debian-12-r5 AS nginx

FROM ${RMS_IMAGE} AS python
# RMS 12.0 and earlier uses Python 3.6.1, but it is so old that I was unable to update the CA certificates,
# and thus unable to download poetry

ENV POETRY_VERSION=1.6.1

WORKDIR /code
ENV PATH="/root/.local/bin:$PATH"

RUN roxenv pip install --user "poetry==$POETRY_VERSION"

# This will overwrite RMS' installed packages in favor of those specified by us
RUN roxenv poetry config virtualenvs.create false --local

# Ensure site-packages, such as roxar / rmsapi are available to us
RUN roxenv poetry config virtualenvs.options.system-site-packages true
COPY pyproject.toml poetry.lock ./
RUN roxenv poetry install

FROM python AS aps
ENV PYTHONPATH=/code

COPY aps/algorithms ./aps/algorithms
COPY aps/toolbox ./aps/toolbox
COPY aps/api ./aps/api
COPY aps/utils ./aps/utils
COPY aps/rms_jobs ./aps/rms_jobs
COPY aps/__init__.py ./aps/


FROM python AS truncation-rules
RUN <<EOF
#!/usr/bin/env bash

OS_ID="$(grep '^ID=' /etc/os-release | tr -d 'ID=' | tr -d '"')"
if [[ $OS_ID == 'debian' ]]; then
  install() {
    apt-get update -y
    apt-get install -y $@
  }
elif [[ $OS_ID == 'centos' ]]; then
  install() {
    yum update -y
    yum install -y $@
  }
elif [[ $OS_ID == 'rhel' ]]; then
  install () {
    dnf update -y
    dnf install -y $@
  }
else
  echo "Unsupported OS ($OS_ID)" >/dev/stderr
  exit 1
fi
install make
EOF

COPY --from=aps /code/aps/ aps/

COPY bin/parse-truncation-rule-templates.py ./bin/
COPY examples/truncation_settings.dat ./examples/
COPY Makefile .

RUN mkdir -p \
    aps/unit_test/integration \
    gui/src/stores/truncation-rules/templates
RUN roxenv make generate-truncation-rules

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
COPY gui/.eslintrc.js .
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
