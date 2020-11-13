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
# Tests:
#   - Pull using 'git -C <dir> pull' syntax.
#   - Pull using 'git -C <dir> -C <dir> pull' syntax.
#   - Pull using 'git pull' syntax within <dir>.
#   - Pull using update interval of 1h to avoid cache update.
# -----------------------------------------------------------------------------
capture_output_success clone git clone https://github.com/seeraven/gitcache.git ${TMP_WORKDIR}/gitcache

capture_output_success pull       git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_stats -s

capture_output_success pull_multi_C       git -C ${TMP_WORKDIR} -C gitcache pull
capture_output_success pull_multi_C_stats -s

pushd ${TMP_WORKDIR}/gitcache
capture_output_success pull_in_dir       git pull
capture_output_success pull_in_dir_stats -s
popd

export GITCACHE_UPDATE_INTERVAL=3600
capture_output_success pull_without_update       git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_without_update_stats -s
export GITCACHE_UPDATE_INTERVAL=0

# Do not update mirror if repository does not use the mirror
git -C ${TMP_WORKDIR}/gitcache remote set-url origin https://github.com/seeraven/gitcache.git
capture_output_success pull_non_mirror       git -C ${TMP_WORKDIR}/gitcache pull
capture_output_success pull_non_mirror_stats -s


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
