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
CURRENT_VERSION     := 1.0.10

UBUNTU_DIST_VERSIONS   := 18.04 20.04 22.04
UBUNTU_RELEASE_TARGETS := $(addprefix releases/gitcache_v$(CURRENT_VERSION)_Ubuntu,$(addsuffix _amd64,$(UBUNTU_DIST_VERSIONS)))
UBUNTU_PIPDEPS_TARGETS := $(addprefix pip-deps-upgrade-Ubuntu,$(addsuffix _amd64,$(UBUNTU_DIST_VERSIONS)))

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
    WIN_PLATFORM_STRING := $(shell python -c "import platform;print(f'win{platform.release()}_{platform.architecture()[0]}',end='')")
    VENV_DIR := venv_$(WIN_PLATFORM_STRING)
    VENV_ACTIVATE := $(VENV_DIR)\Scripts\activate.bat
    VENV_ACTIVATE_PLUS := $(VENV_ACTIVATE) &
    VENV_SHELL := cmd.exe /K $(VENV_ACTIVATE)
    SET_PYTHONPATH := set PYTHONPATH=$(PYTHONPATH) &
    COVERAGERC_UNITTESTS := .coveragerc-unittests-windows
    COVERAGERC_FUNCTIONAL_TESTS := .coveragerc-functional-windows
    FUNCTIONAL_TEST_RUNNER := python tests\functional_tests\run_tests.py
    DIST_GITCACHE := dist/gitcache.exe
    FIX_PATH = $(subst /,\\,$1)
    RMDIR    = rmdir /S /Q $(call FIX_PATH,$1) 2>nul || ver >nul
    RMDIRR   = for /d /r %%i in (*$1*) do @rmdir /s /q "%%i"
    RMFILE   = del /Q $(call FIX_PATH,$1) 2>nul || ver >nul
    RMFILER  = del /Q /S $(call FIX_PATH,$1) 2>nul || ver >nul
    MKDIR    = mkdir $(call FIX_PATH,$1) || ver >nul
    COPY     = copy $(call FIX_PATH,$1) $(call FIX_PATH,$2)
else
    PYTHON := python3
    ifeq (, $(shell which lsb_release))
        VENV_DIR := venv
    else
        VENV_DIR := venv_$(shell lsb_release -i -s)$(shell lsb_release -r -s)
    endif
    VENV_ACTIVATE := source $(VENV_DIR)/bin/activate
    VENV_ACTIVATE_PLUS := $(VENV_ACTIVATE);
    VENV_SHELL := $(VENV_ACTIVATE_PLUS) /bin/bash
    SET_PYTHONPATH := PYTHONPATH=$(PYTHONPATH)
    COVERAGERC_UNITTESTS := .coveragerc-unittests-linux
    COVERAGERC_FUNCTIONAL_TESTS := .coveragerc-functional-linux
    FUNCTIONAL_TEST_RUNNER := tests/functional_tests/run_tests.py
    DIST_GITCACHE := dist/gitcache
    RMDIR    = rm -rf $1
    RMDIRR   = find . -name "$1" -exec rm -rf {} \; 2>/dev/null || true
    RMFILE   = rm -f $1
    RMFILER  = find . -iname "$1" -exec rm -f {} \;
    MKDIR    = mkdir -p $1
    COPY     = cp -a $1 $2
endif

PYTHON_MINOR := $(shell $(PYTHON) -c "import sys;print(sys.version_info[1],end='')")

ifeq ($(PYTHON_MINOR),6)
  ifeq ($(ON_WINDOWS),0)
    ifneq (,$(shell which python3.8))
      PYTHON := python3.8
      PYTHON_MINOR := $(shell $(PYTHON) -c "import sys;print(sys.version_info[1],end='')")
    endif
  endif
endif

ifeq ($(PYTHON_MINOR),6)
  $(warning Old python 3.6 detected. Please install at least python 3.8!)
  ifeq ($(ON_WINDOWS),0)
    $(info On Ubuntu 18.04, you can install python 3.8 in parallel by calling the following commands:)
    $(info $A  sudo apt-get install python3.8-dev python3.8-venv)
  endif
  $(error Python version not supported)
endif

PIP_ENV_ID           := $(shell $(PYTHON) -c "import sys;print(f'{sys.platform}-py{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}',end='')")
PIP_REQUIREMENTS     := pip_deps/requirements-$(PIP_ENV_ID).txt
PIP_DEV_REQUIREMENTS := pip_deps/dev_requirements-$(PIP_ENV_ID).txt


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

.PHONY: help \
        pip-deps-upgrade pip-deps-upgrade-all pip-deps-upgrade-windows \
        pip-setup pip-install-dev pip-upgrade-stuff system-setup \
	venv venv-bash \
	run \
	check-style pylint pycodestyle flake8 mypy \
	tests tests-coverage \
	unittests unittests-coverage \
	print-functional-tests functional-tests functional-tests-coverage \
	test-no-git-lfs test-no-git-lfs-install test-latest-git \
	apidoc doc man \
	pyinstaller \
	start-windows-vm stop-windows-vm destroy-windows-vm build-in-windows-vm update-windows-vm-box \
	distclean clean

