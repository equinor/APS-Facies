#!make
ifneq ("$(wildcard .env)","")
include .env
export
endif

PROJECT_ID := CF80C9B5-C704-4CAB-A5A6-9B93526C7A13

PROJECT_NAME ?= aps-gui
SHELL := /bin/bash
CURRENT_OS := $(shell uname -s)
EMPTY :=

ifneq ("$(wildcard /.dockerenv)","")
MATPLOTLIB_BACKEND ?= Agg
endif
ifeq ($(CURRENT_OS),Linux)
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

TAR_EXTRACT := $(TAR) -xf
# Mode may be 'production', or 'development'
MODE ?= production
CODE_DIR ?= $(shell pwd)
BIN_DIR := $(CODE_DIR)/bin
PYTHONPATH := $(CODE_DIR):$(PYTHONPATH)
SOURCE_DIR := $(CODE_DIR)/aps
BUILD_DIR := $(CODE_DIR)/build
PYTHON_API_DIR := $(SOURCE_DIR)/api
REMOVE_APS_GUI_TEMP_FOLDER := $(EMPTY)
ifeq ($(MODE),production)
REMOVE_APS_GUI_TEMP_FOLDER := --move
endif

GIT_VERSION  := $(shell git --version)

# Time stamp format YY daynumber_in_year hour minutes
BUILD_NUMBER := $(shell date "+%y%j%H%M")
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


APS_VERSION_FROM_GIT :=  $(shell git describe --abbrev=0 --tags)
APS_VERSION := $(shell echo $(APS_VERSION_FROM_GIT) | $(SED) -e "s/v//g")
APS_FULL_VERSION := $(APS_VERSION).$(BUILD_NUMBER)
LATEST_COMMIT_HASH = $(shell git rev-parse --short HEAD)
LATEST_COMMIT_HASH_LONG = $(shell git rev-parse HEAD)

PLUGIN_NAME := aps_gui
PLUGIN_BIN = $(PLUGIN_NAME).$(APS_FULL_VERSION).plugin
PLUGIN_DIR := $(BUILD_DIR)/$(PLUGIN_NAME)
DEPLOY_VERSION_PATH = $(CODE_DIR)/DEPLOY_VERSION.txt
WEB_DIR := $(CODE_DIR)/gui
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
POETRY := $(shell which poetry)
PYTHON ?= $(POETRY) run python3
RUN := PYTHONPATH=$(PYTHONPATH) $(POETRY) run
PIP ?= $(PYTHON) -m pip
PY.TEST := $(RUN) python -m pytest
PIPROT := $(RUN) piprot
PYLINT := $(RUN) pylint
SAFETY_CHECK := $(POETRY) check
FLASK := $(RUN) flask

VUE_APP_APS_PROTOCOL ?= http
VUE_APP_APS_SERVER := localhost
VUE_APP_APS_API_PORT ?= 5000
VUE_APP_APS_GUI_PORT ?= 8080

ifeq ($(CODESPACES),true)
VUE_APP_API_URL := https://$(CODESPACE_NAME)-$(VUE_APP_APS_API_PORT).preview.app.github.dev/api
VUE_APP_GUI_URL := https://$(CODESPACE_NAME)-$(VUE_APP_APS_GUI_PORT).preview.app.github.dev/
else
VUE_APP_API_URL := $(VUE_APP_APS_PROTOCOL)://$(VUE_APP_APS_SERVER):$(VUE_APP_APS_API_PORT)
VUE_APP_GUI_URL := $(VUE_APP_APS_PROTOCOL)://$(VUE_APP_APS_SERVER):$(VUE_APP_APS_GUI_PORT)
endif

# TODO?: SETUP.PY := PYTHONPATH=$(PYTHONPATH) $(PYTHON) setup.py ?
PYTHON_PREFIX := $(shell dirname $(PYTHON))/..
IMAGE_VERSION ?= $(shell $(BIN_DIR)/find-version-of-docker-image.py $(CODE_DIR))
IMAGE_NAME ?= $(PROJECT_NAME):$(IMAGE_VERSION)
DOCKER_IMAGE := $(DOCKER_REGISTRY)/$(IMAGE_NAME)

UI.PY := $(PYTHON_API_DIR)/ui.py
MAIN.PY := $(PYTHON_API_DIR)/main.py
INFO.XML := $(WEB_DIR)/static/info.xml

MKDIR := mkdir -p

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

DUMMY_FMU_PROJECT_LOCATION ?= $(CODE_DIR)/fmu.model
define LOCAL_SETTINGS_JSON
{
  "projectRootLocation": "$(DUMMY_FMU_PROJECT_LOCATION)"
}
endef
export LOCAL_SETTINGS_JSON


