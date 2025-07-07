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
SED := sed
else  # Darwin
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

APS_VERSION_FROM_GIT =  $(shell git describe --match='v*' --abbrev=0 --tags)
APS_VERSION = $(shell echo $(APS_VERSION_FROM_GIT) | $(SED) -e "s/v//g")
APS_FULL_VERSION = $(APS_VERSION).$(BUILD_NUMBER)
LATEST_COMMIT_HASH_LONG = $(shell git rev-parse HEAD)

WEB_DIR := $(CODE_DIR)/gui
# Paths local to the compiled app
RUN := PYTHONPATH=$(PYTHONPATH) uv run
PYTHON ?= $(RUN) python3

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

clean: clean-links
	rm -f $(CODE_DIR)/build.txt

clean-all: clean clean-cache

clean-cache: clean-__pycache__ clean-pyc

clean-__pycache__:
	rm -rf $(shell find $(CODE_DIR) -name __pycache__ -not -path *.rms/*)

clean-pyc:
	rm -f $(shell find $(CODE_DIR) -name *.py[cod] -not -path *.rms/*)

print-%  : ; @echo $($*)
