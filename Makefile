#!make
ifneq ("$(wildcard .env)","")
include .env
export
endif

PROJECT_ID := CF80C9B5-C704-4CAB-A5A6-9B93526C7A13

PROJECT_NAME ?= aps-gui
SHELL := /bin/bash
OS ?= $(shell uname -s)
EMPTY :=

ifeq ($(OS),Linux)
NUMBER_OF_PROCESSORS := $(shell cat /proc/cpuinfo | grep processor | wc -l)
TAR := tar
SED := sed
MATPLOTLIB_BACKEND ?= tkAgg
else  # Darwin
NUMBER_OF_PROCESSORS := $(shell sysctl -n hw.ncpu)
TAR := gtar
SED := gsed
MATPLOTLIB_BACKEND ?= Agg
endif

ifneq ("$(wildcard /.dockerenv)","")
MATPLOTLIB_BACKEND ?= Agg
endif
TAR_EXCRACT := $(TAR) -xf
# Mode may be 'production', or 'development'
MODE ?= production
CODE_DIR ?= $(shell pwd)
BIN_DIR := $(CODE_DIR)/bin
PYTHONPATH := $(CODE_DIR):$(PYTHONPATH)
SOURCE_DIR := $(CODE_DIR)/src
BUILD_DIR := $(CODE_DIR)/build
PYTHON_API_DIR := $(SOURCE_DIR)/api
REMOVE_APS_GUI_TEMP_FOLDER := $(EMPTY)
ifeq ($(MODE),production)
REMOVE_APS_GUI_TEMP_FOLDER := --move
endif

BUILD_NUMBERE_TRACKER := https://version-bot.herokuapp.com/v1/versions?identifier=$(PROJECT_ID)
BUILD_NUMBER = $(shell curl --silent -X GET $(BUILD_NUMBERE_TRACKER) | $(SED) -r 's/.*"?build"?: ?([0-9]+).*/\1/g')

ROXENV := roxenv
HAS_ROXENV := $(shell command -v $(ROXENV) 2>/dev/null)
ZIP := $(ROXENV) --zip
ifndef HAS_ROXENV
ZIP := zip --recurse-paths $(REMOVE_APS_GUI_TEMP_FOLDER) -9
ROXENV := $(EMPTY)
endif

ALLWAYS_INSTALL_WEB_DEPENDENCIES ?= yes
PACKAGE.JSON := $(EMPTY)
ifeq ($(ALLWAYS_INSTALL_WEB_DEPENDENCIES),yes)
PACKAGE.JSON := package.json
endif

RMS_DIR := $(CODE_DIR)/.rms
RMS_PROJECT ?= $(RMS_DIR)/testAPSWorkflow_new.rms11.0.0
WORKFLOWS_TO_PROJECT := $(EMPTY)
CREATE_WORKFLOW_DIR := create-workflow-dir
WRITE_WORKFLOW_FILES_TO_PROJECT ?= no
ifeq ($(WRITE_WORKFLOW_FILES_TO_PROJECT),yes)
WORKFLOWS_TO_PROJECT := --copy-to-rms-project $(RMS_PROJECT)
USE_TEMORARY_DIR ?= no
ifeq ($(USE_TEMORARY_DIR),yes)
WORKFLOWS_TO_PROJECT := --use-temporary-workflow-dir $(WORKFLOWS_TO_PROJECT)
CREATE_WORKFLOW_DIR := $(EMPTY)
endif
endif
STUB_SUFFIX ?= $(EMPTY)
ifneq ($(STUB_PREFIX),$(EMPTY))
WORKFLOWS_TO_PROJECT := --suffix $(STUB_SUFFIX) $(WORKFLOWS_TO_PROJECT)
endif

ALLWAYS_GET_RMS_RESOURCES ?= no
GET_RMS_RESOURCES := $(EMPTY)
ifeq ($(ALLWAYS_GET_RMS_RESOURCES),yes)
GET_RMS_RESOURCES := get-rms get-rms-project
endif

