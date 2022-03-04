#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the submodule update.
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


REPO=https://github.com/seeraven/submodule-example

# test_variation <prefix> <working dir> <relative path prefix> <git_c_options>
function test_variation() {
    PREFIX=$1
    shift
    WDIR=$1
    shift
    SUBPATH=$1
    shift

    rm -rf ${GITCACHE_DIR}
    rm -rf ${TMP_WORKDIR}/*

    # Initial clone
    gitcache_ok  git clone $REPO ${TMP_WORKDIR}/submodules
    assert_db_field mirror-updates of $REPO is 0
    assert_db_field clones of $REPO is 1
    assert_db_field updates of $REPO is 0

    pushd $WDIR
    # Submodule init does not update the mirror nor does it perform any clones
    gitcache_ok  git $@ submodule init
    assert_db_field mirror-updates of $REPO is 0
    assert_db_field clones of $REPO is 1
    assert_db_field updates of $REPO is 0
    assert_db_field mirror-updates of https://github.com/seeraven/dmdcache is ''
    assert_db_field mirror-updates of https://github.com/seeraven/gitcache is ''

    # Submodule update does not update the mirror of this repo ...
    gitcache_ok  git $@ submodule update
    assert_db_field mirror-updates of $REPO is 0
    assert_db_field clones of $REPO is 1
    assert_db_field updates of $REPO is 0

    # ... but it clones the submodule repos
    assert_db_field clones of https://github.com/seeraven/dmdcache is 1
    assert_db_field clones of https://github.com/seeraven/gitcache is 1

    # Another submodule update updates the mirrors
    gitcache_ok  git $@ submodule update
    assert_db_field mirror-updates of https://github.com/seeraven/dmdcache is 1
    assert_db_field mirror-updates of https://github.com/seeraven/gitcache is 1
    assert_db_field updates of https://github.com/seeraven/dmdcache is 1
    assert_db_field updates of https://github.com/seeraven/gitcache is 1
    popd

    rm -rf ${GITCACHE_DIR}
    rm -rf ${TMP_WORKDIR}/*

    # Initial clone
    gitcache_ok  git clone $REPO ${TMP_WORKDIR}/submodules

    pushd $WDIR
    # Submodule init does not update the mirror nor does it perform any clones
    gitcache_ok  git $@ submodule init ${SUBPATH}dmdcache
    assert_db_field mirror-updates of $REPO is 0
    assert_db_field clones of $REPO is 1
    assert_db_field updates of $REPO is 0
    assert_db_field mirror-updates of https://github.com/seeraven/dmdcache is ''
    assert_db_field mirror-updates of https://github.com/seeraven/gitcache is ''

    # Submodule update with a path updates only that path
    gitcache_ok  git $@ submodule update ${SUBPATH}dmdcache
    assert_db_field clones of https://github.com/seeraven/dmdcache is 1
    assert_db_field clones of https://github.com/seeraven/gitcache is ''

    # Submodule update with --init option also initializes the reference
    gitcache_ok  git $@ submodule update --init ${SUBPATH}gitcache
    assert_db_field clones of https://github.com/seeraven/gitcache is 1
    popd
}

test_variation single_C $PWD ${TMP_WORKDIR}/submodules/ -C ${TMP_WORKDIR}/submodules
test_variation multi_C  $PWD ${TMP_WORKDIR}/submodules/ -C ${TMP_WORKDIR} -C submodules
test_variation no_C     ${TMP_WORKDIR}/submodules ""


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
