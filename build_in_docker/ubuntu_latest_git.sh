#!/bin/bash -e
#
# Test gitcache on Ubuntu with the latest git version available
#

# Usage: ubuntu_test.sh [--latest] [--no-lfs] [--no-lfs-install] [--pyinstaller]
USE_LATEST_GIT=0
NO_LFS=0
NO_LFS_INSTALL=0
USE_PYINSTALLER=0
while [[ $# -ge 1 ]]; do
    case $1 in
        --latest)
            USE_LATEST_GIT=1
            ;;
        --no-lfs)
            NO_LFS=1
            ;;
        --no-lfs-install)
            NO_LFS_INSTALL=1
            ;;
        --pyinstaller)
            USE_PYINSTALLER=1
            ;;
        -*)
            echo "ERROR: Unknown option $1"
            exit 1
            ;;
    esac
    shift
done

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true

cat > /tmp/tzdata_preseed <<EOF
tzdata tzdata/Areas select Europe
tzdata tzdata/Zones/Europe select Berlin
EOF
debconf-set-selections /tmp/tzdata_preseed

apt-get update
apt-get -y dist-upgrade

if [[ $USE_LATEST_GIT -eq 1 ]]; then
    apt-get -y install curl software-properties-common
    add-apt-repository ppa:git-core/ppa -y
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | /bin/bash
    apt-get update
fi

apt-get -y install lsb-release make python3-dev python3-venv binutils git jq
if [[ $NO_LFS -eq 0 ]]; then
    apt-get -y install git-lfs
fi

ln -sf bash /bin/sh

if [ $(lsb_release -r -s) == "21.04" ]; then
    git config --global pull.rebase false
fi

cd /workdir
if [[ $NO_LFS -eq 0 ]]; then
    if [[ $NO_LFS_INSTALL -eq 0 ]]; then
        git lfs install
    fi
fi

RETCODE=0
make clean

if [[ $USE_PYINSTALLER -eq 1 ]]; then
    make unittests.venv pyinstaller.venv pyinstaller-test || RETCODE=$?
else
    make tests.venv || RETCODE=$?
fi
make clean

exit $RETCODE
