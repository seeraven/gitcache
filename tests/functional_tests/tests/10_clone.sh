#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the clone output.
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

# Initial clone and updating the mirror
capture_output_success clone git -C ${TMP_WORKDIR} clone https://github.com/seeraven/gitcache.git
capture_output_success clone_stats -s

capture_output_success clone_again git clone https://github.com/seeraven/gitcache     ${TMP_WORKDIR}/gitcache2
capture_output_success clone_again_stats -s

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success clone_without_update git clone https://github.com/seeraven/gitcache ${TMP_WORKDIR}/gitcache3
capture_output_success clone_without_update_stats -s
export GITCACHE_UPDATE_INTERVAL=0

capture_output_success clone_relative git -C ${TMP_WORKDIR} clone https://github.com/seeraven/gitcache gitcache4
capture_output_success clone_relative_stats -s

# Error during clone
capture_output_failure clone_error git clone https://github.com/seeraven/nonexistant ${TMP_WORKDIR}/dummy

# Clone from another directory to skip update
capture_output_success clone_directory git clone ${TMP_WORKDIR}/gitcache ${TMP_WORKDIR}/gitcache5

# Clone an explicit branch
capture_output_success clone_branch       git clone --branch feature_ownUserType https://github.com/seeraven/scm-autologin-plugin ${TMP_WORKDIR}/scm-autologin-plugin
capture_output_success clone_branch_stats -s

# Clone an explicit tag
capture_output_success clone_tag          git clone --branch 1.0-scm1.60 https://github.com/seeraven/scm-autologin-plugin ${TMP_WORKDIR}/scm-autologin-plugin2
capture_output_success clone_tag_stats    -s


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
