#!/bin/bash -e
#
# Build and test gitcache on Ubuntu 16.04, 18.04 and 20.04
#

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true

cat > /tmp/tzdata_preseed <<EOF
tzdata tzdata/Areas select Europe
tzdata tzdata/Zones/Europe select Berlin
EOF
debconf-set-selections /tmp/tzdata_preseed

apt-get update
apt-get -y dist-upgrade

apt-get -y install curl software-properties-common
add-apt-repository ppa:git-core/ppa -y
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | /bin/bash
apt-get update

apt-get -y install lsb-release make python3-dev python3-venv binutils git git-lfs

ln -sf bash /bin/sh

if [ $(lsb_release -r -s) == "21.04" ]; then
    git config --global pull.rebase false
fi

cd /workdir
git lfs install
make clean
make unittests.venv
make pyinstaller.venv
make pyinstaller-test
make clean
