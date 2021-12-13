#!/bin/bash -e
#
# Build gitcache on Ubuntu 18.04, 20.04 and 21.04
#

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true

cat > /tmp/tzdata_preseed <<EOF
tzdata tzdata/Areas select Europe
tzdata tzdata/Zones/Europe select Berlin
EOF
debconf-set-selections /tmp/tzdata_preseed

apt-get update
apt-get -y dist-upgrade

apt-get -y install lsb-release make python3-dev python3-venv binutils git git-lfs jq

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

mv dist/gitcache releases/gitcache_$(lsb_release -i -s)$(lsb_release -r -s)_amd64
chown $TGTUID:$TGTGID releases/gitcache_$(lsb_release -i -s)$(lsb_release -r -s)_amd64

make clean