all:	check-style.venv mypy.venv tests-coverage.venv doc.venv man.venv


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
	@echo "      In the following, the targets are specified with the recommended"
	@echo "      environment."
	@echo ""
	@echo "Targets for Style Checking:"
	@echo " check-style.venv          : Call pylint, pycodestyle and flake8"
	@echo " pylint.venv               : Call pylint on the source files."
	@echo " pycodestyle.venv          : Call pycodestyle on the source files."
	@echo " flake8.venv               : Call flake8 on the source files."
	@echo " mypy.venv                 : Call mypy on the source files."
	@echo ""
	@echo "Targets for Testing:"
	@echo " tests.venv                     : Execute all tests (currently only unittests)."
	@echo " tests-coverage.venv            : Determine code coverage of all tests."
	@echo " unittests.venv                 : Execute unittests."
	@echo " unittests-coverage.venv        : Determine unittest code coverage."
	@echo " print-functional-tests.venv    : Print all available functional tests."
	@echo " functional-tests.venv          : Execute functional tests."
	@echo "                                  Tests can be selected by using the TEST_SELECTION"
	@echo "                                  variable, e.g.,"
	@echo "                                  'TEST_SELECTION=01_usage make functional-tests.venv'."
	@echo "                                  To see a list of available tests, call"
	@echo "                                  'make print-functional-tests.venv'."
	@echo " functional-tests-coverage.venv : Determine functional tests code coverage."
	@echo ""
	@echo "Targets for Functional Test Development:"
	@echo " functional-tests-debug.venv       : Like 'functional-tests' but be more verbose."
	@echo " functional-tests-save-output.venv : Like 'functional-tests' but save the output"
	@echo "                                     as the reference for the expected output."
	@echo ""
	@echo "Targets for Distribution:"
	@echo " pyinstaller.venv          : Generate dist/gitcache distributable."
	@echo " pyinstaller-test          : Test the dist/gitcache distributable"
	@echo "                             using the functional tests."
ifeq ($(ON_WINDOWS),1)
	@echo " build-release             : Build the distributables for the current"
	@echo "                             Windows version."
else
	@echo " build-release             : Build the distributables for Ubuntu ($(UBUNTU_DIST_VERSIONS))"
	@echo "                             in the releases dir."
	@echo " build-in-windows-vm       : Build the distributable for Windows in a"
	@echo "                             virtual machine."
	@echo ""
	@echo "Targets for Windows VM Management:"
	@echo " start-windows-vm          : Start the Windows virtual machine."
	@echo " stop-windows-vm           : Stop the Windows virtual machine."
	@echo " destroy-windows-vm        : Destroy the Windows virtual machine."
	@echo " update-windows-vm-box     : Update the Windows virtual machine box image."
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
	@echo "PIP dependency handling:"
	@echo " pip-deps-upgrade.venv     : Upgrade the pip-dependencies for the current environment."
	@echo " pip-deps-upgrade-all      : Upgrade the pip-dependencies for all platforms."
	@echo ""
	@echo "Misc Targets:"
	@echo " system-setup              : Install all dependencies in the currently"
	@echo "                             active environment (system or venv)."
	@echo " pip-setup                 : Part of system-setup to install latest pip and pip-tools."
	@echo " pip-install-dev           : Part of system-setup to install the pip dev requirements."
	@echo " pip-upgrade-stuff         : Part of system-setup to upgrade setuptools and wheel pip packages."
	@echo " distclean                 : Remove releases and all temporary files."
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
#  PIP REQUIREMENTS HANDLING
# ----------------------------------------------------------------------------

# Targets to generate pip_deps requirements-files if they do not exist
$(PIP_REQUIREMENTS): requirements.in
	@echo "-------------------------------------------------------------"
	@echo "Compile pip dependencies $(PIP_REQUIREMENTS)..."
	@echo "-------------------------------------------------------------"
	@pip-compile --resolver=backtracking requirements.in \
	    --output-file=$(PIP_REQUIREMENTS) \
	    --no-emit-trusted-host --no-emit-index-url --quiet

$(PIP_DEV_REQUIREMENTS): requirements.in dev_requirements.in
	@echo "-------------------------------------------------------------"
	@echo "Compile pip dependencies $(PIP_DEV_REQUIREMENTS)..."
	@echo "-------------------------------------------------------------"
	@pip-compile --resolver=backtracking requirements.in dev_requirements.in \
	    --output-file=$(PIP_DEV_REQUIREMENTS) \
	    --no-emit-trusted-host --no-emit-index-url --quiet

# Targets to upgrade/generate pip_deps requirements-files whether they exist or not
pip-deps-upgrade:
	@echo "-------------------------------------------------------------"
	@echo "Upgrade pip dependencies $(PIP_REQUIREMENTS) and $(PIP_DEV_REQUIREMENTS)..."
	@echo "-------------------------------------------------------------"
	@pip-compile --resolver=backtracking requirements.in \
	    --output-file=$(PIP_REQUIREMENTS) \
	    --no-emit-trusted-host --no-emit-index-url --quiet --upgrade
	@pip-compile --resolver=backtracking requirements.in dev_requirements.in \
	    --output-file=$(PIP_DEV_REQUIREMENTS) \
	    --no-emit-trusted-host --no-emit-index-url --quiet --upgrade

