# ----------------------------------------------------------------------------
# Makefile for gitcache
#
# Copyright (c) 2020-2023 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
APP_NAME             := gitcache
APP_VERSION          := 1.0.14

ALL_TARGET           := check-style.venv
SCRIPT               := src/gitcache

UBUNTU_DIST_VERSIONS := 20.04 22.04 24.04
MAKE4PY_DOCKER_IMAGE := make4py-gitcache
MAKE4PY_DOCKER_PKGS  := git git-lfs


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
