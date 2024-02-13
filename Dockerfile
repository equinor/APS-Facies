# syntax = docker/dockerfile:1.3
FROM node:20.11.0-alpine3.18 AS node

ENV CODE=/code
ENV NODE_MODULES=$CODE/node_modules
ENV TRUNCATION_RULES=src/store/templates/truncationRules.json

FROM bitnami/nginx:1.25.2-debian-11-r46 AS nginx
FROM --platform=amd64 python:3.8.18-slim-bookworm AS python
# RMS 12.0 and earlier uses Python 3.6.1, but it is so old that I was unable to update the CA certificates,
# and thus unable to download poetry


WORKDIR /code
ENV PATH="/root/.local/bin:$PATH"

RUN --mount=type=cache,target=/var/cache/apt --mount=type=cache,target=/var/lib/apt \
    apt-get update -y && \
    apt-get install -y \
        curl \
        ca-certificates \
    && \
    curl -sSL https://install.python-poetry.org | python3 - --version=1.6.1 && \
    apt-get remove -y --purge curl && \
    apt autoremove -y


COPY pyproject.toml poetry.lock ./
RUN poetry install

FROM python AS aps

COPY aps/algorithms ./aps/algorithms
COPY aps/toolbox ./aps/toolbox
COPY aps/api ./aps/api
COPY aps/utils ./aps/utils
COPY aps/rms_jobs ./aps/rms_jobs
COPY aps/__init__.py ./aps/

COPY libraries/rms-mock/_roxar ./_roxar
COPY libraries/rms-mock/roxar ./roxar

CMD ["poetry", "run", "flask", "--app", "aps/api/app.py", "run", "--host", "0.0.0.0"]


FROM python AS truncation-rules
RUN apt-get update -y && \
    apt-get install -y make

COPY --from=aps /code/aps/ aps/

COPY bin/parse-truncation-rule-templates.py ./bin/
COPY examples/truncation_settings.dat ./examples/
COPY Makefile .

RUN mkdir -p \
    aps/unit_test/integration \
    gui/src/store/templates
RUN make generate-truncation-rules

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
COPY gui/babel.config.js .
COPY gui/vue.config.js .

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
