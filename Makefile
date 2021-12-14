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
#  SETTINGS
# ----------------------------------------------------------------------------

SHELL               = /bin/bash
PYLINT_RCFILE      := $(PWD)/.pylintrc
PYCODESTYLE_CONFIG := $(PWD)/.pycodestyle
PIP                ?= pip

MODULES            := git_cache
SCRIPTS            := gitcache
MODULES_ABS        := $(patsubst %,$(PWD)/%,$(MODULES))
SCRIPTS_ABS        := $(patsubst %,$(PWD)/%,$(SCRIPTS))
PYTHONPATH         := $(PWD)
SOURCES            := $(SCRIPTS_ABS) $(MODULES_ABS)
UNITTEST_DIR       := tests/unittests
UNITTEST_FILES     := $(shell find $(UNITTEST_DIR) -name '*.py')

# Keep this version in sync with GITCACHE_VERSION in git_cache/git_cache_command.py
CURRENT_VERSION    := 1.0.6


# ----------------------------------------------------------------------------
#  HANDLE TARGET 'run'
# ----------------------------------------------------------------------------
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets (disabled as it crashes with URLs)
  #$(eval $(RUN_ARGS):;@:)
endif


# ----------------------------------------------------------------------------
#  DEFAULT TARGETS
# ----------------------------------------------------------------------------

.PHONY: help system-setup venv-bash run check-style pylint pycodestyle flake8 tests tests-coverage unittests unittests-coverage functional-tests functional-tests-coverage test-no-git-lfs test-no-git-lfs-install test-latest-git apidoc doc man pyinstaller clean

all:	check-style.venv tests-coverage.venv doc.venv man.venv


# ----------------------------------------------------------------------------
#  USAGE
# ----------------------------------------------------------------------------
help:
	@echo "Makefile for gitcache"
	@echo "====================="
	@echo
	@echo "Note: All targets can be executed in a virtual environment (venv)"
	@echo "      by using the '.venv' suffix."
	@echo "      For example, use the target 'check-style.venv' to perform"
	@echo "      the style checking in a virtual environment."
	@echo
	@echo "Targets for Style Checking:"
	@echo " check-style               : Call pylint, pycodestyle and flake8"
	@echo " pylint                    : Call pylint on the source files."
	@echo " pycodestyle               : Call pycodestyle on the source files."
	@echo " flake8                    : Call flake8 on the source files."
	@echo
	@echo "Targets for Testing:"
	@echo " tests                     : Execute unittests and functional tests."
	@echo " tests-coverage            : Determine code coverage of all tests."
	@echo " unittests                 : Execute unittests."
	@echo " unittests-coverage        : Determine unittest code coverage."
	@echo " functional-tests          : Execute functional tests."
	@echo "                             Tests can be selected by using the TEST_SELECTION"
	@echo "                             variable, e.g.,"
	@echo "                             'TEST_SELECTION=01_usage make functional-tests.venv'."
	@echo "                             To see a list of available tests, call"
	@echo "                             'TEST_SELECTION=-h make functional-tests.venv'."
	@echo " functional-tests-coverage : Determine functional tests code coverage."
	@echo
	@echo "Targets for Functional Test Development:"
	@echo " functional-tests-debug       : Like 'functional-tests' but be more verbose."
	@echo " functional-tests-save-output : Like 'functional-tests' but save the output"
	@echo "                                as the reference for the expected output."
	@echo
	@echo "Targets for Distribution:"
	@echo " pyinstaller               : Generate dist/gitcache distributable."
	@echo " pyinstaller-test          : Test the dist/gitcache distributable"
	@echo "                             using the functional tests."
	@echo " build-release             : Build the distributables for Ubuntu 18.04,"
	@echo "                             20.04 and 21.04 in the releases dir."
	@echo
	@echo "Target for Execution from the sources:"
	@echo " run                       : Run 'gitcache' with the correct"
	@echo "                             PYTHONPATH variable. All remaining"
	@echo "                             arguments are forwarded to gitcache."
	@echo "                             Use '--' to enable the usage of options."
	@echo " Example:"
	@echo "   make run -- clone -h"
	@echo
	@echo "venv Setup:"
	@echo " venv                      : Create the venv."
	@echo " venv-bash                 : Start a new shell in the venv for debugging."
	@echo
	@echo "Misc Targets:"
	@echo " system-setup              : Install all dependencies in the currently"
	@echo "                             active environment (system or venv)."
	@echo " clean                     : Remove all temporary files."
	@echo
	@echo "Development Information:"
	@echo " MODULES    = $(MODULES)"
	@echo " SCRIPTS    = $(SCRIPTS)"
	@echo " PYTHONPATH = $(PYTHONPATH)"
	@echo " SOURCES    = $(SOURCES)"


# ----------------------------------------------------------------------------
#  SYSTEM SETUP
# ----------------------------------------------------------------------------

