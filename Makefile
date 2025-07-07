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

ifeq ($(CURRENT_OS),Linux)
TAR := tar
SED := sed
else  # Darwin
TAR := gtar
SED := gsed
endif

# Mode may be 'production', or 'development'
MODE ?= production
CODE_DIR ?= $(shell pwd)
BIN_DIR := $(CODE_DIR)/bin
PYTHONPATH := $(CODE_DIR):$(PYTHONPATH)
SOURCE_DIR := $(CODE_DIR)/aps
REMOVE_APS_GUI_TEMP_FOLDER := $(EMPTY)
ifeq ($(MODE),production)
REMOVE_APS_GUI_TEMP_FOLDER := --move
endif

GIT_VERSION  = "$(shell git --version)"

# Time stamp format YY daynumber_in_year hour minutes
BUILD_NUMBER := $(shell date "+%y%j%H%M")

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

APS_VERSION_FROM_GIT =  $(shell git describe --match='v*' --abbrev=0 --tags)
APS_VERSION = $(shell echo $(APS_VERSION_FROM_GIT) | $(SED) -e "s/v//g")
APS_FULL_VERSION = $(APS_VERSION).$(BUILD_NUMBER)
LATEST_COMMIT_HASH_LONG = $(shell git rev-parse HEAD)

WEB_DIR := $(CODE_DIR)/gui
EXAMPLES_FOLDER := $(CODE_DIR)/examples
TEST_FOLDER := $(SOURCE_DIR)/tests
AUXILLARY := $(CODE_DIR)/auxillary
# Paths local to the compiled app
RUN := PYTHONPATH=$(PYTHONPATH) uv run
PYTHON ?= $(RUN) python3
PIP ?= $(PYTHON) -m pip
PY.TEST := $(RUN) python -m pytest

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

YARN := yarn --cwd $(WEB_DIR)

COLOR = \033[32;01m
NO_COLOR = \033[0m
.PHONY: help run package.json dotenv VERSION COMMIT STUB_VERSION

# Build / clean / run
build: clean-all

mock-VERSION:
	echo $(APS_FULL_VERSION) > $(SOURCE_DIR)/api/VERSION
	ln -sf $(SOURCE_DIR)/api/VERSION $(CODE_DIR)/VERSION

mock-COMMIT:
	echo $(LATEST_COMMIT_HASH_LONG) > $(SOURCE_DIR)/api/COMMIT
	ln -sf $(SOURCE_DIR)/api/COMMIT $(CODE_DIR)/COMMIT

mock-STUB_VERSION:
	cat $(CODE_DIR)/bin/STUB_VERSION > $(SOURCE_DIR)/api/STUB_VERSION
	ln -sf $(SOURCE_DIR)/api/STUB_VERSION $(CODE_DIR)/STUB_VERSION

links: clean-links create-workflow-dir changelog-link
	ln -sf $(CODE_DIR)/workflow/APS_simulate_gauss_singleprocessing.py $(BIN_DIR)
	ln -sf $(CODE_DIR)/aps/utils/ConvertBitMapToRMS.py $(CODE_DIR)/workflow
	ln -sf $(CODE_DIR)/aps/rms_jobs/bitmap2rms.py $(BIN_DIR)/bitmap2rms_xml.py
	ln -sf $(CODE_DIR)/.env $(WEB_DIR)/.env

changelog-link:
	ln -sf $(WEB_DIR)/public/CHANGELOG.md $(CODE_DIR)/CHANGELOG.md

create-workflow-dir:
	$(MKDIR) $(CODE_DIR)/workflow

clean-links: clean-changelog-link
	rm -f $(SOURCE_DIR)/utils/APSupdateVarioAsimuth.py
	rm -f $(SOURCE_DIR)/utils/roxar/getRMSProjectData.py
	rm -f $(CODE_DIR)/examples/DefineTruncStructure.py
	rm -f $(BIN_DIR)/APS_simulate_gauss_singleprocessing.py
	rm -f $(CODE_DIR)/workflow/ConvertBitMapToRMS.py
	rm -f $(BIN_DIR)/bitmap2rms_xml.py

clean-changelog-link:
	rm -f $(CODE_DIR)/CHANGELOG.md

generate-workflow-files: $(CREATE_WORKFLOW_DIR)
	$(PYTHON) $(BIN_DIR)/generate_workflow_blocks.py $(CODE_DIR) $(WORKFLOWS_TO_PROJECT)

clean: clean-links clean-workflow-blocks
	rm -f $(CODE_DIR)/build.txt

clean-workflow-blocks:
	rm -rf $(CODE_DIR)/workflow

clean-all: clean clean-tests clean-cache

clean-cache: clean-__pycache__ clean-pyc

clean-__pycache__:
	rm -rf $(shell find $(CODE_DIR) -name __pycache__ -not -path *.rms/*)

clean-pyc:
	rm -f $(shell find $(CODE_DIR) -name *.py[cod] -not -path *.rms/*)

update-dependencies: update-node-dependencies

update-node-dependencies:
	$(YARN) upgrade

unit-tests: clean-tests run-tests clean-tests

run-tests: python-unit-tests

python-unit-tests:
	cd $(TEST_FOLDER) && \
	PYTHONPATH=$(PYTHONPATH) \
	$(PY.TEST) --import-mode=importlib

clean-tests:
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

package.json:
	$(YARN) install --dev --frozen-lockfile

print-%  : ; @echo $($*)
