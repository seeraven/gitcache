#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the ls-remote command.
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


REPO=https://github.com/seeraven/submodule-example.git

# Initial clone
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/submodule-example

# ls-remote updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/submodule-example ls-remote
assert_db_field mirror-updates of $REPO is 1
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0

# ls-remote specifying the remote url updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/submodule-example ls-remote $REPO
assert_db_field mirror-updates of $REPO is 2
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0

# ls-remote specifying the origin ref updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/submodule-example ls-remote origin
assert_db_field mirror-updates of $REPO is 3
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0

# ls-remote outside update interval does not update the mirror
export GITCACHE_UPDATE_INTERVAL=3600
gitcache_ok  git -C ${TMP_WORKDIR}/submodule-example ls-remote
assert_db_field mirror-updates of $REPO is 3
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0
export GITCACHE_UPDATE_INTERVAL=0

# ls-remote on non-managed repository
gitcache_ok  git clone ${TMP_WORKDIR}/submodule-example ${TMP_WORKDIR}/submodule-example5
git -C ${TMP_WORKDIR}/submodule-example5 remote set-url origin $REPO
gitcache_ok  git -C ${TMP_WORKDIR}/submodule-example5 ls-remote
assert_db_field clones of ${TMP_WORKDIR}/submodule-example is ''


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
