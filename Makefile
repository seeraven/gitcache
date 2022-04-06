# ----------------------------------------------------------------------------
# Makefile for gitcache
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  OS Detection
# ----------------------------------------------------------------------------
ifdef OS
    ON_WINDOWS = 1
else
    ON_WINDOWS = 0
endif


# ----------------------------------------------------------------------------
#  FUNCTIONS
# ----------------------------------------------------------------------------

# Recursive wildcard function. Call with: $(call rwildcard,<start dir>,<pattern>)
rwildcard = $(foreach d,$(wildcard $(1:=/*)),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------

# Keep this version in sync with GITCACHE_VERSION in git_cache/git_cache_command.py
CURRENT_VERSION     := 1.0.9

ifeq ($(ON_WINDOWS),1)
    PWD             := $(CURDIR)
endif

SHELL                = /bin/bash
PYLINT_RCFILE       := $(PWD)/.pylintrc
PYCODESTYLE_CONFIG  := $(PWD)/.pycodestyle

MODULES             := git_cache
SCRIPTS             := gitcache
MODULES_ABS         := $(patsubst %,$(PWD)/%,$(MODULES))
SCRIPTS_ABS         := $(patsubst %,$(PWD)/%,$(SCRIPTS))
PYTHONPATH          := $(PWD)
SOURCES             := $(SCRIPTS_ABS) $(MODULES_ABS)
UNITTEST_DIR        := tests/unittests
FUNCTIONAL_TEST_DIR := tests/functional_tests

UNITTEST_FILES        := $(call rwildcard,$(UNITTEST_DIR),*.py)
FUNCTIONAL_TEST_FILES := $(call rwildcard,$(FUNCTIONAL_TEST_DIR),*.py)

ifeq ($(ON_WINDOWS),1)
    PYTHON := python
    VENV_ACTIVATE := venv\Scripts\activate.bat
    VENV_ACTIVATE_PLUS := $(VENV_ACTIVATE) &
    SET_PYTHONPATH := set PYTHONPATH=$(PYTHONPATH) &
    COVERAGERC_UNITTESTS := .coveragerc-unittests-windows
    COVERAGERC_FUNCTIONAL_TESTS := .coveragerc-functional-windows
    FUNCTIONAL_TEST_RUNNER := python tests\functional_tests\run_tests.py
    DIST_GITCACHE := dist/gitcache.exe
    WIN_PLATFORM_STRING := $(shell python -c "import platform;print(f'win{platform.release()}_{platform.architecture()[0]}',end='')")
else
    PYTHON := python3
    VENV_ACTIVATE := source venv/bin/activate
    VENV_ACTIVATE_PLUS := $(VENV_ACTIVATE);
    SET_PYTHONPATH := PYTHONPATH=$(PYTHONPATH)
    COVERAGERC_UNITTESTS := .coveragerc-unittests-linux
    COVERAGERC_FUNCTIONAL_TESTS := .coveragerc-functional-linux
    FUNCTIONAL_TEST_RUNNER := tests/functional_tests/run_tests.py
    DIST_GITCACHE := dist/gitcache
endif


# ----------------------------------------------------------------------------
#  HANDLE TARGET 'run'
# ----------------------------------------------------------------------------
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets (disabled as it crashes with URLs)
  #$(eval $(RUN_ARGS):;@:)
endif


# ----------------------------------------------------------------------------
#  PUT TESTS IN TEST_SELECTION ENV INTO "-t" LIST
# ----------------------------------------------------------------------------
ifneq ($(TEST_SELECTION),"")
  TEST_SELECTION_ARGS = $(patsubst %,-t %,$(TEST_SELECTION))
endif


# ----------------------------------------------------------------------------
#  DEFAULT TARGETS
# ----------------------------------------------------------------------------

.PHONY: help system-setup venv-bash run check-style pylint pycodestyle flake8 tests tests-coverage unittests unittests-coverage print-functional-tests functional-tests functional-tests-coverage test-no-git-lfs test-no-git-lfs-install test-latest-git apidoc doc man pyinstaller clean start-windows-vm stop-windows-vm build-in-windows-vm

all:	check-style.venv tests-coverage.venv doc.venv man.venv


# ----------------------------------------------------------------------------
#  USAGE
# ----------------------------------------------------------------------------
help:
	@echo "Makefile for gitcache"
	@echo "====================="
	@echo ""
	@echo "Note: All targets can be executed in a virtual environment (venv)"
	@echo "      by using the '.venv' suffix."
	@echo "      For example, use the target 'check-style.venv' to perform"
	@echo "      the style checking in a virtual environment."
	@echo ""
	@echo "Targets for Style Checking:"
	@echo " check-style               : Call pylint, pycodestyle and flake8"
	@echo " pylint                    : Call pylint on the source files."
	@echo " pycodestyle               : Call pycodestyle on the source files."
	@echo " flake8                    : Call flake8 on the source files."
	@echo ""
	@echo "Targets for Testing:"
	@echo " tests                     : Execute unittests and functional tests."
	@echo " tests-coverage            : Determine code coverage of all tests."
	@echo " unittests                 : Execute unittests."
	@echo " unittests-coverage        : Determine unittest code coverage."
	@echo " print-functional-tests    : Print all available functional tests."
	@echo " functional-tests          : Execute functional tests."
	@echo "                             Tests can be selected by using the TEST_SELECTION"
	@echo "                             variable, e.g.,"
	@echo "                             'TEST_SELECTION=01_usage make functional-tests.venv'."
	@echo "                             To see a list of available tests, call"
	@echo "                             'make print-functional-tests.venv'."
	@echo " functional-tests-coverage : Determine functional tests code coverage."
	@echo ""
	@echo "Targets for Functional Test Development:"
	@echo " functional-tests-debug       : Like 'functional-tests' but be more verbose."
	@echo " functional-tests-save-output : Like 'functional-tests' but save the output"
	@echo "                                as the reference for the expected output."
	@echo ""
	@echo "Targets for Distribution:"
	@echo " pyinstaller               : Generate dist/gitcache distributable."
	@echo " pyinstaller-test          : Test the dist/gitcache distributable"
	@echo "                             using the functional tests."
ifeq ($(ON_WINDOWS),1)
	@echo " build-release             : Build the distributables for the current"
	@echo "                             Windows version."
else
	@echo " build-release             : Build the distributables for Ubuntu 18.04,"
	@echo "                             20.04, 21.10 and 22.04 in the releases dir."
	@echo " build-in-windows-vm       : Build the distributable for Windows in a"
	@echo "                             virtual machine."
endif
	@echo ""
	@echo "Target for Execution from the sources:"
	@echo " run                       : Run 'gitcache' with the correct"
	@echo "                             PYTHONPATH variable. All remaining"
	@echo "                             arguments are forwarded to gitcache."
	@echo "                             Use '--' to enable the usage of options."
	@echo " Example:"
	@echo "   make run -- clone -h"
	@echo ""
	@echo "venv Setup:"
	@echo " venv                      : Create the venv."
	@echo " venv-bash                 : Start a new shell in the venv for debugging."
	@echo ""
	@echo "Misc Targets:"
	@echo " system-setup              : Install all dependencies in the currently"
	@echo "                             active environment (system or venv)."
	@echo " clean                     : Remove all temporary files."
	@echo ""
	@echo "Development Information:"
	@echo " PWD        = $(PWD)"
	@echo " MODULES    = $(MODULES)"
	@echo " SCRIPTS    = $(SCRIPTS)"
	@echo " PYTHONPATH = $(PYTHONPATH)"
	@echo " SOURCES    = $(SOURCES)"
	@echo " TEST_SELECTION = $(TEST_SELECTION_ARGS)"


# ----------------------------------------------------------------------------
#  SYSTEM SETUP
# ----------------------------------------------------------------------------

system-setup:
	@echo "-------------------------------------------------------------"
	@echo "Installing pip..."
	@echo "-------------------------------------------------------------"
# Note: pip install -U pip had problems running on Windows, so we use now:
	@$(PYTHON) -m pip install --upgrade pip
	@echo "-------------------------------------------------------------"
	@echo "Installing package requirements..."
	@echo "-------------------------------------------------------------"
	@pip install -r requirements.txt
	@echo "-------------------------------------------------------------"
	@echo "Installing package development requirements..."
	@echo "-------------------------------------------------------------"
	@pip install -r dev_requirements.txt
	@pip install -U setuptools wheel


# ----------------------------------------------------------------------------
#  VENV SUPPORT
# ----------------------------------------------------------------------------

venv:
	@$(PYTHON) -m venv venv
	@$(VENV_ACTIVATE_PLUS) make system-setup
	@echo "-------------------------------------------------------------"
	@echo "Virtualenv venv setup. Call"
	@echo "  $(VENV_ACTIVATE)"
	@echo "to activate it."
	@echo "-------------------------------------------------------------"


venv-bash: venv
	@echo "Entering a new shell using the venv setup:"
ifeq ($(ON_WINDOWS),1)
	@cmd.exe /K $(VENV_ACTIVATE)
else
	@$(VENV_ACTIVATE_PLUS) /bin/bash
endif
	@echo "Leaving sandbox shell."


%.venv: venv
	@$(VENV_ACTIVATE_PLUS) make $*


# ----------------------------------------------------------------------------
#  RUN TARGET
# ----------------------------------------------------------------------------

run:
	@source venv/bin/activate; \
	PYTHONPATH=$(PYTHONPATH) ./gitcache $(RUN_ARGS)


# ----------------------------------------------------------------------------
#  STYLE CHECKING
# ----------------------------------------------------------------------------

check-style: pylint pycodestyle flake8

pylint:
	@pylint --rcfile=$(PYLINT_RCFILE) $(SOURCES) $(UNITTEST_FILES) $(FUNCTIONAL_TEST_FILES)
	@echo "pylint found no errors."


pycodestyle:
	@pycodestyle --config=$(PYCODESTYLE_CONFIG) $(SOURCES) $(UNITTEST_DIR) $(FUNCTIONAL_TEST_FILES)
	@echo "pycodestyle found no errors."


flake8:
	@flake8 $(SOURCES) $(UNITTEST_DIR) $(FUNCTIONAL_TEST_DIR)
	@echo "flake8 found no errors."


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------

tests: unittests functional-tests

tests-coverage: unittests-coverage functional-tests-coverage
	@coverage combine --rcfile=.coveragerc-combined .coverage-unittests .coverage-functional-tests
	@echo "Unit and Functional Tests Code Coverage:"
	@coverage report --rcfile=.coveragerc-combined
	@coverage html --rcfile=.coveragerc-combined
	@coverage xml --rcfile=.coveragerc-combined


# ----------------------------------------------------------------------------
#  UNIT TESTS
# ----------------------------------------------------------------------------

unittests:
	@$(SET_PYTHONPATH) $(PYTHON) -m unittest discover --failfast -s $(UNITTEST_DIR)

unittests-coverage:
ifeq ($(ON_WINDOWS),1)
	@rmdir /S /Q doc\coverage 2>nul || ver >nul
	@del /Q .coverage 2>nul || ver >nul
	@mkdir doc\coverage
else
	@rm -rf doc/coverage
	@rm -f .coverage
	@mkdir -p doc/coverage
endif
	@$(SET_PYTHONPATH) coverage run --rcfile=$(COVERAGERC_UNITTESTS) -m unittest discover -s $(UNITTEST_DIR)
	@coverage report --rcfile=$(COVERAGERC_UNITTESTS)
	@coverage html --rcfile=$(COVERAGERC_UNITTESTS)
	@coverage xml --rcfile=$(COVERAGERC_UNITTESTS)


# ----------------------------------------------------------------------------
#  FUNCTIONAL TESTS
# ----------------------------------------------------------------------------

print-functional-tests:
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) -t help

functional-tests:
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) $(TEST_SELECTION_ARGS)

functional-tests-debug:
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) -v $(TEST_SELECTION_ARGS)

functional-tests-save-output:
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) -s $(TEST_SELECTION_ARGS)

functional-tests-coverage:
ifeq ($(ON_WINDOWS),1)
	@del /Q .coverage-functional-tests 2>nul || ver >nul
else
	@rm -f .coverage-functional-tests
endif
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) -c
	@echo "Functional Tests Code Coverage:"
	@coverage report --rcfile=$(COVERAGERC_FUNCTIONAL_TESTS)
	@coverage html --rcfile=$(COVERAGERC_FUNCTIONAL_TESTS)
	@coverage xml --rcfile=$(COVERAGERC_FUNCTIONAL_TESTS)


# ----------------------------------------------------------------------------
#  SYSTEM TESTS
# ----------------------------------------------------------------------------
ifeq ($(ON_WINDOWS),0)

test-no-git-lfs:
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:21.04 \
	/workdir/build_in_docker/ubuntu_latest_git.sh --no-lfs

test-no-git-lfs-install:
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:21.04 \
	/workdir/build_in_docker/ubuntu_latest_git.sh --no-lfs-install

test-latest-git:
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:20.04 \
	/workdir/build_in_docker/ubuntu_latest_git.sh --latest --pyinstaller

endif

# ----------------------------------------------------------------------------
#  DOCUMENTATION
# ----------------------------------------------------------------------------

apidoc:
ifeq ($(ON_WINDOWS),1)
	@rmdir /S /Q doc\source\apidoc 2>nul || ver >nul
else
	@rm -rf doc/source/apidoc
endif
	@$(SET_PYTHONPATH) sphinx-apidoc -f -M -T -o doc/source/apidoc $(MODULES)

doc: apidoc
	@$(SET_PYTHONPATH) sphinx-build -W -b html doc/source doc/build

man:
	@$(SET_PYTHONPATH) sphinx-build -W -b man doc/manpage doc/build


# ----------------------------------------------------------------------------
#  DISTRIBUTION
# ----------------------------------------------------------------------------

pyinstaller: $(DIST_GITCACHE)

$(DIST_GITCACHE):
	@pyinstaller gitcache --onefile

pyinstaller-test: $(DIST_GITCACHE)
	@$(SET_PYTHONPATH) $(FUNCTIONAL_TEST_RUNNER) -p

ifeq ($(ON_WINDOWS),1)

build-release: releases/gitcache_v$(CURRENT_VERSION)_$(WIN_PLATFORM_STRING).exe

releases/gitcache_v$(CURRENT_VERSION)_$(WIN_PLATFORM_STRING).exe: $(DIST_GITCACHE)
	@mkdir releases 2>nul || ver >nul
	@copy dist\gitcache.exe releases\gitcache_v$(CURRENT_VERSION)_$(WIN_PLATFORM_STRING).exe

else

build-release: releases/gitcache_v$(CURRENT_VERSION)_Ubuntu18.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu20.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.10_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu22.04_amd64

releases/gitcache_v$(CURRENT_VERSION)_Ubuntu18.04_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:18.04 \
	/workdir/build_in_docker/ubuntu.sh
	@mv releases/gitcache_Ubuntu18.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu18.04_amd64

releases/gitcache_v$(CURRENT_VERSION)_Ubuntu20.04_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:20.04 \
	/workdir/build_in_docker/ubuntu.sh
	@mv releases/gitcache_Ubuntu20.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu20.04_amd64

releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.10_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:21.10 \
	/workdir/build_in_docker/ubuntu.sh
	@mv releases/gitcache_Ubuntu21.10_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.10_amd64

releases/gitcache_v$(CURRENT_VERSION)_Ubuntu22.04_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:22.04 \
	/workdir/build_in_docker/ubuntu.sh
	@mv releases/gitcache_Ubuntu22.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu22.04_amd64

endif


# ----------------------------------------------------------------------------
#  WINDOWS VM
# ----------------------------------------------------------------------------
start-windows-vm:
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant up

stop-windows-vm:
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant halt

build-in-windows-vm: clean
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant up
# Note: Execution of unittests requires a stdin which is not possible to provide using the
#       'vagrant ssh -- make ...' syntax. To execute everything as we do in the docker
#       for ubuntu, call
#           VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant ssh
#           make -C C:\\vagrant unittests.venv pyinstaller.venv pyinstaller-test
#
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant ssh -- make -C C:\\vagrant pyinstaller.venv pyinstaller-test build-release.venv
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant halt


# ----------------------------------------------------------------------------
#  MAINTENANCE TARGETS
# ----------------------------------------------------------------------------

clean:
ifeq ($(ON_WINDOWS),1)
	@rmdir /S /Q venv dist build doc\build doc\*coverage doc\source\apidoc 2>nul || ver >nul
	@del /Q .coverage     2>nul || ver >nul
	@del /Q .coverage-*   2>nul || ver >nul
	@del /Q *.spec        2>nul || ver >nul
	@del /Q /S *~         2>nul || ver >nul
	@del /Q /S *.pyc      2>nul || ver >nul
else
	@rm -rf venv doc/*coverage doc/build doc/source/apidoc .coverage .coverage-*
	@rm -rf dist build *.spec
	@find . -name "__pycache__" -exec rm -rf {} \; 2>/dev/null || true
	@find . -iname "*~" -exec rm -f {} \;
	@find . -iname "*.pyc" -exec rm -f {} \;
endif


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
