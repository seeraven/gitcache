#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the update all.
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

capture_output_success clone git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache

capture_output_success update_via_git       git update-mirrors
capture_output_success update_via_git_stats -s

capture_output_success update_via_gitcache       -u
capture_output_success update_via_gitcache_stats -s

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success update_despite_interval       git update-mirrors
capture_output_success update_despite_interval_stats -s
export GITCACHE_UPDATE_INTERVAL=0

# Update without any mirrors


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
