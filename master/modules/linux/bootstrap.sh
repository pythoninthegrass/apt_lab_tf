#!/usr/bin/env bash

set -euo pipefail

# install python3.11
apt update && apt install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt update && apt install -y python3.11 python3.11-venv p7zip-full tree

# set path for pip
logged_in_user=$(logname)
logged_in_home=$(eval echo "~${logged_in_user}")
export PATH=${PATH//":${logged_in_home}/.local/bin"/}

# install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# install tools
chmod 777 /opt
cd /opt/
wget https://github.com/pythoninthegrass/apt_lab_tf_linux/raw/master/linuxtools.7z
7z x /opt/linuxtools.7z
mkdir -p /opt/SilentTrinity
mkdir -p /opt/CrackMapExec
mv /opt/st /opt/SilentTrinity/
mv /opt/cme* /opt/CrackMapExec/
rm /opt/linuxtools.7z
git clone https://github.com/lgandx/Responder.git /opt/Responder

# install impacket and setup venv
git clone https://github.com/SecureAuthCorp/impacket.git /opt/impacket
cd /opt/impacket
python3.11 -m venv env

# clone and run helk container
git clone https://github.com/Cyb3rWard0g/HELK.git /opt/HELK
cd /opt/HELK/docker
./helk_install.sh -p hunting -i 10.10.98.20 -b 'helk-kibana-analysis-alert'
