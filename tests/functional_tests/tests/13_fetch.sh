#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the fetch output.
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

capture_output_success fetch       git -C ${TMP_WORKDIR}/gitcache fetch
capture_output_success fetch_stats -s

capture_output_success fetch_with_url       git -C ${TMP_WORKDIR}/gitcache fetch https://github.com/seeraven/gitcache.git
capture_output_success fetch_with_urlstats -s

capture_output_success fetch_with_ref       git -C ${TMP_WORKDIR}/gitcache fetch origin
capture_output_success fetch_with_refstats -s

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success fetch_without_update       git -C ${TMP_WORKDIR}/gitcache fetch
capture_output_success fetch_without_update_stats -s
export GITCACHE_UPDATE_INTERVAL=0

# Fetch on non-managed repository
capture_output_success clone_directory  git clone ${TMP_WORKDIR}/gitcache ${TMP_WORKDIR}/gitcache5
git -C ${TMP_WORKDIR}/gitcache5 remote set-url origin https://github.com/seeraven/gitcache.git
capture_output_success fetch_non_mirror git -C ${TMP_WORKDIR}/gitcache5 fetch


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
