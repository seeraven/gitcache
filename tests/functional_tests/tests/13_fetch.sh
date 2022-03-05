#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the fetch command.
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

# Fetch updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch
assert_db_field mirror-updates of $REPO is 1
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 1

# Fetch with explicit origin url updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch $REPO
assert_db_field mirror-updates of $REPO is 2
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 2

# Fetch with origin ref updates the mirror
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch origin
assert_db_field mirror-updates of $REPO is 3
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 3

# Fetch outside update interval does not update the mirror
export GITCACHE_UPDATE_INTERVAL=3600
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch
assert_db_field mirror-updates of $REPO is 3
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 4
export GITCACHE_UPDATE_INTERVAL=0

# Fetch on non-managed repository
gitcache_ok  git clone ${TMP_WORKDIR}/gitcache ${TMP_WORKDIR}/gitcache5
git -C ${TMP_WORKDIR}/gitcache5 remote set-url origin $REPO
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache5 fetch
assert_db_field clones of ${TMP_WORKDIR}/gitcache is ''

# Fetch from within directory
pushd ${TMP_WORKDIR}/gitcache
gitcache_ok  git fetch
assert_db_field mirror-updates of $REPO is 4
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 5
popd

# Explicit exclude of the fetch URL
export GITCACHE_URLPATTERNS_INCLUDE_REGEX='.*'
export GITCACHE_URLPATTERNS_EXCLUDE_REGEX='.*/github\.com/.*'
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch $REPO
assert_db_field mirror-updates of $REPO is 4
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 5

# Explicit include of the fetch URL
export GITCACHE_URLPATTERNS_INCLUDE_REGEX='.*/github\.com/.*'
export GITCACHE_URLPATTERNS_EXCLUDE_REGEX=''
gitcache_ok  git -C ${TMP_WORKDIR}/gitcache fetch $REPO
assert_db_field mirror-updates of $REPO is 5
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 6


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
