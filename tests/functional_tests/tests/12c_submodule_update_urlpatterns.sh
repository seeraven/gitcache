#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the submodule update with exclude and include patterns.
#
# Copyright (c) 2022 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh
source $TEST_BASE_DIR/helpers/test_helpers.sh


REPO=https://github.com/seeraven/submodule-example

# Explicit exclude of *dmdcache repositories
export GITCACHE_URLPATTERNS_INCLUDE_REGEX='.*'
export GITCACHE_URLPATTERNS_EXCLUDE_REGEX='.*/github\.com/seeraven/.*dmdcache'
rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/submodules
assert_db_field mirror-updates of $REPO is 0
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0

gitcache_ok  git -C ${TMP_WORKDIR}/submodules submodule update --init
assert_db_field clones of https://github.com/seeraven/dmdcache is ''
assert_db_field clones of https://github.com/seeraven/gitcache is 1

# Explicit include of *dmdcache repositories
export GITCACHE_URLPATTERNS_INCLUDE_REGEX='.*/github\.com/seeraven/.*dmdcache'
export GITCACHE_URLPATTERNS_EXCLUDE_REGEX=''
rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/submodules
gitcache_ok  git -C ${TMP_WORKDIR}/submodules submodule update --init
assert_db_field clones of https://github.com/seeraven/dmdcache is 1
assert_db_field clones of https://github.com/seeraven/gitcache is ''


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
