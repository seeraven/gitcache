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

    capture_output_success ${PREFIX}_clone       git clone https://github.com/seeraven/submodule-example ${TMP_WORKDIR}/submodules
    capture_output_success ${PREFIX}_clone_stats -s

    pushd $WDIR
    capture_output_success ${PREFIX}_submodule_init       git $@ submodule init
    capture_output_success ${PREFIX}_submodule_init_stats -s
    
    capture_output_success ${PREFIX}_submodule_update       git $@ submodule update
    capture_output_success ${PREFIX}_submodule_update_stats -s

    capture_output_success ${PREFIX}_submodule_update_again       git $@ submodule update
    capture_output_success ${PREFIX}_submodule_update_again_stats -s
    popd

    rm -rf ${GITCACHE_DIR}
    rm -rf ${TMP_WORKDIR}/*

    capture_output_success ${PREFIX}_clone2       git clone https://github.com/seeraven/submodule-example ${TMP_WORKDIR}/submodules
    capture_output_success ${PREFIX}_clone2_stats -s

    pushd $WDIR
    capture_output_success ${PREFIX}_submodule_init_dmdcache       git $@ submodule init ${SUBPATH}dmdcache
    capture_output_success ${PREFIX}_submodule_init_dmdcache_stats -s

    capture_output_success ${PREFIX}_submodule_update_dmdcache       git $@ submodule update ${SUBPATH}dmdcache
    capture_output_success ${PREFIX}_submodule_update_dmdcache_stats -s

    capture_output_success ${PREFIX}_submodule_update_gitcache       git $@ submodule update --init ${SUBPATH}gitcache
    capture_output_success ${PREFIX}_submodule_update_gitcache_stats -s
    popd
}

test_variation single_C $PWD ${TMP_WORKDIR}/submodules/ -C ${TMP_WORKDIR}/submodules
test_variation multi_C  $PWD ${TMP_WORKDIR}/submodules/ -C ${TMP_WORKDIR} -C submodules
test_variation no_C     ${TMP_WORKDIR}/submodules ""


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------