system-setup:
	@echo "-------------------------------------------------------------"
	@echo "Installing pip..."
	@echo "-------------------------------------------------------------"
	@pip install -U "$(PIP)"
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
	@if [ ! -d venv ]; then python3 -m venv venv; fi
	@source venv/bin/activate; \
	make system-setup
	@echo "-------------------------------------------------------------"
	@echo "Virtualenv venv setup. Call"
	@echo "  source venv/bin/activate"
	@echo "to activate it."
	@echo "-------------------------------------------------------------"


venv-bash: venv
	@echo "Entering a new shell using the venv setup:"
	@source venv/bin/activate; \
	/bin/bash
	@echo "Leaving sandbox shell."


%.venv: venv
	@source venv/bin/activate; \
	make $*


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
	@pylint --rcfile=$(PYLINT_RCFILE) $(SOURCES) $(UNITTEST_FILES)
	@echo "pylint found no errors."


pycodestyle:
	@pycodestyle --config=$(PYCODESTYLE_CONFIG) $(SOURCES) $(UNITTEST_DIR)
	@echo "pycodestyle found no errors."


flake8:
	@flake8 $(SOURCES) $(UNITTEST_DIR)
	@echo "flake8 found no errors."


# ----------------------------------------------------------------------------
#  TESTS
# ----------------------------------------------------------------------------

tests: unittests functional-tests

tests-coverage: unittests-coverage functional-tests-coverage
	@coverage combine --rcfile=.coveragerc-combined .coverage .coverage-functional-tests
	@echo "Unit and Functional Tests Code Coverage:"
	@coverage report --rcfile=.coveragerc-combined
	@coverage html --rcfile=.coveragerc-combined
	@coverage xml --rcfile=.coveragerc-combined


# ----------------------------------------------------------------------------
#  UNIT TESTS
# ----------------------------------------------------------------------------

unittests:
	@PYTHONPATH=$(PYTHONPATH) nosetests -v -w tests/unittests

unittests-coverage:
	@rm -rf doc/coverage
	@rm -f .coverage
	@mkdir -p doc/coverage
	@PYTHONPATH=$(PYTHONPATH) nosetests -v -w tests/unittests --with-coverage \
        --cover-package=git_cache --cover-erase --cover-min-percentage=80 \
	--cover-inclusive \
        --cover-branches \
        --cover-html --cover-html-dir=../../doc/unittests-coverage \
        --cover-xml  --cover-xml-file=../../doc/unittests-coverage/coverage.xml


# ----------------------------------------------------------------------------
#  FUNCTIONAL TESTS
# ----------------------------------------------------------------------------

functional-tests:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh $(TEST_SELECTION)

functional-tests-debug:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -v $(TEST_SELECTION)

functional-tests-save-output:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -s $(TEST_SELECTION)

functional-tests-coverage:
	@rm -f .coverage-functional-tests
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -c
	@echo "Functional Tests Code Coverage:"
	@coverage report --rcfile=.coveragerc-functional
	@coverage html --rcfile=.coveragerc-functional
	@coverage xml --rcfile=.coveragerc-functional


# ----------------------------------------------------------------------------
#  SYSTEM TESTS
# ----------------------------------------------------------------------------

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


# ----------------------------------------------------------------------------
#  DOCUMENTATION
# ----------------------------------------------------------------------------

apidoc:
	@rm -rf doc/source/apidoc
	@PYTHONPATH=$(PYTHONPATH) sphinx-apidoc -f -M -T -o doc/source/apidoc $(MODULES)

doc: apidoc
	@PYTHONPATH=$(PYTHONPATH) sphinx-build -W -b html doc/source doc/build

man:
	@PYTHONPATH=$(PYTHONPATH) sphinx-build -W -b man doc/manpage doc/build


# ----------------------------------------------------------------------------
#  DISTRIBUTION
# ----------------------------------------------------------------------------

pyinstaller: dist/gitcache

dist/gitcache:
	@pyinstaller gitcache --onefile

pyinstaller-test: dist/gitcache
	@tests/functional_tests/run_tests.sh -p

build-release: releases/gitcache_v$(CURRENT_VERSION)_Ubuntu18.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu20.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.04_amd64

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

releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.04_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:21.04 \
	/workdir/build_in_docker/ubuntu.sh
	@mv releases/gitcache_Ubuntu21.04_amd64 releases/gitcache_v$(CURRENT_VERSION)_Ubuntu21.04_amd64


# ----------------------------------------------------------------------------
#  MAINTENANCE TARGETS
# ----------------------------------------------------------------------------

clean:
	@rm -rf venv doc/*coverage doc/build doc/source/apidoc .coverage .coverage-*
	@rm -rf dist build *.spec
	@find . -name "__pycache__" -exec rm -rf {} \; 2>/dev/null || true
	@find . -iname "*~" -exec rm -f {} \;
	@find . -iname "*.pyc" -exec rm -f {} \;


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
