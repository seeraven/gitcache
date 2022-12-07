#!/bin/bash -e
#
# Collect pip dependencies for gitcache on Ubuntu
#

export DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true

cat > /tmp/tzdata_preseed <<EOF
tzdata tzdata/Areas select Europe
tzdata tzdata/Zones/Europe select Berlin
EOF
debconf-set-selections /tmp/tzdata_preseed

apt-get update
apt-get -y dist-upgrade

apt-get -y install lsb-release make binutils

if [ $(lsb_release -r -s) == "18.04" ]; then
    apt-get -y install software-properties-common
    add-apt-repository ppa:deadsnakes/ppa
    apt-get update
    apt-get -y install python3-venv python3.8-dev python3.8-venv
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2
else
    apt-get -y install python3-dev python3-venv
fi

ln -sf bash /bin/sh

function cleanup() {
    echo "Cleanup..."
    cd /workdir
    make clean || true
}
trap cleanup EXIT

cd /workdir
make clean
make pip-deps-upgrade.venv
chown $TGTUID:$TGTGID pip_deps/*.txt