APS_VERSION := $(shell echo $(shell git describe --abbrev=0 --tags) | $(SED) -e "s/v//g")
APS_FULL_VERSION = $(APS_VERSION).$(BUILD_NUMBER)
LATEST_COMMIT_HASH := $(shell git rev-parse --short HEAD)
LATEST_COMMIT_HASH_LONG := $(shell git rev-parse HEAD)

PLUGIN_NAME := aps_gui
PLUGIN_BIN = $(PLUGIN_NAME).$(APS_FULL_VERSION).plugin
PLUGIN_DIR := $(BUILD_DIR)/$(PLUGIN_NAME)
WEB_DIR := $(SOURCE_DIR)/gui
TRUNCATION_RULE_VISUALIZATIONS := $(WEB_DIR)/public/truncation-rules
LIB_PREFIX := $(CODE_DIR)/libraries
LIB_SOURCE := $(LIB_PREFIX)/sources
EXAMPLES_FOLDER := $(CODE_DIR)/examples
TEST_FOLDER := $(SOURCE_DIR)/unit_test
INTEGRATION_TESTS := $(TEST_FOLDER)/integration
AUXILLARY := $(CODE_DIR)/auxillary
DOCKERFILE := $(CODE_DIR)/Dockerfile
DOCKER_REGISTRY_SERVER := registry.git.equinor.com
DOCKER_REGISTRY := $(DOCKER_REGISTRY_SERVER)/aps/gui
# Paths local to the compiled app
REQUESTS_CA_BUNDLE ?= $(SSL_CERT_FILE)
PYTHON ?= $(shell which python)
PIPENV := $(PYTHON) -m pipenv
RUN := PYTHONPATH=$(PYTHONPATH) $(PIPENV) run
PIP ?= $(PYTHON) -m pip
PY.TEST := $(RUN) python -m pytest
PIPROT := $(RUN) piprot
PYLINT := $(RUN) pylint
SAFETY_CHECK := $(PIPENV) check
FLASK := $(RUN) flask

VUE_APP_APS_PROTOCOL := http
VUE_APP_APS_SERVER := localhost
VUE_APP_APS_API_PORT ?= 5000
VUE_APP_APS_GUI_PORT ?= 8080

# TODO?: SETUP.PY := PYTHONPATH=$(PYTHONPATH) $(PYTHON) setup.py ?
PYTHON_PREFIX := $(shell dirname $(PYTHON))/..
IMAGE_VERSION ?= $(shell $(BIN_DIR)/find-version-of-docker-image.py $(CODE_DIR))
IMAGE_NAME ?= $(PROJECT_NAME):$(IMAGE_VERSION)
DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(IMAGE_NAME)

UI.PY := $(PYTHON_API_DIR)/ui.py
MAIN.PY := $(PYTHON_API_DIR)/main.py
INFO.XML := $(WEB_DIR)/static/info.xml

MKDIR := mkdir -p
REPLACE_SRC_BY_PYTHON_LOCATION := $(SED) -i -E 's/^( *from )src/\1aps/g'

DEPLOYMENT_USER := cicd_aps
DEPLOYMENT_PATH := /project/res/APSGUI/releases
DEPLOY_SERVER ?= tr-linrgsn019.tr.statoil.no

REMOTE_RGS_DEVELOP := /project/res/APSGUI/DevelopmentBranch/APSGUI
REMOTE_RGS_MASTER := /project/res/APSGUI/MasterBranch

