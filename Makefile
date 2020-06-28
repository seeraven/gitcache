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

SCRIPTS            := gitcache
SCRIPTS_ABS        := $(patsubst %,$(PWD)/%,$(SCRIPTS))
PYTHONPATH         := $(PWD)
SOURCES            := $(SCRIPTS_ABS)


# ----------------------------------------------------------------------------
#  HANDLE TARGET 'run'
# ----------------------------------------------------------------------------
ifeq (run,$(firstword $(MAKECMDGOALS)))
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # Turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif


# ----------------------------------------------------------------------------
#  DEFAULT TARGETS
# ----------------------------------------------------------------------------

.PHONY: help system-setup venv-bash run check-style pylint pycodestyle flake8 functional-tests functional-tests-coverage clean

all:	check-style.venv functional-tests-coverage.venv


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
	@echo " functional-tests          : Execute functional tests."
	@echo " functional-tests-coverage : Determine functional tests code coverage."
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
	@pip install -U pip
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
	@pylint --rcfile=$(PYLINT_RCFILE) $(SOURCES)
	@echo "pylint found no errors."


pycodestyle:
	@pycodestyle --config=$(PYCODESTYLE_CONFIG) $(SOURCES)
	@echo "pycodestyle found no errors."


flake8:
	@flake8 $(SOURCES)
	@echo "flake8 found no errors."


# ----------------------------------------------------------------------------
#  FUNCTIONAL TESTS
# ----------------------------------------------------------------------------

functional-tests:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh

functional-tests-debug:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -v -w

functional-tests-save-output:
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -s

functional-tests-coverage:
	@rm -f .coverage-functional-tests
	@PYTHONPATH=$(PYTHONPATH) tests/functional_tests/run_tests.sh -c
	@echo "Functional Tests Code Coverage:"
	@coverage report --rcfile=.coveragerc-functional
	@coverage html --rcfile=.coveragerc-functional
	@coverage xml --rcfile=.coveragerc-functional


# ----------------------------------------------------------------------------
#  MAINTENANCE TARGETS
# ----------------------------------------------------------------------------

clean:
	@rm -rf venv .coverage .coverage-*
	@rm -rf dist build *.spec
	@find . -name "__pycache__" -exec rm -rf {} \; 2>/dev/null || true
	@find . -iname "*~" -exec rm -f {} \;
	@find . -iname "*.pyc" -exec rm -f {} \;

