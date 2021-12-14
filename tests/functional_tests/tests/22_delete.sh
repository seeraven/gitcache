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
source $TEST_BASE_DIR/helpers/test_helpers.sh


REPO=https://github.com/seeraven/gitcache.git
REPO2=https://github.com/seeraven/submodule-example

# Delete giving the URL
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
gitcache_ok  git delete-mirror $REPO
assert_db_field mirror-updates of $REPO is ''
rm -rf ${TMP_WORKDIR}/gitcache

# Delete giving the path
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
gitcache_ok  git delete-mirror ${GITCACHE_DIR}/mirrors/github.com/seeraven/gitcache
assert_db_field mirror-updates of $REPO is ''
rm -rf ${TMP_WORKDIR}/gitcache

# Delete using gitcache command
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
gitcache_ok  -d $REPO
assert_db_field mirror-updates of $REPO is ''
rm -rf ${TMP_WORKDIR}/gitcache

# Delete using gitcache command giving the path
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache
gitcache_ok  -d ${GITCACHE_DIR}/mirrors/github.com/seeraven/gitcache
assert_db_field mirror-updates of $REPO is ''
rm -rf ${TMP_WORKDIR}/gitcache

# Delete using invalid URL
gitcache_ok     git clone $REPO ${TMP_WORKDIR}/gitcache
gitcache_error  -d https://github.com/seeraven/gatcache.git
rm -rf ${TMP_WORKDIR}/gitcache

# Delete using invalid path
gitcache_error  -d ${GITCACHE_DIR}/mirrors/github.com/seeraven/gatcache

# Delete more than one mirror at once
gitcache_ok  git clone $REPO2 ${TMP_WORKDIR}/submodules
gitcache_ok  -d $REPO -d $REPO2
assert_db_field mirror-updates of $REPO is ''
assert_db_field mirror-updates of $REPO2 is ''
rm -rf ${TMP_WORKDIR}/submodules


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
