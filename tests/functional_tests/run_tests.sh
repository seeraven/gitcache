#!/bin/bash -eu
# ----------------------------------------------------------------------------
# Functional tests for the gitcache command
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
#  SETTINGS
# ----------------------------------------------------------------------------
export TEST_BASE_DIR=$(dirname $(readlink -f $0))
BASE_DIR=$(dirname $(dirname $TEST_BASE_DIR))
GITCACHE_BIN=${BASE_DIR}/gitcache


# -----------------------------------------------------------------------------
# CHECK COMMAND LINE ARGUMENTS
# -----------------------------------------------------------------------------
SAVE_REFERENCE=0
VERBOSE=0
WAIT_ON_ERROR=0

function usage() {
    echo
    echo "Usage: $1 [-h] [-s] [-c|-p] [-v]"
    echo ""
    echo "Functional tests of gitcache."
    echo
    echo "Options:"
    echo " -h                : Print this help."
    echo " -s                : Save the gitcache output as reference."
    echo " -c                : Use the coverage wrapper."
    echo " -p                : Use the pyinstaller generated executable."
    echo " -v                : Be more verbose."
    exit 1
}

while getopts ":hscpv" OPT; do
    case $OPT in
        h )
            usage $0
            ;;
        s )
            SAVE_REFERENCE=1
            ;;
        c )
            GITCACHE_BIN="coverage run --append --rcfile=${BASE_DIR}/.coveragerc-functional $GITCACHE_BIN"
            ;;
        p )
            GITCACHE_BIN=${BASE_DIR}/dist/gitcache
            ;;
        v )
            VERBOSE=1
            ;;
        \? )
            usage $0
            ;;
    esac
done


# -----------------------------------------------------------------------------
# EXPORTS FOR TEST SCRIPTS
# -----------------------------------------------------------------------------
export EXPECTED_OUTPUT_DIR=$TEST_BASE_DIR/expected
mkdir -p ${EXPECTED_OUTPUT_DIR}
export GITCACHE_BIN
export SAVE_REFERENCE

export TMP_WORKDIR=$(mktemp --directory)
export GITCACHE_DIR=$(mktemp --directory)
export GITCACHE_REAL_GIT=/usr/bin/git
export GITCACHE_LOGFORMAT='%(message)s'


# -----------------------------------------------------------------------------
# RUN TESTS
# -----------------------------------------------------------------------------
RETVAL=0
TMPOUTPUT=$(tempfile)

for SCRIPT in ${TEST_BASE_DIR}/tests/*.sh; do
    echo -n "Running test $(basename $SCRIPT) ... "
    if $SCRIPT &> $TMPOUTPUT; then
        echo "OK"
        if [[ $VERBOSE -eq 1 ]]; then
            echo "-----------------------------------------------------------------"
            echo " Output:"
            cat $TMPOUTPUT
            echo "-----------------------------------------------------------------"
        fi
    else
        echo "FAILED"
        echo "-----------------------------------------------------------------"
        echo " Output:"
        cat $TMPOUTPUT
        echo "-----------------------------------------------------------------"
        RETVAL=1
    fi
done

rm -f $TMPOUTPUT
rm -rf $GITCACHE_DIR $TMP_WORKDIR

exit $RETVAL


# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