pip-deps-upgrade-all: pip-deps-upgrade.venv $(UBUNTU_PIPDEPS_TARGETS) pip-deps-upgrade-windows

$(UBUNTU_PIPDEPS_TARGETS): pip-deps-upgrade-Ubuntu%_amd64:
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:$* \
	/workdir/build_in_docker/pip-deps-upgrade.sh

pip-deps-upgrade-windows: clean
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant up
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant ssh -- make -C C:\\vagrant pip-deps-upgrade.venv clean
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant halt


# ----------------------------------------------------------------------------
#  SYSTEM SETUP
# ----------------------------------------------------------------------------

pip-setup:
	@echo "-------------------------------------------------------------"
	@echo "Installing pip..."
	@echo "-------------------------------------------------------------"
# Note: pip install -U pip had problems running on Windows, so we use now:
	@$(PYTHON) -m pip install --upgrade pip
	@echo "-------------------------------------------------------------"
	@echo "Installing pip-tools..."
	@echo "-------------------------------------------------------------"
	@pip install pip-tools

pip-install-dev: $(PIP_DEV_REQUIREMENTS)
	@echo "-------------------------------------------------------------"
	@echo "Installing package requirements (development)..."
	@echo "-------------------------------------------------------------"
	@pip install -r $(PIP_DEV_REQUIREMENTS)

pip-upgrade-stuff:
	@echo "-------------------------------------------------------------"
	@echo "Upgrade setuptools and wheel..."
	@echo "-------------------------------------------------------------"
	@pip install --upgrade setuptools wheel

system-setup: pip-setup pip-install-dev pip-upgrade-stuff


# ----------------------------------------------------------------------------
#  VENV SUPPORT
# ----------------------------------------------------------------------------

$(VENV_DIR):
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(VENV_ACTIVATE_PLUS) make system-setup
	@echo "-------------------------------------------------------------"
	@echo "Virtualenv venv setup. Call"
	@echo "  $(VENV_ACTIVATE)"
	@echo "to activate it."
	@echo "-------------------------------------------------------------"

venv: $(VENV_DIR)

venv-bash: venv
	@echo "Entering a new shell using the venv setup:"
	@$(VENV_SHELL)
	@echo "Leaving sandbox shell."


%.venv: venv
	@$(VENV_ACTIVATE_PLUS) make $*


# ----------------------------------------------------------------------------
#  RUN TARGET
# ----------------------------------------------------------------------------

run:
	@$(VENV_ACTIVATE_PLUS) $(SET_PYTHONPATH) \
	./gitcache $(RUN_ARGS)


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

mypy:
	@mypy $(SOURCES) $(UNITTEST_DIR) $(FUNCTIONAL_TEST_DIR)


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
	@$(call RMFILE,.coverage)
	@$(call RMDIR,doc/coverage)
	@$(call MKDIR,doc/coverage)
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
	@$(call RMFILE,.coverage-functional-tests)
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
	@$(call RMDIR,doc/source/apidoc)
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
	@$(call MKDIR,releases)
	@$(call COPY,$<,$@)

else

build-release: $(UBUNTU_RELEASE_TARGETS)

$(UBUNTU_RELEASE_TARGETS): releases/gitcache_v$(CURRENT_VERSION)_Ubuntu%_amd64:
	@mkdir -p releases
	@docker run --rm \
	-e TGTUID=$(shell id -u) -e TGTGID=$(shell id -g) \
	-v $(PWD):/workdir \
	ubuntu:$* \
	/workdir/build_in_docker/ubuntu.sh $@

endif


# ----------------------------------------------------------------------------
#  WINDOWS VM
# ----------------------------------------------------------------------------
start-windows-vm:
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant up

stop-windows-vm:
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant halt

destroy-windows-vm:
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant destroy -f

build-in-windows-vm: clean
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant up
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant ssh -- make -C C:\\vagrant pyinstaller.venv pyinstaller-test build-release.venv
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant ssh -- make -C C:\\vagrant clean
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant halt

update-windows-vm-box: destroy-windows-vm
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant box update
	@VAGRANT_VAGRANTFILE=Vagrantfile.win vagrant box prune --force --keep-active-boxes


# ----------------------------------------------------------------------------
#  MAINTENANCE TARGETS
# ----------------------------------------------------------------------------

distclean: clean
	@$(call RMDIRR,releases)
	@$(call RMDIRR,.mypy_cache)

clean:
	@$(call RMDIR,$(VENV_DIR) dist build doc/build doc/*coverage doc/source/apidoc)
	@$(call RMFILE,.coverage .coverage-* *.spec)
	@$(call RMDIRR,__pycache__)
	@$(call RMFILER,*~)
	@$(call RMFILER,*.pyc)


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
