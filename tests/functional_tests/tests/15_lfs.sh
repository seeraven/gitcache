#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the git-lfs handling.
#
# Copyright (c) 2021 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh
source $TEST_BASE_DIR/helpers/test_helpers.sh


# -----------------------------------------------------------------------------
# Tests of git lfs fetch:
# -----------------------------------------------------------------------------

REPO=https://github.com/seeraven/lfs-example.git

# Initial clone ignoring git-lfs excluded entries
gitcache_ok  git -C ${TMP_WORKDIR} clone ${REPO}
assert_db_field mirror-updates of $REPO is 0
assert_db_field lfs-updates of $REPO is 1

if grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example/included/first.png; then
    echo "ERROR: Included git-lfs file should be fetched during clone!"
    exit 10
fi

if ! grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example/excluded/first.png; then
    echo "ERROR: Excluded git-lfs file should not be fetched!"
    exit 10
fi

# Fetching commands with no mirror update
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example lfs fetch
assert_db_field lfs-updates of $REPO is 1

gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example lfs fetch origin
assert_db_field lfs-updates of $REPO is 1

# Fetching commands with mirror update
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example lfs fetch --include '*' --exclude ''
assert_db_field lfs-updates of $REPO is 2

gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example lfs fetch origin --include '*' --exclude ''
assert_db_field lfs-updates of $REPO is 3

# Pulling excluded entries
if ! grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example/excluded/first.png; then
    echo "ERROR: Excluded git-lfs file should not be pulled yet!"
    exit 10
fi

# TODO: A git lfs pull is like a git pull and should be handled like a git lfs fetch
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example lfs pull --include '*' --exclude ''
assert_db_field lfs-updates of $REPO is 3

if grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example/excluded/first.png; then
    echo "ERROR: Included git-lfs file should be pulled during git lfs pull!"
    exit 10
fi


# -----------------------------------------------------------------------------
# Tests of git lfs pull:
# -----------------------------------------------------------------------------

gitcache_ok  -d ${REPO}
gitcache_ok  git -C ${TMP_WORKDIR} clone ${REPO} lfs-example2
assert_db_field lfs-updates of $REPO is 1

if ! grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example2/excluded/first.png; then
    echo "ERROR: Excluded git-lfs file should not be pulled yet!"
    exit 10
fi

# TODO: A git lfs pull is like a git pull and should be handled like a git lfs fetch
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example2 lfs pull --include '*' --exclude ''
assert_db_field lfs-updates of $REPO is 1

if grep -q "oid sha256" ${TMP_WORKDIR}/lfs-example2/excluded/first.png; then
    echo "ERROR: Included git-lfs file should be pulled during git lfs pull!"
    exit 10
fi


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
