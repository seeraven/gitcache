#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the mirror delete.
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

# Delete giving the URL
capture_output_success clone git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache
rm -rf ${TMP_WORKDIR}/gitcache
capture_output_success delete_via_git       git delete-mirror https://github.com/seeraven/gitcache.git
capture_output_success delete_via_git_stats -s

# Delete giving the path
capture_output_success clone2 git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache
rm -rf ${TMP_WORKDIR}/gitcache
capture_output_success delete2_via_git       git delete-mirror ${GITCACHE_DIR}/mirrors/github.com/seeraven/gitcache
capture_output_success delete2_via_git_stats -s

# Delete using gitcache command
capture_output_success clone3 git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache
rm -rf ${TMP_WORKDIR}/gitcache
capture_output_success delete_via_gitcache       -d https://github.com/seeraven/gitcache.git
capture_output_success delete_via_gitcache_stats -s

# Delete using gitcache command giving the path
capture_output_success clone4 git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache
rm -rf ${TMP_WORKDIR}/gitcache
capture_output_success delete2_via_gitcache       -d ${GITCACHE_DIR}/mirrors/github.com/seeraven/gitcache
capture_output_success delete2_via_gitcache_stats -s

# Delete using invalid URL
# Delete using invalid path
# Delete more than one mirror at once


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
