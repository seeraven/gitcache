# ----------------------------------------------------------------------------
# Helper functions for the functional tests.
#
# Copyright (c) 2021 by Clemens Rabe <clemens.rabe@clemensrabe.de>
# All rights reserved.
# This file is part of gitcache (https://github.com/seeraven/gitcache)
# and is released under the "BSD 3-Clause License". Please see the LICENSE file
# that is included as part of this package.
# ----------------------------------------------------------------------------

# Usage: assert_dir_exists <dir> <short name>
function assert_dir_exists()
{
    RETVAL=0

    if [ -d "$1" ]; then
        echo "INFO: $2 directory ($1) exists."
    else
        echo "ERROR: $2 directory ($1) does not exist!"
        RETVAL=10
    fi

    return $RETVAL
}

# Usage: assert_dir_does_not_exist <dir> <short_name>
function assert_dir_does_not_exist()
{
    RETVAL=0

    if [ -d "$1" ]; then
        echo "ERROR: $2 directory ($1) exists!"
        RETVAL=10
    else
        echo "INFO: $2 directory ($1) does not exist."
    fi

    return $RETVAL
}

# Usage: assert_file_exists <file> <short name>
function assert_file_exists()
{
    RETVAL=0

    if [ -e "$1" ]; then
        echo "INFO: $2 file ($1) exists."
    else
        echo "ERROR: $2 file ($1) does not exist!"
        RETVAL=10
    fi

    return $RETVAL
}

# Usage: assert_file_does_not_exist <file> <short name>
function assert_file_does_not_exist()
{
    RETVAL=0

    if [ -e "$1" ]; then
        echo "ERROR: $2 file ($1) exists!"
        RETVAL=10
    else
        echo "INFO: $2 file ($1) does not exist."
    fi

    return $RETVAL
}

# Usage: assert_gitcache_dir_exists
function assert_gitcache_dir_exists()
{
    assert_dir_exists "${GITCACHE_DIR}" "gitcache"
}

# Usage: assert_gitcache_dir_does_not_exist
function assert_gitcache_dir_does_not_exist()
{
    assert_dir_does_not_exist "${GITCACHE_DIR}" "gitcache"
}

# Usage: assert_gitcache_config_exists
function assert_gitcache_config_exists()
{
    assert_file_exists "${GITCACHE_DIR}/config" "gitcache config"
}

# Usage: assert_gitcache_config_does_not_exist
function assert_gitcache_config_does_not_exist()
{
    assert_file_does_not_exist "${GITCACHE_DIR}/config" "gitcache config"
}

# Usage: assert_gitcache_db_exists
function assert_gitcache_db_exists()
{
    assert_file_exists "${GITCACHE_DIR}/db" "gitcache database"
}

# Usage: assert_gitcache_db_does_not_exist
function assert_gitcache_db_does_not_exist()
{
    assert_file_does_not_exist "${GITCACHE_DIR}/db" "gitcache database"
}

# Usage: get_db_field [mirror-updates|clones|updates] <url>
function get_db_field()
{
    jq '.[] | select(.url=="'$2'") | .["'$1'"]' < "${GITCACHE_DIR}/db"
}

# Usage: assert_db_field [mirror-updates|clones|updates] of <url> is <value>
function assert_db_field()
{
    DB_FIELD=$(get_db_field "$1" "$3")
    RETVAL=0

    if [ "${DB_FIELD}" != "$5" ]; then
        echo "ERROR: Field $1 of mirror for $3 should be $5!"
        echo "       However, the current value is ${DB_FIELD}!"
        RETVAL=10
    fi

    return $RETVAL
}

# Usage: assert_remote_of_clone <dir>
function assert_remote_of_clone()
{
    FETCH_URL=$(git -C "$1" remote get-url origin)
    RETVAL=0

    if [[ ${FETCH_URL} != ${GITCACHE_DIR}/* ]]; then
        echo "ERROR: Fetch URL of clone $1 does not point to gitcache dir!"
        echo "       Fetch URL is ${FETCH_URL}"
        RETVAL=10
    fi

    return $RETVAL
}

# Usage: assert_branch <dir> <branch>
function assert_branch()
{
    BRANCH=$(git -C "$1" rev-parse --abbrev-ref HEAD)
    RETVAL=0

    if [ "$BRANCH" != "$2" ]; then
        echo "ERROR: Checked out repository is on branch $BRANCH but should be on branch $2!"
        RETVAL=10
    fi

    return $RETVAL
}

# Usage: assert_tag <dir> <tag>
function assert_tag()
{
    TAG=$(git -C "$1" describe --tags)
    RETVAL=0

    if [ "$TAG" != "$2" ]; then
        echo "ERROR: Checked out repository is on tag $TAG but should be on tag $2!"
        RETVAL=10
    fi

    return $RETVAL
}

# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
