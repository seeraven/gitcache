#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the statistics.
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh
source $TEST_BASE_DIR/helpers/test_helpers.sh


REPO=https://github.com/seeraven/gitcache.git

# -----------------------------------------------------------------------------
# Tests:
#   - Test the initial statistics output by calling 'gitcache -s'
#   - Test the statistics after a clone by calling 'gitcache -s'
#   - Test clearing the statistics by calling 'gitcache -z'
# -----------------------------------------------------------------------------

# Initial statistics returned by 'gitcache -s'
capture_output_success init_stats  -s
assert_gitcache_dir_exists
assert_gitcache_config_does_not_exist
assert_gitcache_db_does_not_exist

# Clone via 'gitcache git clone ...'
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
assert_gitcache_config_exists
assert_gitcache_db_exists
assert_db_field clones of $REPO is 1

# After clone statistics returned by 'gitcache -s'
capture_output_success clone_stats -s

# Zero statistics with 'gitcache -z' and check empty statistics returned by 'gitcache -s'
gitcache_ok  -z
assert_db_field clones of $REPO is 0
capture_output_success clone_zeroed_stats -s


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
