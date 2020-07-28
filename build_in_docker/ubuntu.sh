#!/bin/bash -e
#
# Build gitcache on Ubuntu 16.04, 18.04 and 20.04
#

apt-get update
apt-get -y dist-upgrade

apt-get -y install lsb-release make python3-dev python3-venv binutils git

if [ $(lsb_release -r -s) == "16.04" ]; then
    apt-get -y install curl
    curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | /bin/bash
fi
apt-get -y install git-lfs

ln -sf bash /bin/sh

cd /workdir
make clean
make unittests.venv
make pyinstaller.venv
make pyinstaller-test

mv dist/gitcache releases/gitcache_$(lsb_release -i -s)$(lsb_release -r -s)_amd64
chown $TGTUID:$TGTGID releases/gitcache_$(lsb_release -i -s)$(lsb_release -r -s)_amd64

make clean
