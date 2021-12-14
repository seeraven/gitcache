#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the version command.
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
#  Test 'gitcache --version' that prints the current version. We do not test
#  for the output but rather the return code.
# -----------------------------------------------------------------------------
gitcache_ok --version
assert_gitcache_dir_does_not_exist


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
