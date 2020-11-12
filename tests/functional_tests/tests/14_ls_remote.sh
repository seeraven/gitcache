#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the ls-remote output.
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*

capture_output_success clone git clone https://github.com/seeraven/submodule-example.git ${TMP_WORKDIR}/submodule-example

capture_output_success ls_remote       git -C ${TMP_WORKDIR}/submodule-example ls-remote
capture_output_success ls_remote_stats -s

capture_output_success ls_remote_with_url       git -C ${TMP_WORKDIR}/submodule-example ls-remote https://github.com/seeraven/submodule-example.git
capture_output_success ls_remote_with_urlstats -s

capture_output_success ls_remote_with_ref       git -C ${TMP_WORKDIR}/submodule-example ls-remote origin
capture_output_success ls_remote_with_refstats -s

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success ls_remote_without_update       git -C ${TMP_WORKDIR}/submodule-example ls-remote
capture_output_success ls_remote_without_update_stats -s
export GITCACHE_UPDATE_INTERVAL=0

# Ls-Remote on non-managed repository
capture_output_success clone_directory      git clone ${TMP_WORKDIR}/submodule-example ${TMP_WORKDIR}/submodule-example5
git -C ${TMP_WORKDIR}/submodule-example5 remote set-url origin https://github.com/seeraven/submodule-example.git
capture_output_success ls_remote_non_mirror git -C ${TMP_WORKDIR}/submodule-example5 ls-remote


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