YARN := yarn --cwd $(WEB_DIR)

define STANDARD_DOTENV
STANDARD_RMS_DATA=synthetic-Neslen

#VUE_APP_APP_USE_CORS=yes
VUE_APP_API_URL="$(VUE_APP_API_URL)"
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
.PHONY: help run package.json matplotlibrc dotenv VERSION COMMIT

# Build / clean / run
build: clean-all init

build-stable-gui:
	cat $(CODE_DIR)/CHANGELOG.md | grep $(APS_VERSION) >/dev/null || { \
	    echo "When building a stable version, the changelog MUST have some information of this version ($(APS_VERSION))." ; \
	    exit 1 ; \
	}
	make build-gui VUE_APP_BUILD_MODE=stable

build-gui: clean-build build-front-end compile-files-for-plugin
	cd $(BUILD_DIR) && \
	$(ZIP) $(PLUGIN_BIN) $(PLUGIN_NAME)
	mv $(BUILD_DIR)/$(PLUGIN_BIN) $(CODE_DIR) 2>/dev/null || mv $(BUILD_DIR)/zip.zip $(CODE_DIR)/$(PLUGIN_BIN)
	echo "$(PLUGIN_BIN)" > $(DEPLOY_VERSION_PATH)

compile-files-for-plugin: gather-python-scripts auxillary-files compile-python-files

gather-python-scripts: copy-python-files __init__.py
	cp $(UI.PY) $(PLUGIN_DIR)
	cp $(MAIN.PY) $(PLUGIN_DIR)
	rm -rf $(PLUGIN_DIR)/aps/unit_test \
	       $(PLUGIN_DIR)/aps/api

__init__.py:
	touch $(PLUGIN_DIR)/__init__.py

compile-python-files: compile-pydist remove-extraneous-files

compile-pydist: move-pydist move-python-files-to-pydist

move-python-files-to-pydist:
	mv $(PLUGIN_DIR)/aps $(PLUGIN_DIR)/pydist/aps
	cp $(PLUGIN_DIR)/VERSION $(PLUGIN_DIR)/pydist/aps/toolbox/VERSION

copy-python-files:
	$(PYTHON) $(BIN_DIR)/gather-python-files.py $(CODE_DIR) $(PLUGIN_DIR)
	cp $(BIN_DIR)/generate_workflow_blocks.py $(PLUGIN_DIR)

move-pydist:
	mv $(PLUGIN_DIR)/aps/pydist $(PLUGIN_DIR)

remove-extraneous-files:

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
	$(RUN) python $(CODE_DIR)/bin/parse-truncation-rule-templates.py $(WEB_DIR)/src/store/templates/truncationRules.json

generate-truncation-rule-images: clean-generated-truncation-rules truncation-rule-vislualization-dir
	cd $(TRUNCATION_RULE_VISUALIZATIONS) && \
	printf "r\n$(EXAMPLES_FOLDER)/truncation_settings.dat\nm\na\nq\nq\n" | \
	HIDE_TITLE='yes' \
	DONT_WRITE_OVERVIEW='yes' \
	WRITE_TO_DIRECTORIES='yes' \
	MPLBACKEND=$(MATPLOTLIB_BACKEND) \
	$(RUN) python $(SOURCE_DIR)/algorithms/setupInteractiveTruncationSetting.py

build-dir:
	$(MKDIR) $(BUILD_DIR)

auxillary-files: VERSION COMMIT STUB_VERSION
	cp $(INFO.XML) $(PLUGIN_DIR)

VERSION:
	echo $(APS_FULL_VERSION) > $(PLUGIN_DIR)/VERSION
	echo $(CURRENT_OS)
	echo $(SED)
	echo $(GIT_VERSION)
	echo $(APS_VERSION_FROM_GIT)

COMMIT:
	echo $(LATEST_COMMIT_HASH_LONG) > $(PLUGIN_DIR)/COMMIT

STUB_VERSION:
	cat $(CODE_DIR)/bin/STUB_VERSION > $(PLUGIN_DIR)/STUB_VERSION



mock-VERSION:
	echo $(APS_FULL_VERSION) > $(SOURCE_DIR)/api/VERSION
	ln -sf $(SOURCE_DIR)/api/VERSION $(CODE_DIR)/VERSION

mock-COMMIT:
	echo $(LATEST_COMMIT_HASH_LONG) > $(SOURCE_DIR)/api/COMMIT
	ln -sf $(SOURCE_DIR)/api/COMMIT $(CODE_DIR)/COMMIT

