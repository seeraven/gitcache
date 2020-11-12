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


if [ $(lsb_release -r -s) == "16.04" ]; then
    echo "Skipped on 16.04 due to different git output on stdout/stderr."
    exit 0
fi


# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------
rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*

capture_output_success clone       git clone https://github.com/seeraven/submodule-example ${TMP_WORKDIR}/submodules
capture_output_success clone_stats -s

capture_output_success submodule_init       git -C ${TMP_WORKDIR}/submodules submodule init
capture_output_success submodule_init_stats -s

capture_output_success submodule_update       git -C ${TMP_WORKDIR}/submodules submodule update
capture_output_success submodule_update_stats -s

capture_output_success submodule_update_again       git -C ${TMP_WORKDIR}/submodules submodule update
capture_output_success submodule_update_again_stats -s


rm -rf ${GITCACHE_DIR}
rm -rf ${TMP_WORKDIR}/*

capture_output_success clone2       git clone https://github.com/seeraven/submodule-example ${TMP_WORKDIR}/submodules
capture_output_success clone2_stats -s

capture_output_success submodule_init_dmdcache       git -C ${TMP_WORKDIR}/submodules submodule init ${TMP_WORKDIR}/submodules/dmdcache
capture_output_success submodule_init_dmdcache_stats -s

capture_output_success submodule_update_dmdcache       git -C ${TMP_WORKDIR}/submodules submodule update ${TMP_WORKDIR}/submodules/dmdcache
capture_output_success submodule_update_dmdcache_stats -s

capture_output_success submodule_update_gitcache       git -C ${TMP_WORKDIR}/submodules submodule update --init ${TMP_WORKDIR}/submodules/gitcache
capture_output_success submodule_update_gitcache_stats -s


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------


