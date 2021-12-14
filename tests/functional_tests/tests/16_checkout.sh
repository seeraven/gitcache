#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the checkout command.
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


REPO=https://github.com/seeraven/lfs-example.git

# Initial clone
gitcache_ok  git -C ${TMP_WORKDIR} clone ${REPO}
assert_db_field mirror-updates of $REPO is 0
assert_db_field lfs-updates of $REPO is 1

# Modify a file and perform checkout call to restore it
rm -f ${TMP_WORKDIR}/lfs-example/README.md
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example checkout README.md
assert_file_exists ${TMP_WORKDIR}/lfs-example/README.md "previously deleted"

# Checkout command using the branch specified
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example checkout main

LFS_OBJ_FILE=${GITCACHE_DIR}/mirrors/github.com/seeraven/lfs-example/lfs/objects/c0/c9/c0c955aa4aa976424645d86e82ba4452bb715364171e7db3bf715214b2cfb99d

# gitcache checkout command using a new branch should fetch additional files
gitcache_ok  git -C ${TMP_WORKDIR}/lfs-example checkout extra_branch

if [ ! -e ${LFS_OBJ_FILE} ]; then
    echo "ERROR: git-lfs file on extra branch should be fetched by gitcache checkout!"
    exit 10
fi


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
