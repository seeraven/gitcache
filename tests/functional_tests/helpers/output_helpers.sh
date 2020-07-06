# ----------------------------------------------------------------------------
# Helper functions for the functional tests.
#
# Copyright (c) 2020 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------

# Usage: capture_output <expected retval> <name> <args>
function capture_output()
{
    STDOUT_FILE=$(tempfile)
    STDERR_FILE=$(tempfile)

    EXPECTED_RETVAL=$1
    shift

    EXPECTED_STDOUT_FILE=${EXPECTED_OUTPUT_DIR}/${EXPECTED_OUTPUT_PREFIX}_$1_stdout.txt
    EXPECTED_STDERR_FILE=${EXPECTED_OUTPUT_DIR}/${EXPECTED_OUTPUT_PREFIX}_$1_stderr.txt
    shift

    set +e
    $GITCACHE_BIN $@ > $STDOUT_FILE 2> $STDERR_FILE
    RETVAL=$?
    set -e

    if [ $RETVAL != $EXPECTED_RETVAL ]; then
        echo "ERROR: Command gitcache $@ gave unexpected return value $RETVAL (expected ${EXPECTED_RETVAL})"
        RETVAL=10
    else
        RETVAL=0
    fi

    # Replace substitutions of the variables
    sed -i "s#${GITCACHE_DIR}#GITCACHE_DIR#g" $STDOUT_FILE $STDERR_FILE
    sed -i "s#${TMP_WORKDIR}#TMP_WORKDIR#g"   $STDOUT_FILE $STDERR_FILE
    sed -i 's# [0-9][0-9.]* seconds# TIME#g'  $STDOUT_FILE $STDERR_FILE
    sed -i '/^remote: .*$/d'                  $STDOUT_FILE $STDERR_FILE
    sed -i '/^Receiving objects: .*$/d'       $STDOUT_FILE $STDERR_FILE
    sed -i '/^Resolving deltas: .*$/d'        $STDOUT_FILE $STDERR_FILE
    sed -i '/^Unpacking objects: .*$/d'       $STDOUT_FILE $STDERR_FILE

    if [ "$SAVE_REFERENCE" == "1" ]; then
        cp $STDOUT_FILE $EXPECTED_STDOUT_FILE
        cp $STDERR_FILE $EXPECTED_STDERR_FILE
    else
        if ! cmp -s $STDOUT_FILE $EXPECTED_STDOUT_FILE; then
            echo "ERROR: Command gitcache $@ gave unexpected stdout output:"
            cat $STDOUT_FILE
            echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
            if [ -e $EXPECTED_STDOUT_FILE ]; then
                echo "Stdout diff:"
                diff $STDOUT_FILE $EXPECTED_STDOUT_FILE
                echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
            fi
            RETVAL=10
        fi
        if ! cmp -s $STDERR_FILE $EXPECTED_STDERR_FILE; then
            echo "ERROR: Command gitcache $@ gave unexpected sterr output:"
            cat $STDERR_FILE
            echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
            if [ -e $EXPECTED_STDERR_FILE ]; then
                echo "Stderr diff:"
                diff $STDERR_FILE $EXPECTED_STDERR_FILE
                echo "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
            fi
            RETVAL=10
        fi
    fi

    rm -f $STDOUT_FILE $STDERR_FILE

    return $RETVAL
}

# Usage: capture_output_success <name> <args>
function capture_output_success()
{
    capture_output 0 $@
}

# Usage: capture_output_failure <name> <args>
function capture_output_failure()
{
    capture_output 1 $@
}

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