RGS_EXEC := ssh $(DEPLOYMENT_USER)@$(DEPLOY_SERVER)
RMS_VERSION := $(shell cat $(CODE_DIR)/Dockerfile | grep RMS_VERSION= | $(SED) -E 's/.*=([0-9]+\.[0-9]+\.[0-9]+).*/\1/g')
RGS_UPDATE_APS := git pull \
 && rm -rf workflow \
 && mkdir -p workflow/pythoncomp/ \
 && touch workflow/.master \
 && USE_TEMORARY_DIR=no \
 APS_PROJECT_DIR=$(pwd) \
 ./bin/initialize-project.sh workflow/ \
 && mv workflow/pythoncomp/* workflow \
 && rm -rf workflow/pythoncomp \
           workflow/.master \
           aps_workflows


# NRlib
BUILD_NRLIB ?= no
NRLIB := $(EMPTY)
TEST_NRLIB := $(EMPTY)
ifeq ($(BUILD_NRLIB),yes)
NRLIB := install-nrlib
TEST_NRLIB := test-nrlib
endif
NRLIB_PATH := $(LIB_SOURCE)/nrlib
NRLIB_VERSION ?= 1.1-r7

YARN := yarn --cwd $(WEB_DIR)

define STANDARD_DOTENV
STANDARD_RMS_DATA=synthetic-Neslen

#VUE_APP_APP_USE_CORS=yes
#VUE_APP_APS_PROTOCOL=http
VUE_APP_APS_SERVER=127.0.0.1
VUE_APP_APS_HOST_SERVER=127.0.0.1
VUE_APP_APS_API_PORT=5000
VUE_APP_APS_GUI_PORT=8080
endef
export STANDARD_DOTENV

define MATPLOTLIBRC
backend             : $(MATPLOTLIB_BACKEND)
savefig.facecolor   : white
savefig.transparent : False
endef
export MATPLOTLIBRC

SYSTEM_INSTALL_PIPENV ?= no
USER_INSTALL_PIPENV := $(EMPTY)
ifeq ($(SYSTEM_INSTALL_PIPENV),no)
USER_INSTALL_PIPENV := --user
endif

COLOR = \033[32;01m
NO_COLOR = \033[0m
.PHONY: help run package.json matplotlibrc dotenv

# Build / clean / run
build: clean-all init

build-stable-gui:
	cat $(CODE_DIR)/CHANGELOG.md | grep $(APS_VERSION) >/dev/null || { \
	    echo "When building a stable version, the changelog MUST have some information of this version ($(APS_VERSION))." ; \
	    exit 1 ; \
	}
	make build-gui VUE_APP_BUILD_MODE=stable

build-gui: clean-build increase-build-number build-front-end compile-files-for-plugin
	cd $(BUILD_DIR) && \
	$(ZIP) $(PLUGIN_BIN) $(PLUGIN_NAME)
	mv $(BUILD_DIR)/$(PLUGIN_BIN) $(CODE_DIR) 2>/dev/null || mv $(BUILD_DIR)/zip.zip $(CODE_DIR)/$(PLUGIN_BIN)

compile-files-for-plugin: gather-python-scripts auxillary-files compile-python-files

gather-python-scripts: copy-python-files __init__.py
	cp $(UI.PY) $(PLUGIN_DIR)
	cp $(MAIN.PY) $(PLUGIN_DIR)
	rm -rf $(PLUGIN_DIR)/src/unit_test \
	       $(PLUGIN_DIR)/src/api

__init__.py:
	touch $(PLUGIN_DIR)/__init__.py

compile-python-files: compile-pydist remove-extraneous-files

increase-build-number:
	curl --silent -X POST $(BUILD_NUMBERE_TRACKER) > /dev/null

compile-pydist: move-pydist move-python-files-to-pydist
	$(REPLACE_SRC_BY_PYTHON_LOCATION) $(shell find $(PLUGIN_DIR) -name '*.py')

move-python-files-to-pydist:
	mv $(PLUGIN_DIR)/src $(PLUGIN_DIR)/pydist/aps

copy-python-files:
	$(PYTHON) $(BIN_DIR)/gather-python-files.py $(CODE_DIR) $(PLUGIN_DIR)

move-pydist:
	mv $(PLUGIN_DIR)/src/pydist $(PLUGIN_DIR)

remove-extraneous-files: remove-node_modules-stubs

remove-node_modules-stubs:
	rm -rf $(PLUGIN_DIR)/pydist/aps/gui/node_modules
	rmdir $(PLUGIN_DIR)/pydist/aps/gui

clean-build: clean-plugin clean-links clean-build-dir

clean-build-dir:
	rm -rf $(BUILD_DIR)

clean-plugin:
	rm -rf $(PLUGIN_DIR) \
	       $(PLUGIN_DIR).plugin \
	       $(PLUGIN_DIR).*.plugin

build-front-end: $(PACKAGE.JSON) build-dir generate-truncation-rules _build-front-end copy-changelog.md

_build-front-end:
	VUE_APP_APS_VERSION="$(APS_VERSION)" \
	VUE_APP_BUILD_NUMBER="$(BUILD_NUMBER)" \
	VUE_APP_HASH="$(LATEST_COMMIT_HASH)" \
	$(YARN) build && \
	mv $(WEB_DIR)/dist $(PLUGIN_DIR)

copy-changelog.md:
	cp $(CODE_DIR)/CHANGELOG.md $(PLUGIN_DIR)/CHANGELOG.md

truncation-rule-vislualization-dir: relink-matplotlibrc
	$(MKDIR) $(TRUNCATION_RULE_VISUALIZATIONS)
	ln -sf $(CODE_DIR)/matplotlibrc $(TRUNCATION_RULE_VISUALIZATIONS)/matplotlibrc

clean-generated-truncation-rules:
	rm -rf $(TRUNCATION_RULE_VISUALIZATIONS)
	rm -f  $(WEB_DIR)/src/store/templates/truncationRules.json

generate-truncation-rules: generate-truncation-rule-images
	$(PYTHON) $(CODE_DIR)/bin/parse-truncation-rule-templates.py > $(WEB_DIR)/src/store/templates/truncationRules.json

generate-truncation-rule-images: clean-generated-truncation-rules truncation-rule-vislualization-dir
	cd $(TRUNCATION_RULE_VISUALIZATIONS) && \
	printf "r\n$(EXAMPLES_FOLDER)/truncation_settings.dat\nm\na\nq\nq\n" | \
	HIDE_TITLE='yes' \
	DONT_RITE_OVERVIEW='yes' \
	WRITE_TO_DIRECTORIES='yes' \
	MPLBACKEND=$(MATPLOTLIB_BACKEND) \
	$(PYTHON) $(SOURCE_DIR)/algorithms/setupInteractiveTruncationSetting.py

build-dir:
	$(MKDIR) $(BUILD_DIR)

auxillary-files: VERSION COMMIT
	cp $(INFO.XML) $(PLUGIN_DIR)

VERSION:
	echo $(APS_FULL_VERSION) > $(PLUGIN_DIR)/VERSION

COMMIT:
	echo $(LATEST_COMMIT_HASH_LONG) > $(PLUGIN_DIR)/COMMIT

init: initialize-python-environment dependencies init-workflow package.json dotenv generate-truncation-rules

init-workflow: links generate-workflow-files

dotenv:
	[ -f "$(CODE_DIR)/.env" ] \
	|| { \
		echo "$$STANDARD_DOTENV" > $(CODE_DIR)/.env ; \
	}
	ln -sf $(CODE_DIR)/.env $(WEB_DIR)/.env


links: clean-links create-workflow-dir matplotlibrc-links changelog-link
	ln -sf $(CODE_DIR)/depricated/APS_make_gauss_IPL.py $(BIN_DIR)
	ln -sf $(CODE_DIR)/depricated/APSGaussFieldJobs.py $(SOURCE_DIR)/algorithms
	ln -sf $(CODE_DIR)/depricated/APSupdateVarioAsimuth.py $(SOURCE_DIR)/utils
	ln -sf $(CODE_DIR)/depricated/getRMSProjectData.py $(SOURCE_DIR)/utils/roxar
	ln -sf $(CODE_DIR)/depricated/DefineTruncStructure.py $(CODE_DIR)/examples
	ln -sf $(CODE_DIR)/depricated/to_be_deleted/APS_simulate_gauss_multiprocessing.ipl $(CODE_DIR)/workflow
	ln -sf $(CODE_DIR)/depricated/to_be_deleted/Cleanup_tmpdir.ipl $(CODE_DIR)/workflow
	ln -sf $(CODE_DIR)/workflow/APS_simulate_gauss_multiprocessing.py $(BIN_DIR)
	ln -sf $(CODE_DIR)/workflow/APS_simulate_gauss_singleprocessing.py $(BIN_DIR)
	ln -sf $(CODE_DIR)/src/utils/ConvertBitMapToRMS.py $(CODE_DIR)/workflow
	ln -sf $(CODE_DIR)/src/rms_jobs/bitmap2rms.py $(BIN_DIR)/bitmap2rms_xml.py
	ln -sf $(CODE_DIR)/.env $(WEB_DIR)/.env

changelog-link:
	ln -sf $(CODE_DIR)/CHANGELOG.md $(WEB_DIR)/public/CHANGELOG.md

create-workflow-dir:
	$(MKDIR) $(CODE_DIR)/workflow

clean-links: clean-matplotlibrc clean-changelog-link
	rm -f $(BIN_DIR)/APS_make_gauss_IPL.py
	rm -f $(SOURCE_DIR)/algorithms/APSGaussFieldJobs.py
	rm -f $(SOURCE_DIR)/utils/APSupdateVarioAsimuth.py
	rm -f $(SOURCE_DIR)/utils/roxar/getRMSProjectData.py
	rm -f $(CODE_DIR)/examples/DefineTruncStructure.py
	rm -f $(CODE_DIR)/workflow/APS_simulate_gauss_multiprocessing.ipl
	rm -f $(CODE_DIR)/workflow/Cleanup_tmpdir.ipl
	rm -f $(BIN_DIR)/APS_simulate_gauss_multiprocessing.py
	rm -f $(BIN_DIR)/APS_simulate_gauss_singleprocessing.py
	rm -f $(CODE_DIR)/workflow/ConvertBitMapToRMS.py
	rm -f $(BIN_DIR)/bitmap2rms_xml.py

clean-changelog-link:
	rm -f $(WEB_DIR)/public/CHANGELOG.md

generate-workflow-files: $(CREATE_WORKFLOW_DIR)
	$(PYTHON) $(BIN_DIR)/generate_workflow_blocks.py $(CODE_DIR) $(WORKFLOWS_TO_PROJECT)

dependencies: nrlib requirements $(TEST_NRLIB)

nrlib: $(NRLIB)

install-nrlib: build-nrlib
	cd $(CODE_DIR) && \
	$(PIPENV) install $(NRLIB_PATH) && \
	git checkout -- $(CODE_DIR)/Pipfile $(CODE_DIR)/Pipfile.lock

build-nrlib: get-nrlib
	cd $(NRLIB_PATH) && \
	CODE_DIR=$(NRLIB_PATH) \
	make build-boost-python

test-nrlib:
	$(PY.TEST) $(NRLIB_PATH)/tests

get-nrlib:
	$(MKDIR) $(NRLIB_PATH)
	[ -d $(NRLIB_PATH) ] && { \
	    echo "NRlib has been downloaded. Updating" ; \
	    cd $(NRLIB_PATH) ; \
	    git fetch ; \
	    git checkout v$(NRLIB_VERSION) ; \
	} || { \
	    echo "Fetching NRlib" ;\
	    git clone git@git.equinor.com:/sdp/nrlib.git \
	        $(NRLIB_PATH) ; \
	    git checkout v$(NRLIB_VERSION) ; \
	}

initialize-python-environment: install-pipenv
	cd $(CODE_DIR) && \
	{ $(PIPENV) --venv || $(PIPENV) --python=$(PYTHON) --site-packages ; }

install-pipenv:
	type pipenv >/dev/null || $(PIPENV) >/dev/null || { $(PIP) install $(USER_INSTALL_PIPENV) pipenv ; }

requirements: matplotlibrc
	cd $(CODE_DIR) && \
	$(PIPENV) install --dev --keep-outdated

relink-matplotlibrc: clean-matplotlibrc matplotlibrc matplotlibrc-links

matplotlibrc:
	echo "$$MATPLOTLIBRC" > $(CODE_DIR)/matplotlibrc

clean-matplotlibrc:
	rm -f $(CODE_DIR)/matplotlibrc \
	      $(TEST_FOLDER)/matplotlibrc \
	      $(INTEGRATION_TESTS)/matplotlibrc

matplotlibrc-links: matplotlibrc
	# Matplotlibrc (Force use of Agg in tests)
	ln -sf $(CODE_DIR)/matplotlibrc $(TEST_FOLDER)/matplotlibrc
	ln -sf $(CODE_DIR)/matplotlibrc $(INTEGRATION_TESTS)/matplotlibrc

clean: clean-links clean-workflow-blocks
	rm -rf $(BUILD_DIR)
	rm -f $(CODE_DIR)/build.txt

clean-workflow-blocks:
	rm -rf $(CODE_DIR)/workflow

clean-all: clean clean-tests clean-cache clean-nrlib

clean-nrlib: uninstall-nrlib remove-nrlib-source

remove-nrlib-source:
	rm -rf $(NRLIB_PATH)
	rm -f nrlib-$(NRLIB_VERSION).tar.gz

uninstall-nrlib:
	$(PIPENV) uninstall nrlib 2>/dev/null || echo "NRlib not installed"

clean-cache: clean-__pycache__ clean-pyc

clean-__pycache__:
	rm -rf $(shell find $(CODE_DIR) -name __pycache__ -not -path *.rms/*)

clean-pyc:
	rm -f $(shell find $(CODE_DIR) -name *.py[cod] -not -path *.rms/*)

docker-image: $(GET_RMS_RESOURCES) get-nrlib
	docker build --rm --pull --tag $(DOCKER_IMAGE) --file $(DOCKERFILE) $(CODE_DIR)

docker-login:
	docker login $(DOCKER_REGISTRY_SERVER)
	# TODO: Add new user / bot to gitlab

docker-push-image: docker-image
	docker push $(DOCKER_IMAGE)

copy-source:
	cd $(CODE_DIR)
	$(TAR) --exclude-vcs-ignore \
	    -cvzf code.tar.gz .

docker-bash:
	docker run --rm -it -v $(CODE_DIR):/code --workdir=/code $(DOCKER_IMAGE) bash

check-requirements:
	$(PIPENV) lock --dev --requirements | $(PIPROT) --outdated -

check-node-dependencies:
	$(YARN) outdated

safety-check:
	$(PIPENV) check

update-dependencies: update-node-dependencies update-python-dependencies

update-node-dependencies:
	$(YARN) upgrade

update-python-dependencies:
	$(PIPENV) update --dev

integration-tests: clean-integration init-workflow links link-example-files
	MATPLOTLIB_BACKEND="Agg" \
	make clean-matplotlibrc matplotlibrc-links
	cd $(INTEGRATION_TESTS) && \
	RMS_PROJECT="$(RMS_PROJECT)" \
	APS_RESOURCES="$(INTEGRATION_TESTS)" \
	APS_ROOT="$(CODE_DIR)" \
	./test_workflows_in_rms11.sh

clean-integration: clean-workflow-blocks clean-example-link clean-matplotlibrc
	cd $(INTEGRATION_TESTS) && \
	rm -f examples \
	      matplotlibrc && \
	rm -f *.log \
	      *.html \
	      *.xml \
	      *.irap \
	      *.roff \
	      *.dat

link-example-files: clean-example-link
	ln -s $(EXAMPLES_FOLDER) $(INTEGRATION_TESTS)/examples

clean-example-link:
	rm -f $(INTEGRATION_TESTS)/examples

unit-tests: clean-tests run-tests clean-tests

run-tests: init-mock-project python-unit-tests javascript-unit-tests

python-unit-tests:
	cd $(TEST_FOLDER) && \
	PYTHONPATH=$(PYTHONPATH) \
	$(PY.TEST) --import-mode=importlib

javascript-unit-tests:
	$(YARN) test:unit

clean-tests: clean-integration
	cd $(TEST_FOLDER) && \
	rm -rf .cache && \
	rm -f  *.dat \
	       *.xml \
	       *.png \
	       fmu_attributes.yaml \
	       fmu_attributes.txt

find-circular-dependencies:
	cd $(WEB_DIR) && \
	npx strip-json-comments-cli --no-whitespace $(WEB_DIR)/tsconfig.json > /tmp/tsconfig.json && \
	npx madge --circular \
	          --warning \
	          --ts-config /tmp/tsconfig.json \
	          --webpack-config $(WEB_DIR)/node_modules/@vue/cli-service/webpack.config.js \
	          --extensions js,ts \
	          $(WEB_DIR)/src

linting: run-python-linting javascript-linting

python-linting: clean-links run-python-linting links

run-python-linting:
	$(PYLINT) --jobs=$(NUMBER_OF_PROCESSORS) $(SOURCE_DIR) $(CODE_DIR)/depricated $(BIN_DIR)

javascript-linting:
	$(YARN) lint

web-start: $(PACKAGE.JSON)
	$(YARN) serve:gui --port=$(VUE_APP_APS_GUI_PORT) \
	                  --host=$(VUE_APP_APS_SERVER)

web-e2e:
	$(YARN) test:e2e

web-test:
	$(YARN) test:unit

web-lint:
	$(YARN) lint

web-build:
	$(YARN) build

web-install-dev: $(PACKAGE.JSON)

package.json:
	$(YARN) install --dev --frozen-lockfile


run-api-gunicorn:
	gunicorn --workers 8 \
	         --chdir $(CODE_DIR)/src/api \
	         --bind $(VUE_APP_APS_SERVER):$(VUE_APP_APS_API_PORT) \
	         --timeout 1200 \
	         --graceful-timeout 1200 \
	         --reload \
	         app:app

run-rms.uipy-mock: matplotlibrc
	FLASK_APP=$(SOURCE_DIR)/api/app.py \
	FLASK_ENV=development \
	APS_MODE='develop' \
	$(FLASK) run --port=$(VUE_APP_APS_API_PORT) \
	             --host=$(VUE_APP_APS_SERVER)

# TODO: Add versioning to the plugin file
deploy:
	cd $(CODE_DIR) && \
	rsync -avz \
	      --rsh=ssh \
	      $(PLUGIN_BIN) $(DEPLOYMENT_USER)@$(DEPLOY_SERVER):$(DEPLOYMENT_PATH)/$(PLUGIN_BIN)

update-remote-develop:
	$(RGS_EXEC) 'cd $(REMOTE_RGS_DEVELOP) && $(RGS_UPDATE_APS)'

update-remote-master:
	$(RGS_EXEC) 'cd $(REMOTE_RGS_MASTER) && $(RGS_UPDATE_APS)'

deploy-stable: deploy
	cd $(CODE_DIR) && \
	ssh $(DEPLOYMENT_USER)@$(DEPLOY_SERVER) ln -s $(DEPLOYMENT_PATH)/$(PLUGIN_BIN) $(DEPLOYMENT_PATH)/stable/$(PLUGIN_NAME).$(APS_VERSION).plugin

# Getting RMS 11,
get-rms-repo:
	git clone git@git.equinor.com:APS/RMS.git $(RMS_DIR) || git -C $(RMS_DIR) pull

rms-bundle: get-rms-repo
	cd $(RMS_DIR) && \
	CODE_DIR=$(RMS_DIR) \
	make -f $(RMS_DIR)/Makefile bundle


print-%  : ; @echo $($*)
