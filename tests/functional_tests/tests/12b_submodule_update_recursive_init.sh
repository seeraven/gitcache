#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the submodule update with the options --recursive --init on a
# real-world example.
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


REPO=https://github.com/aws/aws-sdk-cpp

# Initial clone
gitcache_ok  git clone $REPO ${TMP_WORKDIR}/aws-sdk-cpp --single-branch --branch 1.9.188
assert_db_field mirror-updates of $REPO is 0
assert_db_field clones of $REPO is 1
assert_db_field updates of $REPO is 0

pushd ${TMP_WORKDIR}/aws-sdk-cpp
gitcache_ok  git submodule update --recursive --init
assert_db_field clones of https://github.com/awslabs/aws-crt-cpp.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-common.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-io.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-compression.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-cal.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-auth.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-http.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-mqtt.git is 1
assert_db_field clones of https://github.com/awslabs/s2n.git is 1
assert_db_field clones of https://github.com/awslabs/aws-checksums.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-event-stream.git is 1
assert_db_field clones of https://github.com/awslabs/aws-c-s3.git is 1
assert_db_field clones of https://github.com/awslabs/aws-lc.git is 1
assert_db_field clones of https://github.com/awslabs/aws-templates-for-cbmc-proofs.git is 2
popd


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
