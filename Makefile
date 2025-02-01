# ----------------------------------------------------------------------------
# Makefile for gitcache
#
# Copyright (c) 2020-2024 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
APP_NAME             := gitcache
APP_VERSION          := 1.0.24

ALL_TARGET           := check-style.venv
SCRIPT               := src/gitcache

UBUNTU_DIST_VERSIONS := 20.04 22.04 24.04
ALPINE_DIST_VERSIONS := 3.20
MAKE4PY_DOCKER_IMAGE := make4py-gitcache
MAKE4PY_DOCKER_PKGS  := git git-lfs
MAKE4PY_ALPINE_DOCKER_PKGS  := git git-lfs

PYINSTALLER_ARGS_LINUX   := --clean --onefile
PYINSTALLER_ARGS_DARWIN  := --clean --onedir
PYINSTALLER_ARGS_WINDOWS := --clean --onefile


# ----------------------------------------------------------------------------
#  MAKE4PY INTEGRATION
# ----------------------------------------------------------------------------
include .make4py/make4py.mk


# ----------------------------------------------------------------------------
#  WHEEL BUILD
# ----------------------------------------------------------------------------
.PHONY: build-wheel

WHEEL := dist/$(APP_NAME)-$(APP_VERSION)-py3-none-any.whl

ifeq ($(SWITCH_TO_VENV),1)

$(WHEEL): $(WHEEL).venv

else

$(WHEEL): pyproject.toml
	@pip install --upgrade build
	@python3 -m build

endif

build-wheel: $(WHEEL)


# ----------------------------------------------------------------------------
#  WHEEL TEST INSTALLATION
# ----------------------------------------------------------------------------
ifeq ($(ON_WINDOWS),1)
    PPTEST_VENV_DIR := $(BUILD_DIR)\venv_pptest_$(WIN_PLATFORM_STRING)$(PLATFORM_SUFFIX)
    PPTEST_VENV_ACTIVATE := $(PPTEST_VENV_DIR)\Scripts\activate.bat
    PPTEST_VENV_ACTIVATE_PLUS := $(PPTEST_VENV_ACTIVATE) &
else
    PPTEST_VENV_DIR := $(BUILD_DIR)/venv_pptest_$(LINUX_PLATFORM_STRING)$(PLATFORM_SUFFIX)
    PPTEST_VENV_ACTIVATE := source $(PPTEST_VENV_DIR)/bin/activate
    PPTEST_VENV_ACTIVATE_PLUS := $(PPTEST_VENV_ACTIVATE);
endif

$(PPTEST_VENV_DIR):
	@$(PYTHON) -m venv $(PPTEST_VENV_DIR)
	@$(PPTEST_VENV_ACTIVATE_PLUS) make pptest-system-setup

%.pptest_venv: $(PPTEST_VENV_DIR)
	@echo "Entering venv $(PPTEST_VENV_DIR):"
	@$(PPTEST_VENV_ACTIVATE_PLUS) make $*
	@echo "Leaving venv $(PPTEST_VENV_DIR)."


.PHONY: pptest-system-setup

pptest-system-setup: pip-setup
	@echo "-------------------------------------------------------------"
	@echo "Installing requirements for pip package test..."
	@echo "-------------------------------------------------------------"
	@pip install $(WHEEL)
	@pip install pytest

ifeq ($(SWITCH_TO_VENV),1)


.PHONY: functional-tests-wheel

functional-tests-wheel: functional-tests-wheel.pptest_venv

else

functional-tests-wheel: $(SOURCES)
	pytest $(FUNCTEST_SELECTION) --executable $(shell which gitcache) $(FUNCTEST_DIR)

endif
