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
APP_VERSION          := 1.0.22

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
#  OWN TARGETS
# ----------------------------------------------------------------------------
.PHONY: precheck-releases

precheck-releases: check-style.ubuntu22.04 tests.all doc man releases test-releases


# ----------------------------------------------------------------------------
#  EOF
# ----------------------------------------------------------------------------
