#!make
ifneq ("$(wildcard .env)","")
include .env
export
endif

SHELL := /bin/bash
CURRENT_OS := $(shell uname -s)

ifeq ($(CURRENT_OS),Linux)
SED := sed
else  # Darwin
SED := gsed
endif

CODE_DIR ?= $(shell pwd)
PYTHONPATH := $(CODE_DIR):$(PYTHONPATH)
SOURCE_DIR := $(CODE_DIR)/aps

APS_VERSION_FROM_GIT =  $(shell git describe --match='v*' --abbrev=0 --tags)
APS_VERSION = $(shell echo $(APS_VERSION_FROM_GIT) | $(SED) -e "s/v//g")
APS_FULL_VERSION = $(APS_VERSION).$(BUILD_NUMBER)
LATEST_COMMIT_HASH_LONG = $(shell git rev-parse HEAD)

COLOR = \033[32;01m
NO_COLOR = \033[0m
.PHONY: help run package.json dotenv VERSION COMMIT STUB_VERSION

mock-VERSION:
	echo $(APS_FULL_VERSION) > $(SOURCE_DIR)/api/VERSION
	ln -sf $(SOURCE_DIR)/api/VERSION $(CODE_DIR)/VERSION

mock-COMMIT:
	echo $(LATEST_COMMIT_HASH_LONG) > $(SOURCE_DIR)/api/COMMIT
	ln -sf $(SOURCE_DIR)/api/COMMIT $(CODE_DIR)/COMMIT

print-%  : ; @echo $($*)