init: dependencies init-workflow package.json local.settings.json dotenv generate-truncation-rules

init-workflow: links generate-workflow-files

local.settings.json: dummy-fmu-location
	echo "$$LOCAL_SETTINGS_JSON" > $(CODE_DIR)/local.settings.json

dummy-fmu-location:
	mkdir -p $(DUMMY_FMU_PROJECT_LOCATION)

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
	ln -sf $(CODE_DIR)/aps/utils/ConvertBitMapToRMS.py $(CODE_DIR)/workflow
	ln -sf $(CODE_DIR)/aps/rms_jobs/bitmap2rms.py $(BIN_DIR)/bitmap2rms_xml.py
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

dependencies: requirements

requirements: matplotlibrc

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

clean-all: clean clean-tests clean-cache

clean-cache: clean-__pycache__ clean-pyc

clean-__pycache__:
	rm -rf $(shell find $(CODE_DIR) -name __pycache__ -not -path *.rms/*)

clean-pyc:
	rm -f $(shell find $(CODE_DIR) -name *.py[cod] -not -path *.rms/*)

docker-image: $(GET_RMS_RESOURCES)
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
	$(POETRY) lock --dev --requirements | $(PIPROT) --outdated -

check-node-dependencies:
	$(YARN) outdated

safety-check:
	$(POETRY) check

check-node-dependencies-for-vulnerabilities:
	$(YARN) run improved-yarn-audit --fail-on-missing-exclutions  --ignore-dev-deps

update-dependencies: update-node-dependencies update-python-dependencies

update-node-dependencies:
	$(YARN) upgrade

update-python-dependencies:
	$(POETRY) update --dev

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

run-tests: python-unit-tests javascript-unit-tests

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
	npx strip-json-comments-cli@1 --no-whitespace $(WEB_DIR)/tsconfig.json > /tmp/tsconfig.json && \
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
	VUE_APP_API_URL=$(VUE_APP_API_URL) \
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
	         --chdir $(CODE_DIR)/aps/api \
	         --bind $(VUE_APP_APS_SERVER):$(VUE_APP_APS_API_PORT) \
	         --timeout 1200 \
	         --graceful-timeout 1200 \
	         --reload \
	         app:app

api-start: run-rms.uipy-mock

run-rms.uipy-mock: matplotlibrc
	FLASK_APP=$(SOURCE_DIR)/api/app.py \
	FLASK_DEBUG=1 \
	APS_MODE='develop' \
	VUE_APP_GUI_URL=$(VUE_APP_GUI_URL) \
	$(RUN) flask \
		--app $(SOURCE_DIR)/api/app.py \
		run \
		--port=$(VUE_APP_APS_API_PORT) \
		--host=$(VUE_APP_APS_SERVER)

# TODO: Add versioning to the plugin file
deploy:
	$(eval $@_PLUGIN := $(shell cat $(DEPLOY_VERSION_PATH) || echo $(PLUGIN_BIN)))
	cd $(CODE_DIR) && \
	rsync -avz \
	      --rsh=ssh \
	      $($@_PLUGIN) $(DEPLOYMENT_USER)@$(DEPLOY_SERVER):$(DEPLOYMENT_PATH)/$($@_PLUGIN)

update-remote-develop:
	$(RGS_EXEC) 'cd $(REMOTE_RGS_DEVELOP) && $(RGS_UPDATE_APS)'

update-remote-master:
	$(RGS_EXEC) 'cd $(REMOTE_RGS_MASTER) && $(RGS_UPDATE_APS)'

# Get the plugin name from the file $(DEPLOY_VERSION_PATH), not from $(PLUGIN_BIN)
deploy-stable: deploy
	$(eval $@_PLUGIN := $(shell cat $(DEPLOY_VERSION_PATH)))
	cd $(CODE_DIR) && \
	ssh $(DEPLOYMENT_USER)@$(DEPLOY_SERVER) ln -s $(DEPLOYMENT_PATH)/$($@_PLUGIN) $(DEPLOYMENT_PATH)/stable/$(PLUGIN_NAME).$(APS_VERSION).plugin

# Getting RMS 11,
get-rms-repo:
	git clone git@git.equinor.com:APS/RMS.git $(RMS_DIR) || git -C $(RMS_DIR) pull

rms-bundle: get-rms-repo
	cd $(RMS_DIR) && \
	CODE_DIR=$(RMS_DIR) \
	make -f $(RMS_DIR)/Makefile bundle


print-%  : ; @echo $($*)
