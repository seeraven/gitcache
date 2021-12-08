#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the cleanup.
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

# Initial clone
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache

# Cleanup with 'git cleanup'
export GITCACHE_CLEANUP_AFTER=1
sleep 2s
gitcache_ok  git cleanup
assert_db_field mirror-updates of $REPO is ''

# Clone again
rm -rf ${TMP_WORKDIR}/gitcache
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache

# Cleanup with 'gitcache -c'
sleep 2s
gitcache_ok  -c
assert_db_field mirror-updates of $REPO is ''
export GITCACHE_CLEANUP_AFTER=3600


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
