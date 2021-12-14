#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the clone command.
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

# Command without arguments yields an error (error code 129)
run_gitcache 129  git clone

# Initial clone
gitcache_ok  git -C ${TMP_WORKDIR} clone $REPO
assert_db_field mirror-updates of $REPO is 0
assert_db_field clones of $REPO is 1
assert_remote_of_clone ${TMP_WORKDIR}/gitcache
assert_branch ${TMP_WORKDIR}/gitcache master

# Second clone with update of the mirror
gitcache_ok  git clone https://github.com/seeraven/gitcache     ${TMP_WORKDIR}/gitcache2
assert_db_field mirror-updates of $REPO is 1
assert_db_field clones of $REPO is 2
assert_remote_of_clone ${TMP_WORKDIR}/gitcache2

# Third clone without updating the mirror
export GITCACHE_UPDATE_INTERVAL=3600
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache3
assert_db_field mirror-updates of $REPO is 1
assert_db_field clones of $REPO is 3
assert_remote_of_clone ${TMP_WORKDIR}/gitcache3
export GITCACHE_UPDATE_INTERVAL=0

# Fourth clone with updating the mirror
gitcache_ok  git -C ${TMP_WORKDIR} clone $REPO gitcache4
assert_db_field mirror-updates of $REPO is 2
assert_db_field clones of $REPO is 4
assert_remote_of_clone ${TMP_WORKDIR}/gitcache4

# Error during clone
gitcache_error  git clone https://github.com/seeraven/nonexistant ${TMP_WORKDIR}/dummy

# Clone from another directory to skip update
REPO=${TMP_WORKDIR}/gitcache
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/gitcache5
assert_db_field clones of $REPO is ''

# Clone an explicit branch
REPO=https://github.com/seeraven/scm-autologin-plugin
gitcache_ok  git clone --branch feature_ownUserType $REPO ${TMP_WORKDIR}/scm-autologin-plugin
assert_db_field mirror-updates of $REPO is 0
assert_db_field clones of $REPO is 1
assert_remote_of_clone ${TMP_WORKDIR}/scm-autologin-plugin
assert_branch ${TMP_WORKDIR}/scm-autologin-plugin feature_ownUserType

# Clone an explicit tag
gitcache_ok  git clone --branch 1.0-scm1.60 $REPO ${TMP_WORKDIR}/scm-autologin-plugin2
assert_db_field mirror-updates of $REPO is 1
assert_db_field clones of $REPO is 2
assert_remote_of_clone ${TMP_WORKDIR}/scm-autologin-plugin2
assert_tag ${TMP_WORKDIR}/scm-autologin-plugin2 1.0-scm1.60

# Clone with the branch option given at the end of the clone command
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/scm-autologin-plugin3 -b feature_ownUserType
assert_db_field mirror-updates of $REPO is 2
assert_db_field clones of $REPO is 3
assert_remote_of_clone ${TMP_WORKDIR}/scm-autologin-plugin3
assert_branch ${TMP_WORKDIR}/scm-autologin-plugin3 feature_ownUserType


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
