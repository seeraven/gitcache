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
source $TEST_BASE_DIR/helpers/test_helpers.sh


REPO=https://github.com/seeraven/gitcache.git

# Update mirrors without any active mirror
gitcache_ok  git update-mirrors
gitcache_ok  -u

# Initial clone
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
assert_db_field mirror-updates of $REPO is 0

# Update with 'git update-mirrors'
gitcache_ok  git update-mirrors
assert_db_field mirror-updates of $REPO is 1

# Update with 'gitcache -u'
gitcache_ok  -u
assert_db_field mirror-updates of $REPO is 2

# Explicit update ignores update interval
export GITCACHE_UPDATE_INTERVAL=3600
gitcache_ok  git update-mirrors
assert_db_field mirror-updates of $REPO is 3
export GITCACHE_UPDATE_INTERVAL=0


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
