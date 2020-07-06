#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the pull output.
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

capture_output_success pull git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_stats -s

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success pull_without_update git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_without_update_stats -s
export GITCACHE_UPDATE_INTERVAL=0

# Do not update mirror if repository does not use the mirror
git -C ${TMP_WORKDIR}/gitcache remote set-url origin https://github.com/seeraven/gitcache.git
capture_output_success pull_non_mirror git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_non_mirror_stats -s


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
