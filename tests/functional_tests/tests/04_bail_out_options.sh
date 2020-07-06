#!/bin/bash -e
# ----------------------------------------------------------------------------
# Check the bail out git options.
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


EXPECTED_OUTPUT_PREFIX=$(basename $0 .sh)
source $TEST_BASE_DIR/helpers/output_helpers.sh


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*

capture_output_success version   git --version
capture_output_success exec_path git --exec-path
capture_output_success html_path git --html-path
capture_output_success man_path  git --man-path
capture_output_success info_path git --info-path


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
