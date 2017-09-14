PROJECT_NAME ?= aps-gui
SHELL := /bin/bash
LOG_DIR = logs
# Valid options: TRACE, DEBUG, INFO (default), WARN, ERROR, CRITICAL
LOG_LEVEL = INFO
EXEC_NAME = app
MAIN_FILE = app.py
ifeq ($(CODE_DIR),)
CODE_DIR := .
endif
ifeq ($(PYTHONPATH),)
PYTHONPATH := $(shell pwd)
endif
SOURCE_DIR = $(CODE_DIR)/src
BUILD_DIR = $(CODE_DIR)/build
LIB_PREFIX = $(CODE_DIR)/libraries
ENTRY_POINT = $(SOURCE_DIR)/gui/$(MAIN_FILE)
UI_FOLDER = $(CODE_DIR)/ui
UI_FILES := $(shell echo $(UI_FOLDER)/*.ui)
RESOURCE_ROOT = $(CODE_DIR)/resources
RESOURCE_FILE = $(RESOURCE_ROOT)/Resources.qrc
PYQT_GENERATED_FILES = $(SOURCE_DIR)/resources
PYQT_GENERATED_UI_FILS = $(PYQT_GENERATED_FILES)/ui
PY_RESOURCE_FILE = $(PYQT_GENERATED_FILES)/Resources_rc.py
TEST_FOLDER = $(SOURCE_DIR)/unit_test
AUXILLARY = $(CODE_DIR)/auxillary
VULNERABILITY_DB = $(AUXILLARY)/vulnerability/data
DOCKERFILE = Dockerfile
GCC_VERSION = 4.9.4
QT_VERSION = 5.9.1
ifeq ($(PIP),)
PIP := $(shell which pip)
endif
ifeq ($(UPX_DIR),)
UPX_DIR := $(shell dirname $(shell which upx))
endif
ifeq ($(IMAGE_VERSION),)
IMAGE_VERSION := $(shell ./bin/find-version-of-docker-image.sh $(CODE_DIR))
endif
ifeq ($(IMAGE_NAME),)
IMAGE_NAME := $(PROJECT_NAME):$(IMAGE_VERSION)
endif

COLOR = \033[32;01m
NO_COLOR = \033[0m
.PHONY: help run

# Build / clean / run

build: clean libdraw2D.so resource-file ui-files
	pyinstaller --onefile \
	            --clean \
	            --noconfirm \
	            --add-data="../README.md:." \
	            --add-binary="../libraries/libdraw2D.so:lib" \
	            --upx-dir="$(UPX_DIR)" \
	            --workpath $(BUILD_DIR) \
	            --distpath $(BUILD_DIR)/dist \
	            --specpath $(BUILD_DIR) \
	            --log-level $(LOG_LEVEL) \
	            --name $(EXEC_NAME) \
	            $(ENTRY_POINT) \
	&& mv $(BUILD_DIR)/dist/$(EXEC_NAME) $(CODE_DIR)

# Build libgaussField
libdraw2D.so:
	cd $(LIB_PREFIX) && \
	./buildSharedLib.sh -O3

clean:
	rm -rf $(BUILD_DIR) && \
	rm -rf $(LIB_PREFIX)/libgaussField/build && \
	rm -f  $(EXEC_NAME).spec

clean-all: clean clean-resource-file clean-ui-files clean-safety clean-tests clean-generated-pyqt-files clean-cache

clean-cache: clean-__pycache__ clean-pyc

clean-__pycache__:
	rm -rf $(shell find $(SOURCE_DIR) -name __pycache__)

clean-pyc:
	rm -f $(shell find $(SOURCE_DIR) -name *.pyc)

clean-generated-pyqt-files:
	rm -rf $(PYQT_GENERATED_FILES)

clean-resource-file:
	rm -f $(PY_RESOURCE_FILE)

clean-ui-files:
	rm -rf $(PYQT_GENERATED_UI_FILS)

ui-files: clean-ui-files
	mkdir -p $(PYQT_GENERATED_UI_FILS) && \
	$(foreach file,$(UI_FILES),pyuic5 $(file) --import-from=src.resources --output="$(PYQT_GENERATED_UI_FILS)/$(shell basename $(file) .ui)_ui.py";)

resource-file: clean-resource-file
	mkdir -p $(PYQT_GENERATED_FILES)  && \
	pyrcc5 $(RESOURCE_FILE) -o $(PY_RESOURCE_FILE) -name resources

resources: ui-files resource-file

pepify: resources
	autopep8 $(PYQT_GENERATED_FILES) --recursive --in-place --pep8-passes 5000 --max-line-length 120 --jobs $(shell nproc)

docker-image: check-docker-dependencies
	docker build --rm --tag $(IMAGE_NAME) --file $(DOCKERFILE) .

check-docker-dependencies: #copy-source
	[[ -d gcc-$(GCC_VERSION) ]] || { cp -R /prog/sdpsoft/gcc-$(GCC_VERSION) .; } && \
	[[ -d qt-x11-$(QT_VERSION) ]] || { cp -R /prog/sdpsoft/qt-x11-$(QT_VERSION) .; }

copy-source:
	tar --exclude='$(CODE_DIR)/.git/' --exclude="$(CODE_DIR)/documentation" -cvzf code.tar.gz *

safety-check: clean-safety install-safety get-vulnerability-db
	safety check --full-report --db $(VULNERABILITY_DB)

install-safety:
	$(PIP) install safety

get-vulnerability-db:
	mkdir -p $(VULNERABILITY_DB) && \
    for file in 'insecure.json' 'insecure_full.json' ; do \
        curl --proxy $(HTTP_PROXY) \
             --output $(VULNERABILITY_DB)/$$file \
             --insecure \
             https://raw.githubusercontent.com/pyupio/safety-db/master/data/$$file; \
    done

clean-safety:
	rm -rf $(VULNERABILITY_DB)
	$(shell type safety >/dev/null 2>&1 && pip-autoremove safety -y)

unit-tests: copy-libdraw-to-test run-tests clean-tests

copy-libdraw-to-test: libdraw2D.so
	cp $(LIB_PREFIX)/libdraw2D.so $(TEST_FOLDER)

run-tests:
	cd $(TEST_FOLDER) && \
	pytest

clean-tests:
	rm -rf $(TEST_FOLDER)/.cache && \
	rm -f  $(TEST_FOLDER)/*.dat  && \
	rm -f  $(TEST_FOLDER)/*.xml && \
	rm -f  $(TEST_FOLDER)/libdraw2D.so

# TODO: Add diagrams for Previewer, and other files / classes of interest
uml-diagrams:
	cd $(CODE_DIR) && \
	pyreverse -ASmy -k -o png $(SOURCE_DIR)/app.py -p APS-GUI

linting:
	pylint $(SOURCE_DIR)

print-%  : ; @echo $($*)
